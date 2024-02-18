from .baseauthorizationrequest import BaseAuthorizedRequest

class ApiKeyAuthorizationParameters:
    def __init__(self):
        self.api_key_key = None
        self.api_key_value = None
        self.api_key_add_to = None

class ApiKeyAuthorizationRequest(BaseAuthorizedRequest):
    def __init__(self, requests, parameters : ApiKeyAuthorizationParameters):
        BaseAuthorizedRequest.__init__(self, requests)
        self.parameters = parameters
    
    def request(self, url):
        if self.parameters.api_key_add_to == 'Header':
            if (self.headers is None):
                self.headers = {}
            self.headers[self.parameters.api_key_key] = self.parameters.api_key_value
        elif self.parameters.api_key_add_to == 'QueryParams':
            if (url.find('?') == -1):
                url = url + '?' + self.parameters.api_key_key + '=' + self.parameters.api_key_value
            else:
                url = url.replace("?", '?' + self.parameters.api_key_key + '=' + self.parameters.api_key_value + '&')
        else:
            raise ValueError('Unknown api_key_add_to: ' + self.parameters.api_key_add_to)
        return self._make_request(url)