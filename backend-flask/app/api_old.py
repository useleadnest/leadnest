from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging
import csv
import io
import os
import json
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from redis import Redis
from rq import Queue
from marshmallow import Schema, fields, validate

from .auth import require_auth, issue_token
from .db import db
from .models import Lead, Booking, Business, Conversation, Message, IdempotencyKey

api_bp = Blueprint('api', __name__)


@api_bp.get('/healthz')
def healthz():
    return jsonify({"status": "ok"})


@api_bp.post('/auth/login')
def login():
    data = request.get_json() or {}
    email = data.get('email', 'test@example.com')
    password = data.get('password', 'password')
    
    # Simple demo auth
    if email and password:
        token = issue_token({"sub": email, "email": email})
        return jsonify({'token': token, 'email': email})
    
    return jsonify({'error': 'Invalid credentials'}), 401


@api_bp.post('/leads')
@require_auth
def create_lead():
    data = request.get_json() or {}
    lead = Lead(**data)
    db.session.add(lead)
    db.session.commit()
    return jsonify(lead.to_dict()), 201


@api_bp.get('/leads')
@require_auth
def list_leads():
    q = Lead.query.order_by(Lead.created_at.desc()).limit(100)
    return jsonify([l.to_dict() for l in q])


@api_bp.post('/bookings')
@require_auth
def create_booking():
    data = request.get_json() or {}
    
    # Safer booking validation
    starts_at_str = data.get('starts_at')
    if starts_at_str:
        if isinstance(starts_at_str, str) and starts_at_str.endswith('Z'):
            starts_at_str = starts_at_str[:-1] + '+00:00'
        try:
            starts_at = datetime.fromisoformat(str(starts_at_str).replace('Z', '+00:00'))
            data['starts_at'] = starts_at
        except Exception as e:
            return jsonify({'error': f'invalid starts_at format, expected ISO 8601: {e}'}), 400
    
    booking = Booking(**data)
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking.to_dict()), 201


@api_bp.post('/admin/seed-demo')
def seed_demo():
    """Seed a default business, leads, and messages for demo/testing."""
    if os.environ.get("ENABLE_DEMO_SEED") != "true":
        return jsonify({"error": "disabled"}), 403
        
    # Create business if not exists
    biz = Business.query.first()
    if not biz:
        biz = Business(name="Demo Spa", niche="medspa", owner_email="owner@demo.com")
        db.session.add(biz)
        db.session.commit()

    # Create a couple of leads
    lead1 = Lead(full_name="Alice Johnson", email="alice@example.com", phone="+1111111111", source="demo", business_id=biz.id)
    lead2 = Lead(full_name="Bob Smith", email="bob@example.com", phone="+2222222222", source="demo", business_id=biz.id)
    db.session.add_all([lead1, lead2])
    db.session.commit()

    # Add conversation + messages for lead1
    convo = Conversation(lead_id=lead1.id, channel="sms")
    db.session.add(convo)
    db.session.commit()

    msg1 = Message(conversation_id=convo.id, role="user", text="Hi, I'd like more info!", ts=datetime.utcnow())
    msg2 = Message(conversation_id=convo.id, role="ai", text="Sure! We offer packages starting at $99.", ts=datetime.utcnow())
    db.session.add_all([msg1, msg2])
    db.session.commit()

    return jsonify({"message": "Demo data seeded", "business_id": biz.id, "lead_ids": [lead1.id, lead2.id]})


@api_bp.get('/leads/<int:lead_id>/messages')
@require_auth
def get_lead_messages(lead_id):
    """Return all messages for a lead across conversations, ordered by ts."""
    convos = Conversation.query.filter_by(lead_id=lead_id).all()
    convo_ids = [c.id for c in convos]
    if not convo_ids:
        return jsonify([])

    msgs = Message.query.filter(Message.conversation_id.in_(convo_ids)).order_by(Message.ts.asc()).all()
    return jsonify([{
        "id": m.id,
        "role": m.role,
        "text": m.text,
        "ts": m.ts.isoformat()
    } for m in msgs])


# Helper functions
def get_twilio_client():
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    if account_sid and auth_token:
        return Client(account_sid, auth_token)
    return None

def get_redis_queue():
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        redis_conn = Redis.from_url(redis_url)
        return Queue(connection=redis_conn)
    except Exception:
        return None

# Input validation schemas
class LeadSchema(Schema):
    full_name = fields.Str(required=False, validate=validate.Length(max=255))
    email = fields.Email(required=False)
    phone = fields.Str(required=False, validate=validate.Length(min=7, max=50))
    source = fields.Str(missing="api", validate=validate.Length(max=100))
    status = fields.Str(missing="new", validate=validate.Length(max=50))

class BookingSchema(Schema):
    lead_id = fields.Int(required=True)
    starts_at = fields.Str(required=True)
    notes = fields.Str(required=False)


@api_bp.get('/readyz')
def readyz():
    try:
        db.session.execute("SELECT 1")
        return jsonify({"status": "ready"})
    except Exception as e:
        return jsonify({"status": "not-ready", "error": str(e)}), 500


@api_bp.post('/twilio/inbound')
def twilio_inbound():
    # Validate Twilio signature
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    if auth_token:
        validator = RequestValidator(auth_token)
        signature = request.headers.get('X-Twilio-Signature', '')
        
        # Handle Render HTTPS termination
        public_base = os.environ.get("PUBLIC_BASE_URL", "")
        url = public_base + "/twilio/inbound" if public_base else request.url
        params = request.form.to_dict()
        
        if not validator.validate(url, params, signature):
            return jsonify({'error': 'Invalid signature'}), 403
    
    # Extract SMS data
    from_number = request.form.get('From', '')
    to_number = request.form.get('To', '')
    body = request.form.get('Body', '')
    message_sid = request.form.get('MessageSid', '')
    
    try:
        # Find or create lead by phone
        lead = Lead.query.filter_by(phone=from_number).first()
        if not lead:
            lead = Lead(
                phone=from_number,
                source='sms',
                status='new',
                business_id=1
            )
            db.session.add(lead)
            db.session.flush()
        
        # Find or create conversation
        conversation = Conversation.query.filter_by(lead_id=lead.id, channel='sms').first()
        if not conversation:
            conversation = Conversation(lead_id=lead.id, channel='sms')
            db.session.add(conversation)
            db.session.flush()
        
        # Add incoming message
        message = Message(
            conversation_id=conversation.id,
            role='user',
            text=body,
            ts=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()
        
        # Send auto-reply via TwiML
        resp = MessagingResponse()
        resp.message("Thanks for your message! We'll get back to you soon.")
        
        return str(resp), 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logging.error(f"Twilio inbound error: {e}")
        return jsonify({'error': 'Internal error'}), 500


@api_bp.post('/twilio/send')
@require_auth
def twilio_send():
    data = request.get_json() or {}
    lead_id = data.get('lead_id')
    body = data.get('body', '')
    
    if not lead_id or not body:
        return jsonify({'error': 'lead_id and body required'}), 400
    
    try:
        # Get lead
        lead = Lead.query.get(lead_id)
        if not lead or not lead.phone:
            return jsonify({'error': 'Lead not found or no phone number'}), 404
        
        # Send via Twilio REST API
        client = get_twilio_client()
        if not client:
            return jsonify({'error': 'Twilio not configured'}), 503
        
        from_number = os.environ.get('TWILIO_FROM')
        message = client.messages.create(
            body=body,
            from_=from_number,
            to=lead.phone
        )
        
        # Find or create conversation
        conversation = Conversation.query.filter_by(lead_id=lead.id, channel='sms').first()
        if not conversation:
            conversation = Conversation(lead_id=lead.id, channel='sms')
            db.session.add(conversation)
            db.session.flush()
        
        # Store outbound message
        msg_record = Message(
            conversation_id=conversation.id,
            role='ai',
            text=body,
            ts=datetime.utcnow()
        )
        db.session.add(msg_record)
        db.session.commit()
        
        return jsonify({
            'message_sid': message.sid,
            'status': message.status,
            'to': message.to,
            'body': message.body
        })
        
    except Exception as e:
        logging.error(f"Twilio send error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.get('/jobs/<job_id>')
@require_auth
def get_job_status(job_id):
    try:
        queue = get_redis_queue()
        if not queue:
            return jsonify({'error': 'Job queue unavailable'}), 503
        
        from rq import Job
        job = Job.fetch(job_id, connection=queue.connection)
        
        result = {
            'id': job_id,
            'status': job.get_status(),
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'ended_at': job.ended_at.isoformat() if job.ended_at else None,
        }
        
        if job.is_finished:
            result['result'] = job.result
        elif job.is_failed:
            result['error'] = str(job.exc_info)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404
