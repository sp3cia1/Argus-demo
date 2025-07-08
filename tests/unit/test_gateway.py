"""
Tests for the main ArgusGateway.
"""

import unittest
from unittest.mock import Mock, patch
from src.argus.core.gateway import ArgusGateway

class TestArgusGateway(unittest.TestCase):
    """Test cases for ArgusGateway."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.gateway = ArgusGateway()
    
    @patch('src.argus.core.gateway.check_input_filters')
    @patch('src.argus.core.gateway.get_llm_response')
    @patch('src.argus.core.gateway.check_output_filters')
    @patch('src.argus.core.gateway.analyze_response_with_guard')
    def test_clean_prompt_flow(self, mock_guard, mock_output, mock_llm, mock_input):
        """Test the complete flow with a clean prompt."""
        # Setup mocks
        mock_input.return_value = None  # L1 input passes
        mock_llm.return_value = "This is a clean response."
        mock_output.return_value = None  # L1 output passes
        mock_guard.return_value = {'status': 'success', 'decision': 'CLEAN', 'reason': None}
        
        # Test
        result = self.gateway.process_prompt("Tell me about the weather.")
        
        # Verify
        self.assertEqual(result, "This is a clean response.")
        mock_input.assert_called_once()
        mock_llm.assert_called_once()
        mock_output.assert_called_once()
        mock_guard.assert_called_once()
    
    @patch('src.argus.core.gateway.check_input_filters')
    def test_l1_input_violation(self, mock_input):
        """Test L1 input filter violation."""
        mock_input.return_value = "PII detected"
        
        result = self.gateway.process_prompt("My SSN is 123-45-6789")
        
        self.assertIn("[Argus]", result)
        self.assertIn("Input blocked", result)
    
    @patch('src.argus.core.gateway.check_input_filters')
    @patch('src.argus.core.gateway.get_llm_response')
    @patch('src.argus.core.gateway.check_output_filters')
    @patch('src.argus.core.gateway.analyze_response_with_guard')
    def test_l2_violation(self, mock_guard, mock_output, mock_llm, mock_input):
        """Test L2 guard violation."""
        # Setup mocks
        mock_input.return_value = None
        mock_llm.return_value = "This contains sensitive data."
        mock_output.return_value = None
        mock_guard.return_value = {'status': 'success', 'decision': 'VIOLATION', 'reason': 'PII_DETECTED'}
        
        # Test
        result = self.gateway.process_prompt("What is sensitive data?")
        
        # Verify
        self.assertIn("[Argus]", result)
        self.assertIn("Response blocked", result)

if __name__ == '__main__':
    unittest.main()
