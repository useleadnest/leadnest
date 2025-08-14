import requests
import openai
from typing import List, Dict, Optional
import time
import random
import logging

from config import config

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = config.openai_api_key

class LeadScraper:
    def __init__(self):
        self.yelp_headers = {
            'Authorization': f'Bearer {config.yelp_api_key}',
        }
    
    def scrape_yelp_businesses(self, location: str, trade: str, limit: int = 50) -> List[Dict]:
        """Scrape businesses from Yelp API"""
        try:
            # Map trade to Yelp categories
            category_mapping = {
                'roofing': 'roofing',
                'solar': 'solar_installation',
                'pool': 'poolservices',
                'painting': 'painters',
                'plumbing': 'plumbing',
                'electrical': 'electricians',
                'hvac': 'hvac',
                'landscaping': 'landscaping',
                'construction': 'contractors',
                'remodeling': 'homeandgarden'
            }
            
            category = category_mapping.get(trade.lower(), 'contractors')
            
            url = 'https://api.yelp.com/v3/businesses/search'
            params = {
                'location': location,
                'categories': category,
                'limit': min(limit, 50),  # Yelp API limit
                'sort_by': 'rating'
            }
            
            response = requests.get(url, headers=self.yelp_headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                businesses = []
                
                for business in data.get('businesses', []):
                    # Extract business info
                    business_data = {
                        'business_name': business.get('name', ''),
                        'phone': business.get('phone', ''),
                        'website': business.get('url', ''),
                        'address': self._format_address(business.get('location', {})),
                        'category': ', '.join([cat['title'] for cat in business.get('categories', [])]),
                        'rating': business.get('rating', 0),
                        'review_count': business.get('review_count', 0),
                        'email': None  # Yelp doesn't provide emails
                    }
                    businesses.append(business_data)
                
                return businesses
            else:
                print(f"Yelp API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error scraping Yelp: {str(e)}")
            return []
    
    def scrape_mock_data(self, location: str, trade: str, limit: int = 50) -> List[Dict]:
        """Generate mock data for demo purposes when APIs aren't available"""
        mock_businesses = []
        
        business_names = [
            f"{trade.title()} Pro",
            f"Elite {trade.title()}",
            f"{location} {trade.title()} Co",
            f"Best {trade.title()} Services",
            f"Quality {trade.title()} Solutions",
            f"Premier {trade.title()} Group",
            f"Local {trade.title()} Experts",
            f"Reliable {trade.title()} Inc",
            f"Top-Tier {trade.title()}",
            f"{trade.title()} Masters LLC"
        ]
        
        for i in range(min(limit, len(business_names))):
            business_data = {
                'business_name': business_names[i],
                'phone': f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                'website': f"https://www.{business_names[i].lower().replace(' ', '').replace(',', '')}.com",
                'address': f"{random.randint(100, 9999)} Main St, {location}",
                'category': trade.title(),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'review_count': random.randint(5, 200),
                'email': f"info@{business_names[i].lower().replace(' ', '').replace(',', '')}.com"
            }
            mock_businesses.append(business_data)
        
        return mock_businesses
    
    def _format_address(self, location_data: Dict) -> str:
        """Format Yelp location data into address string"""
        if not location_data:
            return ""
        
        address_parts = []
        if location_data.get('address1'):
            address_parts.append(location_data['address1'])
        if location_data.get('city'):
            address_parts.append(location_data['city'])
        if location_data.get('state'):
            address_parts.append(location_data['state'])
        if location_data.get('zip_code'):
            address_parts.append(location_data['zip_code'])
        
        return ', '.join(address_parts)
    
    def enrich_with_ai(self, lead_data: Dict, contractor_name: str = "a local contractor") -> Dict:
        """Generate AI-powered follow-up messages for leads"""
        try:
            business_name = lead_data.get('business_name', 'Business')
            category = lead_data.get('category', 'business')
            
            # Email message prompt
            email_prompt = f"""
            Write a friendly, casual email from {contractor_name} to {business_name} ({category}). 
            The goal is to offer to send them 5-10 exclusive leads per month. 
            Keep it short, personable, and not salesy. Mention you found them online.
            Don't use formal business language - be conversational.
            """
            
            # SMS message prompt
            sms_prompt = f"""
            Write a short, friendly text message from {contractor_name} to {business_name}.
            Offer to send them leads. Keep it under 160 characters and casual.
            Example tone: "Hey John, saw your business online - would love to chat about sending you 5-10 extra leads/month. Interested?"
            """
            
            # Generate email message
            email_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": email_prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            # Generate SMS message
            sms_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": sms_prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            lead_data['ai_email_message'] = email_response.choices[0].message.content.strip()
            lead_data['ai_sms_message'] = sms_response.choices[0].message.content.strip()
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(lead_data)
            lead_data['quality_score'] = quality_score
            
            return lead_data
            
        except Exception as e:
            print(f"Error enriching with AI: {str(e)}")
            # Fallback messages
            lead_data['ai_email_message'] = f"Hi there! I found {business_name} online and would love to chat about sending you some exclusive leads. Would you be interested in 5-10 quality leads per month? Let me know!"
            lead_data['ai_sms_message'] = f"Hi! Saw {business_name} online - interested in 5-10 extra leads/month? Quick chat?"
            lead_data['quality_score'] = 0.5
            return lead_data
    
    def _calculate_quality_score(self, lead_data: Dict) -> float:
        """Calculate a quality score for the lead based on available data"""
        score = 0.0
        
        # Base score
        score += 0.2
        
        # Has phone
        if lead_data.get('phone'):
            score += 0.2
        
        # Has email
        if lead_data.get('email'):
            score += 0.2
        
        # Has website
        if lead_data.get('website'):
            score += 0.2
        
        # Good rating
        rating = lead_data.get('rating', 0)
        if rating >= 4.0:
            score += 0.1
        elif rating >= 3.5:
            score += 0.05
        
        # Has reviews
        review_count = lead_data.get('review_count', 0)
        if review_count >= 20:
            score += 0.1
        elif review_count >= 5:
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
