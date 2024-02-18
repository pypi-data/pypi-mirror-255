import pytest
from covalent.services.util.back_off import ExponentialBackoff, MaxRetriesExceededError

class TestBackOff:
    """ back off test class """
    
    @pytest.fixture
    def mock_retry_logic(self, mocker):
        # Create a mock for the function with retry logic
        mock_function = mocker.patch('requests.get')
        
        # Set expectations on the mock to control its behavior
        mock_function.side_effect = [None, None, Exception("Max retries (3) exceeded.")]
        
        return mock_function

    def test_mock_retry_attempt(self, mock_retry_logic):
        max_retries = 3
        api_key = "YOUR_API_KEY"
        backoff = ExponentialBackoff(api_key, False, max_retries)
        mock_response = "Max retries (3) exceeded."
        
        try:
            result = backoff.back_off("https://example.com")
        except Exception as error:
            assert str(error) == mock_response