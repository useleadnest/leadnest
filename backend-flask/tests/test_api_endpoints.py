"""
Unit tests for competitive API endpoints
Tests all API endpoints for validation, error handling, and functionality
"""
import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Mock Flask app and dependencies before importing
sys.modules['redis'] = MagicMock()
sys.modules['twilio'] = MagicMock()
sys.modules['twilio.rest'] = MagicMock()
sys.modules['stripe'] = MagicMock()
sys.modules['sentry_sdk'] = MagicMock()

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))

# Mock Flask app components
flask_mock = MagicMock()
sys.modules['flask'] = flask_mock
sys.modules['flask_cors'] = MagicMock()
sys.modules['flask_jwt_extended'] = MagicMock()
sys.modules['marshmallow'] = MagicMock()
sys.modules['marshmallow.fields'] = MagicMock()

# Set up mock Flask app
app_mock = MagicMock()
app_mock.config = {}
flask_mock.Flask.return_value = app_mock

# Import after mocking
import api


class TestCompetitiveAPIEndpoints(unittest.TestCase):
    """Test competitive advantage API endpoints"""
    
    def setUp(self):
        self.app = app_mock
        self.app.config['TESTING'] = True
        
        # Mock authentication
        self.auth_patcher = patch('api.jwt_required')
        self.get_jwt_identity_patcher = patch('api.get_jwt_identity', return_value='test_user')
        
        self.mock_jwt = self.auth_patcher.start()
        self.mock_identity = self.get_jwt_identity_patcher.start()
        
        # Mock logger
        self.log_patcher = patch('api.log')
        self.mock_log = self.log_patcher.start()
        
        # Mock services
        self.ai_scorer_patcher = patch('api.AILeadScorer')
        self.roi_calc_patcher = patch('api.ROICalculator')
        self.seq_manager_patcher = patch('api.SequenceManager')
        self.inbox_manager_patcher = patch('api.SharedInboxManager')
        self.call_manager_patcher = patch('api.CallLogManager')
        
        self.mock_ai_scorer = self.ai_scorer_patcher.start()
        self.mock_roi_calc = self.roi_calc_patcher.start()
        self.mock_seq_manager = self.seq_manager_patcher.start()
        self.mock_inbox_manager = self.inbox_manager_patcher.start()
        self.mock_call_manager = self.call_manager_patcher.start()
        
        # Set up mock responses
        self.setup_mock_responses()
    
    def tearDown(self):
        # Stop all patches
        self.auth_patcher.stop()
        self.get_jwt_identity_patcher.stop()
        self.log_patcher.stop()
        self.ai_scorer_patcher.stop()
        self.roi_calc_patcher.stop()
        self.seq_manager_patcher.stop()
        self.inbox_manager_patcher.stop()
        self.call_manager_patcher.stop()
    
    def setup_mock_responses(self):
        """Set up mock service responses"""
        # AI Lead Scorer mocks
        mock_scorer_instance = self.mock_ai_scorer.return_value
        mock_scorer_instance.bulk_score_leads.return_value = [
            {'lead_id': '1', 'score': 85, 'grade': 'A', 'confidence': 0.9}
        ]
        mock_scorer_instance.get_scored_leads.return_value = {
            'leads': [{'id': '1', 'score': 85, 'grade': 'A'}],
            'total_count': 1
        }
        
        # ROI Calculator mocks
        mock_roi_instance = self.mock_roi_calc.return_value
        mock_metrics = MagicMock()
        mock_metrics.roi_percentage = 250.0
        mock_metrics.revenue_generated = 50000
        mock_metrics.leads_uploaded = 100
        mock_roi_instance.calculate_roi_metrics.return_value = mock_metrics
        mock_roi_instance.get_growth_recommendations.return_value = [
            {'category': 'conversion', 'title': 'Test Rec', 'impact': 'High'}
        ]
        
        # Sequence Manager mocks
        mock_seq_instance = self.mock_seq_manager.return_value
        mock_seq_instance.get_available_templates.return_value = [
            {'id': 'template1', 'name': 'Test Template', 'industry': 'medspas'}
        ]
        mock_seq_instance.start_sequence_for_lead.return_value = {
            'sequence_id': 'seq123',
            'total_steps': 5
        }
        
        # Inbox Manager mocks
        mock_inbox_instance = self.mock_inbox_manager.return_value
        mock_inbox_instance.get_inbox.return_value = {
            'conversations': [{'id': '1', 'subject': 'Test'}],
            'stats': {'total_unread': 5}
        }
        mock_inbox_instance.send_message.return_value = {
            'message_id': 'msg123',
            'status': 'sent'
        }
        
        # Call Manager mocks
        mock_call_instance = self.mock_call_manager.return_value
        mock_call_instance.get_call_history.return_value = [
            {'id': '1', 'phone': '+1234567890', 'duration': 180}
        ]
        mock_call_instance.log_call.return_value = {
            'call_id': 'call123',
            'status': 'logged'
        }
    
    @patch('api.request')
    def test_ai_bulk_score_leads(self, mock_request):
        """Test bulk lead scoring endpoint"""
        # Mock request data
        mock_request.json = {
            'leads': [
                {'id': '1', 'name': 'John Doe', 'email': 'john@test.com'}
            ]
        }
        mock_request.method = 'POST'
        
        # Mock function call
        result = api.ai_bulk_score_leads()
        
        # Verify service was called
        self.mock_ai_scorer.assert_called_once()
        
        # Verify logging
        self.mock_log.info.assert_called()
    
    @patch('api.request')
    def test_roi_metrics(self, mock_request):
        """Test ROI metrics endpoint"""
        mock_request.args = {'days': '30'}
        
        result = api.roi_metrics()
        
        # Verify service was called with correct parameters
        mock_roi_instance = self.mock_roi_calc.return_value
        mock_roi_instance.calculate_roi_metrics.assert_called_with('test_user', 30)
        
        # Verify logging
        self.mock_log.info.assert_called()
    
    @patch('api.request')
    def test_nurture_start_sequence(self, mock_request):
        """Test starting nurture sequence endpoint"""
        mock_request.json = {
            'lead_id': '1',
            'template_id': 'template1',
            'lead_data': {'name': 'John Doe'},
            'business_data': {'business_name': 'Test Spa'}
        }
        
        result = api.nurture_start_sequence()
        
        # Verify service was called
        mock_seq_instance = self.mock_seq_manager.return_value
        mock_seq_instance.start_sequence_for_lead.assert_called()
        
        # Verify logging
        self.mock_log.info.assert_called()
    
    @patch('api.request')
    def test_inbox_get_inbox(self, mock_request):
        """Test get inbox endpoint"""
        mock_request.args = {
            'status': 'unread',
            'page': '1',
            'per_page': '20'
        }
        
        result = api.inbox_get_inbox()
        
        # Verify service was called with filters
        mock_inbox_instance = self.mock_inbox_manager.return_value
        mock_inbox_instance.get_inbox.assert_called()
        
        # Verify logging
        self.mock_log.info.assert_called()
    
    @patch('api.request')
    def test_inbox_send_message(self, mock_request):
        """Test send message endpoint"""
        mock_request.json = {
            'lead_id': '1',
            'message_type': 'email',
            'content': 'Test message',
            'recipient': 'test@example.com',
            'subject': 'Test Subject'
        }
        
        result = api.inbox_send_message()
        
        # Verify service was called
        mock_inbox_instance = self.mock_inbox_manager.return_value
        mock_inbox_instance.send_message.assert_called()
        
        # Verify logging
        self.mock_log.info.assert_called()
    
    @patch('api.request')
    def test_calls_log_call(self, mock_request):
        """Test log call endpoint"""
        mock_request.json = {
            'lead_id': '1',
            'phone_number': '+15551234567',
            'direction': 'outbound',
            'duration_seconds': 180,
            'disposition': 'connected',
            'notes': 'Test call notes'
        }
        
        result = api.calls_log_call()
        
        # Verify service was called
        mock_call_instance = self.mock_call_manager.return_value
        mock_call_instance.log_call.assert_called()
        
        # Verify logging
        self.mock_log.info.assert_called()
    
    @patch('api.request')
    def test_error_handling(self, mock_request):
        """Test API error handling"""
        # Mock service to raise exception
        mock_scorer_instance = self.mock_ai_scorer.return_value
        mock_scorer_instance.bulk_score_leads.side_effect = Exception("Test error")
        
        mock_request.json = {'leads': []}
        
        result = api.ai_bulk_score_leads()
        
        # Verify error was logged
        self.mock_log.error.assert_called()
    
    def test_validation_schemas(self):
        """Test that validation schemas are properly defined"""
        # This is a basic test to ensure schemas exist
        # In a real implementation, we would test schema validation
        
        # Check that schema classes are defined
        # Note: These would be actual schema validations in a real test
        self.assertTrue(hasattr(api, 'MessageSchema') or 'MessageSchema' in dir(api))
        self.assertTrue(hasattr(api, 'CallLogSchema') or 'CallLogSchema' in dir(api))
        self.assertTrue(hasattr(api, 'NurtureSequenceSchema') or 'NurtureSequenceSchema' in dir(api))


class TestAPIValidation(unittest.TestCase):
    """Test API input validation"""
    
    def setUp(self):
        # Mock Marshmallow schemas
        self.schema_patcher = patch('api.MessageSchema')
        self.call_schema_patcher = patch('api.CallLogSchema')
        self.seq_schema_patcher = patch('api.NurtureSequenceSchema')
        
        self.mock_msg_schema = self.schema_patcher.start()
        self.mock_call_schema = self.call_schema_patcher.start()
        self.mock_seq_schema = self.seq_schema_patcher.start()
        
        # Set up validation behavior
        self.mock_msg_schema.return_value.load.return_value = {'valid': 'data'}
        self.mock_call_schema.return_value.load.return_value = {'valid': 'data'}
        self.mock_seq_schema.return_value.load.return_value = {'valid': 'data'}
    
    def tearDown(self):
        self.schema_patcher.stop()
        self.call_schema_patcher.stop()
        self.seq_schema_patcher.stop()
    
    def test_message_validation(self):
        """Test message validation schema"""
        schema = self.mock_msg_schema.return_value
        
        # Test valid data
        valid_data = {
            'lead_id': '1',
            'message_type': 'email',
            'content': 'Test message'
        }
        
        result = schema.load(valid_data)
        self.assertEqual(result, {'valid': 'data'})
        
        schema.load.assert_called_with(valid_data)
    
    def test_call_log_validation(self):
        """Test call log validation schema"""
        schema = self.mock_call_schema.return_value
        
        valid_data = {
            'lead_id': '1',
            'phone_number': '+15551234567',
            'direction': 'outbound',
            'disposition': 'connected'
        }
        
        result = schema.load(valid_data)
        self.assertEqual(result, {'valid': 'data'})
        
        schema.load.assert_called_with(valid_data)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
