from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging, csv, io, os

from twilio.rest import Client
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from redis import Redis
from rq import Queue, Job

from marshmallow import Schema, fields, validate

from .auth import require_auth, issue_token
from .db import db
from .models import Lead, Booking, Business, Conversation, Message, IdempotencyKey
from .__init__ import limiter
from .tasks import enqueue_bulk_import

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

# ---------- Health ----------
@api_bp.get("/healthz")
def healthz():
    return {"status": "ok"}

@api_bp.get("/readyz")
def readyz():
    try:
        db.session.execute("SELECT 1")
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
@api_bp.post("/twilio/inbound")
def twilio_inbound():
    # Validate signature (protects from spoofed requests)
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if auth_token:
        validator = RequestValidator(auth_token)
        signature = request.headers.get("X-Twilio-Signature", "")
        public = os.environ.get("PUBLIC_BASE_URL", "")
        # Render may pass http internally, so prefer the configured public base
        url = public + "/twilio/inbound" if public else request.url
        if not validator.validate(url, request.form.to_dict(), signature):
            return {"error": "invalid signature"}, 403

    from_number = request.form.get("From", "")
    body = request.form.get("Body", "")

    try:
        lead = Lead.query.filter_by(phone=from_number).first()
        if not lead:
            lead = Lead(phone=from_number, source="sms", status="new", business_id=1)
            db.session.add(lead)
            db.session.flush()

        convo = Conversation.query.filter_by(lead_id=lead.id, channel="sms").first()
        if not convo:
            convo = Conversation(lead_id=lead.id, channel="sms")
            db.session.add(convo)
            db.session.flush()

        db.session.add(Message(conversation_id=convo.id, role="user", text=body, ts=datetime.utcnow()))
        db.session.commit()

        resp = MessagingResponse()
        resp.message("Thanks! We got your message and will reply shortly.")
        return str(resp), 200, {"Content-Type": "text/xml"}
    except Exception as e:
        log.exception("twilio inbound failed: %s", e)
        return {"error": "internal"}, 500

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
        job = Job.fetch(job_id, connection=q.connection)
        result = {
            "id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }
        if job.is_finished:
            result["result"] = job.result
        elif job.is_failed:
            result["error"] = str(job.exc_info)
        return result
    except Exception as e:
        return {"error": str(e)}, 404

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
