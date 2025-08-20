"""
ROI Calculation Worker for Launch Multiplier.
Handles automated ROI calculations, progress tracking, and insights generation.
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from ..db import db
from ..models import Business, ROIReport, ActivityLog, User
import json
import logging

logger = logging.getLogger(__name__)


class ROICalculationWorker:
    """Worker class for ROI calculations and insights."""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_roi_for_business(self, business_id):
        """Calculate ROI metrics for a specific business."""
        try:
            business = Business.query.filter_by(id=business_id).first()
            if not business:
                self.logger.warning(f"Business {business_id} not found")
                return None
            
            # Get date range (last 30 days by default)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Calculate metrics
            metrics = self._calculate_metrics(business, start_date, end_date)
            
            # Create or update ROI calculation record
            roi_calc = ROIReport.query.filter_by(
                business_id=business_id,
                calculation_type='monthly'
            ).order_by(ROIReport.calculated_at.desc()).first()
            
            if not roi_calc or self._should_recalculate(roi_calc):
                roi_calc = ROIReport(
                    business_id=business_id,
                    calculation_type='monthly'
                )
                db.session.add(roi_calc)
            
            # Update ROI calculation
            roi_calc.period_start = start_date
            roi_calc.period_end = end_date
            roi_calc.estimated_revenue = metrics['total_revenue']
            roi_calc.total_cost = metrics['total_cost']
            roi_calc.roi_percentage = metrics['roi_percentage']
            roi_calc.leads_received = metrics['lead_count']
            roi_calc.deals_closed = int(metrics['lead_count'] * (business.close_rate or 0.15))
            roi_calc.calculated_at = datetime.utcnow()
            
            # Log activity
            activity = ActivityLog(
                business_id=business_id,
                action='roi_calculated',
                description=f'ROI calculated: {metrics["roi_percentage"]:.1f}% ROI',
                extra_data={
                    'roi_percentage': metrics['roi_percentage'],
                    'total_revenue': float(metrics['total_revenue']),
                    'net_profit': float(metrics['net_profit']),
                    'lead_count': metrics['lead_count']
                },
                source='worker'
            )
            db.session.add(activity)
            
            db.session.commit()
            
            self.logger.info(f"ROI calculated for business {business_id}: {metrics['roi_percentage']:.1f}%")
            return roi_calc
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI for business {business_id}: {str(e)}")
            db.session.rollback()
            return None
    
    def _calculate_metrics(self, business, start_date, end_date):
        """Calculate ROI metrics for a business in a date range."""
        # Use business settings for calculations
        avg_deal_size = business.avg_deal_size or 5000.0
        close_rate = business.close_rate or 0.15
        cost_per_lead = business.cost_per_lead or 50.0
        
        # For demo purposes, generate realistic metrics
        # In production, this would query actual data from leads/deals tables
        
        # Simulate lead activity based on business age and size
        days_in_period = (end_date - start_date).days
        base_leads_per_day = 3  # Conservative estimate
        
        # Simulate some variance
        import random
        random.seed(business.id)  # Consistent results per business
        
        lead_count = int(days_in_period * base_leads_per_day * random.uniform(0.7, 1.3))
        lead_count = max(lead_count, 1)  # At least 1 lead
        
        # Calculate metrics
        total_cost = lead_count * cost_per_lead
        deals_closed = int(lead_count * close_rate)
        total_revenue = deals_closed * avg_deal_size
        net_profit = total_revenue - total_cost
        
        roi_percentage = (net_profit / total_cost * 100) if total_cost > 0 else 0
        conversion_rate = close_rate * 100
        revenue_per_lead = total_revenue / lead_count if lead_count > 0 else 0
        
        # Generate insights (for API use, not stored in model)
        insights = self._generate_insights(
            roi_percentage, conversion_rate, cost_per_lead, 
            revenue_per_lead, lead_count, deals_closed
        )
        
        return {
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'net_profit': net_profit,
            'roi_percentage': roi_percentage,
            'lead_count': lead_count,
            'conversion_rate': conversion_rate,
            'cost_per_lead': cost_per_lead,
            'revenue_per_lead': revenue_per_lead,
            'insights': insights
        }
    
    def _generate_insights(self, roi_percentage, conversion_rate, cost_per_lead, 
                          revenue_per_lead, lead_count, deals_closed):
        """Generate actionable insights based on ROI metrics."""
        insights = []
        
        # ROI insights
        if roi_percentage > 300:
            insights.append({
                'type': 'success',
                'title': 'Excellent ROI Performance',
                'message': f'Your {roi_percentage:.1f}% ROI is outstanding! Consider scaling your current strategies.',
                'action': 'Increase marketing budget to capitalize on high-performing channels.'
            })
        elif roi_percentage > 200:
            insights.append({
                'type': 'success', 
                'title': 'Strong ROI Performance',
                'message': f'Your {roi_percentage:.1f}% ROI is very good. Look for optimization opportunities.',
                'action': 'Focus on converting more leads to maximize revenue.'
            })
        elif roi_percentage > 100:
            insights.append({
                'type': 'info',
                'title': 'Positive ROI',
                'message': f'Your {roi_percentage:.1f}% ROI is positive but has room for improvement.',
                'action': 'Review lead quality and follow-up processes.'
            })
        else:
            insights.append({
                'type': 'warning',
                'title': 'ROI Needs Improvement',
                'message': f'Your {roi_percentage:.1f}% ROI needs attention. Focus on efficiency.',
                'action': 'Reduce cost per lead or improve conversion rates.'
            })
        
        # Conversion rate insights
        if conversion_rate < 10:
            insights.append({
                'type': 'opportunity',
                'title': 'Conversion Rate Opportunity', 
                'message': f'{conversion_rate:.1f}% conversion rate suggests lead quality or follow-up improvements needed.',
                'action': 'Implement better lead qualification and faster response times.'
            })
        elif conversion_rate > 25:
            insights.append({
                'type': 'success',
                'title': 'Excellent Conversion Rate',
                'message': f'{conversion_rate:.1f}% conversion rate is excellent! Your sales process is working well.',
                'action': 'Document your successful process and consider generating more leads.'
            })
        
        # Volume insights
        if lead_count < 30:
            insights.append({
                'type': 'opportunity',
                'title': 'Lead Volume Opportunity',
                'message': f'Only {lead_count} leads this period. Consider increasing marketing efforts.',
                'action': 'Expand your marketing channels or increase budget for lead generation.'
            })
        
        # Cost efficiency
        if cost_per_lead > 100:
            insights.append({
                'type': 'warning',
                'title': 'High Cost Per Lead',
                'message': f'${cost_per_lead:.0f} per lead is high. Look for more efficient channels.',
                'action': 'Test lower-cost marketing channels like content marketing or referrals.'
            })
        
        return insights
    
    def _should_recalculate(self, roi_calc):
        """Determine if ROI should be recalculated."""
        if not roi_calc.calculated_at:
            return True
        
        # Recalculate if more than 24 hours old
        return datetime.utcnow() - roi_calc.calculated_at > timedelta(hours=24)
    
    def calculate_roi_for_all_active_businesses(self):
        """Calculate ROI for all businesses that need updates."""
        try:
            # Get businesses that need ROI calculation
            businesses = Business.query.filter(Business.is_active == True).all()
            
            results = []
            for business in businesses:
                result = self.calculate_roi_for_business(business.id)
                if result:
                    results.append({
                        'business_id': business.id,
                        'business_name': business.name,
                        'roi_percentage': result.roi_percentage,
                        'status': 'success'
                    })
                else:
                    results.append({
                        'business_id': business.id,
                        'business_name': business.name,
                        'status': 'error'
                    })
            
            self.logger.info(f"ROI calculation completed for {len(results)} businesses")
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI for all businesses: {str(e)}")
            return []
    
    def get_roi_trend(self, business_id, days=90):
        """Get ROI trend over time for a business."""
        try:
            calculations = ROIReport.query.filter_by(
                business_id=business_id
            ).filter(
                ROIReport.calculated_at >= datetime.utcnow() - timedelta(days=days)
            ).order_by(ROIReport.calculated_at.asc()).all()
            
            trend_data = []
            for calc in calculations:
                trend_data.append({
                    'date': calc.calculated_at.isoformat() if calc.calculated_at else calc.created_at.isoformat(),
                    'roi_percentage': float(calc.roi_percentage or 0),
                    'total_revenue': float(calc.estimated_revenue or 0),
                    'total_cost': float(calc.total_cost or 0),
                    'net_profit': float(calc.estimated_revenue or 0) - float(calc.total_cost or 0),
                    'lead_count': calc.leads_received or 0
                })
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"Error getting ROI trend for business {business_id}: {str(e)}")
            return []


# Global worker instance
roi_worker = ROICalculationWorker()
