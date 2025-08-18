"""
Shared Inbox & Call Log
Competitive advantage feature for LeadNest
"""
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    EMAIL = "email"
    SMS = "sms"
    CALL = "call"
    VOICEMAIL = "voicemail"
    NOTE = "note"

class MessageStatus(Enum):
    UNREAD = "unread"
    READ = "read"
    REPLIED = "replied"
    ARCHIVED = "archived"

class CallDisposition(Enum):
    CONNECTED = "connected"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    VOICEMAIL = "voicemail"
    WRONG_NUMBER = "wrong_number"
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    NOT_INTERESTED = "not_interested"

@dataclass
class Message:
    message_id: str
    lead_id: str
    user_id: str
    message_type: MessageType
    direction: str  # "inbound" or "outbound"
    content: str
    subject: Optional[str]
    sender: str
    recipient: str
    timestamp: datetime.datetime
    status: MessageStatus
    thread_id: Optional[str] = None
    attachments: List[str] = None
    priority: str = "normal"  # "low", "normal", "high", "urgent"

@dataclass
class CallLog:
    call_id: str
    lead_id: str
    user_id: str
    direction: str  # "inbound" or "outbound"
    phone_number: str
    duration_seconds: int
    disposition: CallDisposition
    timestamp: datetime.datetime
    recording_url: Optional[str] = None
    notes: Optional[str] = None
    follow_up_required: bool = False
    scheduled_callback: Optional[datetime.datetime] = None

class SharedInboxManager:
    """
    Unified inbox for all lead communications
    """
    
    def __init__(self):
        self.messages = []  # In real app, this would be database
        self.call_logs = []
    
    def get_inbox(self, user_id: str, filters: Dict = None) -> Dict:
        """
        Get unified inbox with filtering and pagination
        """
        # Apply filters
        messages = self._filter_messages(user_id, filters or {})
        
        # Group by conversations
        conversations = self._group_by_conversations(messages)
        
        # Get summary stats
        stats = self._get_inbox_stats(user_id)
        
        return {
            'conversations': conversations,
            'stats': stats,
            'filters_applied': filters,
            'total_unread': len([m for m in messages if m.status == MessageStatus.UNREAD])
        }
    
    def _filter_messages(self, user_id: str, filters: Dict) -> List[Message]:
        """
        Apply filters to messages
        """
        # Mock implementation - replace with database queries
        all_messages = self._get_user_messages(user_id)
        
        filtered_messages = all_messages
        
        if filters.get('status'):
            filtered_messages = [m for m in filtered_messages if m.status.value == filters['status']]
        
        if filters.get('message_type'):
            filtered_messages = [m for m in filtered_messages if m.message_type.value == filters['message_type']]
        
        if filters.get('priority'):
            filtered_messages = [m for m in filtered_messages if m.priority == filters['priority']]
        
        if filters.get('date_from'):
            date_from = datetime.datetime.fromisoformat(filters['date_from'])
            filtered_messages = [m for m in filtered_messages if m.timestamp >= date_from]
        
        if filters.get('search_term'):
            term = filters['search_term'].lower()
            filtered_messages = [m for m in filtered_messages 
                               if term in m.content.lower() or 
                               (m.subject and term in m.subject.lower())]
        
        return sorted(filtered_messages, key=lambda x: x.timestamp, reverse=True)
    
    def _group_by_conversations(self, messages: List[Message]) -> List[Dict]:
        """
        Group messages into conversation threads
        """
        conversations = {}
        
        for message in messages:
            thread_key = message.thread_id or message.lead_id
            
            if thread_key not in conversations:
                conversations[thread_key] = {
                    'thread_id': thread_key,
                    'lead_id': message.lead_id,
                    'messages': [],
                    'last_message_time': message.timestamp,
                    'unread_count': 0,
                    'priority': 'normal'
                }
            
            conversations[thread_key]['messages'].append({
                'message_id': message.message_id,
                'type': message.message_type.value,
                'direction': message.direction,
                'content': message.content,
                'subject': message.subject,
                'sender': message.sender,
                'timestamp': message.timestamp.isoformat(),
                'status': message.status.value
            })
            
            if message.timestamp > conversations[thread_key]['last_message_time']:
                conversations[thread_key]['last_message_time'] = message.timestamp
            
            if message.status == MessageStatus.UNREAD:
                conversations[thread_key]['unread_count'] += 1
            
            # Set conversation priority to highest message priority
            if message.priority == 'urgent':
                conversations[thread_key]['priority'] = 'urgent'
            elif message.priority == 'high' and conversations[thread_key]['priority'] not in ['urgent']:
                conversations[thread_key]['priority'] = 'high'
        
        # Convert to list and sort by last message time
        conversation_list = list(conversations.values())
        return sorted(conversation_list, key=lambda x: x['last_message_time'], reverse=True)
    
    def _get_inbox_stats(self, user_id: str) -> Dict:
        """
        Get inbox statistics
        """
        messages = self._get_user_messages(user_id)
        calls = self._get_user_calls(user_id)
        
        today = datetime.datetime.now().date()
        today_messages = [m for m in messages if m.timestamp.date() == today]
        today_calls = [c for c in calls if c.timestamp.date() == today]
        
        return {
            'total_messages': len(messages),
            'unread_messages': len([m for m in messages if m.status == MessageStatus.UNREAD]),
            'today_messages': len(today_messages),
            'today_calls': len(today_calls),
            'pending_callbacks': len([c for c in calls if c.scheduled_callback and c.scheduled_callback > datetime.datetime.now()]),
            'high_priority_messages': len([m for m in messages if m.priority in ['high', 'urgent']]),
            'response_rate_24h': 0.85,  # Mock metric
            'avg_response_time_hours': 2.3  # Mock metric
        }
    
    def send_message(self, user_id: str, lead_id: str, message_type: MessageType, 
                    content: str, recipient: str, subject: str = None) -> Dict:
        """
        Send a message through the unified inbox
        """
        message = Message(
            message_id=f"msg_{datetime.datetime.now().timestamp()}",
            lead_id=lead_id,
            user_id=user_id,
            message_type=message_type,
            direction="outbound",
            content=content,
            subject=subject,
            sender=user_id,  # In real app, would be user's contact info
            recipient=recipient,
            timestamp=datetime.datetime.now(),
            status=MessageStatus.READ  # Outbound messages start as read
        )
        
        self.messages.append(message)
        
        # Mock sending logic based on message type
        if message_type == MessageType.EMAIL:
            delivery_status = self._send_email(recipient, subject, content)
        elif message_type == MessageType.SMS:
            delivery_status = self._send_sms(recipient, content)
        else:
            delivery_status = {'status': 'queued'}
        
        return {
            'message_id': message.message_id,
            'status': 'sent',
            'delivery_status': delivery_status,
            'timestamp': message.timestamp.isoformat()
        }
    
    def mark_as_read(self, message_ids: List[str]) -> Dict:
        """
        Mark messages as read
        """
        updated = 0
        for message in self.messages:
            if message.message_id in message_ids and message.status == MessageStatus.UNREAD:
                message.status = MessageStatus.READ
                updated += 1
        
        return {
            'updated': updated,
            'message_ids': message_ids
        }
    
    def _get_user_messages(self, user_id: str) -> List[Message]:
        """
        Get all messages for a user (mock data)
        """
        # Mock data - replace with database queries
        mock_messages = [
            Message(
                message_id="msg_001",
                lead_id="lead_001",
                user_id=user_id,
                message_type=MessageType.EMAIL,
                direction="inbound",
                content="Hi, I'm interested in your medspa services. Can we schedule a consultation?",
                subject="Consultation Request",
                sender="sarah.johnson@email.com",
                recipient="info@yourmedspa.com",
                timestamp=datetime.datetime.now() - datetime.timedelta(hours=2),
                status=MessageStatus.UNREAD,
                priority="high"
            ),
            Message(
                message_id="msg_002",
                lead_id="lead_002",
                user_id=user_id,
                message_type=MessageType.SMS,
                direction="outbound",
                content="Hi John! Thanks for your interest in our kitchen remodeling services. I'd love to schedule a free estimate. When works best for you?",
                subject=None,
                sender="+15551234567",
                recipient="+15559876543",
                timestamp=datetime.datetime.now() - datetime.timedelta(hours=4),
                status=MessageStatus.READ
            ),
        ]
        
        return mock_messages
    
    def _get_user_calls(self, user_id: str) -> List[CallLog]:
        """
        Get all calls for a user (mock data)
        """
        return []  # Mock implementation
    
    def _send_email(self, recipient: str, subject: str, content: str) -> Dict:
        """
        Mock email sending
        """
        return {'status': 'delivered', 'provider': 'sendgrid'}
    
    def _send_sms(self, recipient: str, content: str) -> Dict:
        """
        Mock SMS sending
        """
        return {'status': 'delivered', 'provider': 'twilio'}

class CallLogManager:
    """
    Manage call logs and phone interactions
    """
    
    def __init__(self):
        self.call_logs = []
    
    def log_call(self, user_id: str, lead_id: str, phone_number: str, 
                direction: str, duration_seconds: int, disposition: CallDisposition,
                notes: str = None, recording_url: str = None) -> Dict:
        """
        Log a phone call
        """
        call = CallLog(
            call_id=f"call_{datetime.datetime.now().timestamp()}",
            lead_id=lead_id,
            user_id=user_id,
            direction=direction,
            phone_number=phone_number,
            duration_seconds=duration_seconds,
            disposition=disposition,
            timestamp=datetime.datetime.now(),
            recording_url=recording_url,
            notes=notes
        )
        
        # Auto-schedule follow-up based on disposition
        if disposition in [CallDisposition.NO_ANSWER, CallDisposition.BUSY]:
            call.follow_up_required = True
            call.scheduled_callback = datetime.datetime.now() + datetime.timedelta(hours=2)
        elif disposition == CallDisposition.VOICEMAIL:
            call.follow_up_required = True
            call.scheduled_callback = datetime.datetime.now() + datetime.timedelta(hours=4)
        
        self.call_logs.append(call)
        
        return {
            'call_id': call.call_id,
            'status': 'logged',
            'follow_up_required': call.follow_up_required,
            'scheduled_callback': call.scheduled_callback.isoformat() if call.scheduled_callback else None
        }
    
    def get_call_history(self, user_id: str, lead_id: str = None, days: int = 30) -> List[Dict]:
        """
        Get call history with optional lead filtering
        """
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        filtered_calls = [
            c for c in self.call_logs 
            if c.user_id == user_id and 
            c.timestamp >= start_date and
            (not lead_id or c.lead_id == lead_id)
        ]
        
        return [
            {
                'call_id': call.call_id,
                'lead_id': call.lead_id,
                'phone_number': call.phone_number,
                'direction': call.direction,
                'duration': f"{call.duration_seconds // 60}:{call.duration_seconds % 60:02d}",
                'disposition': call.disposition.value,
                'timestamp': call.timestamp.isoformat(),
                'notes': call.notes,
                'recording_url': call.recording_url,
                'follow_up_required': call.follow_up_required
            }
            for call in sorted(filtered_calls, key=lambda x: x.timestamp, reverse=True)
        ]
    
    def get_callbacks_due(self, user_id: str) -> List[Dict]:
        """
        Get calls that need follow-up
        """
        now = datetime.datetime.now()
        due_callbacks = [
            c for c in self.call_logs 
            if c.user_id == user_id and 
            c.scheduled_callback and 
            c.scheduled_callback <= now and
            c.follow_up_required
        ]
        
        return [
            {
                'call_id': call.call_id,
                'lead_id': call.lead_id,
                'phone_number': call.phone_number,
                'original_call_time': call.timestamp.isoformat(),
                'callback_due': call.scheduled_callback.isoformat(),
                'disposition': call.disposition.value,
                'notes': call.notes
            }
            for call in sorted(due_callbacks, key=lambda x: x.scheduled_callback)
        ]
    
    def get_call_analytics(self, user_id: str, days: int = 30) -> Dict:
        """
        Get call performance analytics
        """
        calls = [c for c in self.call_logs if c.user_id == user_id]
        
        if not calls:
            return {'total_calls': 0}
        
        total_calls = len(calls)
        connected_calls = len([c for c in calls if c.disposition == CallDisposition.CONNECTED])
        appointments_scheduled = len([c for c in calls if c.disposition == CallDisposition.APPOINTMENT_SCHEDULED])
        
        avg_duration = sum(c.duration_seconds for c in calls if c.disposition == CallDisposition.CONNECTED) / max(connected_calls, 1)
        
        return {
            'total_calls': total_calls,
            'connected_calls': connected_calls,
            'connection_rate': connected_calls / total_calls if total_calls > 0 else 0,
            'appointments_scheduled': appointments_scheduled,
            'appointment_rate': appointments_scheduled / total_calls if total_calls > 0 else 0,
            'avg_call_duration_minutes': avg_duration / 60,
            'callbacks_pending': len(self.get_callbacks_due(user_id))
        }
