from datetime import datetime, timedelta
from .db import db
from sqlalchemy import func, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Base model class for common fields
class Base(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Business(Base):
    __tablename__ = 'businesses'
    
    name = db.Column(db.String(200), nullable=False)
    niche = db.Column(db.String(100))  # Keep existing column for backward compatibility
    owner_email = db.Column(db.String(255), nullable=False, default='owner@example.com')
    
    # Twilio integration (new columns for Launch Multiplier)
    twilio_account_sid = db.Column(db.String(100))
    twilio_auth_token = db.Column(db.String(100))
    twilio_phone_number = db.Column(db.String(20))
    
    # Calendly integration  
    calendly_url = db.Column(db.String(500))
    
    # Business metrics for ROI calculation
    avg_deal_size = db.Column(db.Numeric(10, 2))
    close_rate = db.Column(db.Float)
    cost_per_lead = db.Column(db.Numeric(10, 2))
    
    def __repr__(self):
        return f'<Business {self.name}>'


class Lead(Base):
    __tablename__ = 'leads'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(255), index=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company = db.Column(db.String(200))
    title = db.Column(db.String(100))
    status = db.Column(db.String(20), default='new')
    source = db.Column(db.String(100))
    notes = db.Column(db.Text)
    score = db.Column(db.Float)
    priority = db.Column(db.String(20), default='medium')
    last_contacted_at = db.Column(db.DateTime)
    next_followup_at = db.Column(db.DateTime)
    
    # Relationships
    business = db.relationship('Business', backref='leads')
    
    def __repr__(self):
        return f'<Lead {self.phone} {self.email}>'


class Conversation(Base):
    __tablename__ = 'conversations'
    
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')
    subject = db.Column(db.String(200))
    last_message_at = db.Column(db.DateTime)
    
    # Relationships
    lead = db.relationship('Lead', backref='conversations')
    messages = db.relationship('Message', backref='conversation')
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.channel}>'


class Message(Base):
    __tablename__ = 'messages'
    
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user', 'lead', 'assistant'
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file, template
    external_id = db.Column(db.String(100))  # Twilio/email provider message ID
    status = db.Column(db.String(20), default='sent')  # sent, delivered, read, failed
    extra_data = db.Column(db.JSON, default={})
    ts = db.Column(db.Integer)  # Unix timestamp
    
    def __repr__(self):
        return f'<Message {self.id}: {self.sender} -> {self.content[:50]}>'


class Booking(Base):
    __tablename__ = 'bookings'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, completed, canceled
    booking_type = db.Column(db.String(50), default='consultation')  # consultation, demo, follow_up
    external_id = db.Column(db.String(100))  # Calendly event ID
    show_status = db.Column(db.String(20))  # showed, no_show, rescheduled
    outcome = db.Column(db.String(50))  # qualified, unqualified, closed, follow_up_needed
    revenue_generated = db.Column(db.Numeric(10, 2))
    
    business = db.relationship('Business', backref='bookings')
    lead = db.relationship('Lead', backref='bookings')
    
    def __repr__(self):
        return f'<Booking {self.id}: {self.starts_at}>'


class IdempotencyKey(Base):
    __tablename__ = 'idempotency_keys'
    
    key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    expires_at = db.Column(db.DateTime)
    
    business = db.relationship('Business', backref='idempotency_keys')
    
    def __repr__(self):
        return f'<IdempotencyKey {self.key}>'


# New models for Launch Multiplier features

class User(Base):
    __tablename__ = 'users'
    
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))  
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='owner')  # owner, agency_owner, agency_member, admin
    
    # Agency relationships
    agency_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Self-referencing
    sub_accounts = db.relationship('User', backref=db.backref('agency_owner', remote_side='User.id'))
    
    # Subscription info
    stripe_customer_id = db.Column(db.String(100), unique=True)
    subscription_status = db.Column(db.String(20), default='trial')  # trial, active, past_due, canceled, unpaid
    trial_ends_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    subscription_ends_at = db.Column(db.DateTime)
    
    # Business relationship
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=True)
    business = db.relationship('Business', backref='users')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'subscription_status': self.subscription_status,
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            'subscription_ends_at': self.subscription_ends_at.isoformat() if self.subscription_ends_at else None,
            'business_id': self.business_id
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class OnboardingProgress(Base):
    __tablename__ = 'onboarding_progress'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    step = db.Column(db.String(50), nullable=False)  # connect_twilio, import_csv, enable_auto_reply, send_test_sms, connect_calendly
    completed_at = db.Column(db.DateTime)
    data = db.Column(db.JSON)  # Step-specific data
    
    user = db.relationship('User', backref='onboarding_steps')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'step', name='unique_user_step'),
    )
    
    def __repr__(self):
        return f'<OnboardingProgress {self.user_id}:{self.step}>'


class ROIReport(Base):
    __tablename__ = 'roi_reports'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # Report metrics
    leads_received = db.Column(db.Integer, default=0)
    leads_responded = db.Column(db.Integer, default=0)
    calls_booked = db.Column(db.Integer, default=0)
    deals_closed = db.Column(db.Integer, default=0)
    estimated_revenue = db.Column(db.Numeric(12, 2), default=0)
    total_cost = db.Column(db.Numeric(12, 2), default=0)
    roi_percentage = db.Column(db.Float, default=0)
    
    # Report delivery
    pdf_url = db.Column(db.String(500))
    emailed_at = db.Column(db.DateTime)
    
    business = db.relationship('Business', backref='roi_reports')
    
    def __repr__(self):
        return f'<ROIReport {self.business_id}: {self.period_start} - {self.period_end}>'


class Integration(Base):
    __tablename__ = 'integrations'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # zapier, slack, calendly, twilio
    name = db.Column(db.String(100), nullable=False)
    webhook_url = db.Column(db.String(500))
    api_key = db.Column(db.String(255))
    settings = db.Column(db.JSON, default={})
    enabled = db.Column(db.Boolean, default=True)
    last_triggered_at = db.Column(db.DateTime)
    
    business = db.relationship('Business', backref='integrations')
    
    __table_args__ = (
        db.UniqueConstraint('business_id', 'type', 'name', name='unique_business_integration'),
    )
    
    def __repr__(self):
        return f'<Integration {self.type}:{self.name}>'


class NurtureSequence(Base):
    __tablename__ = 'nurture_sequences'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    vertical = db.Column(db.String(50))  # contractors, dentists, lawyers, etc.
    steps = db.Column(db.JSON, nullable=False)  # Array of step objects with timing and content
    total_sent = db.Column(db.Integer, default=0)
    total_opened = db.Column(db.Integer, default=0)
    total_replied = db.Column(db.Integer, default=0)
    total_booked = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    
    business = db.relationship('Business', backref='nurture_sequences')
    
    def __repr__(self):
        return f'<NurtureSequence {self.name}>'


class NurtureExecution(Base):
    __tablename__ = 'nurture_executions'
    
    sequence_id = db.Column(db.Integer, db.ForeignKey('nurture_sequences.id'), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    current_step = db.Column(db.Integer, default=0)
    next_action_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    stopped_at = db.Column(db.DateTime)
    stop_reason = db.Column(db.String(100))  # replied, unsubscribed, booked, manual
    
    sequence = db.relationship('NurtureSequence', backref='executions')
    lead = db.relationship('Lead', backref='nurture_executions')
    
    __table_args__ = (
        db.UniqueConstraint('sequence_id', 'lead_id', name='unique_sequence_lead'),
    )
    
    def __repr__(self):
        return f'<NurtureExecution {self.sequence_id}:{self.lead_id}>'


class AIScoring(Base):
    __tablename__ = 'ai_scoring'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 0-100 score
    factors = db.Column(db.JSON)  # Contributing factors and weights
    priority = db.Column(db.String(20))  # high, medium, low
    recommended_action = db.Column(db.String(100))  # call_immediately, send_nurture, qualify_further
    best_contact_time = db.Column(db.String(50))  # morning, afternoon, evening
    
    business = db.relationship('Business', backref='ai_scores')
    lead = db.relationship('Lead', backref='ai_scores')
    
    __table_args__ = (
        db.UniqueConstraint('business_id', 'lead_id', name='unique_business_lead_score'),
    )
    
    def __repr__(self):
        return f'<AIScoring {self.lead_id}: {self.score}>'


class AIScoringConfig(Base):
    __tablename__ = 'ai_scoring_config'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False, unique=True)
    recency_weight = db.Column(db.Float, default=0.3)
    source_weight = db.Column(db.Float, default=0.2)
    engagement_weight = db.Column(db.Float, default=0.3)
    profile_completeness_weight = db.Column(db.Float, default=0.2)
    high_value_sources = db.Column(db.JSON, default=lambda: ['google_ads', 'referral', 'website'])
    peak_contact_hours = db.Column(db.JSON, default=lambda: {'start': 9, 'end': 17})
    
    business = db.relationship('Business', backref='ai_config')
    
    def __repr__(self):
        return f'<AIScoringConfig {self.business_id}>'


class Testimonial(Base):
    __tablename__ = 'testimonials'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=True)  # Optional - may be manual entry
    content = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(200))
    author_title = db.Column(db.String(200))
    star_rating = db.Column(db.Integer)  # 1-5 stars
    public = db.Column(db.Boolean, default=False)
    featured = db.Column(db.Boolean, default=False)
    
    business = db.relationship('Business', backref='testimonials')
    lead = db.relationship('Lead', backref='testimonials')
    
    def __repr__(self):
        return f'<Testimonial {self.author_name}: {self.star_rating} stars>'


class ActivityLog(Base):
    __tablename__ = 'activity_logs'
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Activity details
    action = db.Column(db.String(100), nullable=False)  # lead_created, message_sent, call_logged, etc.
    description = db.Column(db.Text)
    extra_data = db.Column(db.JSON, default={})
    
    # Source tracking
    source = db.Column(db.String(50))  # api, webhook, manual, automation
    integration_id = db.Column(db.Integer, db.ForeignKey('integrations.id'), nullable=True)
    
    business = db.relationship('Business', backref='activities')
    lead = db.relationship('Lead', backref='activities')
    user = db.relationship('User', backref='activities')
    integration = db.relationship('Integration', backref='activities')
    
    def __repr__(self):
        return f'<ActivityLog {self.action}: {self.description[:50]}>'
