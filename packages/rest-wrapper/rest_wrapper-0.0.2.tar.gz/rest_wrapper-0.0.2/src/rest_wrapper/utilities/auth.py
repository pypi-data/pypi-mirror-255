

class SimpleAuthMixin(object):
    login_extras = {}
    login_endpoint = ''
    login_response = None
    get_login_first = True
    use_json_login = False
    username_key = 'username'
    password_key = 'password'

    def authenticate(self):
        if self.get_login_first:
            self.get_login_endpoint()

        payload_key = 'json' if self.use_json_login else 'data'
        request_kwargs = {
            payload_key: self.get_auth_request_payload()
        }
        request_kwargs.update(self.get_login_request_extras())

        self.login_response = self.post(self.login_endpoint, **request_kwargs)

    def get_auth_request_payload(self):
        return {
            self.username_key: self.username,
            self.password_key: self.password,
            **self.login_extras
        }

    def get_login_request_extras(self):
        """ Override with network-specific login request parameters """
        return {}

    def get_login_endpoint(self, **kwargs):
        return self.get(self.login_endpoint, **kwargs)


class HeaderAuthMixin(object):
    header_auth_key: str  # Name of header field to be set
    
    def __init__(self, api_key: str = None, *args, **kwargs):
        self.api_key = api_key or self.api_key
        super(HeaderAuthMixin, self).__init__(*args, **kwargs)

    def authenticate(self):
        self.session.headers.update({
            self.header_auth_key: self.api_key
        })


class BearerTokenMixin(object):
    
    def authenticate(self):
        self.session.headers.update({
            'Authorization': 'Token {}'.format(self.api_key)
        })
