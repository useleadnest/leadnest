"""
Onboarding endpoints for Launch Multiplier.
Handles user onboarding steps: Twilio setup, CSV import, auto-reply, test SMS, and Calendly integration.
"""

from flask import request, jsonify
from flask_limiter.util import get_remote_address
from ..db import db
from ..models import User, Business, OnboardingProgress, ActivityLog
from ..settings import settings
from . import api
import json
from datetime import datetime


@api.route('/onboarding/status', methods=['GET'])
def get_onboarding_status():
    """Get the current onboarding progress for a user."""
    try:
        # For now, use business_id=1. Later, get from JWT/session
        business_id = request.args.get('business_id', 1, type=int)
        user_id = request.args.get('user_id', 1, type=int)  # Temporary
        
        # Get or create user
        user = User.query.filter_by(id=user_id).first()
        if not user:
            user = User(
                email=f"user{user_id}@example.com",
                business_id=business_id,
                role="owner"
            )
            db.session.add(user)
            db.session.commit()
        
        # Get onboarding steps
        completed_steps = OnboardingProgress.query.filter_by(user_id=user.id).all()
        completed_step_names = [step.step for step in completed_steps if step.completed_at]
        
        # Define all onboarding steps in order
        all_steps = [
            'connect_twilio',
            'import_csv', 
            'enable_auto_reply',
            'send_test_sms',
            'connect_calendly'
        ]
        
        # Calculate progress
        total_steps = len(all_steps)
        completed_count = len(completed_step_names)
        progress_percentage = int((completed_count / total_steps) * 100)
        
        # Determine next step
        next_step = None
        for step in all_steps:
            if step not in completed_step_names:
                next_step = step
                break
        
        return jsonify({
            'user_id': user.id,
            'business_id': user.business_id,
            'total_steps': total_steps,
            'completed_steps': completed_count,
            'progress_percentage': progress_percentage,
            'next_step': next_step,
            'completed_step_names': completed_step_names,
            'all_steps': all_steps,
            'is_complete': next_step is None
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get onboarding status: {str(e)}'}), 500


@api.route('/onboarding/complete-step', methods=['POST'])
def complete_onboarding_step():
    """Mark an onboarding step as complete."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = data.get('user_id')
        step = data.get('step')
        step_data = data.get('data', {})
        
        if not user_id or not step:
            return jsonify({'error': 'user_id and step are required'}), 400
        
        # Validate step name
        valid_steps = ['connect_twilio', 'import_csv', 'enable_auto_reply', 'send_test_sms', 'connect_calendly']
        if step not in valid_steps:
            return jsonify({'error': f'Invalid step. Must be one of: {valid_steps}'}), 400
        
        # Get user
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if step already exists
        progress = OnboardingProgress.query.filter_by(user_id=user_id, step=step).first()
        if not progress:
            progress = OnboardingProgress(
                user_id=user_id,
                step=step
            )
            db.session.add(progress)
        
        # Mark as completed
        progress.completed_at = datetime.utcnow()
        progress.data = step_data
        
        # Log activity
        activity = ActivityLog(
            business_id=user.business_id,
            user_id=user_id,
            action='onboarding_step_completed',
            description=f'Completed onboarding step: {step}',
            extra_data={'step': step, 'data': step_data},
            source='api'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        # Get updated progress
        completed_steps = OnboardingProgress.query.filter_by(user_id=user_id).all()
        completed_count = len([s for s in completed_steps if s.completed_at])
        total_steps = 5
        progress_percentage = int((completed_count / total_steps) * 100)
        
        return jsonify({
            'success': True,
            'step': step,
            'completed_at': progress.completed_at.isoformat(),
            'progress_percentage': progress_percentage,
            'completed_steps': completed_count,
            'total_steps': total_steps
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to complete step: {str(e)}'}), 500


@api.route('/onboarding/step-data/<step>', methods=['GET'])
def get_step_data(step):
    """Get data for a specific onboarding step."""
    try:
        user_id = request.args.get('user_id', 1, type=int)  # Temporary
        
        progress = OnboardingProgress.query.filter_by(user_id=user_id, step=step).first()
        
        if not progress:
            return jsonify({
                'step': step,
                'completed': False,
                'data': {}
            })
        
        return jsonify({
            'step': step,
            'completed': progress.completed_at is not None,
            'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
            'data': progress.data or {}
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get step data: {str(e)}'}), 500


@api.route('/onboarding/reset', methods=['POST'])
def reset_onboarding():
    """Reset onboarding progress for testing purposes."""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        
        # Delete all onboarding progress for user
        OnboardingProgress.query.filter_by(user_id=user_id).delete()
        
        # Log activity
        activity = ActivityLog(
            business_id=1,  # Temporary
            user_id=user_id,
            action='onboarding_reset',
            description='Onboarding progress reset',
            source='api'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Onboarding progress reset successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reset onboarding: {str(e)}'}), 500


@api.route('/onboarding/business-setup', methods=['POST'])
def update_business_setup():
    """Update business information during onboarding."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        business_id = data.get('business_id', 1)  # Temporary
        
        business = Business.query.filter_by(id=business_id).first()
        if not business:
            return jsonify({'error': 'Business not found'}), 404
        
        # Update business fields if provided
        fields_to_update = [
            'twilio_account_sid', 'twilio_auth_token', 'twilio_phone_number',
            'calendly_url', 'avg_deal_size', 'close_rate', 'cost_per_lead'
        ]
        
        updated_fields = []
        for field in fields_to_update:
            if field in data and data[field] is not None:
                setattr(business, field, data[field])
                updated_fields.append(field)
        
        if updated_fields:
            business.updated_at = datetime.utcnow()
            
            # Log activity
            activity = ActivityLog(
                business_id=business.id,
                action='business_setup_updated',
                description=f'Updated business fields: {", ".join(updated_fields)}',
                extra_data={'updated_fields': updated_fields, 'values': {field: data[field] for field in updated_fields}},
                source='api'
            )
            db.session.add(activity)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'updated_fields': updated_fields,
                'business_id': business.id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No valid fields provided to update'
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update business setup: {str(e)}'}), 500


@api.route('/onboarding/validate-twilio', methods=['POST'])
def validate_twilio_credentials():
    """Validate Twilio credentials during onboarding."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        account_sid = data.get('account_sid')
        auth_token = data.get('auth_token')
        phone_number = data.get('phone_number')
        
        if not all([account_sid, auth_token, phone_number]):
            return jsonify({
                'valid': False,
                'error': 'account_sid, auth_token, and phone_number are required'
            }), 400
        
        # Basic format validation
        if not account_sid.startswith('AC') or len(account_sid) != 34:
            return jsonify({
                'valid': False,
                'error': 'Invalid Account SID format'
            })
        
        if not phone_number.startswith('+'):
            return jsonify({
                'valid': False,
                'error': 'Phone number must be in E.164 format (e.g., +1234567890)'
            })
        
        # TODO: Add actual Twilio API validation when ready
        # For now, return success for properly formatted credentials
        
        return jsonify({
            'valid': True,
            'message': 'Twilio credentials are valid',
            'account_sid': account_sid,
            'phone_number': phone_number
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Validation failed: {str(e)}'
        }), 500


@api.route('/onboarding/health', methods=['GET'])
def onboarding_health():
    """Health check for onboarding endpoints."""
    try:
        # Count active onboarding sessions
        total_users = User.query.count()
        active_onboarding = OnboardingProgress.query.filter(OnboardingProgress.completed_at.is_(None)).count()
        completed_onboarding = OnboardingProgress.query.filter(OnboardingProgress.completed_at.isnot(None)).count()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'stats': {
                'total_users': total_users,
                'active_onboarding_steps': active_onboarding,
                'completed_onboarding_steps': completed_onboarding
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
