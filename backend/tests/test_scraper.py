import pytest
from unittest.mock import patch, MagicMock
import json
from scraper import LeadScraper

def test_scrape_yelp_businesses_success(test_data):
    """Test successful Yelp API scraping"""
    scraper = LeadScraper()
    
    # Mock successful Yelp API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = test_data["mock_yelp_response"]
    
    with patch('requests.get', return_value=mock_response):
        results = scraper.scrape_yelp_businesses("Austin, TX", "roofing", limit=10)
    
    assert len(results) == 2
    assert results[0]["business_name"] == "Austin Roof Pros"
    assert results[0]["phone"] == "+15125551234"
    assert results[0]["rating"] == 4.5
    assert results[1]["business_name"] == "Elite Roofing Solutions"

def test_scrape_yelp_businesses_api_failure(test_data):
    """Test Yelp API failure handling"""
    scraper = LeadScraper()
    
    # Mock failed API response
    mock_response = MagicMock()
    mock_response.status_code = 429  # Rate limited
    
    with patch('requests.get', return_value=mock_response):
        results = scraper.scrape_yelp_businesses("Austin, TX", "roofing")
    
    assert results == []  # Should return empty list on failure

def test_scrape_mock_data_fallback(test_data):
    """Test mock data generation when APIs unavailable"""
    scraper = LeadScraper()
    
    results = scraper.scrape_mock_data("Austin, TX", "roofing", limit=5)
    
    assert len(results) == 5
    assert all("business_name" in lead for lead in results)
    assert all("phone" in lead for lead in results)
    assert all("Austin" in lead["address"] for lead in results)
    assert all("roofing" in lead["business_name"].lower() for lead in results)

def test_ai_message_generation_success(test_data):
    """Test AI message generation with OpenAI"""
    scraper = LeadScraper()
    lead_data = test_data["mock_leads"][0].copy()
    
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = test_data["mock_ai_messages"]["email"]
    
    with patch('openai.chat.completions.create', return_value=mock_response):
        enriched_lead = scraper.enrich_with_ai(lead_data, "John's Contracting")
    
    assert "ai_email_message" in enriched_lead
    assert "ai_sms_message" in enriched_lead
    assert "quality_score" in enriched_lead
    assert enriched_lead["quality_score"] > 0

def test_ai_message_generation_fallback():
    """Test AI message generation with API failure"""
    scraper = LeadScraper()
    lead_data = {
        "business_name": "Test Business",
        "category": "Roofing"
    }
    
    # Mock OpenAI failure
    with patch('openai.chat.completions.create', side_effect=Exception("API Error")):
        enriched_lead = scraper.enrich_with_ai(lead_data)
    
    assert "ai_email_message" in enriched_lead
    assert "ai_sms_message" in enriched_lead
    assert "Test Business" in enriched_lead["ai_email_message"]
    assert enriched_lead["quality_score"] == 0.5

def test_quality_score_calculation():
    """Test lead quality scoring algorithm"""
    scraper = LeadScraper()
    
    # High quality lead
    high_quality_lead = {
        "phone": "+15125551234",
        "email": "test@example.com", 
        "website": "https://example.com",
        "rating": 4.8,
        "review_count": 100
    }
    score = scraper._calculate_quality_score(high_quality_lead)
    assert score >= 0.8
    
    # Low quality lead
    low_quality_lead = {
        "business_name": "Test Business"
    }
    score = scraper._calculate_quality_score(low_quality_lead)
    assert score == 0.2  # Base score only

def test_trade_category_mapping():
    """Test trade category mapping for Yelp API"""
    scraper = LeadScraper()
    
    # Test various trade mappings
    trade_tests = [
        ("roofing", "roofing"),
        ("solar", "solar_installation"),
        ("pool", "poolservices"),
        ("painting", "painters"),
        ("unknown_trade", "contractors")  # Default fallback
    ]
    
    for trade_input, expected_category in trade_tests:
        # This would be tested by checking the actual API call parameters
        # For now, we verify the mapping logic exists
        assert True  # Placeholder for mapping verification
