# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class Collection(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, collection_id=None, name=None, database=None, href=None, default_style=None, preview_url=None,
                 geojson_url=None, wfs_url=None):
        """Collection - a model defined in OpenAPI

        :param collection_id: The id of this Collection.  # noqa: E501
        :type collection_id: str
        :param name: The name of this Collection.  # noqa: E501
        :type name: str
        :param database: The database of this Collection.  # noqa: E501
        :type database: str
        :param href: The href of this Collection.  # noqa: E501
        :type href: str
        :param default_style: The default_style of this Collection.  # noqa: E501
        :type default_style: str
        :param preview_url: The preview_url of this Collection.  # noqa: E501
        :type preview_url: str
        :param geojson_url: The geojson_url of this Collection.  # noqa: E501
        :type geojson_url: str
        :param wfs_url: The wfs_url of this Collection.  # noqa: E501
        :type wfs_url: str
        """
        self.openapi_types = {
            'collection_id': str,
            'name': str,
            'database': str,
            'href': str,
            'default_style': str,
            'preview_url': str,
            'geojson_url': str,
            'wfs_url': str
        }

        self.attribute_map = {
            'collection_id': 'collection_id',
            'name': 'name',
            'database': 'database',
            'href': 'href',
            'default_style': 'default_style',
            'preview_url': 'preview_url',
            'geojson_url': 'geojson_url',
            'wfs_url': 'wfs_url'
        }

        self._collection_id = collection_id
        self._name = name
        self._database = database
        self._href = href
        self._default_style = default_style
        self._preview_url = preview_url
        self._geojson_url = geojson_url
        self._wfs_url = wfs_url

    @classmethod
    def from_dict(cls, dikt) -> 'Collection':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Collection of this Collection.  # noqa: E501
        :rtype: Collection
        """
        return util.deserialize_model(dikt, cls)

    @property
    def collection_id(self):
        """Gets the collection_id of this Collection.


        :return: The collection_id of this Collection.
        :rtype: str
        """
        return self._collection_id

    @collection_id.setter
    def collection_id(self, collection_id):
        """Sets the collection_id of this Collection.


        :param collection_id: The collection_id of this Collection.
        :type collection_id: str
        """

        self._collection_id = collection_id

    @property
    def name(self):
        """Gets the name of this Collection.


        :return: The name of this Collection.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Collection.


        :param name: The name of this Collection.
        :type name: str
        """

        self._name = name

    @property
    def database(self):
        """Gets the database of this Collection.


        :return: The database of this Collection.
        :rtype: str
        """
        return self._database

    @database.setter
    def database(self, database):
        """Sets the database of this Collection.


        :param database: The database of this Collection.
        :type database: str
        """
        if database is None:
            raise ValueError("Invalid value for `database`, must not be `None`")  # noqa: E501

        self._database = database

    @property
    def href(self):
        """Gets the href of this Collection.


        :return: The href of this Collection.
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this Collection.


        :param href: The href of this Collection.
        :type href: str
        """
        if href is None:
            raise ValueError("Invalid value for `href`, must not be `None`")  # noqa: E501

        self._href = href

    @property
    def default_style(self):
        """Gets the default_styleof this Collection.


        :return: The default_styleof this Collection.
        :rtype: str
        """
        return self._default_style

    @default_style.setter
    def default_style(self, default_style):
        """Sets the default_styleof this Collection.


        :param default_style: The default_styleof this Collection.
        :type default_style: str
        """

        self._default_style= default_style

    @property
    def preview_url(self):
        """Gets the preview_url of this Collection.


        :return: The preview_url of this Collection.
        :rtype: str
        """
        return self._preview_url

    @preview_url.setter
    def preview_url(self, preview_url):
        """Sets the preview_url of this Collection.


        :param preview_url: The preview_url of this Collection.
        :type preview_url: str
        """

        self._preview_url = preview_url

    @property
    def geojson_url(self):
        """Gets the geojson_url of this Collection.


        :return: The geojson_url of this Collection.
        :rtype: str
        """
        return self._geojson_url

    @geojson_url.setter
    def geojson_url(self, geojson_url):
        """Sets the layer of this Collection.


        :param geojson_url: The geojson_url of this Collection.
        :type geojson_url: str
        """

        self._geojson_url = geojson_url

    @property
    def wfs_url(self):
        """Gets the wfs_url of this Collection.


        :return: The wfs_url of this Collection.
        :rtype: str
        """
        return self._wfs_url

    @wfs_url.setter
    def wfs_url(self, wfs_url):
        """Sets the layer of this Collection.


        :param wfs_url: The wfs_url of this Collection.
        :type wfs_url: str
        """

        self._wfs_url = wfs_url
