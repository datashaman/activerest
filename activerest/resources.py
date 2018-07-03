import inflection
import logging
import requests

from collections import namedtuple
from six.moves.urllib.parse import urlencode

log = logging.getLogger(__name__)


class Resource(object):
    def __init__(self, _meta=None, **attributes):
        instance_defaults = dict((k, v) for k, v in self.__class__.__dict__.items() if k != 'Meta' and k[0] != '_')

        self.__dict__.update(instance_defaults)
        self.__dict__.update(attributes)

        meta_defaults = {
            'persisted': False,
        }

        if _meta is None:
            _meta = {}
        self._meta = {}
        self._meta.update(meta_defaults)
        self._meta.update(_meta)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, str(' '.join('%s=%s' % (k, repr(v)) for k, v in self.__dict__.items() if k[0] != '_')))

    @property
    def attributes(self):
        return dict((k, v) for k, v in self.__dict__.items() if k[0] != '_')

    def primary_key(self):
        return self.__dict__[self.__class__.pk()]

    def is_new(self):
        return not self._meta['persisted']

    def is_persisted(self):
        return self._meta['persisted']

    def load(self, attributes):
        for k, v in attributes.items():
            if k[0] != '_':
                setattr(self, k, v)

    def update_attribute(self, name, value):
        setattr(self, name, value)
        return self.save()

    def update_attributes(self, attributes):
        self.load(attributes)
        return self.save()

    def save(self):
        if self.is_new():
            path = self.__class__.collection_path()
            method = 'POST'
        else:
            path = self.__class__.element_path(self.primary_key())
            method = 'PUT'

        data = self._transform_params(self.attributes)
        response = self.__class__._request(method, path, data=data)

        if (
            method == 'POST' and response.status_code == 201
            or method == 'PUT' and response.status_code == 200
        ):
            self._meta['persisted'] = True
            self.load(response.json())
            return True

        return False

    def destroy(self):
        if self.is_persisted() and self.__class__.delete(self.primary_key()):
            self._meta['persisted'] = False
            return True

        return False

    @classmethod
    def pk(cls):
        return getattr(cls.Meta, 'primary_key', 'id')

    @classmethod
    def all(cls):
        return cls.find()

    @classmethod
    def delete(cls, id):
        path = cls.element_path(id)
        response = cls._request('DELETE', path)
        return response.status_code == 200

    @classmethod
    def exists(cls, id):
        path = cls.element_path(id)
        response = cls._request('HEAD', path)
        return response.status_code == 200

    @classmethod
    def find(cls, id=None, params=None, **query_options):
        if id:
            path = cls.element_path(id)
        else:
            if params is None:
                params = {}
            path = cls.collection_path(**params)

        result = cls._request('GET', path).json()

        if id:
            if result:
                return cls(_meta={'persisted': True}, **result)
            return None

        if result:
            return [cls(_meta={'persisted': True}, **row) for row in result]

        return []

    @classmethod
    def _transform_params(cls, params):
        transformed = {}

        for key, value in params.items():
            if type(value) == bool:
                value = 'true' if value else 'false'

            transformed[key] = value

        return transformed

    @classmethod
    def collection_name(cls):
        if hasattr(cls.Meta, 'collection_name'):
            return cls.Meta.collection_name
        else:
            return inflection.dasherize(inflection.underscore(inflection.pluralize(cls.__name__)))

    @classmethod
    def query_string(cls, query_options=None):
        if query_options:
            query_options = cls._transform_params(query_options)
            return '?%s' % urlencode(query_options)
        return ''

    @classmethod
    def collection_path(cls, **query_options):
        return '/%s%s' % (cls.collection_name(), cls.query_string(query_options))

    @classmethod
    def element_path(cls, id, **query_options):
        return '/%s/%s%s' % (cls.collection_name(), id, cls.query_string(query_options))

    @classmethod
    def _request(cls, method, path, **kwargs):
        if hasattr(cls.Meta, 'auth_type'):
            if cls.Meta.auth_type == 'basic':
                auth_class = requests.auth.HTTPBasicAuth
            if cls.Meta.auth_type == 'digest':
                auth_class = requests.auth.HTTPDigestAuth

            kwargs['auth'] = auth_class(cls.Meta.user, cls.Meta.password)
        if hasattr(cls.Meta, 'timeout'):
            kwargs['timeout'] = cls.Meta.timeout
        url = '%s%s' % (cls.Meta.site, path)
        response = requests.request(method, url, **kwargs)
        return response
