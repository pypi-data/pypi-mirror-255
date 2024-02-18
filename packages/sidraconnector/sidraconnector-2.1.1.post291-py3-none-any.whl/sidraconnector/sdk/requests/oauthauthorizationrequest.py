from .baseauthorizationrequest import BaseAuthorizedRequest

class OAuthAuthorizationParameters:
    def __init__(self):
        self.grant_type = None
        self.token_url = None
        self.client_id = None
        self.client_secret = None
        self.authentication_header_prefix = 'Bearer'
        self.authorization_header_name = 'Authorization'

class OAuthClientCredentialsAuthorizationParameters(OAuthAuthorizationParameters):
    def __init__(self):
        super().__init__()
        self.grant_type = 'client_credentials'

    def get_request_data(self):
        return {
            'grant_type': self.grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }


class OAuthPasswordAuthorizationParameters(OAuthAuthorizationParameters):
    def __init__(self):
        super().__init__()
        self.grant_type = 'password'
        self.user_name = None
        self.password  = None
        
    def get_request_data(self):
        return {
            'grant_type': self.grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.user_name,
            'password': self.password,
        }



class OAuthAuthorizationRequest(BaseAuthorizedRequest):
    def __init__(self, requests, parameters : OAuthAuthorizationParameters):
        BaseAuthorizedRequest.__init__(self, requests)
        self.parameters = parameters
    
    def request(self, url):
        ## Request parameters
        token_request_data = self.parameters.get_request_data()
        # Send a POST request to the token endpoint
        response = self.requests.post(self.parameters.token_url, data=token_request_data)
        if response.status_code == 200:
            token_data = response.json()
            if (self.headers is None):
                self.headers = {}
            self.headers[self.parameters.authorization_header_name] = f'{self.parameters.authentication_header_prefix} {token_data["access_token"]}'
            return self._make_request(url)
        else:
            raise ValueError(f'Failed to get access token. Status code {response.status_code}')
        
