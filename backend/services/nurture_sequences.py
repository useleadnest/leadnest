"""
Automated Nurture Sequences
Competitive advantage feature for LeadNest
"""
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class SequenceType(Enum):
    INITIAL_OUTREACH = "initial_outreach"
    FOLLOW_UP = "follow_up"
    RE_ENGAGEMENT = "re_engagement"
    CLOSING_SEQUENCE = "closing_sequence"
    POST_APPOINTMENT = "post_appointment"

class MessageChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    CALL = "call"
    VOICEMAIL = "voicemail"

@dataclass
class SequenceStep:
    step_number: int
    delay_hours: int
    channel: MessageChannel
    subject: str
    message_template: str
    conditions: Optional[Dict] = None
    stop_if_replied: bool = True

@dataclass
class NurtureSequence:
    sequence_id: str
    name: str
    sequence_type: SequenceType
    industry: str
    steps: List[SequenceStep]
    active: bool = True
    success_rate: float = 0.0

class NurtureSequenceEngine:
    """
    Automated nurture sequences for competitive advantage
    """
    
    def __init__(self):
        self.sequences = self._load_default_sequences()
    
    def _load_default_sequences(self) -> Dict[str, NurtureSequence]:
        """
        Load industry-specific nurture sequences
        """
        sequences = {}
        
        # Medspa Initial Outreach Sequence
        medspa_initial = NurtureSequence(
            sequence_id="medspa_initial",
            name="Medspa New Lead Nurture",
            sequence_type=SequenceType.INITIAL_OUTREACH,
            industry="medspas",
            steps=[
                SequenceStep(
                    step_number=1,
                    delay_hours=0,
                    channel=MessageChannel.SMS,
                    subject="",
                    message_template="Hi {first_name}! Thanks for your interest in {service_type}. I'm {agent_name} from {business_name}. I'd love to schedule a quick consultation to discuss your goals. When works best for you - today or tomorrow?",
                ),
                SequenceStep(
                    step_number=2,
                    delay_hours=2,
                    channel=MessageChannel.EMAIL,
                    subject="Your {service_type} consultation details",
                    message_template="""Hi {first_name},

I wanted to follow up on my text about your {service_type} consultation.

At {business_name}, we've helped over 500 clients achieve their aesthetic goals with our proven approach:

✓ FDA-approved treatments only
✓ Certified medical professionals
✓ Personalized treatment plans
✓ Financing options available

I'd love to show you our before/after gallery and discuss what results you can expect.

Are you available for a 15-minute consultation tomorrow?

Best,
{agent_name}
{business_name}
{phone}""",
                ),
                SequenceStep(
                    step_number=3,
                    delay_hours=24,
                    channel=MessageChannel.CALL,
                    subject="",
                    message_template="Follow-up call script: Mention their inquiry about {service_type}, offer flexible scheduling, address common concerns about safety and results.",
                ),
                SequenceStep(
                    step_number=4,
                    delay_hours=48,
                    channel=MessageChannel.EMAIL,
                    subject="Limited time: Special offer for {first_name}",
                    message_template="""Hi {first_name},

I know you're considering {service_type}, and I wanted to make this easy for you.

This week only, we're offering:
🎉 20% off your first treatment
🎉 Free consultation (normally $150)
🎉 Flexible payment plans

Plus, I can answer any questions you have about:
• What to expect during treatment
• Recovery time and aftercare
• Long-term results
• Safety protocols

Ready to take the next step? Just reply with your preferred day and time.

Limited spots available this week!

{agent_name}
{business_name}""",
                ),
                SequenceStep(
                    step_number=5,
                    delay_hours=120,
                    channel=MessageChannel.SMS,
                    subject="",
                    message_template="Hi {first_name}, just wanted to check if you had any questions about {service_type}? I'm here to help and can work around your schedule. - {agent_name}",
                ),
            ],
            success_rate=0.18
        )
        sequences["medspa_initial"] = medspa_initial
        
        # Contractor Initial Outreach Sequence
        contractor_initial = NurtureSequence(
            sequence_id="contractor_initial",
            name="Contractor New Lead Nurture",
            sequence_type=SequenceType.INITIAL_OUTREACH,
            industry="contractors",
            steps=[
                SequenceStep(
                    step_number=1,
                    delay_hours=0,
                    channel=MessageChannel.CALL,
                    subject="",
                    message_template="Call script: Hi {first_name}, this is {agent_name} from {business_name}. I saw your inquiry about {service_type}. I'd love to schedule a free estimate. Are you available this week?",
                ),
                SequenceStep(
                    step_number=2,
                    delay_hours=1,
                    channel=MessageChannel.SMS,
                    subject="",
                    message_template="Hi {first_name}! Just called about your {service_type} project. I'd love to provide a free estimate. When's the best time to visit your property? - {agent_name}, {business_name}",
                ),
                SequenceStep(
                    step_number=3,
                    delay_hours=24,
                    channel=MessageChannel.EMAIL,
                    subject="Your {service_type} project estimate",
                    message_template="""Hi {first_name},

Thanks for considering {business_name} for your {service_type} project.

We've been serving {city} homeowners for {years_in_business} years with:
✓ Licensed & insured professionals
✓ Free detailed estimates
✓ Quality workmanship guarantee
✓ Competitive pricing
✓ Flexible scheduling

I'd love to visit your property and provide a detailed estimate. Most estimates take 15-20 minutes, and I can work around your schedule.

Are you available this week? I have openings:
• Tuesday 2-6 PM
• Wednesday 10 AM-4 PM
• Thursday 1-5 PM

Just reply with what works best!

{agent_name}
{business_name}
Licensed & Insured | {license_number}
{phone}""",
                ),
                SequenceStep(
                    step_number=4,
                    delay_hours=48,
                    channel=MessageChannel.CALL,
                    subject="",
                    message_template="Follow-up call: Discuss timeline, budget range, show recent project photos, emphasize free estimate value.",
                ),
                SequenceStep(
                    step_number=5,
                    delay_hours=96,
                    channel=MessageChannel.EMAIL,
                    subject="Still planning your {service_type} project?",
                    message_template="""Hi {first_name},

I wanted to follow up on your {service_type} project. 

As we head into {current_season}, it's a great time to get projects scheduled. Here's what's included in our free estimate:

📋 Detailed scope of work
💰 Transparent pricing breakdown
📅 Project timeline
📸 Photos of similar completed projects
🛡️ Warranty information

No pressure - just helpful information to make your decision easier.

Would this weekend work for a quick walkthrough?

{agent_name}
{business_name}""",
                ),
            ],
            success_rate=0.25
        )
        sequences["contractor_initial"] = contractor_initial
        
        return sequences
    
    def get_sequence_for_lead(self, lead_data: Dict, sequence_type: SequenceType = SequenceType.INITIAL_OUTREACH) -> Optional[NurtureSequence]:
        """
        Get the best nurture sequence for a specific lead
        """
        industry = lead_data.get('industry', 'default').lower()
        
        # Find industry-specific sequence
        sequence_key = f"{industry}_{sequence_type.value}"
        if sequence_key in self.sequences:
            return self.sequences[sequence_key]
        
        # Fallback to default sequence
        default_key = f"default_{sequence_type.value}"
        return self.sequences.get(default_key)
    
    def personalize_message(self, template: str, lead_data: Dict, business_data: Dict) -> str:
        """
        Personalize message template with lead and business data
        """
        # Merge lead and business data
        template_vars = {**lead_data, **business_data}
        
        # Add computed variables
        template_vars['current_season'] = self._get_current_season()
        template_vars['first_name'] = lead_data.get('name', 'there').split()[0]
        
        try:
            return template.format(**template_vars)
        except KeyError as e:
            # Return template with unfilled variables if data missing
            return template
    
    def _get_current_season(self) -> str:
        """Get current season for seasonal messaging"""
        month = datetime.datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    def schedule_sequence(self, lead_id: str, sequence: NurtureSequence, lead_data: Dict, business_data: Dict) -> List[Dict]:
        """
        Schedule a nurture sequence for a lead
        """
        scheduled_steps = []
        base_time = datetime.datetime.now()
        
        for step in sequence.steps:
            scheduled_time = base_time + datetime.timedelta(hours=step.delay_hours)
            
            personalized_message = self.personalize_message(step.message_template, lead_data, business_data)
            personalized_subject = self.personalize_message(step.subject, lead_data, business_data) if step.subject else ""
            
            scheduled_step = {
                'lead_id': lead_id,
                'sequence_id': sequence.sequence_id,
                'step_number': step.step_number,
                'scheduled_time': scheduled_time.isoformat(),
                'channel': step.channel.value,
                'subject': personalized_subject,
                'message': personalized_message,
                'stop_if_replied': step.stop_if_replied,
                'status': 'scheduled'
            }
            
            scheduled_steps.append(scheduled_step)
        
        return scheduled_steps
    
    def get_sequence_analytics(self, sequence_id: str, timeframe_days: int = 30) -> Dict:
        """
        Get analytics for a nurture sequence
        """
        # Mock analytics - replace with real database queries
        return {
            'sequence_id': sequence_id,
            'total_leads': 245,
            'completed_sequences': 198,
            'responses': 67,
            'appointments_booked': 45,
            'deals_closed': 18,
            'response_rate': 0.27,
            'appointment_rate': 0.18,
            'close_rate': 0.07,
            'roi': 340,
            'best_performing_step': 2,
            'avg_response_time_hours': 4.2
        }
    
    def optimize_sequence(self, sequence_id: str) -> Dict:
        """
        AI-powered sequence optimization recommendations
        """
        analytics = self.get_sequence_analytics(sequence_id)
        
        recommendations = []
        
        if analytics['response_rate'] < 0.15:
            recommendations.append({
                'type': 'timing',
                'message': 'Try sending the first follow-up 4 hours earlier for better response rates',
                'expected_improvement': '15%'
            })
        
        if analytics['appointment_rate'] < 0.12:
            recommendations.append({
                'type': 'messaging',
                'message': 'Add urgency and specific availability times to improve appointment booking',
                'expected_improvement': '20%'
            })
        
        return {
            'sequence_id': sequence_id,
            'current_performance': analytics,
            'recommendations': recommendations,
            'optimization_score': 85
        }

class SequenceManager:
    """
    Manage active nurture sequences
    """
    
    def __init__(self):
        self.engine = NurtureSequenceEngine()
    
    def start_sequence_for_lead(self, lead_data: Dict, business_data: Dict) -> Dict:
        """
        Start appropriate nurture sequence for a new lead
        """
        sequence = self.engine.get_sequence_for_lead(lead_data)
        if not sequence:
            return {'error': 'No suitable sequence found'}
        
        scheduled_steps = self.engine.schedule_sequence(
            lead_data['id'], 
            sequence, 
            lead_data, 
            business_data
        )
        
        return {
            'sequence_id': sequence.sequence_id,
            'sequence_name': sequence.name,
            'total_steps': len(scheduled_steps),
            'scheduled_steps': scheduled_steps,
            'expected_success_rate': sequence.success_rate
        }
    
    def pause_sequence(self, lead_id: str, reason: str = "manual_pause") -> Dict:
        """
        Pause nurture sequence for a lead
        """
        # Implementation would update database
        return {
            'lead_id': lead_id,
            'status': 'paused',
            'reason': reason,
            'paused_at': datetime.datetime.now().isoformat()
        }
    
    def resume_sequence(self, lead_id: str) -> Dict:
        """
        Resume paused nurture sequence
        """
        # Implementation would update database and reschedule
        return {
            'lead_id': lead_id,
            'status': 'active',
            'resumed_at': datetime.datetime.now().isoformat()
        }
