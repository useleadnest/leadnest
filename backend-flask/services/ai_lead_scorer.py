"""
AI Lead Scoring Engine
Competitive advantage feature for LeadNest
"""
import datetime
from typing import Dict, List, Optional
import re

class AILeadScorer:
    """
    Smart AI Lead Scoring Engine
    Scores leads from 0-100 based on multiple criteria
    """
    
    def __init__(self):
        self.industry_weights = {
            'medspas': {'budget_weight': 0.3, 'urgency_weight': 0.4, 'engagement_weight': 0.3},
            'law_firms': {'budget_weight': 0.4, 'urgency_weight': 0.3, 'engagement_weight': 0.3},
            'contractors': {'budget_weight': 0.35, 'urgency_weight': 0.35, 'engagement_weight': 0.3},
            'salons': {'budget_weight': 0.25, 'urgency_weight': 0.45, 'engagement_weight': 0.3},
            'default': {'budget_weight': 0.33, 'urgency_weight': 0.33, 'engagement_weight': 0.34}
        }
        
        # High-value keywords that indicate hot leads
        self.hot_keywords = [
            'urgent', 'asap', 'emergency', 'immediate', 'ready to start',
            'budget approved', 'decision maker', 'need quote', 'when can you start',
            'looking to hire', 'project starting', 'deadline'
        ]
        
        self.warm_keywords = [
            'interested', 'considering', 'exploring', 'researching',
            'timeline', 'options', 'proposal', 'estimate', 'meeting'
        ]

    def score_lead(self, lead_data: Dict) -> Dict:
        """
        Score a single lead and return score + reasoning
        """
        try:
            # Extract lead information
            company_name = lead_data.get('company_name', '')
            contact_name = lead_data.get('contact_name', '')
            email = lead_data.get('email', '')
            phone = lead_data.get('phone', '')
            project_type = lead_data.get('project_type', '')
            budget = lead_data.get('budget', '')
            timeline = lead_data.get('timeline', '')
            notes = lead_data.get('notes', '')
            created_at = lead_data.get('created_at', '')
            
            # Calculate individual scores
            budget_score = self._score_budget(budget)
            urgency_score = self._score_urgency(timeline, notes)
            engagement_score = self._score_engagement(email, phone, notes, company_name)
            recency_score = self._score_recency(created_at)
            
            # Determine industry for weighted scoring
            industry = self._detect_industry(project_type, company_name, notes)
            weights = self.industry_weights.get(industry, self.industry_weights['default'])
            
            # Calculate weighted final score
            final_score = (
                budget_score * weights['budget_weight'] +
                urgency_score * weights['urgency_weight'] +
                engagement_score * weights['engagement_weight']
            ) * recency_score  # Recency as multiplier
            
            # Cap at 100
            final_score = min(100, max(0, final_score))
            
            # Determine category
            if final_score >= 80:
                category = 'hot'
                priority = 1
            elif final_score >= 60:
                category = 'warm'
                priority = 2
            else:
                category = 'cold'
                priority = 3
            
            # Generate insights
            insights = self._generate_insights(
                budget_score, urgency_score, engagement_score, 
                recency_score, category, notes, timeline
            )
            
            return {
                'ai_score': round(final_score, 1),
                'category': category,
                'priority': priority,
                'industry': industry,
                'breakdown': {
                    'budget_score': round(budget_score, 1),
                    'urgency_score': round(urgency_score, 1),
                    'engagement_score': round(engagement_score, 1),
                    'recency_score': round(recency_score, 2)
                },
                'insights': insights,
                'recommended_action': self._get_recommended_action(category, final_score)
            }
            
        except Exception as e:
            # Fallback scoring
            return {
                'ai_score': 50.0,
                'category': 'warm',
                'priority': 2,
                'industry': 'unknown',
                'breakdown': {},
                'insights': ['Unable to fully analyze lead - manual review recommended'],
                'recommended_action': 'Review manually and follow up within 24 hours'
            }

    def _score_budget(self, budget: str) -> float:
        """Score based on budget information"""
        if not budget:
            return 40.0  # No budget info = neutral
        
        budget_lower = budget.lower()
        
        # Extract budget ranges
        if any(x in budget_lower for x in ['$1m', '$2m', '$5m', '1 million', '2 million']):
            return 95.0
        elif any(x in budget_lower for x in ['$500k', '$750k', '500,000', '750,000']):
            return 85.0
        elif any(x in budget_lower for x in ['$250k', '$300k', '$400k', '250,000']):
            return 75.0
        elif any(x in budget_lower for x in ['$100k', '$150k', '100,000']):
            return 65.0
        elif any(x in budget_lower for x in ['$50k', '$75k', '50,000']):
            return 55.0
        elif any(x in budget_lower for x in ['budget approved', 'funding secured']):
            return 80.0
        elif any(x in budget_lower for x in ['flexible', 'negotiable']):
            return 60.0
        elif any(x in budget_lower for x in ['tight budget', 'limited', 'cheap']):
            return 25.0
        else:
            return 45.0

    def _score_urgency(self, timeline: str, notes: str) -> float:
        """Score based on urgency indicators"""
        text = f"{timeline} {notes}".lower()
        
        # Check for hot keywords
        hot_count = sum(1 for keyword in self.hot_keywords if keyword in text)
        warm_count = sum(1 for keyword in self.warm_keywords if keyword in text)
        
        if hot_count >= 2:
            return 90.0
        elif hot_count >= 1:
            return 75.0
        elif warm_count >= 2:
            return 60.0
        elif warm_count >= 1:
            return 50.0
        
        # Timeline analysis
        if any(x in text for x in ['asap', 'immediate', 'urgent', 'emergency']):
            return 85.0
        elif any(x in text for x in ['this week', 'next week', '1 week']):
            return 80.0
        elif any(x in text for x in ['this month', 'next month', '30 days']):
            return 65.0
        elif any(x in text for x in ['3 months', '6 months', 'quarter']):
            return 45.0
        elif any(x in text for x in ['next year', '12 months', 'someday']):
            return 25.0
        
        return 40.0

    def _score_engagement(self, email: str, phone: str, notes: str, company_name: str) -> float:
        """Score based on lead quality and engagement indicators"""
        score = 0.0
        
        # Email quality
        if email:
            if '@' in email and '.' in email:
                score += 15.0
                if any(domain in email.lower() for domain in ['gmail', 'yahoo', 'hotmail']):
                    score += 5.0
                else:
                    score += 15.0  # Business email = higher quality
        
        # Phone number quality
        if phone:
            cleaned_phone = re.sub(r'[^\d]', '', phone)
            if len(cleaned_phone) >= 10:
                score += 20.0
        
        # Company name indicates business lead
        if company_name and len(company_name) > 2:
            score += 20.0
        
        # Notes indicate engagement
        if notes:
            if len(notes) > 100:
                score += 20.0
            elif len(notes) > 50:
                score += 10.0
            
            # Check for detailed requirements
            if any(x in notes.lower() for x in ['need', 'require', 'looking for', 'project']):
                score += 10.0
        
        return min(100.0, score)

    def _score_recency(self, created_at: str) -> float:
        """Score multiplier based on lead recency"""
        if not created_at:
            return 1.0
        
        try:
            if isinstance(created_at, str):
                lead_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                lead_date = created_at
            
            now = datetime.datetime.now(datetime.timezone.utc)
            hours_old = (now - lead_date).total_seconds() / 3600
            
            if hours_old <= 1:
                return 1.2  # Fresh leads get boost
            elif hours_old <= 24:
                return 1.1
            elif hours_old <= 72:
                return 1.0
            elif hours_old <= 168:  # 1 week
                return 0.9
            else:
                return 0.8  # Older leads penalized
                
        except:
            return 1.0

    def _detect_industry(self, project_type: str, company_name: str, notes: str) -> str:
        """Detect industry from lead data"""
        text = f"{project_type} {company_name} {notes}".lower()
        
        if any(x in text for x in ['medspa', 'botox', 'filler', 'laser', 'aesthetic']):
            return 'medspas'
        elif any(x in text for x in ['law', 'legal', 'attorney', 'lawyer', 'firm']):
            return 'law_firms'
        elif any(x in text for x in ['construction', 'contractor', 'building', 'renovation']):
            return 'contractors'
        elif any(x in text for x in ['salon', 'hair', 'beauty', 'spa', 'nails']):
            return 'salons'
        else:
            return 'default'

    def _generate_insights(self, budget_score: float, urgency_score: float, 
                          engagement_score: float, recency_score: float,
                          category: str, notes: str, timeline: str) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        if category == 'hot':
            insights.append("🔥 HIGH PRIORITY: Contact within 1 hour for best conversion")
        elif category == 'warm':
            insights.append("⚡ Follow up within 4 hours while interest is high")
        
        if budget_score > 80:
            insights.append("💰 High budget potential - emphasize premium services")
        elif budget_score < 40:
            insights.append("💡 Price-sensitive - focus on ROI and value proposition")
        
        if urgency_score > 80:
            insights.append("⏰ Time-sensitive project - fast response critical")
        
        if engagement_score < 40:
            insights.append("📋 Limited contact info - verify details during first call")
        
        if recency_score > 1.1:
            insights.append("🆕 Fresh lead - strike while iron is hot!")
        
        return insights

    def _get_recommended_action(self, category: str, score: float) -> str:
        """Get recommended next action"""
        if category == 'hot':
            return "Call immediately. Send SMS if no answer. Follow up every hour until contact."
        elif category == 'warm':
            return "Call within 4 hours. If no answer, send email and schedule follow-up call."
        else:
            return "Add to nurture sequence. Schedule follow-up in 1 week."

    def bulk_score_leads(self, leads: List[Dict]) -> List[Dict]:
        """Score multiple leads efficiently"""
        scored_leads = []
        for lead in leads:
            score_data = self.score_lead(lead)
            lead_with_score = lead.copy()
            lead_with_score.update(score_data)
            scored_leads.append(lead_with_score)
        
        # Sort by score descending
        return sorted(scored_leads, key=lambda x: x['ai_score'], reverse=True)
