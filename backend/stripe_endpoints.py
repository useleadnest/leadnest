# Add these imports to main_secure.py
from subscription import SubscriptionManager, process_webhook_event
import json

# Add these endpoints to main_secure.py after the existing endpoints

@app.post("/stripe/create-checkout")
@rate_limit_general()
async def create_stripe_checkout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for subscription"""
    try:
        # Create Stripe customer if not exists
        if not current_user.stripe_customer_id:
            customer_id = SubscriptionManager.create_stripe_customer(
                current_user.email, 
                current_user.id
            )
            current_user.stripe_customer_id = customer_id
            db.commit()
        else:
            customer_id = current_user.stripe_customer_id
        
        # Create checkout session
        frontend_url = os.getenv("FRONTEND_URL", "https://useleadnest.com")
        success_url = f"{frontend_url}/dashboard?payment=success"
        cancel_url = f"{frontend_url}/dashboard?payment=cancelled"
        
        session_data = SubscriptionManager.create_checkout_session(
            customer_id, success_url, cancel_url
        )
        
        return session_data
        
    except Exception as e:
        logger.error(f"Checkout creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@app.post("/stripe/cancel-subscription")
@rate_limit_general()
async def cancel_stripe_subscription(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel user's Stripe subscription"""
    if current_user.subscription_status != "active":
        raise HTTPException(status_code=400, detail="No active subscription to cancel")
    
    try:
        # Get user's subscription from Stripe
        if current_user.stripe_customer_id:
            subscriptions = stripe.Subscription.list(
                customer=current_user.stripe_customer_id,
                status='active'
            )
            
            if subscriptions.data:
                subscription_id = subscriptions.data[0].id
                success = SubscriptionManager.cancel_subscription(subscription_id)
                
                if success:
                    current_user.subscription_status = "cancelled"
                    db.commit()
                    return {"message": "Subscription cancelled successfully"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to cancel subscription")
            else:
                raise HTTPException(status_code=404, detail="No active subscription found")
        else:
            raise HTTPException(status_code=404, detail="No Stripe customer found")
            
    except Exception as e:
        logger.error(f"Subscription cancellation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    # Verify webhook signature
    if not SubscriptionManager.verify_webhook_signature(payload, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    try:
        event = json.loads(payload)
        event_type = event['type']
        event_data = event['data']
        
        # Process the webhook event
        success = process_webhook_event(event_type, event_data, db)
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to process webhook")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@app.get("/stripe/subscription-status")
@rate_limit_general() 
async def get_subscription_status(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's subscription status"""
    trial_days_left = None
    if current_user.subscription_status == "trial" and current_user.trial_ends_at:
        days_left = (current_user.trial_ends_at - datetime.utcnow()).days
        trial_days_left = max(0, days_left)
    
    return {
        "subscription_status": current_user.subscription_status,
        "trial_ends_at": current_user.trial_ends_at,
        "trial_days_left": trial_days_left,
        "stripe_customer_id": current_user.stripe_customer_id is not None
    }
