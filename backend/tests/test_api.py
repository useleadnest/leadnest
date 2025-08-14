import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
import csv

def test_create_search_success(client, test_data, db_session):
    """Test successful search creation with lead scraping"""
    from database import User
    from auth import get_password_hash
    from datetime import datetime, timedelta
    
    # Create test user
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        trial_ends_at=datetime.utcnow() + timedelta(days=5),
        subscription_status="trial"
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Mock successful scraping
    with patch('scraper.LeadScraper.scrape_yelp_businesses') as mock_yelp, \
         patch('scraper.LeadScraper.scrape_mock_data') as mock_data, \
         patch('scraper.LeadScraper.enrich_with_ai') as mock_ai:
        
        mock_yelp.return_value = []  # Simulate Yelp failure
        mock_data.return_value = test_data["mock_leads"]
        mock_ai.side_effect = lambda x: {**x, "ai_email_message": "Test email", "ai_sms_message": "Test SMS", "quality_score": 0.8}
        
        response = client.post("/searches",
            json={"location": "Austin, TX", "trade": "roofing"},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Austin, TX"
    assert data["trade"] == "roofing"
    assert data["results_count"] == 2

def test_create_search_expired_trial(client, test_data, db_session):
    """Test search creation with expired trial"""
    from database import User
    from auth import get_password_hash
    from datetime import datetime, timedelta
    
    # Create user with expired trial
    user = User(
        email="expired@example.com",
        hashed_password=get_password_hash("password"),
        trial_ends_at=datetime.utcnow() - timedelta(days=1),
        subscription_status="trial"
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "expired@example.com",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Try to create search
    response = client.post("/searches",
        json={"location": "Austin, TX", "trade": "roofing"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 402
    assert "Trial expired" in response.json()["detail"]

def test_get_searches(client, test_data, db_session):
    """Test retrieving user's search history"""
    from database import User, Search
    from auth import get_password_hash
    from datetime import datetime, timedelta
    
    # Create test user and searches
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        trial_ends_at=datetime.utcnow() + timedelta(days=5),
        subscription_status="trial"
    )
    db_session.add(user)
    db_session.commit()
    
    search1 = Search(user_id=user.id, location="Austin, TX", trade="roofing", results_count=10)
    search2 = Search(user_id=user.id, location="Dallas, TX", trade="solar", results_count=15)
    db_session.add_all([search1, search2])
    db_session.commit()
    
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Get searches
    response = client.get("/searches",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_search_leads(client, test_data, db_session):
    """Test retrieving leads for a specific search"""
    from database import User, Search, Lead
    from auth import get_password_hash
    from datetime import datetime, timedelta
    
    # Create test data
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        trial_ends_at=datetime.utcnow() + timedelta(days=5),
        subscription_status="trial"
    )
    db_session.add(user)
    db_session.commit()
    
    search = Search(user_id=user.id, location="Austin, TX", trade="roofing", results_count=2)
    db_session.add(search)
    db_session.commit()
    
    lead1 = Lead(search_id=search.id, business_name="Test Business 1", quality_score=0.8)
    lead2 = Lead(search_id=search.id, business_name="Test Business 2", quality_score=0.6)
    db_session.add_all([lead1, lead2])
    db_session.commit()
    
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Get leads
    response = client.get(f"/searches/{search.id}/leads",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["business_name"] == "Test Business 1"

def test_export_csv(client, test_data, db_session):
    """Test CSV export functionality"""
    from database import User, Search, Lead
    from auth import get_password_hash
    from datetime import datetime, timedelta
    
    # Create test data
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        trial_ends_at=datetime.utcnow() + timedelta(days=5),
        subscription_status="trial"
    )
    db_session.add(user)
    db_session.commit()
    
    search = Search(user_id=user.id, location="Austin, TX", trade="roofing", results_count=1)
    db_session.add(search)
    db_session.commit()
    
    lead = Lead(
        search_id=search.id,
        business_name="Test Business",
        phone="+15125551234",
        email="test@business.com",
        ai_email_message="Test email message",
        ai_sms_message="Test SMS",
        quality_score=0.85
    )
    db_session.add(lead)
    db_session.commit()
    
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Export CSV
    response = client.get(f"/exports/{search.id}/csv",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # Parse CSV content
    content = response.content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(content))
    rows = list(csv_reader)
    
    assert len(rows) == 2  # Header + 1 data row
    assert rows[0][0] == "Business Name"  # Header
    assert rows[1][0] == "Test Business"  # Data

def test_dashboard_stats(client, test_data, db_session):
    """Test dashboard statistics endpoint"""
    from database import User, Search, Lead, Export
    from auth import get_password_hash
    from datetime import datetime, timedelta
    
    # Create test data
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        trial_ends_at=datetime.utcnow() + timedelta(days=3),
        subscription_status="trial"
    )
    db_session.add(user)
    db_session.commit()
    
    # Add test searches, leads, exports
    search = Search(user_id=user.id, location="Austin, TX", trade="roofing", results_count=2)
    db_session.add(search)
    db_session.commit()
    
    lead1 = Lead(search_id=search.id, business_name="Business 1")
    lead2 = Lead(search_id=search.id, business_name="Business 2")
    db_session.add_all([lead1, lead2])
    
    export = Export(user_id=user.id, search_id=search.id, export_type="csv", leads_count=2)
    db_session.add(export)
    db_session.commit()
    
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Get stats
    response = client.get("/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_searches"] == 1
    assert data["total_leads"] == 2
    assert data["total_exports"] == 1
    assert data["trial_days_left"] == 3
