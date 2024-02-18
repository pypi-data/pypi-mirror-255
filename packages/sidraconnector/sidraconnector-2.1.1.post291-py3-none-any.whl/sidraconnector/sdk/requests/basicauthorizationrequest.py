from .baseauthorizationrequest import BaseAuthorizedRequest

class BasicAuthorizationParameters:
    def __init__(self):
        self.username = None
        self.password = None


class BasicAuthorizationRequest(BaseAuthorizedRequest):
    def __init__(self, requests, parameters : BasicAuthorizationParameters):
        BaseAuthorizedRequest.__init__(self, requests)
        self.parameters = parameters
    
    def request(self, url):
        self.session.auth = (self.parameters.username, self.parameters.password)
        return self._make_request(url)