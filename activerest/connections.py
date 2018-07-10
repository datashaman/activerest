import logging

log = logging.getLogger(__name__)

import requests

from furl import furl


class Connection(object):
    _site = None

    _auth_type = 'basic'
    username = None
    password = None

    _timeout = None
    _open_timeout = None
    _read_timeout = None

    proxies = None

    requests = []

    def __init__(self, site):
        self.site = site

    @property
    def site(self):
        return self._site

    @site.setter
    def site(self, site):

        if isinstance(self._site, furl):
            self._site = site
        else:
            self._site = furl(site)

        if self._site.username:
            self.username = self._site.username

        if self._site.password:
            self.password = self._site.password

    @property
    def auth_type(self):
        return self._auth_type

    @auth_type.setter
    def auth_type(self, auth_type):
        if auth_type in ['basic', 'digest']:
            self._auth_type = auth_type
        else:
            raise ValueError("auth_type must be 'basic' or 'digest'")

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        if isinstance(timeout, (float, int, tuple)):
            self._timeout = timeout
        else:
            raise ValueError('timeout must be an instance of float, int or tuple')

    @property
    def open_timeout(self):
        return self._open_timeout

    @open_timeout.setter
    def open_timeout(self, open_timeout):
        if isinstance(open_timeout, (float, int)):
            self._open_timeout = open_timeout
        else:
            raise ValueError('open_timeout must be an instance of float or int')

    @property
    def read_timeout(self):
        return self._read_timeout

    @read_timeout.setter
    def read_timeout(self, read_timeout):
        if isinstance(read_timeout, (float, int)):
            self._read_timeout = read_timeout
        else:
            raise ValueError('read_timeout must be an instance of float')

    def get(self, path, **kwargs):
        return self._request('GET', path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request('DELETE', path, **kwargs)

    def patch(self, path, **kwargs):
        return self._request('PATCH', path, **kwargs)

    def put(self, path, **kwargs):
        return self._request('PUT', path, **kwargs)

    def post(self, path, **kwargs):
        return self._request('POST', path, **kwargs)

    def head(self, path, **kwargs):
        return self._request('HEAD', path, **kwargs)

    def _request(self, method, path, **kwargs):
        if self.username and self.password:
            if self._auth_type == 'basic':
                auth_class = requests.auth.HTTPBasicAuth
            if self._auth_type == 'digest':
                auth_class = requests.auth.HTTPDigestAuth

            kwargs['auth'] = auth_class(self.username, self.password)

        open_timeout = read_timeout = None

        if self._timeout is not None:
            if isinstance(self._timeout, tuple):
                (open_timeout, read_timeout) = self._timeout
            else:
                open_timeout = read_timeout = self._timeout

        if self._open_timeout is not None:
            open_timeout = self._open_timeout

        if self._read_timeout is not None:
            read_timeout = self._read_timeout

        if self.proxies:
            kwargs['proxies'] = self.proxies

        if open_timeout or read_timeout:
            kwargs['timeout'] = (open_timeout, read_timeout)

        url = self._site.join(path)
        response = requests.request(method, url, **kwargs)
        return response
