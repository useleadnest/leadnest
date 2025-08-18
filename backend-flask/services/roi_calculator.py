"""
ROI Analytics Engine
Competitive advantage feature for LeadNest
"""
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ROIMetrics:
    leads_uploaded: int
    calls_made: int
    emails_sent: int
    appointments_booked: int
    deals_closed: int
    revenue_generated: float
    cost_per_lead: float
    conversion_rate: float
    roi_percentage: float
    projected_monthly_revenue: float

class ROICalculator:
    """
    Calculate and track ROI metrics for competitive advantage
    """
    
    def __init__(self):
        # Industry benchmarks for projections
        self.industry_benchmarks = {
            'medspas': {
                'avg_deal_value': 2500,
                'conversion_rate': 0.12,
                'appointment_to_close': 0.35
            },
            'law_firms': {
                'avg_deal_value': 5000,
                'conversion_rate': 0.08,
                'appointment_to_close': 0.25
            },
            'contractors': {
                'avg_deal_value': 15000,
                'conversion_rate': 0.15,
                'appointment_to_close': 0.40
            },
            'salons': {
                'avg_deal_value': 150,
                'conversion_rate': 0.20,
                'appointment_to_close': 0.60
            },
            'default': {
                'avg_deal_value': 3000,
                'conversion_rate': 0.10,
                'appointment_to_close': 0.30
            }
        }

    def calculate_roi_metrics(self, user_id: str, timeframe_days: int = 30) -> ROIMetrics:
        """
        Calculate comprehensive ROI metrics for a user
        """
        # In real implementation, these would come from database
        # For now, using demo data that scales with user activity
        
        # Mock data based on user activity patterns
        leads_uploaded = self._get_leads_count(user_id, timeframe_days)
        calls_made = int(leads_uploaded * 0.8)  # 80% of leads get called
        emails_sent = int(leads_uploaded * 1.2)  # Multiple emails per lead
        appointments_booked = int(leads_uploaded * 0.15)  # 15% conversion to appointment
        deals_closed = int(appointments_booked * 0.3)  # 30% appointment to close
        
        # Revenue calculations
        avg_deal_value = self._get_avg_deal_value(user_id)
        revenue_generated = deals_closed * avg_deal_value
        
        # Cost calculations (LeadNest subscription + lead acquisition)
        monthly_subscription = self._get_subscription_cost(user_id)
        lead_acquisition_cost = leads_uploaded * 5  # $5 per lead estimate
        total_cost = monthly_subscription + lead_acquisition_cost
        
        cost_per_lead = total_cost / max(leads_uploaded, 1)
        conversion_rate = deals_closed / max(leads_uploaded, 1)
        roi_percentage = ((revenue_generated - total_cost) / max(total_cost, 1)) * 100
        
        # Project monthly revenue based on current trend
        daily_revenue = revenue_generated / max(timeframe_days, 1)
        projected_monthly_revenue = daily_revenue * 30
        
        return ROIMetrics(
            leads_uploaded=leads_uploaded,
            calls_made=calls_made,
            emails_sent=emails_sent,
            appointments_booked=appointments_booked,
            deals_closed=deals_closed,
            revenue_generated=revenue_generated,
            cost_per_lead=cost_per_lead,
            conversion_rate=conversion_rate,
            roi_percentage=roi_percentage,
            projected_monthly_revenue=projected_monthly_revenue
        )

    def get_roi_insights(self, metrics: ROIMetrics, user_industry: str = 'default') -> List[str]:
        """
        Generate actionable ROI insights
        """
        insights = []
        benchmarks = self.industry_benchmarks.get(user_industry, self.industry_benchmarks['default'])
        
        # Revenue insights
        if metrics.revenue_generated > 0:
            insights.append(f"💰 Generated ${metrics.revenue_generated:,.0f} in revenue this month!")
        
        if metrics.roi_percentage > 200:
            insights.append(f"🚀 Exceptional {metrics.roi_percentage:.0f}% ROI - you're crushing it!")
        elif metrics.roi_percentage > 100:
            insights.append(f"📈 Strong {metrics.roi_percentage:.0f}% ROI - great performance!")
        elif metrics.roi_percentage > 0:
            insights.append(f"📊 {metrics.roi_percentage:.0f}% ROI - room for optimization")
        else:
            insights.append("🎯 Focus on lead quality to improve ROI")
        
        # Conversion insights
        if metrics.conversion_rate > benchmarks['conversion_rate']:
            insights.append(f"🎯 Above industry average conversion rate ({metrics.conversion_rate:.1%})")
        else:
            insights.append(f"💡 Conversion rate below industry average - focus on lead nurturing")
        
        # Activity insights
        if metrics.appointments_booked > 20:
            insights.append("📅 High appointment volume - consider automating follow-ups")
        elif metrics.appointments_booked < 5:
            insights.append("📞 Increase appointment bookings with faster response times")
        
        # Cost insights
        if metrics.cost_per_lead < 20:
            insights.append("💸 Excellent cost per lead - scale up your campaigns!")
        elif metrics.cost_per_lead > 50:
            insights.append("🔍 High cost per lead - optimize targeting and sources")
        
        return insights

    def get_growth_recommendations(self, metrics: ROIMetrics, user_industry: str = 'default') -> List[Dict]:
        """
        Generate specific growth recommendations
        """
        recommendations = []
        benchmarks = self.industry_benchmarks.get(user_industry, self.industry_benchmarks['default'])
        
        # Lead volume recommendations
        if metrics.leads_uploaded < 50:
            recommendations.append({
                'category': 'Lead Generation',
                'title': 'Increase Lead Volume',
                'description': 'Scale to 100+ leads/month for better ROI optimization',
                'impact': 'High',
                'effort': 'Medium'
            })
        
        # Conversion rate improvements
        if metrics.conversion_rate < benchmarks['conversion_rate']:
            recommendations.append({
                'category': 'Conversion',
                'title': 'Improve Response Time',
                'description': 'Respond to leads within 5 minutes for 900% better conversion',
                'impact': 'High',
                'effort': 'Low'
            })
        
        # Follow-up improvements
        if metrics.calls_made / max(metrics.leads_uploaded, 1) < 0.9:
            recommendations.append({
                'category': 'Follow-up',
                'title': 'Increase Call Volume',
                'description': 'Call 90%+ of leads for maximum conversion',
                'impact': 'Medium',
                'effort': 'Low'
            })
        
        # Revenue optimization
        if metrics.deals_closed > 0 and metrics.revenue_generated / metrics.deals_closed < benchmarks['avg_deal_value']:
            recommendations.append({
                'category': 'Revenue',
                'title': 'Increase Average Deal Size',
                'description': 'Focus on upselling and premium service packages',
                'impact': 'High',
                'effort': 'Medium'
            })
        
        return recommendations

    def _get_leads_count(self, user_id: str, days: int) -> int:
        """Get actual leads count from database"""
        # Mock implementation - replace with real database query
        base_leads = hash(user_id) % 100 + 20  # 20-120 leads
        return int(base_leads * (days / 30))  # Scale by timeframe

    def _get_avg_deal_value(self, user_id: str) -> float:
        """Get user's average deal value"""
        # Mock implementation - replace with real calculation
        user_hash = hash(user_id) % 4
        if user_hash == 0:
            return 15000  # Contractor
        elif user_hash == 1:
            return 5000   # Law firm
        elif user_hash == 2:
            return 2500   # Medspa
        else:
            return 3000   # Default

    def _get_subscription_cost(self, user_id: str) -> float:
        """Get user's monthly subscription cost"""
        # Mock implementation - replace with real subscription data
        plans = [299, 699, 1299]  # Starter, Pro, Enterprise
        return plans[hash(user_id) % len(plans)]

class CompetitiveAnalyzer:
    """
    Analyze user performance against competitors and industry
    """
    
    def get_competitive_position(self, metrics: ROIMetrics, industry: str) -> Dict:
        """
        Show where user stands vs competition
        """
        benchmarks = {
            'industry_avg_roi': 150,
            'top_10_percent_roi': 400,
            'industry_avg_conversion': 0.08,
            'top_performers_conversion': 0.20
        }
        
        position = {
            'roi_percentile': min(100, (metrics.roi_percentage / benchmarks['top_10_percent_roi']) * 90),
            'conversion_percentile': min(100, (metrics.conversion_rate / benchmarks['top_performers_conversion']) * 90),
            'overall_grade': 'A+',
            'beat_competitors': True,
            'improvement_areas': []
        }
        
        # Determine grade
        if position['roi_percentile'] > 80:
            position['overall_grade'] = 'A+'
        elif position['roi_percentile'] > 60:
            position['overall_grade'] = 'A'
        elif position['roi_percentile'] > 40:
            position['overall_grade'] = 'B'
        else:
            position['overall_grade'] = 'C'
        
        # Improvement areas
        if metrics.roi_percentage < benchmarks['industry_avg_roi']:
            position['improvement_areas'].append('ROI below industry average')
        
        if metrics.conversion_rate < benchmarks['industry_avg_conversion']:
            position['improvement_areas'].append('Conversion rate needs improvement')
        
        return position
