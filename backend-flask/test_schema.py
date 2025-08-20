#!/usr/bin/env python3
"""
Test script to verify Launch Multiplier database schema and models.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models import (
    db, Business, User, OnboardingProgress, ROIReport, Integration,
    NurtureSequence, NurtureExecution, AIScoring, AIScoringConfig,
    Testimonial, ActivityLog, Lead, Conversation, Message, Booking,
    IdempotencyKey
)
from datetime import datetime, timedelta

def test_schema():
    """Test that all models can be created and have the expected fields."""
    app = create_app()
    
    with app.app_context():
        print("✅ Testing Launch Multiplier database schema...")
        
        # Test User model
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="owner",
            subscription_status="trial"
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ User created: {user}")
        
        # Test Business model with new fields
        business = Business(
            name="Test Business",
            owner_email="owner@test.com",
            niche="testing",
            twilio_account_sid="ACtest123",
            twilio_phone_number="+1234567890",
            avg_deal_size=5000.00,
            close_rate=0.25
        )
        db.session.add(business)
        db.session.commit()
        print(f"✅ Business created: {business}")
        
        # Test OnboardingProgress
        progress = OnboardingProgress(
            user_id=user.id,
            step="connect_twilio",
            data={"twilio_sid": "ACtest123"}
        )
        db.session.add(progress)
        db.session.commit()
        print(f"✅ OnboardingProgress created: {progress}")
        
        # Test ROIReport
        roi_report = ROIReport(
            business_id=business.id,
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            leads_received=100,
            calls_booked=25,
            deals_closed=10,
            estimated_revenue=50000.00,
            roi_percentage=400.0
        )
        db.session.add(roi_report)
        db.session.commit()
        print(f"✅ ROIReport created: {roi_report}")
        
        # Test Integration
        integration = Integration(
            business_id=business.id,
            type="twilio",
            name="Primary SMS",
            settings={"account_sid": "ACtest123"},
            enabled=True
        )
        db.session.add(integration)
        db.session.commit()
        print(f"✅ Integration created: {integration}")
        
        # Test Lead model with new fields
        lead = Lead(
            business_id=business.id,
            phone="+1234567890",
            email="lead@example.com",
            first_name="John",
            last_name="Doe",
            company="ACME Corp",
            score=85.5,
            priority="high"
        )
        db.session.add(lead)
        db.session.commit()
        print(f"✅ Lead created: {lead}")
        
        # Test AIScoring
        ai_score = AIScoring(
            business_id=business.id,
            lead_id=lead.id,
            score=85.5,
            factors={"recency": 0.9, "engagement": 0.8},
            priority="high",
            recommended_action="call_immediately"
        )
        db.session.add(ai_score)
        db.session.commit()
        print(f"✅ AIScoring created: {ai_score}")
        
        # Test AIScoringConfig
        ai_config = AIScoringConfig(
            business_id=business.id,
            recency_weight=0.3,
            source_weight=0.2,
            high_value_sources=["google_ads", "referral"]
        )
        db.session.add(ai_config)
        db.session.commit()
        print(f"✅ AIScoringConfig created: {ai_config}")
        
        # Test Testimonial
        testimonial = Testimonial(
            business_id=business.id,
            lead_id=lead.id,
            content="Great service! Highly recommend.",
            author_name="John Doe",
            star_rating=5,
            public=True
        )
        db.session.add(testimonial)
        db.session.commit()
        print(f"✅ Testimonial created: {testimonial}")
        
        # Test ActivityLog
        activity = ActivityLog(
            business_id=business.id,
            lead_id=lead.id,
            user_id=user.id,
            action="lead_created",
            description="New lead imported from website form",
            source="api"
        )
        db.session.add(activity)
        db.session.commit()
        print(f"✅ ActivityLog created: {activity}")
        
        print("\n🎉 ALL TESTS PASSED! Launch Multiplier database schema is ready!")
        print(f"📊 Total records created: {len(db.session.query(User).all())} users, {len(db.session.query(Business).all())} businesses")
        
        return True

if __name__ == '__main__':
    try:
        test_schema()
        print("\n✅ Schema test completed successfully!")
    except Exception as e:
        print(f"\n❌ Schema test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
