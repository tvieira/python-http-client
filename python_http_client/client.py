import json
import encodings.idna


try:
    # Python 3
    import urllib.request as urllib
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    import urllib2 as urllib
    from urllib import urlencode


class Client(object):

    def __init__(self,
                 host=None,
                 api_key=None,
                 request_headers=None,
                 version=None):
        self.host = host
        self.request_headers = {'Authorization': 'Bearer ' + api_key}
        self.methods = ['delete', 'get', 'patch', 'post', 'put']
        self._version = version
        if request_headers:
            self._set_headers(request_headers)
        self._count = 0
        self._url_path = {}
        self._status_code = None
        self._response_body = None
        self._response_headers = None
        self._response = None

    def _reset(self):
        self._count = 0
        self._url_path = {}
        self._response = None

    def _add_to_url_path(self, value):
        self._url_path[self._count] = value
        self._count += 1

    def _build_versioned_url(self, url):
        return self.host + "/v" + str(self._version) + url

    def _build_url(self, query_params):
        url = ""
        count = 0
        while count < len(self._url_path):
            url += "/" + str(self._url_path[count])
            count += 1
        if query_params:
            url_values = urlencode(sorted(query_params.items()))
            url = url + '?' + url_values
        if self._version:
            url = self._build_versioned_url(url)
        else:
            url = self.host + url
        return url

    def _set_response(self, response):
        self._status_code = response.getcode()
        self._response_body = response.read()
        self._response_headers = response.info()

    def _set_headers(self, request_headers):
        self.request_headers.update(request_headers)

    def _(self, value):
        self._add_to_url_path(value)
        return self

    def __getattr__(self, value):
        if value == "version":
            def get_version(*args, **kwargs):
                self._version = args[0]
                return self
            return get_version

        if value in self.methods:
            method = value.upper()

            def http_request(*args, **kwargs):
                if 'request_headers' in kwargs:
                    self._set_headers(kwargs['request_headers'])
                data = json.dumps(kwargs['request_body'])\
                    if 'request_body' in kwargs else None
                params = kwargs['query_params']\
                    if 'query_params' in kwargs else None
                opener = urllib.build_opener()
                request = urllib.Request(self._build_url(params), data=data)
                for key, value in self.request_headers.items():
                    request.add_header(key, value)
                request.get_method = lambda: method
                self._response = opener.open(request)
                self._set_response(self._response)
                self._reset()
                return self
            return http_request
        else:
            self._add_to_url_path(value)
        return self

    @property
    def status_code(self):
        return self._status_code

    @property
    def response_body(self):
        return self._response_body

    @property
    def response_headers(self):
        return self._response_headers