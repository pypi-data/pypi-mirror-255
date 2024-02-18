from retry import retry

class BaseAuthorizedRequest:
    def __init__(self, requests, method = 'GET', params=None, data=None, headers=None, cookies=None, json = None):
        self.method = method
        self.params = params
        self.data = data
        self.headers = headers
        self.cookies = cookies
        self.json = json
        self.requests = requests
        self.session = requests.Session()

    def set_method(self, data):
         self.method = data
    
    def set_data(self, data):
         self.data = data
    
    def add_header(self, key, value):
         if (self.headers is None):
                self.headers = {}
         self.headers[key] = value
    def set_cookies(self, cookies):
         self.cookies = cookies
    
    def set_json(self, json):
         self.json = json
    
    def get_session(self):
         return self.session
    
    @retry(tries=5, delay=1, backoff=2)
    def _make_request(self, url):
            return self.session.request(method=self.method, url=url, params=self.params, data=self.data, headers=self.headers, cookies=self.cookies, json = self.json)
    