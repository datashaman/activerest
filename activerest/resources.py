"""
Python REST client, modeled on Ruby on Rails' ActiveResource
"""
from __future__ import absolute_import

from future.standard_library import install_aliases
from future.utils import viewitems
install_aliases()

import requests
import inflection

from activerest.connections import Connection
from furl import furl
from six import with_metaclass
from urllib.parse import urlencode


CONNECTION_ATTRIBUTES = [
    'auth_type',
    'open_timeout',
    'password',
    'proxies',
    'read_timeout',
    'timeout',
    'username',
]

META_ATTRIBUTES = {
    'auth_type': {
        'reset_connection': True,
    },
    'collection_name': {
        'default': lambda cls: inflection.pluralize(cls.element_name)
    },
    'connection_class': {
        'reset_connection': True,
        'default': lambda cls: Connection
    },
    'element_name': {
        'default': lambda cls: inflection.dasherize(inflection.underscore(cls.__name__))
    },
    'open_timeout': {
        'reset_connection': True,
    },
    'password': {
        'reset_connection': True,
    },
    'proxies': {
        'reset_connection': True,
    },
    'read_timeout': {
        'reset_connection': True,
    },
    'timeout': {
        'reset_connection': True,
    },
    'username': {
        'reset_connection': True,
    },
}


class MetaResource(type):
    _attributes = {}
    _connections = {}

    def __init__(cls, name, bases, dct):
        super(MetaResource, cls).__init__(name, bases, dct)
        for attr in META_ATTRIBUTES:
            if attr in dct:
                value = dct[attr]
                setattr(cls, attr, value)

    def __getattribute__(cls, attr):
        if attr in META_ATTRIBUTES:
            cls_id = id(cls)
            if cls_id not in cls._attributes:
                cls._attributes[cls_id] = {}
            attributes = cls._attributes[cls_id]
            if attr not in attributes:
                default = META_ATTRIBUTES[attr].get('default', lambda cls: None)
                setattr(cls, attr, default(cls))
            return attributes[attr]
        return super(MetaResource, cls).__getattribute__(attr)

    def __setattr__(cls, attr, value):
        if attr in META_ATTRIBUTES:
            cls_id = id(cls)
            if cls_id not in cls._connections \
                    or META_ATTRIBUTES[attr].get('reset_connection', False):
                cls._connections[cls_id] = None
            if cls_id not in cls._attributes:
                cls._attributes[cls_id] = {}
            attributes = cls._attributes[cls_id]
            attributes[attr] = value
        else:
            super(MetaResource, cls).__setattr__(attr, value)


class Resource(with_metaclass(MetaResource, object)):
    def __init__(self, _meta=None, **attributes):
        cls = type(self)

        if not hasattr(cls, 'site'):
            raise ValueError('resource must have site defined')

        if not isinstance(cls.site, furl):
            cls.site = furl(cls.site)

        self.__dict__.update(attributes)

        self._meta = {
            'persisted': False,
        }

        if _meta is not None:
            self._meta.update(_meta)

    def __repr__(self):
        parts = []

        for (key, value) in viewitems(self.__dict__):
            if key[0] != '_':
                parts.append('%s=%s' % (key, repr(value)))

        return '%s(%s)' % (type(self).__name__, ', '.join(parts))

    @property
    def attributes(self):
        """Attributes on the resource."""
        return dict((key, value) for (key, value) in viewitems(self.__dict__) if key[0] != '_')

    def primary_key(self):
        """The primary key value."""
        return self.__dict__[self.pk()]

    def is_new(self):
        """Is the resource new, ie unsaved."""
        return not self._meta['persisted']

    def is_persisted(self):
        """Is the resource persisted, ie saved."""
        return self._meta['persisted']

    def load(self, attributes):
        """Set the attributes on the resource."""
        for (key, value) in viewitems(attributes):
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
        data = self._transform_params(self.attributes)

        if self.is_new():
            path = self.collection_path()
            response = self.connection().post(path, data=data)
        else:
            path = self.element_path(self.primary_key())
            response = self.connection().put(path, data=data)

        if response.status_code in [200, 201]:
            self._meta['persisted'] = True
            self.load(response.json())
            return True

        return False

    def destroy(self):
        """Delete the resource by calling the API."""
        if self.is_persisted() and self.delete(self.primary_key()):
            self._meta['persisted'] = False
            return True

        return False

    @classmethod
    def connection(cls, refresh=False):
        cls_id = id(cls)
        if cls_id not in cls._connections \
                or cls._connections[cls_id] is None \
                or refresh:
            connection = cls.connection_class(cls.site)
            for attr in CONNECTION_ATTRIBUTES:
                value = getattr(cls, attr, None)
                if value:
                    setattr(connection, attr, value)
            cls._connections[cls_id] = connection
        return cls._connections[cls_id]

    @classmethod
    def pk(cls):
        """Name of the primary key attribute."""
        return getattr(cls, '_primary_key', 'id')

    @classmethod
    def all(cls):
        """Return all resources from the API."""
        return cls.find()

    @classmethod
    def delete(cls, identifier):
        """Delete a single resource by identifier."""
        path = cls.element_path(identifier)
        response = cls.connection().delete(path)
        return response.status_code == 200

    @classmethod
    def exists(cls, identifier):
        """Check if a single resource exists by identifier."""
        path = cls.element_path(identifier)
        response = cls.connection().head(path)
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

        result = cls.connection().get(path)

        if identifier:
            if result.status_code == 404:
                return None
            if result.status_code == 200:
                return cls(_meta={'persisted': True}, **result.json())

        if result.status_code == 200:
            return [cls(_meta={'persisted': True}, **row) for row in result.json()]

        result.raise_for_status()

    @classmethod
    def _transform_params(cls, params):
        transformed = {}

        for (key, value) in viewitems(params):
            if isinstance(value, bool):
                value = 'true' if value else 'false'

            transformed[key] = value

        return transformed

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
        return '/%s%s' % (cls.collection_name, cls.query_string(query_options))

    @classmethod
    def element_path(cls, identifier, **query_options):
        """Path to the element API endpoint."""
        return '/%s/%s%s' % (cls.collection_name, identifier, cls.query_string(query_options))
