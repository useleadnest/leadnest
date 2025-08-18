"""
Unit tests for competitive advantage features
Tests AI Lead Scoring, ROI Calculator, Nurture Sequences, and Shared Inbox
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from ai_lead_scorer import AILeadScorer
from roi_calculator import ROICalculator, CompetitiveAnalyzer
from nurture_sequences import SequenceManager, SequenceType
from shared_inbox import SharedInboxManager, CallLogManager, MessageType, CallDisposition


class TestAILeadScorer(unittest.TestCase):
    """Test AI Lead Scoring functionality"""
    
    def setUp(self):
        self.scorer = AILeadScorer()
    
    def test_score_lead_basic(self):
        """Test basic lead scoring"""
        lead_data = {
            'id': '1',
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+15551234567',
            'source': 'website',
            'industry': 'medspas'
        }
        
        result = self.scorer.score_lead(lead_data)
        
        self.assertIn('overall_score', result)
        self.assertIn('grade', result)
        self.assertIn('confidence', result)
        self.assertIn('factors', result)
        
        self.assertIsInstance(result['overall_score'], (int, float))
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)
        self.assertIn(result['grade'], ['A+', 'A', 'B', 'C', 'D'])
    
    def test_bulk_scoring(self):
        """Test bulk lead scoring"""
        leads = [
            {'id': '1', 'name': 'John Doe', 'email': 'john@test.com', 'phone': '+1234567890', 'source': 'web', 'industry': 'medspas'},
            {'id': '2', 'name': 'Jane Smith', 'email': 'jane@test.com', 'phone': '+0987654321', 'source': 'referral', 'industry': 'medspas'}
        ]
        
        results = self.scorer.bulk_score_leads(leads)
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn('lead_id', result)
            self.assertIn('score', result)
            self.assertIn('grade', result)
    
    def test_lead_insights(self):
        """Test lead insights generation"""
        lead_data = {
            'id': '1',
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+15551234567',
            'source': 'google_ads',
            'industry': 'medspas'
        }
        
        score_result = self.scorer.score_lead(lead_data)
        insights = self.scorer.get_lead_insights(score_result, lead_data)
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        for insight in insights:
            self.assertIsInstance(insight, str)
            self.assertGreater(len(insight), 0)
    
    def test_invalid_lead_data(self):
        """Test handling of invalid lead data"""
        invalid_lead = {}
        
        result = self.scorer.score_lead(invalid_lead)
        
        # Should still return a valid score structure
        self.assertIn('overall_score', result)
        self.assertIsInstance(result['overall_score'], (int, float))


class TestROICalculator(unittest.TestCase):
    """Test ROI calculation functionality"""
    
    def setUp(self):
        self.calculator = ROICalculator()
        self.analyzer = CompetitiveAnalyzer()
    
    def test_roi_metrics_calculation(self):
        """Test ROI metrics calculation"""
        metrics = self.calculator.calculate_roi_metrics('test_user', 30)
        
        # Check all required metrics are present
        required_fields = [
            'leads_uploaded', 'calls_made', 'emails_sent', 'appointments_booked',
            'deals_closed', 'revenue_generated', 'cost_per_lead', 'conversion_rate',
            'roi_percentage', 'projected_monthly_revenue'
        ]
        
        for field in required_fields:
            self.assertIn(field, metrics.__dict__)
            self.assertIsInstance(getattr(metrics, field), (int, float))
    
    def test_roi_insights(self):
        """Test ROI insights generation"""
        metrics = self.calculator.calculate_roi_metrics('test_user', 30)
        insights = self.calculator.get_roi_insights(metrics, 'medspas')
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        for insight in insights:
            self.assertIsInstance(insight, str)
            self.assertGreater(len(insight), 0)
    
    def test_growth_recommendations(self):
        """Test growth recommendations"""
        metrics = self.calculator.calculate_roi_metrics('test_user', 30)
        recommendations = self.calculator.get_growth_recommendations(metrics, 'contractors')
        
        self.assertIsInstance(recommendations, list)
        
        for rec in recommendations:
            self.assertIn('category', rec)
            self.assertIn('title', rec)
            self.assertIn('description', rec)
            self.assertIn('impact', rec)
            self.assertIn('effort', rec)
    
    def test_competitive_analysis(self):
        """Test competitive position analysis"""
        metrics = self.calculator.calculate_roi_metrics('test_user', 30)
        position = self.analyzer.get_competitive_position(metrics, 'law_firms')
        
        self.assertIn('roi_percentile', position)
        self.assertIn('conversion_percentile', position)
        self.assertIn('overall_grade', position)
        self.assertIn('beat_competitors', position)
        self.assertIn('improvement_areas', position)
        
        self.assertIsInstance(position['roi_percentile'], (int, float))
        self.assertIsInstance(position['beat_competitors'], bool)
        self.assertIsInstance(position['improvement_areas'], list)


class TestNurtureSequences(unittest.TestCase):
    """Test nurture sequence functionality"""
    
    def setUp(self):
        self.manager = SequenceManager()
    
    def test_sequence_templates(self):
        """Test sequence template loading"""
        sequences = self.manager.engine.sequences
        
        self.assertGreater(len(sequences), 0)
        
        # Check medspa sequence exists
        self.assertIn('medspa_initial', sequences)
        medspa_seq = sequences['medspa_initial']
        
        self.assertEqual(medspa_seq.industry, 'medspas')
        self.assertEqual(medspa_seq.sequence_type, SequenceType.INITIAL_OUTREACH)
        self.assertGreater(len(medspa_seq.steps), 0)
    
    def test_sequence_personalization(self):
        """Test message personalization"""
        template = "Hi {first_name}! Thanks for your interest in {service_type}."
        lead_data = {'first_name': 'John', 'service_type': 'consultation'}
        business_data = {'business_name': 'Test Spa'}
        
        personalized = self.manager.engine.personalize_message(template, lead_data, business_data)
        
        self.assertIn('John', personalized)
        self.assertIn('consultation', personalized)
        self.assertNotIn('{first_name}', personalized)
    
    def test_sequence_scheduling(self):
        """Test sequence scheduling"""
        lead_data = {
            'id': '1',
            'name': 'John Doe',
            'email': 'john@test.com',
            'phone': '+1234567890',
            'industry': 'medspas'
        }
        
        business_data = {
            'business_name': 'Test Business',
            'agent_name': 'Test Agent'
        }
        
        result = self.manager.start_sequence_for_lead(lead_data, business_data)
        
        self.assertIn('sequence_id', result)
        self.assertIn('total_steps', result)
        self.assertIn('scheduled_steps', result)
        self.assertGreater(result['total_steps'], 0)
    
    def test_sequence_analytics(self):
        """Test sequence analytics"""
        analytics = self.manager.engine.get_sequence_analytics('medspa_initial')
        
        required_fields = [
            'sequence_id', 'total_leads', 'completed_sequences', 'responses',
            'appointments_booked', 'response_rate', 'appointment_rate'
        ]
        
        for field in required_fields:
            self.assertIn(field, analytics)


class TestSharedInbox(unittest.TestCase):
    """Test shared inbox functionality"""
    
    def setUp(self):
        self.inbox_manager = SharedInboxManager()
        self.call_manager = CallLogManager()
    
    def test_inbox_filtering(self):
        """Test inbox message filtering"""
        filters = {
            'status': 'unread',
            'message_type': 'email',
            'priority': 'high'
        }
        
        inbox_data = self.inbox_manager.get_inbox('test_user', filters)
        
        self.assertIn('conversations', inbox_data)
        self.assertIn('stats', inbox_data)
        self.assertIn('total_unread', inbox_data)
        self.assertIsInstance(inbox_data['conversations'], list)
    
    def test_message_sending(self):
        """Test message sending"""
        result = self.inbox_manager.send_message(
            user_id='test_user',
            lead_id='1',
            message_type=MessageType.EMAIL,
            content='Test message',
            recipient='test@example.com',
            subject='Test Subject'
        )
        
        self.assertIn('message_id', result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'sent')
    
    def test_call_logging(self):
        """Test call logging"""
        result = self.call_manager.log_call(
            user_id='test_user',
            lead_id='1',
            phone_number='+15551234567',
            direction='outbound',
            duration_seconds=180,
            disposition=CallDisposition.CONNECTED,
            notes='Test call notes'
        )
        
        self.assertIn('call_id', result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'logged')
    
    def test_call_history(self):
        """Test call history retrieval"""
        history = self.call_manager.get_call_history('test_user', None, 30)
        
        self.assertIsInstance(history, list)
        # History might be empty, but should be a list
    
    def test_call_analytics(self):
        """Test call analytics"""
        analytics = self.call_manager.get_call_analytics('test_user', 30)
        
        required_fields = [
            'total_calls', 'connected_calls', 'connection_rate',
            'appointments_scheduled', 'appointment_rate', 'avg_call_duration_minutes'
        ]
        
        for field in required_fields:
            self.assertIn(field, analytics)
            self.assertIsInstance(analytics[field], (int, float))
    
    def test_callbacks_due(self):
        """Test callback retrieval"""
        callbacks = self.call_manager.get_callbacks_due('test_user')
        
        self.assertIsInstance(callbacks, list)
        # Callbacks might be empty, but should be a list


class TestIntegration(unittest.TestCase):
    """Test integration between services"""
    
    def setUp(self):
        self.scorer = AILeadScorer()
        self.calculator = ROICalculator()
        self.sequence_manager = SequenceManager()
        self.inbox_manager = SharedInboxManager()
    
    def test_lead_scoring_to_sequence(self):
        """Test using lead score to trigger nurture sequence"""
        lead_data = {
            'id': '1',
            'name': 'High Value Lead',
            'email': 'hvl@test.com',
            'phone': '+1234567890',
            'source': 'referral',
            'industry': 'medspas'
        }
        
        # Score the lead
        score = self.scorer.score_lead(lead_data)
        
        # If high score, start premium sequence
        if score['overall_score'] >= 70:
            business_data = {'business_name': 'Test Spa', 'agent_name': 'Agent'}
            sequence_result = self.sequence_manager.start_sequence_for_lead(lead_data, business_data)
            
            self.assertIn('sequence_id', sequence_result)
            self.assertGreater(sequence_result['total_steps'], 0)
    
    def test_roi_improvement_suggestions(self):
        """Test ROI-based improvement suggestions"""
        metrics = self.calculator.calculate_roi_metrics('test_user', 30)
        recommendations = self.calculator.get_growth_recommendations(metrics, 'contractors')
        
        # Should have actionable recommendations
        self.assertGreater(len(recommendations), 0)
        
        # Check recommendation structure
        for rec in recommendations:
            self.assertIn('impact', rec)
            self.assertIn(rec['impact'], ['Low', 'Medium', 'High'])


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
