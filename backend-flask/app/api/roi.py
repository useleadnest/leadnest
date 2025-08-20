"""
ROI endpoints for Launch Multiplier.
Handles ROI calculations, insights, and progress tracking.
"""

from flask import request, jsonify
from sqlalchemy import func
from ..db import db
from ..models import Business, ROIReport, ActivityLog
from ..workers.roi_worker import roi_worker
from . import api
from datetime import datetime, timedelta
import json


@api.route('/roi/calculate', methods=['POST'])
def calculate_roi():
    """Trigger ROI calculation for a business."""
    try:
        data = request.get_json() or {}
        business_id = data.get('business_id', 1)  # Temporary default
        
        # Validate business exists
        business = Business.query.filter_by(id=business_id).first()
        if not business:
            return jsonify({'error': 'Business not found'}), 404
        
        # Trigger ROI calculation
        result = roi_worker.calculate_roi_for_business(business_id)
        
        if result:
            return jsonify({
                'success': True,
                'business_id': business_id,
                'roi_percentage': float(result.roi_percentage or 0),
                'total_revenue': float(result.estimated_revenue or 0),
                'total_cost': float(result.total_cost or 0),
                'net_profit': float(result.estimated_revenue or 0) - float(result.total_cost or 0),
                'lead_count': result.leads_received or 0,
                'calculated_at': result.calculated_at.isoformat() if result.calculated_at else result.created_at.isoformat(),
                'deals_closed': result.deals_closed or 0
            })
        else:
            return jsonify({'error': 'ROI calculation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to calculate ROI: {str(e)}'}), 500


@api.route('/roi/status/<int:business_id>', methods=['GET'])
def get_roi_status(business_id):
    """Get current ROI status and metrics for a business."""
    try:
        # Get latest ROI calculation
        roi_calc = ROIReport.query.filter_by(
            business_id=business_id,
            calculation_type='monthly'
        ).order_by(ROIReport.calculated_at.desc()).first()
        
        if not roi_calc:
            return jsonify({
                'business_id': business_id,
                'has_data': False,
                'message': 'No ROI calculations found. Click "Calculate ROI" to generate your first report.'
            })
        
        # Calculate freshness
        now = datetime.utcnow()
        calculated_time = roi_calc.calculated_at or roi_calc.created_at
        calculated_hours_ago = (now - calculated_time).total_seconds() / 3600
        is_fresh = calculated_hours_ago < 24
        
        net_profit = float(roi_calc.estimated_revenue or 0) - float(roi_calc.total_cost or 0)
        
        return jsonify({
            'business_id': business_id,
            'has_data': True,
            'is_fresh': is_fresh,
            'calculated_at': calculated_time.isoformat(),
            'calculated_hours_ago': round(calculated_hours_ago, 1),
            'period_start': roi_calc.period_start.isoformat() if roi_calc.period_start else None,
            'period_end': roi_calc.period_end.isoformat() if roi_calc.period_end else None,
            'metrics': {
                'roi_percentage': float(roi_calc.roi_percentage or 0),
                'total_revenue': float(roi_calc.estimated_revenue or 0),
                'total_cost': float(roi_calc.total_cost or 0),
                'net_profit': net_profit,
                'lead_count': roi_calc.leads_received or 0,
                'deals_closed': roi_calc.deals_closed or 0,
                'conversion_rate': (roi_calc.deals_closed / roi_calc.leads_received * 100) if roi_calc.leads_received else 0,
                'cost_per_lead': float(roi_calc.total_cost or 0) / roi_calc.leads_received if roi_calc.leads_received else 0,
                'revenue_per_lead': float(roi_calc.estimated_revenue or 0) / roi_calc.leads_received if roi_calc.leads_received else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get ROI status: {str(e)}'}), 500


@api.route('/roi/insights/<int:business_id>', methods=['GET'])
def get_roi_insights(business_id):
    """Get ROI insights for a business."""
    try:
        roi_calc = ROIReport.query.filter_by(
            business_id=business_id
        ).order_by(ROIReport.calculated_at.desc()).first()
        
        if not roi_calc:
            return jsonify({
                'business_id': business_id,
                'insights': [],
                'message': 'No insights available. Calculate ROI to generate insights.'
            })
        
        # Generate insights based on current metrics
        insights = []
        roi_percentage = float(roi_calc.roi_percentage or 0)
        lead_count = roi_calc.leads_received or 0
        conversion_rate = (roi_calc.deals_closed / roi_calc.leads_received * 100) if roi_calc.leads_received else 0
        
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
        
        return jsonify({
            'business_id': business_id,
            'insights': insights,
            'total_insights': len(insights),
            'generated_at': roi_calc.calculated_at.isoformat() if roi_calc.calculated_at else roi_calc.created_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get ROI insights: {str(e)}'}), 500


@api.route('/roi/trend/<int:business_id>', methods=['GET'])
def get_roi_trend(business_id):
    """Get ROI trend data for a business."""
    try:
        days = request.args.get('days', 90, type=int)
        days = min(days, 365)  # Limit to 1 year
        
        trend_data = roi_worker.get_roi_trend(business_id, days)
        
        # Calculate trend direction
        trend_direction = 'stable'
        if len(trend_data) >= 2:
            recent_roi = trend_data[-1]['roi_percentage']
            older_roi = trend_data[0]['roi_percentage']
            
            if recent_roi > older_roi * 1.1:
                trend_direction = 'improving'
            elif recent_roi < older_roi * 0.9:
                trend_direction = 'declining'
        
        return jsonify({
            'business_id': business_id,
            'trend_data': trend_data,
            'trend_direction': trend_direction,
            'data_points': len(trend_data),
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get ROI trend: {str(e)}'}), 500


@api.route('/roi/benchmark', methods=['GET'])
def get_roi_benchmark():
    """Get ROI benchmarks and industry standards."""
    try:
        business_id = request.args.get('business_id', type=int)
        
        # Industry benchmarks (these would come from database in production)
        benchmarks = {
            'excellent_roi': 300,  # 300%+
            'good_roi': 200,       # 200-300%
            'average_roi': 150,    # 150-200%
            'poor_roi': 100,       # Below 100%
            'conversion_rates': {
                'excellent': 25,
                'good': 15,
                'average': 10,
                'poor': 5
            },
            'cost_per_lead': {
                'excellent': 25,
                'good': 50,
                'average': 75,
                'expensive': 100
            }
        }
        
        result = {
            'benchmarks': benchmarks,
            'industry': 'General Contracting',  # Would be dynamic in production
        }
        
        # Add comparison if business_id provided
        if business_id:
            roi_calc = ROIReport.query.filter_by(
                business_id=business_id
            ).order_by(ROIReport.calculated_at.desc()).first()
            
            if roi_calc:
                user_roi = float(roi_calc.roi_percentage or 0)
                user_conversion = float(roi_calc.conversion_rate or 0)
                user_cpl = float(roi_calc.cost_per_lead or 0)
                
                # Determine performance levels
                if user_roi >= benchmarks['excellent_roi']:
                    roi_level = 'excellent'
                elif user_roi >= benchmarks['good_roi']:
                    roi_level = 'good'
                elif user_roi >= benchmarks['average_roi']:
                    roi_level = 'average'
                else:
                    roi_level = 'poor'
                
                result['user_performance'] = {
                    'roi_percentage': user_roi,
                    'roi_level': roi_level,
                    'conversion_rate': user_conversion,
                    'cost_per_lead': user_cpl,
                    'vs_benchmark': {
                        'roi_vs_average': user_roi - benchmarks['average_roi'],
                        'better_than_average': user_roi > benchmarks['average_roi']
                    }
                }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get benchmarks: {str(e)}'}), 500


@api.route('/roi/settings/<int:business_id>', methods=['GET', 'POST'])
def roi_settings(business_id):
    """Get or update ROI calculation settings for a business."""
    try:
        business = Business.query.filter_by(id=business_id).first()
        if not business:
            return jsonify({'error': 'Business not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'business_id': business_id,
                'settings': {
                    'avg_deal_size': float(business.avg_deal_size or 5000),
                    'close_rate': float(business.close_rate or 0.15),
                    'cost_per_lead': float(business.cost_per_lead or 50)
                }
            })
        
        # POST - Update settings
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        updated_fields = []
        
        if 'avg_deal_size' in data and data['avg_deal_size'] > 0:
            business.avg_deal_size = data['avg_deal_size']
            updated_fields.append('avg_deal_size')
        
        if 'close_rate' in data and 0 <= data['close_rate'] <= 1:
            business.close_rate = data['close_rate']
            updated_fields.append('close_rate')
        
        if 'cost_per_lead' in data and data['cost_per_lead'] > 0:
            business.cost_per_lead = data['cost_per_lead']
            updated_fields.append('cost_per_lead')
        
        if updated_fields:
            business.updated_at = datetime.utcnow()
            
            # Log activity
            activity = ActivityLog(
                business_id=business_id,
                action='roi_settings_updated',
                description=f'Updated ROI settings: {", ".join(updated_fields)}',
                extra_data={
                    'updated_fields': updated_fields,
                    'new_values': {field: getattr(business, field) for field in updated_fields}
                },
                source='api'
            )
            db.session.add(activity)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'updated_fields': updated_fields,
                'settings': {
                    'avg_deal_size': float(business.avg_deal_size or 5000),
                    'close_rate': float(business.close_rate or 0.15),
                    'cost_per_lead': float(business.cost_per_lead or 50)
                }
            })
        else:
            return jsonify({'error': 'No valid settings provided'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to handle ROI settings: {str(e)}'}), 500


@api.route('/roi/health', methods=['GET'])
def roi_health():
    """Health check for ROI calculation system."""
    try:
        # Get calculation statistics
        total_calculations = ROIReport.query.count()
        recent_calculations = ROIReport.query.filter(
            ROIReport.calculated_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Get average ROI
        avg_roi = db.session.query(func.avg(ROIReport.roi_percentage)).scalar()
        avg_roi = float(avg_roi) if avg_roi else 0
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'stats': {
                'total_calculations': total_calculations,
                'calculations_last_24h': recent_calculations,
                'average_roi_percentage': round(avg_roi, 2)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
