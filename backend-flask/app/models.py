from datetime import datetime
from .db import db


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Business(Base):
    __tablename__ = 'businesses'
    name = db.Column(db.String(160), nullable=False)
    niche = db.Column(db.String(80))


class Lead(Base):
    __tablename__ = 'leads'
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'))
    full_name = db.Column(db.String(160))
    phone = db.Column(db.String(40))
    email = db.Column(db.String(160))
    source = db.Column(db.String(80))
    status = db.Column(db.String(40), default='new')

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'source': self.source,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }


class Conversation(Base):
    __tablename__ = 'conversations'
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    channel = db.Column(db.String(20))  # sms, email, ig


class Message(Base):
    __tablename__ = 'messages'
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'))
    role = db.Column(db.String(10))  # ai | user | agent
    text = db.Column(db.Text)
    ts = db.Column(db.DateTime, default=datetime.utcnow)


class Booking(Base, db.Model):
    __tablename__ = 'bookings'
    __table_args__ = (db.Index('ix_bookings_starts_at', 'starts_at'),)
    
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    starts_at = db.Column(db.DateTime, index=True)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'notes': self.notes,
        }


class IdempotencyKey(Base, db.Model):
    __tablename__ = 'idempotency_keys'
    key = db.Column(db.String(255), unique=True, index=True, nullable=False)
    response_data = db.Column(db.JSON)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'response_data': self.response_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
