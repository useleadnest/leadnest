import stripe
from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from typing import Dict, Any
import hmac
import hashlib

from config import config
from database import get_db, User

# Configure Stripe
stripe.api_key = config.stripe_secret_key

logger = logging.getLogger(__name__)

class SubscriptionManager:
    """Handle Stripe subscription logic and webhooks"""
    
    @staticmethod
    def create_stripe_customer(email: str, user_id: int) -> str:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={"user_id": str(user_id)}
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create customer")
    
    @staticmethod
    def create_checkout_session(customer_id: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        """Create a Stripe checkout session for subscription"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'LeadNest Pro',
                            'description': 'Unlimited lead generation and AI-powered follow-up messages'
                        },
                        'unit_amount': 4900,  # $49.00
                        'recurring': {
                            'interval': 'month'
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                trial_period_days=7,
                metadata={
                    "customer_id": customer_id
                }
            )
            return {"checkout_url": session.url, "session_id": session.id}
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create checkout session")
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """Cancel a Stripe subscription"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            return False
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            stripe.Webhook.construct_event(
                payload, signature, config.stripe_webhook_secret
            )
            return True
        except ValueError:
            logger.error("Invalid payload in webhook")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in webhook")
            return False

class WebhookHandler:
    """Handle Stripe webhook events"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def handle_checkout_completed(self, event_data: Dict[str, Any]) -> bool:
        """Handle successful checkout completion"""
        try:
            session = event_data['object']
            customer_id = session.get('customer')
            subscription_id = session.get('subscription')
            
            if not customer_id:
                logger.error("No customer ID in checkout session")
                return False
            
            # Find user by Stripe customer ID
            user = self.db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.error(f"User not found for customer ID: {customer_id}")
                return False
            
            # Update user subscription status
            user.subscription_status = "active"
            user.stripe_customer_id = customer_id
            
            # Extend trial if still active, otherwise set subscription start
            if user.trial_ends_at and user.trial_ends_at > datetime.utcnow():
                # Trial still active, subscription starts after trial
                subscription_start = user.trial_ends_at
            else:
                # Trial expired or no trial, start immediately
                subscription_start = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"User {user.email} subscription activated")
            return True
            
        except Exception as e:
            logger.error(f"Error handling checkout completion: {str(e)}")
            self.db.rollback()
            return False
    
    def handle_subscription_created(self, event_data: Dict[str, Any]) -> bool:
        """Handle new subscription creation"""
        try:
            subscription = event_data['object']
            customer_id = subscription.get('customer')
            subscription_id = subscription.get('id')
            
            user = self.db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.error(f"User not found for customer ID: {customer_id}")
                return False
            
            user.subscription_status = "active"
            self.db.commit()
            
            logger.info(f"Subscription created for user {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling subscription creation: {str(e)}")
            self.db.rollback()
            return False
    
    def handle_subscription_updated(self, event_data: Dict[str, Any]) -> bool:
        """Handle subscription updates"""
        try:
            subscription = event_data['object']
            customer_id = subscription.get('customer')
            status = subscription.get('status')
            
            user = self.db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.error(f"User not found for customer ID: {customer_id}")
                return False
            
            # Map Stripe status to our status
            status_mapping = {
                'active': 'active',
                'past_due': 'past_due',
                'canceled': 'cancelled',
                'unpaid': 'past_due',
                'incomplete': 'trial',
                'incomplete_expired': 'cancelled',
                'trialing': 'trial'
            }
            
            user.subscription_status = status_mapping.get(status, 'cancelled')
            self.db.commit()
            
            logger.info(f"Subscription updated for user {user.email}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling subscription update: {str(e)}")
            self.db.rollback()
            return False
    
    def handle_subscription_deleted(self, event_data: Dict[str, Any]) -> bool:
        """Handle subscription cancellation"""
        try:
            subscription = event_data['object']
            customer_id = subscription.get('customer')
            
            user = self.db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.error(f"User not found for customer ID: {customer_id}")
                return False
            
            user.subscription_status = "cancelled"
            self.db.commit()
            
            logger.info(f"Subscription cancelled for user {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling subscription deletion: {str(e)}")
            self.db.rollback()
            return False
    
    def handle_invoice_payment_failed(self, event_data: Dict[str, Any]) -> bool:
        """Handle failed invoice payments"""
        try:
            invoice = event_data['object']
            customer_id = invoice.get('customer')
            attempt_count = invoice.get('attempt_count', 0)
            
            user = self.db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.error(f"User not found for customer ID: {customer_id}")
                return False
            
            # After 3 failed attempts, suspend access
            if attempt_count >= 3:
                user.subscription_status = "cancelled"
                user.is_active = False
                logger.info(f"User {user.email} access suspended after {attempt_count} failed payments")
            else:
                user.subscription_status = "past_due"
                logger.info(f"Payment failed for user {user.email}, attempt {attempt_count}")
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment failure: {str(e)}")
            self.db.rollback()
            return False
    
    def handle_invoice_payment_succeeded(self, event_data: Dict[str, Any]) -> bool:
        """Handle successful invoice payments"""
        try:
            invoice = event_data['object']
            customer_id = invoice.get('customer')
            
            user = self.db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.error(f"User not found for customer ID: {customer_id}")
                return False
            
            # Reactivate user if they were suspended
            user.subscription_status = "active"
            user.is_active = True
            self.db.commit()
            
            logger.info(f"Payment succeeded for user {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment success: {str(e)}")
            self.db.rollback()
            return False

def process_webhook_event(event_type: str, event_data: Dict[str, Any], db: Session) -> bool:
    """Process different types of Stripe webhook events"""
    handler = WebhookHandler(db)
    
    event_handlers = {
        'checkout.session.completed': handler.handle_checkout_completed,
        'customer.subscription.created': handler.handle_subscription_created,
        'customer.subscription.updated': handler.handle_subscription_updated,
        'customer.subscription.deleted': handler.handle_subscription_deleted,
        'invoice.payment_failed': handler.handle_invoice_payment_failed,
        'invoice.payment_succeeded': handler.handle_invoice_payment_succeeded,
    }
    
    handler_func = event_handlers.get(event_type)
    if handler_func:
        return handler_func(event_data)
    else:
        logger.info(f"Unhandled webhook event type: {event_type}")
        return True  # Return True for unhandled events to acknowledge receipt
