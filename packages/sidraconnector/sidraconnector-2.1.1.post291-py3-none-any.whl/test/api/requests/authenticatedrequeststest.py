import json
import unittest
import xmlrunner
from parameterized import parameterized
from unittest.mock import MagicMock
import requests
import requests_mock

from sidraconnector.sdk.requests.basicauthorizationrequest import BasicAuthorizationRequest, BasicAuthorizationParameters
from sidraconnector.sdk.requests.apikeyauthorizationrequest import ApiKeyAuthorizationRequest, ApiKeyAuthorizationParameters
from sidraconnector.sdk.requests.oauthauthorizationrequest import OAuthAuthorizationRequest, OAuthClientCredentialsAuthorizationParameters, OAuthPasswordAuthorizationParameters 

class TestAuthenticatedRequests(unittest.TestCase):
  sample_url = 'http://faketest.xyz/'

  # Test functions should start with 'test' to be discovered by unittest
  @requests_mock.Mocker()
  def test_basic_authentication_should_authenticate_request(self, mock_requests):
    # Arrange
    mock_requests.get('http://faketest.xyz/success', text='{"authenticated": true}')
    parameters = BasicAuthorizationParameters()
    parameters.username = "foo"
    parameters.password = "bar"
    service = BasicAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    # Act
    response = service.request(url='http://faketest.xyz/success')
    jsonResponse = json.loads(response.text)
    # Assert
    self.assertTrue(jsonResponse['authenticated'] is True)

  @requests_mock.Mocker()
  def test_basic_authentication_wrong_password_should_return_unauthorized(self, mock_requests):
    #Arrange 
    parameters = BasicAuthorizationParameters()
    parameters.username = "foo"
    parameters.password = "incorrectpass"
    service = BasicAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.get('http://faketest.xyz/incorrectpass', status_code=401)
    # Act
    response = service.request(url='http://faketest.xyz/incorrectpass')
    # Assert
    self.assertTrue(response.status_code == 401)

  @requests_mock.Mocker()
  def test_basic_authentication_wrong_username_should_return_unauthorized(self, mock_requests):
    # Arrange
    mock_requests.get('http://faketest.xyz/incorrectuser', status_code=401)
    parameters = BasicAuthorizationParameters()
    parameters.username = "incorrectuser"
    parameters.password = "bar"
    service = BasicAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    # Act
    response = service.request(url = 'http://faketest.xyz/incorrectuser')
    # Assert
    self.assertTrue(response.status_code == 401)

  @requests_mock.Mocker()
  def test_api_key_authentication_should_send_api_key_in_query(self, mock_requests):
    # Arrange
    parameters = ApiKeyAuthorizationParameters()
    parameters.api_key_add_to = "QueryParams"
    parameters.api_key_key = "access_key"
    parameters.api_key_value = "bf840afd71e5e50bccefe6585966495d"
    mock_requests.get(self.sample_url)
    service = ApiKeyAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    # Act
    response = service.request(url= self.sample_url)
    # Assert
    assert 'access_key=bf840afd71e5e50bccefe6585966495d' in mock_requests.last_request.query
    
  @requests_mock.Mocker()
  def test_api_key_authentication_should_send_api_key_in_query_when_has_params(self, mock_requests):
    # Arrange
    parameters = ApiKeyAuthorizationParameters()
    parameters.api_key_add_to = "QueryParams"
    parameters.api_key_key = "access_key"
    parameters.api_key_value = "bf840afd71e5e50bccefe6585966495d"
    mock_requests.get(self.sample_url)
    service = ApiKeyAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.get('http://faketest.xyz/?something=value')
    # Act
    service.request(url='http://faketest.xyz/?something=value')
    # Assert
    assert 'access_key=bf840afd71e5e50bccefe6585966495d&something=value' in mock_requests.last_request.query


  @requests_mock.Mocker()
  def test_api_key_authentication_wrong_key_should_return_error_response(self, mock_requests):
    # Arrange
    parameters = ApiKeyAuthorizationParameters()
    parameters.api_key_add_to = "QueryParams"
    parameters.api_key_key = "access_key"
    parameters.api_key_value = "wrongkey"
    service = ApiKeyAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.get(self.sample_url, text='{"success": false, "error": {"type": "invalid_access_key"} }')
    # Act
    response = service.request(url=self.sample_url)
    # Assert
    self.assertTrue(json.loads(response.text)['success'] is False)
    self.assertTrue(json.loads(response.text)['error']["type"] == "invalid_access_key")

  @requests_mock.Mocker()
  def test_api_key_authentication_add_access_key_to_header_with_other_headers(self, mock_requests):
    # Arrange
    parameters = ApiKeyAuthorizationParameters()
    parameters.api_key_add_to = "Header"
    parameters.api_key_key = "access_key"
    parameters.api_key_value = "bf840afd71e5e50bccefe6585966495d"
    service = ApiKeyAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.get(self.sample_url)
    # Act
    response = service.request(url=self.sample_url)
    # Assert
    assert mock_requests.last_request.headers['Accept'] == 'application/json'
    assert mock_requests.last_request.headers['access_key'] == 'bf840afd71e5e50bccefe6585966495d'

  @requests_mock.Mocker()
  def test_api_key_authentication_add_access_key_to_header_without_other_headers(self, mock_requests):
    # Arrange
    parameters = ApiKeyAuthorizationParameters()
    parameters.api_key_add_to = "Header"
    parameters.api_key_key = "access_key"
    parameters.api_key_value = "bf840afd71e5e50bccefe6585966495d"
    service = ApiKeyAuthorizationRequest(requests, parameters)
    mock_requests.get(self.sample_url)
    # Act
    response = service.request(url=self.sample_url)
    # Assert
    assert mock_requests.last_request.headers['access_key'] == 'bf840afd71e5e50bccefe6585966495d'

  @requests_mock.Mocker()
  def test_api_key_authentication_wrong_addto_should_raise_exception(self, mock_requests):
    # Arrange
    parameters = ApiKeyAuthorizationParameters()
    parameters.api_key_add_to = "WrongAddTo"
    parameters.api_key_key = "access_key"
    parameters.api_key_value = "bf840afd71e5e50bccefe6585966495d"
    service = ApiKeyAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.get(self.sample_url)
    # Act
    try:
      response = service.request(url=self.sample_url)
      self.assertTrue(False)
    except ValueError as e:
      self.assertTrue(True)

  @requests_mock.Mocker()
  def test_oauth_password_flow_should_call_url_with_access_token(self, mock_requests):
    # Arrange
    parameters = OAuthPasswordAuthorizationParameters()
    parameters.client_id = "clientId"
    parameters.client_secret = "clientSecret"
    parameters.token_url = "http://faketest.xyz/token"
    parameters.user_name = "foo"
    parameters.password = "bar"
    service = OAuthAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.post(parameters.token_url, text='{"access_token": "bf840afd71e5e50bccefe6585966495d"}')
    mock_requests.get(self.sample_url, text='{"test": "value"}')
    # Act
    service.request(self.sample_url)
    # Assert
    assert mock_requests.last_request.url == self.sample_url
    assert mock_requests.last_request.headers['Authorization'] == f'{parameters.authentication_header_prefix} bf840afd71e5e50bccefe6585966495d'

  @requests_mock.Mocker()
  def test_oauth_client_credentials_flow_should_call_url_with_access_token(self, mock_requests):
    # Arrange
    parameters = OAuthClientCredentialsAuthorizationParameters()
    parameters.client_id = "clientId"
    parameters.client_secret = "clientSecret"
    parameters.token_url = "http://faketest.xyz/token"

    service = OAuthAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.post(parameters.token_url, text='{"access_token": "bf840afd71e5e50bccefe6585966495d"}')
    mock_requests.get(self.sample_url, text='{"test": "value"}')
    # Act
    service.request(self.sample_url)
    # Assert
    assert mock_requests.last_request.url == self.sample_url
    assert mock_requests.last_request.headers['Authorization'] == f'{parameters.authentication_header_prefix} bf840afd71e5e50bccefe6585966495d'


  @requests_mock.Mocker()
  def test_oauth_password_flow_should_throw_exception_when_fails_to_get_token(self, mock_requests):
    # Arrange
    parameters = OAuthPasswordAuthorizationParameters()
    parameters.client_id = "clientId"
    parameters.client_secret = "clientSecret"
    parameters.token_url = "http://faketest.xyz/token"
    parameters.user_name = "foo"
    parameters.password = "bar"
    service = OAuthAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.post(parameters.token_url, status_code=400, text='{"error": "invalid_client"}')
    mock_requests.get(self.sample_url, text='{"test": "value"}')
    # Act
    try:
      service.request(self.sample_url)
      self.assertTrue(False)
    except ValueError as e:
      self.assertTrue(True)

  @requests_mock.Mocker()
  def test_oauth_client_credentials_flow_should_throw_exception_when_fails_to_get_token(self, mock_requests):
    # Arrange
    parameters = OAuthClientCredentialsAuthorizationParameters()
    parameters.client_id = "clientId"
    parameters.client_secret = "clientSecret"
    parameters.token_url = "http://faketest.xyz/token"

    service = OAuthAuthorizationRequest(requests, parameters)
    service.add_header('Accept', 'application/json')
    mock_requests.post(parameters.token_url, status_code=400, text='{"error": "invalid_client"}')
    mock_requests.get(self.sample_url, text='{"test": "value"}')
    # Act
    try:
      service.request(self.sample_url)
      self.assertTrue(False)
    except ValueError as e:
      self.assertTrue(True)

def run_tests():
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    # add tests to the test suite
    suite.addTests(loader.loadTestsFromTestCase(testCaseClass=TestAuthenticatedRequests))
    
    # initialize a runner, pass it your suite and run it
    runner = xmlrunner.XMLTestRunner(verbosity=3, descriptions=True, output='/dbfs/runtests/Test_AuthenticatedRequests_Report')
    result = runner.run(suite)
    
    # ensure job failed if there are issues
    assert len(result.failures) == 0
    assert len(result.errors) == 0