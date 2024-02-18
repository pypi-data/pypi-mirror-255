import unittest
from unittest.mock import patch, Mock

from cast_ai.se.services.request_handle_svc import CustomHTTPError
from cast_ai.se.services.api_requests_svc import cast_api_get


class TestApiRequestsService(unittest.TestCase):
    # TODO: implement successful call
    # @patch('services.api_requests_svc.setup_logging')
    # @patch('services.api_requests_svc.get_api_key_headers')
    # @patch('services.request_handle_svc.get_api_key_headers')
    # @patch('services.request_handle_svc.handle_request')
    # def test_cast_api_get_success(self, mock_setup_logging, mock_get_api_key_headers1,
    #                               mock_get_api_key_headers2, mock_handle_request):
    #     # Arrange
    #     mock_setup_logging.return_value = None
    #     mock_get_api_key_headers1.return_value = {'Authorization': 'Bearer YOUR_API_KEY'}
    #     mock_get_api_key_headers2.return_value = {'Authorization': 'Bearer YOUR_API_KEY'}
    #     mock_response = Mock()
    #     mock_response.content.decode.return_value = '{"key": "value"}'
    #     mock_handle_request.return_value = mock_response
    #
    #     # Act
    #     result = cast_api_get('https://example.com/api')
    #
    #     # Assert
    #     self.assertEqual(result, {'key': 'value'})
    #     mock_setup_logging.assert_called_once()
    #     mock_get_api_key_headers1.assert_called_once()
    #     mock_get_api_key_headers2.assert_called_once()
    #     mock_handle_request.assert_called_once_with('https://example.com/api',
    #                                                 {'Authorization': 'Bearer YOUR_API_KEY'}, method='GET')

    @patch('misc_utils.setup_logging')
    @patch('services.api_requests_svc.get_api_key_headers')
    @patch('services.request_handle_svc.handle_request')
    def test_cast_api_get_failure(self, mock_setup_logging, mock_get_api_key_headers, mock_handle_request):
        # Arrange
        mock_setup_logging.return_value = None
        mock_get_api_key_headers.return_value = {'Authorization': 'Bearer YOUR_API_KEY'}
        mock_response = Mock()
        mock_response.content.decode.return_value = '{"error": "Something went wrong"}'
        mock_handle_request.side_effect = CustomHTTPError(response=mock_response)

        # Act & Assert
        with self.assertRaises(CustomHTTPError) as context:
            cast_api_get('https://example.com/api')

        self.assertEqual(str(context.exception),
                         'HTTP Error: 404 Client Error: Not Found for url: https://example.com/api')
        # mock_setup_logging.assert_called_once()
        # mock_get_api_key_headers.assert_called_once()
        # mock_handle_request.assert_called_once_with('https://example.com/api',
        # {'Authorization': 'Bearer YOUR_API_KEY'}, method='GET')


if __name__ == '__main__':
    unittest.main()
