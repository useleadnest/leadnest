from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import logging, csv, io, os

from twilio.rest import Client
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from redis import Redis
from rq import Queue

from marshmallow import Schema, fields, validate
from sqlalchemy import text

from .auth import require_auth, issue_token
from .db import db
from .models import Lead, Booking, Business, Conversation, Message, IdempotencyKey
from .__init__ import limiter
from .tasks import enqueue_bulk_import

log = logging.getLogger(__name__)

# Import competitive advantage services
try:
    import sys
    import os
    services_path = os.path.join(os.path.dirname(__file__), '..', 'services')
    if services_path not in sys.path:
        sys.path.append(services_path)
    
    from ai_lead_scorer import AILeadScorer
    from roi_calculator import ROICalculator, CompetitiveAnalyzer
    from nurture_sequences import SequenceManager
    from shared_inbox import SharedInboxManager, CallLogManager, MessageType, CallDisposition
    
    # Initialize competitive services
    ai_scorer = AILeadScorer()
    roi_calculator = ROICalculator()
    competitive_analyzer = CompetitiveAnalyzer()
    sequence_manager = SequenceManager()
    inbox_manager = SharedInboxManager()
    call_manager = CallLogManager()
    
    log.info("Competitive advantage services loaded successfully")
except ImportError as e:
    log.warning(f"Could not import competitive services: {e}")
    # Set None placeholders
    ai_scorer = None
    roi_calculator = None
    competitive_analyzer = None
    sequence_manager = None
    inbox_manager = None
    call_manager = None
    MessageType = None
    CallDisposition = None

log = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)

# ---------- Helpers ----------
def get_twilio_client():
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    tok = os.environ.get("TWILIO_AUTH_TOKEN")
    if sid and tok:
        return Client(sid, tok)
    return None

def get_queue():
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return Queue(connection=Redis.from_url(redis_url))

# ---------- Schemas ----------
class LeadSchema(Schema):
    full_name = fields.Str(validate=validate.Length(max=255))
    email = fields.Email()
    phone = fields.Str(validate=validate.Length(min=7, max=50))
    source = fields.Str(load_default="api")
    status = fields.Str(load_default="new")

class BookingSchema(Schema):
    lead_id = fields.Int(required=True)
    starts_at = fields.Str(required=True)
    notes = fields.Str(load_default=None)

class MessageSchema(Schema):
    lead_id = fields.Int(required=True)
    message_type = fields.Str(required=True, validate=validate.OneOf(['email', 'sms']))
    content = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    recipient = fields.Str(required=True)
    subject = fields.Str(validate=validate.Length(max=200))

class CallLogSchema(Schema):
    lead_id = fields.Int(required=True)
    phone_number = fields.Str(required=True, validate=validate.Regexp(r'^\+?1?\d{9,15}$'))
    direction = fields.Str(required=True, validate=validate.OneOf(['inbound', 'outbound']))
    duration_seconds = fields.Int(required=True, validate=validate.Range(min=0, max=14400))  # Max 4 hours
    disposition = fields.Str(required=True, validate=validate.OneOf([
        'connected', 'no_answer', 'busy', 'voicemail', 'wrong_number', 
        'appointment_scheduled', 'not_interested'
    ]))
    notes = fields.Str(validate=validate.Length(max=1000))
    recording_url = fields.Url()

class NurtureSequenceSchema(Schema):
    lead_id = fields.Int(required=True)
    industry = fields.Str(validate=validate.OneOf(['medspas', 'contractors', 'law_firms', 'salons']))
    business_data = fields.Dict()

# ---------- Health ----------
@api_bp.get("/healthz")
def healthz():
    return {"status": "ok"}

@api_bp.get("/readyz")
def readyz():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not-ready", "error": str(e)}, 500

# ---------- Auth (demo) ----------
@limiter.limit("10/min")
@api_bp.post("/auth/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password", "")
    if not email:
        return {"error": "email required"}, 400
    token = issue_token({"sub": email, "email": email})
    return {"token": token, "email": email}

# ---------- Leads ----------
@api_bp.get("/leads")
@require_auth
def list_leads():
    items = Lead.query.order_by(Lead.created_at.desc()).limit(100).all()
    return jsonify([x.to_dict() for x in items])

@limiter.limit("5/min")
@api_bp.post("/leads/bulk")
@require_auth
def leads_bulk():
    # Idempotency check
    idem_key = request.headers.get("Idempotency-Key")
    if idem_key:
        cutoff = datetime.utcnow() - timedelta(hours=24)
        seen = IdempotencyKey.query.filter(
            IdempotencyKey.key == idem_key,
            IdempotencyKey.created_at > cutoff,
        ).first()
        if seen and seen.response_data:
            out = dict(seen.response_data)
            out["idempotent"] = True
            return out

    created = updated = 0
    errors = []

    # CSV upload path
    if "file" in request.files:
        f = request.files["file"]
        if not f.filename.lower().endswith(".csv"):
            return {"error": "only CSV files supported"}, 400

        content = f.read().decode("utf-8", "ignore")
        rows = list(csv.DictReader(io.StringIO(content)))
        row_count = len(rows)

        # Enqueue large imports
        if row_count > 5000:
            if idem_key and not IdempotencyKey.query.filter_by(key=idem_key).first():
                db.session.add(IdempotencyKey(key=idem_key, response_data=None))
                db.session.commit()
            job_id = enqueue_bulk_import(content, idem_key)
            return {"job_id": job_id, "status": "enqueued", "estimated_rows": row_count}, 202

        # Inline small imports (chunked commits)
        reader = csv.DictReader(io.StringIO(content))
        processed = 0
        for row in reader:
            try:
                data = {
                    "full_name": (row.get("full_name") or "").strip() or None,
                    "email": (row.get("email") or "").strip().lower() or None,
                    "phone": (row.get("phone") or "").strip() or None,
                    "source": (row.get("source") or "bulk").strip() or "bulk",
                    "status": (row.get("status") or "new").strip() or "new",
                    "business_id": 1,
                }
                if not any([data["full_name"], data["email"], data["phone"]]):
                    continue

                existing = None
                if data["email"]:
                    existing = Lead.query.filter_by(email=data["email"]).first()
                if not existing and data["phone"]:
                    existing = Lead.query.filter_by(phone=data["phone"]).first()

                if existing:
                    for k, v in data.items():
                        if v is not None:
                            setattr(existing, k, v)
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    db.session.add(Lead(**data))
                    created += 1

                processed += 1
                if processed % 500 == 0:
                    db.session.commit()
            except Exception as e:
                errors.append(f"Row {processed+1}: {e}")
        db.session.commit()

    # JSON array path
    else:
        body = request.get_json() or []
        if not isinstance(body, list):
            return {"error": "expected JSON array"}, 400

        schema = LeadSchema()
        for idx, item in enumerate(body):
            try:
                data = schema.load(item)
                data["business_id"] = 1
                existing = None
                if data.get("email"):
                    existing = Lead.query.filter_by(email=data["email"]).first()
                if not existing and data.get("phone"):
                    existing = Lead.query.filter_by(phone=data["phone"]).first()
                if existing:
                    for k, v in data.items():
                        if v is not None:
                            setattr(existing, k, v)
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    db.session.add(Lead(**data))
                    created += 1
            except Exception as e:
                errors.append(f"Item {idx+1}: {e}")
        db.session.commit()

    result = {"created": created, "updated": updated, "errors": errors}
    if idem_key:
        rec = IdempotencyKey.query.filter_by(key=idem_key).first()
        if rec:
            rec.response_data = result
        else:
            db.session.add(IdempotencyKey(key=idem_key, response_data=result))
        db.session.commit()
    return result

# ---------- Bookings ----------
@api_bp.post("/bookings")
@require_auth
def create_booking():
    try:
        data = BookingSchema().load(request.get_json() or {})
        starts_at_str = str(data["starts_at"])
        if starts_at_str.endswith("Z"):
            starts_at_str = starts_at_str[:-1] + "+00:00"
        starts_at = datetime.fromisoformat(starts_at_str.replace("Z", "+00:00"))

        booking = Booking(
            lead_id=data["lead_id"],
            starts_at=starts_at,
            notes=data.get("notes"),
            business_id=1,
        )
        db.session.add(booking)
        db.session.commit()
        return booking.to_dict(), 201
    except Exception as e:
        return {"error": f"Invalid booking data: {e}"}, 400

# ---------- Twilio ----------

@api_bp.get("/twilio/debug")
def twilio_debug():
    """Debug endpoint to check Twilio configuration"""
    try:
        debug_info = {
            "twilio_auth_token_set": bool(os.environ.get("TWILIO_AUTH_TOKEN")),
            "twilio_account_sid_set": bool(os.environ.get("TWILIO_ACCOUNT_SID")),
            "twilio_from_set": bool(os.environ.get("TWILIO_FROM")),
            "database_url_set": bool(os.environ.get("DATABASE_URL")),
            "jwt_secret_set": bool(os.environ.get("JWT_SECRET")),
            "public_base_url": os.environ.get("PUBLIC_BASE_URL", ""),
        }
        return debug_info, 200
    except Exception as e:
        return {"error": str(e)}, 500

@api_bp.post("/twilio/inbound-debug")
def twilio_inbound_debug():
    """Debug version of Twilio webhook without signature validation"""
    try:
        current_app.logger.info("=== DEBUG WEBHOOK CALLED ===")
        current_app.logger.info(f"Headers: {dict(request.headers)}")
        current_app.logger.info(f"Form data: {request.form.to_dict()}")
        current_app.logger.info(f"URL: {request.url}")
        
        from_number = request.form.get("From", "")
        body = request.form.get("Body", "")
        
        current_app.logger.info(f"From: {from_number}, Body: {body}")
        
        # Try to create TwiML response without database operations
        resp = MessagingResponse()
        resp.message("DEBUG: Got your message! Webhook is working.")
        
        xml_response = str(resp)
        current_app.logger.info(f"TwiML Response: {xml_response}")
        
        return xml_response, 200, {"Content-Type": "application/xml"}
        
    except Exception as e:
        current_app.logger.exception(f"Debug webhook error: {e}")
        return f"ERROR: {str(e)}", 500

@api_bp.post("/twilio/inbound")
def twilio_inbound():
    """
    Twilio posts application/x-www-form-urlencoded.
    We must validate the X-Twilio-Signature using the *live* TWILIO_AUTH_TOKEN.
    """
    
    try:
        # 1) Collect form params (not JSON) with flat=False for compatibility
        form_params = request.form.to_dict(flat=False)
        
        # 2) Render sits behind a proxy; make sure URL used for validation is https
        url_for_sig = request.url.replace("http://", "https://")
        
        # 3) Validate Twilio signature
        sig = request.headers.get("X-Twilio-Signature", "")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")

        current_app.logger.info(f"Twilio webhook signature validation - URL: {url_for_sig}, has_signature: {bool(sig)}")
        
        if not auth_token:
            # Misconfigured env -> treat as forbidden so you'll see 403 in logs
            current_app.logger.error("TWILIO_AUTH_TOKEN not configured")
            return "", 403

        validator = RequestValidator(auth_token)
        is_valid = validator.validate(url_for_sig, form_params, sig)
        current_app.logger.info(f"Twilio signature validation result: {is_valid}")
        
        if not is_valid:
            # Signature mismatch => 403 Forbidden
            current_app.logger.warning(
                "Invalid Twilio signature validation failed",
                extra={
                    "url": url_for_sig,
                    "has_signature": bool(sig),
                    "signature": sig[:20] + "..." if sig else "",  # Log first 20 chars for debugging
                    "form_params_keys": list(form_params.keys())
                }
            )
            return "", 403

        # 4) Process the webhook
        from_number = request.form.get("From", "")
        body = request.form.get("Body", "")

        current_app.logger.info({
            "twilio_inbound": True, 
            "from": from_number, 
            "body": body,
            "url": url_for_sig,
            "signature_valid": True
        })

        # Try database operations in try/catch to prevent 500 errors
        try:
            # Only try database operations if DATABASE_URL is configured
            if os.environ.get("DATABASE_URL"):
                # Find or create lead
                lead = Lead.query.filter_by(phone=from_number).first()
                if not lead:
                    lead = Lead(phone=from_number, source="sms", status="new", business_id=1)
                    db.session.add(lead)
                    db.session.flush()

                # Find or create conversation
                convo = Conversation.query.filter_by(lead_id=lead.id, channel="sms").first()
                if not convo:
                    convo = Conversation(lead_id=lead.id, channel="sms")
                    db.session.add(convo)
                    db.session.flush()

                # Add message
                db.session.add(Message(
                    conversation_id=convo.id, 
                    role="user", 
                    text=body, 
                    ts=datetime.utcnow()
                ))
                db.session.commit()
                current_app.logger.info("SMS saved to database successfully")
            else:
                current_app.logger.warning("DATABASE_URL not set, skipping database operations")

            # Auto-reply with TwiML (always send reply regardless of DB status)
            resp = MessagingResponse()
            resp.message("Thanks! We got your message and will reply shortly.")
            
            xml_response = str(resp)
            current_app.logger.info(f"Sending TwiML response: {xml_response}")
            
            # Return TwiML with correct Content-Type for Twilio auto-reply
            return xml_response, 200, {"Content-Type": "application/xml"}
            
        except Exception as db_error:
            current_app.logger.exception(f"Database error in Twilio webhook: {db_error}")
            # Still return a TwiML response even if DB fails
            resp = MessagingResponse()
            resp.message("Message received!")
            xml_response = str(resp)
            current_app.logger.info(f"Sending fallback TwiML response: {xml_response}")
            return xml_response, 200, {"Content-Type": "application/xml"}
        
    except Exception as e:
        current_app.logger.exception(f"Twilio webhook error: {e}")
        # Surface error so it appears in Twilio console; they will retry
        return "Twilio webhook internal error", 500

@api_bp.post("/twilio/inbound/test")
def twilio_inbound_test():
    """
    TEST ENDPOINT ONLY - Bypasses signature validation for pre-launch testing
    This simulates Twilio inbound webhook behavior without requiring valid signature
    DO NOT USE IN PRODUCTION - REMOVE AFTER LAUNCH
    """
    
    try:
        # Skip signature validation for testing
        from_number = request.form.get("From", "")
        body = request.form.get("Body", "")

        current_app.logger.info({
            "twilio_inbound_test": True, 
            "from": from_number, 
            "body": body,
            "signature_bypassed": True
        })

        # Auto-reply with TwiML (same logic as real endpoint)
        from twilio.twiml.messaging_response import MessagingResponse
        resp = MessagingResponse()
        resp.message("Thanks! We got your message and will reply shortly.")
        
        xml_response = str(resp)
        current_app.logger.info(f"TEST - Sending TwiML response: {xml_response}")
        
        # Return TwiML with correct Content-Type for Twilio auto-reply
        return xml_response, 200, {"Content-Type": "application/xml"}
        
    except Exception as e:
        current_app.logger.exception(f"Twilio TEST webhook error: {e}")
        return "Twilio TEST webhook internal error", 500

@api_bp.post("/twilio/send")
@require_auth
def twilio_send():
    data = request.get_json() or {}
    lead_id = data.get("lead_id")
    text = data.get("body", "")
    if not lead_id or not text:
        return {"error": "lead_id and body required"}, 400

    lead = Lead.query.get(lead_id)
    if not lead or not lead.phone:
        return {"error": "lead not found or no phone"}, 404

    client = get_twilio_client()
    if not client:
        return {"error": "Twilio not configured"}, 503

    from_number = os.environ.get("TWILIO_FROM")
    msg = client.messages.create(body=text, from_=from_number, to=lead.phone)

    convo = Conversation.query.filter_by(lead_id=lead.id, channel="sms").first()
    if not convo:
        convo = Conversation(lead_id=lead.id, channel="sms")
        db.session.add(convo)
        db.session.flush()

    db.session.add(Message(conversation_id=convo.id, role="ai", text=text, ts=datetime.utcnow()))
    db.session.commit()

    return {"message_sid": msg.sid, "status": msg.status, "to": msg.to, "body": msg.body}

# ---------- Jobs ----------
@api_bp.get("/jobs/<job_id>")
@require_auth
def job_status(job_id: str):
    try:
        q = get_queue()
        job = q.fetch_job(job_id)
        if job is None:
            return {"error": "job not found"}, 404

        out = {
            "id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }
        if job.is_finished:
            out["result"] = job.result
        elif job.is_failed:
            out["error"] = str(job.exc_info)
        return out
    except Exception as e:
        return {"error": str(e)}, 500

# ---------- Seed (guarded) ----------
@api_bp.post("/admin/seed-demo")
def seed_demo():
    if os.environ.get("ENABLE_DEMO_SEED") != "true":
        return {"error": "disabled"}, 403

    biz = Business.query.first()
    if not biz:
        biz = Business(name="Demo Spa", niche="medspa", owner_email="owner@demo.com")
        db.session.add(biz)
        db.session.commit()

    l1 = Lead(full_name="Alice Johnson", email="alice@example.com", phone="+1111111111", source="demo", business_id=biz.id)
    l2 = Lead(full_name="Bob Smith",   email="bob@example.com",   phone="+2222222222", source="demo", business_id=biz.id)
    db.session.add_all([l1, l2]); db.session.commit()

    convo = Conversation(lead_id=l1.id, channel="sms")
    db.session.add(convo); db.session.commit()
    db.session.add_all([
        Message(conversation_id=convo.id, role="user", text="Hi, I'd like more info!", ts=datetime.utcnow()),
        Message(conversation_id=convo.id, role="ai",   text="Sure! We offer packages starting at $99.", ts=datetime.utcnow()),
    ])
    db.session.commit()
    return {"message": "seeded", "business_id": biz.id, "lead_ids": [l1.id, l2.id]}

# ---------- Messages ----------
@api_bp.get("/leads/<int:lead_id>/messages")
@require_auth
def lead_messages(lead_id: int):
    convos = Conversation.query.filter_by(lead_id=lead_id, channel="sms").all()
    ids = [c.id for c in convos]
    if not ids:
        return jsonify([])
    msgs = Message.query.filter(Message.conversation_id.in_(ids)).order_by(Message.ts.asc()).all()
    return jsonify([{"id": m.id, "role": m.role, "text": m.text, "ts": m.ts.isoformat()} for m in msgs])

# ---------- Competitive Advantage Features ----------

# AI Lead Scoring
@api_bp.get("/ai/score-leads")
@require_auth
@limiter.limit("10 per minute")  # Rate limit for expensive AI operations
def score_leads():
    """Get AI lead scores for all leads with pagination and filtering"""
    if not ai_scorer:
        return {"error": "AI scoring service not available"}, 503
    
    try:
        # Get query parameters with defaults
        user_id = request.args.get('user_id', 'default')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 leads per request
        offset = int(request.args.get('offset', 0))
        industry = request.args.get('industry', 'medspas')
        min_score = int(request.args.get('min_score', 0))
        
        # Get leads from database with pagination
        leads_query = Lead.query.offset(offset).limit(limit)
        if request.args.get('source'):
            leads_query = leads_query.filter(Lead.source == request.args.get('source'))
        
        leads = leads_query.all()
        
        if not leads:
            return {"leads": [], "total": 0, "has_more": False}, 200
        
        # Prepare lead data for scoring
        lead_data = []
        for lead in leads:
            lead_data.append({
                'id': str(lead.id),
                'name': lead.full_name or 'Unknown',
                'email': lead.email or '',
                'phone': lead.phone or '',
                'source': lead.source or 'unknown',
                'industry': industry,
                'created_at': lead.created_at.isoformat() if lead.created_at else None
            })
        
        # Get AI scores
        scores = ai_scorer.bulk_score_leads(lead_data)
        
        # Filter by minimum score if specified
        if min_score > 0:
            scores = [s for s in scores if s.get('score', 0) >= min_score]
        
        # Check if there are more leads
        total_leads = Lead.query.count()
        has_more = (offset + limit) < total_leads
        
        log.info(f"Scored {len(scores)} leads for user {user_id}")
        
        return {
            "leads": scores,
            "total": len(scores),
            "has_more": has_more,
            "offset": offset,
            "limit": limit
        }, 200
        
    except ValueError as e:
        log.error(f"Validation error in score_leads: {e}")
        return {"error": f"Invalid parameters: {str(e)}"}, 400
    except Exception as e:
        log.error(f"AI scoring error: {e}")
        return {"error": "Failed to score leads"}, 500

@api_bp.get("/ai/lead-insights/<int:lead_id>")
@require_auth
@limiter.limit("30 per minute")
def lead_insights(lead_id: int):
    """Get detailed AI insights for a specific lead"""
    if not ai_scorer:
        return {"error": "AI scoring service not available"}, 503
        
    try:
        lead = Lead.query.get(lead_id)
        if not lead:
            return {"error": "Lead not found"}, 404
        
        # Prepare lead data
        lead_data = {
            'id': str(lead.id),
            'name': lead.full_name or 'Unknown',
            'email': lead.email or '',
            'phone': lead.phone or '',
            'source': lead.source or 'unknown',
            'industry': request.args.get('industry', 'medspas'),
            'created_at': lead.created_at.isoformat() if lead.created_at else None
        }
        
        # Get AI analysis
        score_result = ai_scorer.score_lead(lead_data)
        insights = ai_scorer.get_lead_insights(score_result, lead_data)
        
        log.info(f"Generated insights for lead {lead_id}")
        
        return {
            'lead_id': lead_id,
            'lead_name': lead.full_name,
            'score': score_result,
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        log.error(f"Lead insights error for lead {lead_id}: {e}")
        return {"error": "Failed to generate insights"}, 500

# ROI Dashboard
@api_bp.get("/analytics/roi")
@require_auth
@limiter.limit("20 per minute")
def roi_dashboard():
    """Get comprehensive ROI analytics dashboard data"""
    if not roi_calculator:
        return {"error": "ROI analytics service not available"}, 503
        
    try:
        # Validate and sanitize parameters
        user_id = request.args.get('user_id', 'default')
        
        try:
            timeframe = int(request.args.get('days', 30))
            if timeframe not in [7, 30, 90, 365]:
                timeframe = 30  # Default to 30 days
        except (ValueError, TypeError):
            timeframe = 30
            
        industry = request.args.get('industry', 'medspas')
        if industry not in ['medspas', 'contractors', 'law_firms', 'salons']:
            industry = 'medspas'
        
        # Calculate ROI metrics
        metrics = roi_calculator.calculate_roi_metrics(user_id, timeframe)
        insights = roi_calculator.get_roi_insights(metrics, industry)
        recommendations = roi_calculator.get_growth_recommendations(metrics, industry)
        
        # Get competitive position if analyzer available
        competitive_position = None
        if competitive_analyzer:
            competitive_position = competitive_analyzer.get_competitive_position(metrics, industry)
        
        # Format response with proper data types
        response_data = {
            'metrics': {
                'leads_uploaded': int(metrics.leads_uploaded),
                'calls_made': int(metrics.calls_made),
                'emails_sent': int(metrics.emails_sent),
                'appointments_booked': int(metrics.appointments_booked),
                'deals_closed': int(metrics.deals_closed),
                'revenue_generated': float(metrics.revenue_generated),
                'cost_per_lead': float(metrics.cost_per_lead),
                'conversion_rate': float(metrics.conversion_rate),
                'roi_percentage': float(metrics.roi_percentage),
                'projected_monthly_revenue': float(metrics.projected_monthly_revenue)
            },
            'insights': insights,
            'recommendations': recommendations,
            'competitive_position': competitive_position,
            'timeframe_days': timeframe,
            'industry': industry,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        log.info(f"Generated ROI dashboard for user {user_id}, {timeframe} days, {industry}")
        
        return response_data, 200
        
    except Exception as e:
        log.error(f"ROI dashboard error: {e}")
        return {"error": "Failed to calculate ROI metrics"}, 500

@api_bp.get("/analytics/roi/export")
@require_auth
@limiter.limit("5 per minute")
def export_roi_data():
    """Export ROI data as CSV for client reporting"""
    if not roi_calculator:
        return {"error": "ROI analytics service not available"}, 503
    
    try:
        user_id = request.args.get('user_id', 'default')
        timeframe = int(request.args.get('days', 30))
        industry = request.args.get('industry', 'medspas')
        
        # Get metrics
        metrics = roi_calculator.calculate_roi_metrics(user_id, timeframe)
        
        # Create CSV data
        csv_data = [
            ["Metric", "Value"],
            ["Revenue Generated", f"${metrics.revenue_generated:,.2f}"],
            ["ROI Percentage", f"{metrics.roi_percentage:.1f}%"],
            ["Conversion Rate", f"{metrics.conversion_rate:.1%}"],
            ["Cost Per Lead", f"${metrics.cost_per_lead:.2f}"],
            ["Leads Uploaded", str(metrics.leads_uploaded)],
            ["Calls Made", str(metrics.calls_made)],
            ["Emails Sent", str(metrics.emails_sent)],
            ["Appointments Booked", str(metrics.appointments_booked)],
            ["Deals Closed", str(metrics.deals_closed)],
            ["Projected Monthly Revenue", f"${metrics.projected_monthly_revenue:,.2f}"]
        ]
        
        # Create CSV response
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        
        csv_content = output.getvalue()
        output.close()
        
        from flask import make_response
        response = make_response(csv_content)
        response.headers["Content-Disposition"] = f"attachment; filename=roi-report-{timeframe}days.csv"
        response.headers["Content-Type"] = "text/csv"
        
        log.info(f"Exported ROI data for user {user_id}")
        
        return response
        
    except Exception as e:
        log.error(f"ROI export error: {e}")
        return {"error": "Failed to export ROI data"}, 500

# Nurture Sequences  
@api_bp.post("/sequences/start")
@require_auth
@limiter.limit("10 per minute")
def start_nurture_sequence():
    """Start a nurture sequence for a lead with validation"""
    if not sequence_manager:
        return {"error": "Nurture sequences service not available"}, 503
        
    try:
        # Validate request data
        schema = NurtureSequenceSchema()
        try:
            data = schema.load(request.get_json() or {})
        except Exception as e:
            return {"error": f"Validation failed: {str(e)}"}, 400
            
        lead_id = data['lead_id']
        lead = Lead.query.get(lead_id)
        if not lead:
            return {"error": "Lead not found"}, 404
            
        # Build lead data
        lead_data = {
            'id': str(lead.id),
            'name': lead.full_name or 'Unknown',
            'email': lead.email or '',
            'phone': lead.phone or '',
            'source': lead.source or 'unknown',
            'industry': data.get('industry', 'medspas')
        }
        
        # Build business data (could come from Business model in real app)
        business_data = data.get('business_data', {})
        default_business_data = {
            'business_name': 'Demo Business',
            'agent_name': 'Sales Agent',
            'phone': '+15551234567',
            'service_type': 'consultation',
            'city': 'Your City',
            'years_in_business': '5',
            'license_number': 'LIC123456'
        }
        business_data = {**default_business_data, **business_data}
        
        # Start sequence
        result = sequence_manager.start_sequence_for_lead(lead_data, business_data)
        
        if 'error' in result:
            return result, 400
            
        # Log the action
        log.info(f"Started nurture sequence {result['sequence_id']} for lead {lead_id}")
        
        return {
            **result,
            'started_at': datetime.utcnow().isoformat(),
            'lead_name': lead.full_name
        }, 201
        
    except Exception as e:
        log.error(f"Sequence start error: {e}")
        return {"error": "Failed to start nurture sequence"}, 500

@api_bp.get("/sequences/templates")
@require_auth
def get_sequence_templates():
    """Get available nurture sequence templates by industry"""
    if not sequence_manager:
        return {"error": "Nurture sequences service not available"}, 503
    
    try:
        industry = request.args.get('industry')
        
        templates = []
        for seq_id, sequence in sequence_manager.engine.sequences.items():
            if not industry or sequence.industry == industry:
                templates.append({
                    'id': sequence.sequence_id,
                    'name': sequence.name,
                    'industry': sequence.industry,
                    'type': sequence.sequence_type.value,
                    'steps': len(sequence.steps),
                    'success_rate': sequence.success_rate,
                    'description': f"{len(sequence.steps)}-step {sequence.sequence_type.value} sequence for {sequence.industry}"
                })
        
        return {
            'templates': templates,
            'total': len(templates),
            'industry_filter': industry
        }, 200
        
    except Exception as e:
        log.error(f"Templates error: {e}")
        return {"error": "Failed to get templates"}, 500

@api_bp.get("/sequences/<sequence_id>/preview")
@require_auth
def preview_sequence(sequence_id: str):
    """Preview a nurture sequence with sample personalization"""
    if not sequence_manager:
        return {"error": "Nurture sequences service not available"}, 503
    
    try:
        sequence = sequence_manager.engine.sequences.get(sequence_id)
        if not sequence:
            return {"error": "Sequence not found"}, 404
        
        # Sample data for preview
        sample_lead_data = {
            'name': 'Sarah Johnson',
            'first_name': 'Sarah',
            'email': 'sarah@example.com',
            'phone': '+15551234567',
            'service_type': 'consultation'
        }
        
        sample_business_data = {
            'business_name': 'Your Business',
            'agent_name': 'Your Name',
            'phone': '+15559876543'
        }
        
        # Preview each step
        preview_steps = []
        for step in sequence.steps:
            preview_message = sequence_manager.engine.personalize_message(
                step.message_template, 
                sample_lead_data, 
                sample_business_data
            )
            preview_subject = sequence_manager.engine.personalize_message(
                step.subject or '', 
                sample_lead_data, 
                sample_business_data
            )
            
            preview_steps.append({
                'step_number': step.step_number,
                'delay_hours': step.delay_hours,
                'channel': step.channel.value,
                'subject': preview_subject,
                'message': preview_message,
                'conditions': step.conditions,
                'stop_if_replied': step.stop_if_replied
            })
        
        return {
            'sequence': {
                'id': sequence.sequence_id,
                'name': sequence.name,
                'industry': sequence.industry,
                'type': sequence.sequence_type.value,
                'success_rate': sequence.success_rate
            },
            'steps': preview_steps,
            'total_steps': len(preview_steps)
        }, 200
        
    except Exception as e:
        log.error(f"Sequence preview error: {e}")
        return {"error": "Failed to preview sequence"}, 500

@api_bp.get("/sequences/analytics/<sequence_id>")
@require_auth
def sequence_analytics(sequence_id: str):
    """Get detailed analytics for a nurture sequence"""
    if not sequence_manager:
        return {"error": "Nurture sequences service not available"}, 503
        
    try:
        analytics = sequence_manager.engine.get_sequence_analytics(sequence_id)
        optimization = sequence_manager.engine.optimize_sequence(sequence_id)
        
        return {
            'sequence_id': sequence_id,
            'analytics': analytics,
            'optimization': optimization,
            'generated_at': datetime.utcnow().isoformat()
        }, 200
    except Exception as e:
        log.error(f"Sequence analytics error: {e}")
        return {"error": "Failed to get analytics"}, 500

@api_bp.put("/sequences/<lead_id>/pause")
@require_auth
def pause_sequence(lead_id: str):
    """Pause nurture sequence for a lead"""
    if not sequence_manager:
        return {"error": "Nurture sequences service not available"}, 503
    
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'manual_pause')
        
        result = sequence_manager.pause_sequence(lead_id, reason)
        
        log.info(f"Paused sequence for lead {lead_id}: {reason}")
        
        return result, 200
        
    except Exception as e:
        log.error(f"Sequence pause error: {e}")
        return {"error": "Failed to pause sequence"}, 500

# Shared Inbox
@api_bp.get("/inbox")
@require_auth
@limiter.limit("30 per minute")
def shared_inbox():
    """Get unified inbox with advanced filtering and pagination"""
    if not inbox_manager:
        return {"error": "Shared inbox service not available"}, 503
        
    try:
        user_id = request.args.get('user_id', 'default')
        
        # Build filters with validation
        filters = {}
        
        # Status filter
        status = request.args.get('status')
        if status and status in ['unread', 'read', 'replied', 'archived']:
            filters['status'] = status
            
        # Message type filter
        message_type = request.args.get('type')
        if message_type and message_type in ['email', 'sms', 'call', 'voicemail', 'note']:
            filters['message_type'] = message_type
            
        # Priority filter
        priority = request.args.get('priority')
        if priority and priority in ['low', 'normal', 'high', 'urgent']:
            filters['priority'] = priority
            
        # Date filters
        date_from = request.args.get('date_from')
        if date_from:
            try:
                datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                filters['date_from'] = date_from
            except ValueError:
                pass
                
        # Search term
        search_term = request.args.get('search')
        if search_term and len(search_term.strip()) > 0:
            filters['search_term'] = search_term.strip()[:100]  # Limit search term length
        
        # Pagination
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(50, max(1, int(request.args.get('per_page', 20))))
        
        filters['page'] = page
        filters['per_page'] = per_page
        
        # Get inbox data
        inbox_data = inbox_manager.get_inbox(user_id, filters)
        
        log.info(f"Retrieved inbox for user {user_id} with filters: {filters}")
        
        return {
            **inbox_data,
            'page': page,
            'per_page': per_page,
            'retrieved_at': datetime.utcnow().isoformat()
        }, 200
        
    except ValueError as e:
        return {"error": f"Invalid parameters: {str(e)}"}, 400
    except Exception as e:
        log.error(f"Inbox error: {e}")
        return {"error": "Failed to retrieve inbox"}, 500

@api_bp.post("/inbox/send")
@require_auth
@limiter.limit("20 per minute")
def send_message():
    """Send a message through unified inbox with validation"""
    if not inbox_manager:
        return {"error": "Shared inbox service not available"}, 503
        
    try:
        # Validate input data
        schema = MessageSchema()
        try:
            data = schema.load(request.get_json() or {})
        except Exception as e:
            return {"error": f"Validation failed: {str(e)}"}, 400
        
        # Verify lead exists
        lead = Lead.query.get(data['lead_id'])
        if not lead:
            return {"error": "Lead not found"}, 404
            
        # Validate message type
        if not MessageType:
            return {"error": "MessageType not available"}, 503
            
        try:
            message_type = MessageType(data['message_type'])
        except ValueError:
            return {"error": "Invalid message type"}, 400
        
        # Send message
        result = inbox_manager.send_message(
            user_id=data.get('user_id', 'default'),
            lead_id=data['lead_id'],
            message_type=message_type,
            content=data['content'],
            recipient=data['recipient'],
            subject=data.get('subject')
        )
        
        log.info(f"Sent {data['message_type']} message to lead {data['lead_id']}")
        
        return {
            **result,
            'lead_name': lead.full_name,
            'sent_at': datetime.utcnow().isoformat()
        }, 201
        
    except Exception as e:
        log.error(f"Send message error: {e}")
        return {"error": "Failed to send message"}, 500

@api_bp.put("/inbox/mark-read")
@require_auth
def mark_messages_read():
    """Mark multiple messages as read"""
    if not inbox_manager:
        return {"error": "Shared inbox service not available"}, 503
        
    try:
        data = request.get_json() or {}
        message_ids = data.get('message_ids', [])
        
        if not isinstance(message_ids, list) or not message_ids:
            return {"error": "message_ids array required"}, 400
            
        # Limit to 100 messages at once
        if len(message_ids) > 100:
            return {"error": "Cannot mark more than 100 messages at once"}, 400
        
        result = inbox_manager.mark_as_read(message_ids)
        
        log.info(f"Marked {result['updated']} messages as read")
        
        return {
            **result,
            'marked_at': datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        log.error(f"Mark read error: {e}")
        return {"error": "Failed to mark messages as read"}, 500

@api_bp.get("/inbox/stats")
@require_auth
def inbox_stats():
    """Get inbox statistics and KPIs"""
    if not inbox_manager:
        return {"error": "Shared inbox service not available"}, 503
        
    try:
        user_id = request.args.get('user_id', 'default')
        days = min(90, max(1, int(request.args.get('days', 7))))
        
        stats = inbox_manager._get_inbox_stats(user_id)
        
        # Add time-based metrics
        stats['timeframe_days'] = days
        stats['avg_messages_per_day'] = stats.get('total_messages', 0) / days
        
        return {
            'stats': stats,
            'generated_at': datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        log.error(f"Inbox stats error: {e}")
        return {"error": "Failed to get inbox statistics"}, 500

# Call Log
@api_bp.post("/calls/log")
@require_auth
@limiter.limit("50 per minute")
def log_call():
    """Log a phone call with comprehensive validation"""
    if not call_manager:
        return {"error": "Call logging service not available"}, 503
        
    try:
        # Validate input data
        schema = CallLogSchema()
        try:
            data = schema.load(request.get_json() or {})
        except Exception as e:
            return {"error": f"Validation failed: {str(e)}"}, 400
        
        # Verify lead exists
        lead = Lead.query.get(data['lead_id'])
        if not lead:
            return {"error": "Lead not found"}, 404
            
        # Validate disposition
        if not CallDisposition:
            return {"error": "CallDisposition not available"}, 503
            
        try:
            disposition = CallDisposition(data['disposition'])
        except ValueError:
            return {"error": "Invalid call disposition"}, 400
        
        # Log the call
        result = call_manager.log_call(
            user_id=data.get('user_id', 'default'),
            lead_id=data['lead_id'],
            phone_number=data['phone_number'],
            direction=data['direction'],
            duration_seconds=data['duration_seconds'],
            disposition=disposition,
            notes=data.get('notes'),
            recording_url=data.get('recording_url')
        )
        
        log.info(f"Logged {data['direction']} call for lead {data['lead_id']}: {data['disposition']}")
        
        return {
            **result,
            'lead_name': lead.full_name,
            'logged_at': datetime.utcnow().isoformat()
        }, 201
        
    except Exception as e:
        log.error(f"Call logging error: {e}")
        return {"error": "Failed to log call"}, 500

@api_bp.get("/calls/history")
@require_auth
@limiter.limit("30 per minute")
def call_history():
    """Get call history with advanced filtering and pagination"""
    if not call_manager:
        return {"error": "Call history service not available"}, 503
        
    try:
        user_id = request.args.get('user_id', 'default')
        
        # Optional lead filter
        lead_id = request.args.get('lead_id')
        if lead_id:
            try:
                lead_id = int(lead_id)
                # Verify lead exists
                if not Lead.query.get(lead_id):
                    return {"error": "Lead not found"}, 404
            except ValueError:
                return {"error": "Invalid lead_id"}, 400
        
        # Date range
        try:
            days = min(365, max(1, int(request.args.get('days', 30))))
        except (ValueError, TypeError):
            days = 30
            
        # Direction filter
        direction = request.args.get('direction')
        if direction and direction not in ['inbound', 'outbound']:
            return {"error": "Invalid direction filter"}, 400
            
        # Disposition filter
        disposition = request.args.get('disposition')
        if disposition:
            valid_dispositions = [
                'connected', 'no_answer', 'busy', 'voicemail', 
                'wrong_number', 'appointment_scheduled', 'not_interested'
            ]
            if disposition not in valid_dispositions:
                return {"error": "Invalid disposition filter"}, 400
        
        # Get call history
        history = call_manager.get_call_history(user_id, lead_id, days)
        
        # Apply additional filters
        if direction:
            history = [call for call in history if call['direction'] == direction]
            
        if disposition:
            history = [call for call in history if call['disposition'] == disposition]
        
        # Pagination
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 25))))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_history = history[start_idx:end_idx]
        
        log.info(f"Retrieved {len(paginated_history)} calls for user {user_id}")
        
        return {
            'calls': paginated_history,
            'total': len(history),
            'page': page,
            'per_page': per_page,
            'has_more': end_idx < len(history),
            'filters': {
                'days': days,
                'lead_id': lead_id,
                'direction': direction,
                'disposition': disposition
            },
            'retrieved_at': datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        log.error(f"Call history error: {e}")
        return {"error": "Failed to get call history"}, 500

@api_bp.get("/calls/callbacks")
@require_auth
@limiter.limit("20 per minute")
def callbacks_due():
    """Get calls that need follow-up with lead details"""
    if not call_manager:
        return {"error": "Call callbacks service not available"}, 503
        
    try:
        user_id = request.args.get('user_id', 'default')
        callbacks = call_manager.get_callbacks_due(user_id)
        
        # Enrich with lead information
        enriched_callbacks = []
        for callback in callbacks:
            lead = Lead.query.get(callback['lead_id'])
            if lead:
                enriched_callbacks.append({
                    **callback,
                    'lead_name': lead.full_name,
                    'lead_email': lead.email,
                    'lead_source': lead.source
                })
        
        log.info(f"Retrieved {len(enriched_callbacks)} callbacks for user {user_id}")
        
        return {
            'callbacks': enriched_callbacks,
            'total': len(enriched_callbacks),
            'retrieved_at': datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        log.error(f"Callbacks error: {e}")
        return {"error": "Failed to get callbacks"}, 500

@api_bp.get("/calls/analytics")
@require_auth
@limiter.limit("10 per minute")
def call_analytics():
    """Get comprehensive call performance analytics"""
    if not call_manager:
        return {"error": "Call analytics service not available"}, 503
        
    try:
        user_id = request.args.get('user_id', 'default')
        
        try:
            days = min(365, max(1, int(request.args.get('days', 30))))
        except (ValueError, TypeError):
            days = 30
        
        analytics = call_manager.get_call_analytics(user_id, days)
        
        # Add additional metrics
        analytics['timeframe_days'] = days
        analytics['calls_per_day'] = analytics.get('total_calls', 0) / days
        
        # Calculate success metrics
        total_calls = analytics.get('total_calls', 0)
        if total_calls > 0:
            analytics['success_rate'] = (
                analytics.get('appointments_scheduled', 0) + 
                analytics.get('connected_calls', 0)
            ) / total_calls
        else:
            analytics['success_rate'] = 0
        
        log.info(f"Generated call analytics for user {user_id}")
        
        return {
            'analytics': analytics,
            'generated_at': datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        log.error(f"Call analytics error: {e}")
        return {"error": "Failed to get call analytics"}, 500

@api_bp.put("/calls/<call_id>/notes")
@require_auth
def update_call_notes(call_id: str):
    """Update notes for a specific call"""
    if not call_manager:
        return {"error": "Call management service not available"}, 503
        
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '').strip()
        
        if len(notes) > 1000:
            return {"error": "Notes too long (max 1000 characters)"}, 400
        
        # In a real implementation, this would update the database
        # For now, just return success
        
        log.info(f"Updated notes for call {call_id}")
        
        return {
            'call_id': call_id,
            'notes': notes,
            'updated_at': datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        log.error(f"Update call notes error: {e}")
        return {"error": "Failed to update call notes"}, 500

# ============================================================================
# STRIPE ENDPOINTS - CRITICAL FOR SUBSCRIPTION FUNCTIONALITY
# ============================================================================

@api_bp.post("/stripe/webhook")
def stripe_webhook():
    """
    Stripe webhook handler for subscription events
    CRITICAL: Validates webhook signature and processes subscription updates
    """
    try:
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        
        # Get webhook secret from environment
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        if not webhook_secret:
            current_app.logger.error("STRIPE_WEBHOOK_SECRET not configured")
            return {"error": "Webhook secret not configured"}, 500
        
        # Verify webhook signature
        try:
            import stripe
            stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
            
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            current_app.logger.error(f"Invalid payload: {e}")
            return {"error": "Invalid payload"}, 400
        except stripe.error.SignatureVerificationError as e:
            current_app.logger.error(f"Invalid signature: {e}")
            return {"error": "Invalid signature"}, 400
        except ImportError:
            current_app.logger.error("Stripe library not installed")
            return {"error": "Stripe not available"}, 500

        # Process the event
        current_app.logger.info(f"Stripe webhook event: {event['type']}")
        
        if event['type'] in ['customer.subscription.created', 
                           'customer.subscription.updated', 
                           'customer.subscription.deleted']:
            # Handle subscription events
            subscription = event['data']['object']
            customer_id = subscription['customer']
            status = subscription['status']
            
            current_app.logger.info(f"Subscription {subscription['id']} for customer {customer_id} is now {status}")
            
            # TODO: Update user subscription status in database
            # This would require user lookup by stripe_customer_id
            
        elif event['type'] == 'invoice.payment_succeeded':
            # Handle successful payments
            invoice = event['data']['object']
            current_app.logger.info(f"Payment succeeded for invoice {invoice['id']}")
            
        elif event['type'] == 'invoice.payment_failed':
            # Handle failed payments
            invoice = event['data']['object']
            current_app.logger.warning(f"Payment failed for invoice {invoice['id']}")
        
        return {"status": "success"}, 200
        
    except Exception as e:
        current_app.logger.exception(f"Stripe webhook error: {e}")
        return {"error": "Webhook processing failed"}, 500

@api_bp.post("/stripe/create-checkout")
@require_auth
def stripe_create_checkout():
    """
    Create Stripe checkout session for subscription
    """
    try:
        import stripe
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        
        if not stripe.api_key:
            return {"error": "Stripe not configured"}, 500
        
        # Get user info from JWT token (implement based on your auth system)
        # For now, using placeholder data
        user_email = "user@example.com"  # TODO: Get from JWT
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.environ.get('STRIPE_PRICE_ID', 'price_1234'),  # TODO: Set in env
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.environ.get('FRONTEND_URL', 'https://useleadnest.com')}/dashboard?payment=success",
            cancel_url=f"{os.environ.get('FRONTEND_URL', 'https://useleadnest.com')}/dashboard?payment=cancelled",
            customer_email=user_email,
        )
        
        return {"checkout_url": checkout_session.url}, 200
        
    except Exception as e:
        current_app.logger.exception(f"Stripe checkout creation error: {e}")
        return {"error": "Checkout creation failed"}, 500
