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

    def is_new(self):
        return not self._meta['persisted']

    def is_persisted(self):
        return self._meta['persisted']

    def save(self):
        if self.is_new():
            url = self.__class__.Meta.site
            method = 'POST'
        else:
            url = '%s/%s' % (self.__class__.Meta.site, self.id)
            method = 'PUT'

        data = self._transform_params(self.attributes)
        response = requests.request(method, url, data=data)

        if (
            method == 'POST' and response.status_code == 201
            or method == 'PUT' and response.status_code == 200
        ):
            self._meta['persisted'] = True
            self.__dict__.update(response.json())
            return True

        return False

    def destroy(self):
        if self.is_persisted() and self.__class__.delete(self.id):
            self._meta['persisted'] = False
            return True

        return False

    @classmethod
    def all(cls):
        return cls.find()

    @classmethod
    def delete(cls, id):
        url = '%s/%s' % (cls.Meta.site, id)
        response = requests.delete(url)
        return response.status_code == 200

    @classmethod
    def exists(cls, id):
        url = '%s/%s' % (cls.Meta.site, id)
        response = requests.head(url)
        return response.status_code == 200

    @classmethod
    def find(cls, id=None, params=None):
        result = cls._json(id, params)

        if id:
            if result:
                return cls(_meta={'persisted': True}, **result)
            return None

        if result:
            return [cls(_meta={'persisted': True}, **row) for row in result]

        return []

    @classmethod
    def _json(cls, id=None, params=None):
        if id:
            url = '%s/%s' % (cls.Meta.site, id)
        else:
            if params:
                params = cls._transform_params(params)
                url = '%s?%s' % (cls.Meta.site, urlencode(params))
            else:
                url = cls.Meta.site

        return requests.get(url).json()

    @classmethod
    def _transform_params(cls, params):
        transformed = {}

        for key, value in params.items():
            if type(value) == bool:
                value = 'true' if value else 'false'

            transformed[key] = value

        return transformed
