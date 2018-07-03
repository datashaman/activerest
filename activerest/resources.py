"""
Python REST client, modeled on Ruby on Rails' ActiveResource
"""

import requests
import inflection

from six.moves.urllib.parse import urlencode


class Resource(object):
    def __init__(self, _meta=None, **attributes):
        instance_defaults = {}

        for key, value in self.__class__.__dict__.items():
            if key != 'Meta' and key[0] != '_':
                instance_defaults[key] = value

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
        parts = {}

        for key, value in self.__dict__.items():
            if key[0] != '_':
                parts[key] = repr(value)

        string = ' '.join(['%s=%s' % (key, value) for key, value in parts.items()])

        return '%s(%s)' % (self.__class__.__name__, string)


    @property
    def attributes(self):
        """Attributes on the resource."""
        return dict((k, v) for k, v in self.__dict__.items() if k[0] != '_')

    def primary_key(self):
        """The primary key value."""
        return self.__dict__[self.__class__.pk()]

    def is_new(self):
        """Is the resource new, ie unsaved."""
        return not self._meta['persisted']

    def is_persisted(self):
        """Is the resource persisted, ie saved."""
        return self._meta['persisted']

    def load(self, attributes):
        """Set the attributes on the resource."""
        for key, value in attributes.items():
            if key[0] != '_':
                setattr(self, key, value)

    def update_attribute(self, name, value):
        """Update a single attribute and save the resource."""
        setattr(self, name, value)
        return self.save()

    def update_attributes(self, attributes):
        """Update a dictionary of attributes and save the resource."""
        self.load(attributes)
        return self.save()

    def save(self):
        """Save the resource by calling the API."""
        if self.is_new():
            path = self.__class__.collection_path()
            method = 'POST'
        else:
            path = self.__class__.element_path(self.primary_key())
            method = 'PUT'

        data = self._transform_params(self.attributes)
        response = self.__class__.request(method, path, data=data)

        if (method == 'POST' and response.status_code == 201
                or method == 'PUT' and response.status_code == 200):
            self._meta['persisted'] = True
            self.load(response.json())
            return True

        return False

    def destroy(self):
        """Delete the resource by calling the API."""
        if self.is_persisted() and self.__class__.delete(self.primary_key()):
            self._meta['persisted'] = False
            return True

        return False

    @classmethod
    def pk(cls):
        """Name of the primary key attribute."""
        return getattr(cls.Meta, 'primary_key', 'id')

    @classmethod
    def all(cls):
        """Return all resources from the API."""
        return cls.find()

    @classmethod
    def delete(cls, identifier):
        """Delete a single resource by identifier."""
        path = cls.element_path(identifier)
        response = cls.request('DELETE', path)
        return response.status_code == 200

    @classmethod
    def exists(cls, identifier):
        """Check if a single resource exists by identifier."""
        path = cls.element_path(identifier)
        response = cls.request('HEAD', path)
        return response.status_code == 200

    @classmethod
    def find(cls, identifier=None, params=None):
        """Find resources by ID or by query options."""
        if identifier:
            path = cls.element_path(identifier)
        else:
            if params is None:
                params = {}
            path = cls.collection_path(**params)

        result = cls.request('GET', path).json()

        if identifier:
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
            if isinstance(value, bool):
                value = 'true' if value else 'false'

            transformed[key] = value

        return transformed

    @classmethod
    def collection_name(cls):
        """Collection name used in generating collection path."""
        if hasattr(cls.Meta, 'collection_name'):
            return cls.Meta.collection_name

        return inflection.dasherize(inflection.underscore(inflection.pluralize(cls.__name__)))

    @classmethod
    def query_string(cls, query_options=None):
        """Generate query string from query options."""
        if query_options:
            query_options = cls._transform_params(query_options)
            return '?%s' % urlencode(query_options)
        return ''

    @classmethod
    def collection_path(cls, **query_options):
        """Path to the collection API endpoint."""
        return '/%s%s' % (cls.collection_name(), cls.query_string(query_options))

    @classmethod
    def element_path(cls, identifier, **query_options):
        """Path to the element API endpoint."""
        return '/%s/%s%s' % (cls.collection_name(), identifier, cls.query_string(query_options))

    @classmethod
    def request(cls, method, path, **kwargs):
        """Request an API endpoint."""
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
