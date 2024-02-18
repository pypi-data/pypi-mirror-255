"""Main module."""
from urllib.parse import urljoin

import requests


class RestClient(object):
    base_url: str

    def __init__(self, base_url: str = None, *args, **kwargs):
        """ Base RestClient class. Provide a base_url as either an overridden class attribute, or as an argument on init.

        To access the common session for all requests, use `self.session`

        :param base_url: base url of resource
        """
        
        if not hasattr(self, 'base_url') and not base_url:
            raise ValueError('You must provide a `base_url` when you create a RestClient.')
        self.base_url = base_url or self.base_url
        self.session = requests.Session()

        super(RestClient, self).__init__(*args, **kwargs)

        self.authenticate()

    def authenticate(self):
        """ Override with a unique authentication flow, if necessary. """
        pass

    def _request(self, method: str, endpoint: str, params: dict = None, data: dict = None, append_url=True, **kwargs) -> requests.Response:        
        """ Protected method. Send any request. All `kwargs` are passed directly to the request.

        :param method: HTTP method
        :param endpoint: request endpoint (omit base URL if append_url is True)
        :param params: query string parameters (optional)
        :param data: request body (optional)
        :param append_url: set to true if the endpoint should be appended to base URL. defaults to true
        :param \**kwargs: request keyword arguments
        :return: response object
        """
        url = self.build_url(endpoint) if append_url else endpoint
        params = self.get_query_params(params)
        data = data or {}
        response = self.session.request(method, url, params=params, data=data, **kwargs)
        return response

    def get(self, endpoint: str, append_url=True, **kwargs) -> requests.Response:
        """ Make a HTTP GET request. 
        
        :param endpoint: request endpoint
        :param append_url: set to true if the endpoint should be appended to base URL. defaults to true
        :param \**kwargs: request keyword arguments
        """
        return self._request('get', endpoint=endpoint, append_url=append_url, **kwargs)

    def post(self, endpoint: str, append_url=True, **kwargs) -> requests.Response:
        """ Make a HTTP POST request. 
        
        :param endpoint: request endpoint
        :param append_url: set to true if the endpoint should be appended to base URL. defaults to true
        :param \**kwargs: request keyword arguments
        """
        return self._request('post', endpoint=endpoint, append_url=append_url, **kwargs)

    def put(self, endpoint: str, append_url=True, **kwargs) -> requests.Response:
        """ Make a HTTP PUT request. 
        
        :param endpoint: request endpoint
        :param append_url: set to true if the endpoint should be appended to base URL. defaults to true
        :param \**kwargs: request keyword arguments
        """
        return self._request('put', endpoint=endpoint, append_url=append_url, **kwargs)
    
    def patch(self, endpoint: str, append_url=True, **kwargs) -> requests.Response:
        """ Make a HTTP PATCH request. 
        
        :param endpoint: request endpoint
        :param append_url: set to true if the endpoint should be appended to base URL. defaults to true
        :param \**kwargs: request keyword arguments
        """
        return self._request('patch', endpoint=endpoint, append_url=append_url, **kwargs)
    
    def options(self, endpoint: str, append_url=True, **kwargs) -> requests.Response:
        """ Make a HTTP OPTIONS request. 
        
        :param endpoint: request endpoint
        :param append_url: set to true if the endpoint should be appended to base URL. defaults to true
        :param \**kwargs: request keyword arguments
        """
        return self._request('options', endpoint=endpoint, append_url=append_url, **kwargs)
    
    def head(self, endpoint: str, append_url=True, **kwargs) -> requests.Response:
        """ Make a HTTP HEAD request. 
        
        :param endpoint: request endpoint
        :param append_url: set to true if the endpoint should be appended to base URL. defaults to true
        :param \**kwargs: request keyword arguments
        """
        return self._request('head', endpoint=endpoint, append_url=append_url, **kwargs)
    
    def delete(self, endpoint: str, append_url=True, **kwargs) -> requests.Response:
        """ Make a HTTP DELETE request. 
        
        :param endpoint: request endpoint
        :param append_url: set to true if the endpoint should be appended to base URL. defaults to true
        :param \**kwargs: request keyword arguments
        """
        return self._request('delete', endpoint=endpoint, append_url=append_url, **kwargs)

    def get_query_params(self, params: dict) -> dict:
        """ Format a dictionary of query parameters by looking up the class defaults, then overriding with 
        argument to `params`.

        :param params: request parameters (will override defaults)
        :return: default parameters + `params`
        """
        _params = self.get_default_query_params()
        _params.update(params or {})
        return _params

    def get_default_query_params(self) -> dict:
        """ Override with a set of default parameters to include in every request. Often helpful for API keys passed in query params. """
        return {}
    
    def build_url(self, endpoint: str) -> str:
        """ Build the request URL using self.base_url and `endpoint`.

        :param endpoint: request endpoint
        :return: formatted URL
        """
        return urljoin(self.base_url, endpoint) if endpoint else self.base_url
    
    def __repr__(self):
        return """RestClient(base_url='{}')""".format(self.base_url)
