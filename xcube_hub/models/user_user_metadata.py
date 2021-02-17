# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class UserUserMetadata(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, client_id=None, client_secret=None, punits=None):  # noqa: E501
        """UserUserMetadata - a model defined in OpenAPI

        :param client_id: The client_id of this UserUserMetadata.  # noqa: E501
        :type client_id: str
        :param client_secret: The client_secret of this UserUserMetadata.  # noqa: E501
        :type client_secret: str
        :param punits: The punits of this UserUserMetadata.  # noqa: E501
        :type punits: float
        """
        self.openapi_types = {
            'client_id': str,
            'client_secret': str,
            'punits': float
        }

        self.attribute_map = {
            'client_id': 'client_id',
            'client_secret': 'client_secret',
            'punits': 'punits'
        }

        self._client_id = client_id
        self._client_secret = client_secret
        self._punits = punits

    @classmethod
    def from_dict(cls, dikt) -> 'UserUserMetadata':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The User_user_metadata of this UserUserMetadata.  # noqa: E501
        :rtype: UserUserMetadata
        """
        return util.deserialize_model(dikt, cls)

    @property
    def client_id(self):
        """Gets the client_id of this UserUserMetadata.


        :return: The client_id of this UserUserMetadata.
        :rtype: str
        """
        return self._client_id

    @client_id.setter
    def client_id(self, client_id):
        """Sets the client_id of this UserUserMetadata.


        :param client_id: The client_id of this UserUserMetadata.
        :type client_id: str
        """

        self._client_id = client_id

    @property
    def client_secret(self):
        """Gets the client_secret of this UserUserMetadata.


        :return: The client_secret of this UserUserMetadata.
        :rtype: str
        """
        return self._client_secret

    @client_secret.setter
    def client_secret(self, client_secret):
        """Sets the client_secret of this UserUserMetadata.


        :param client_secret: The client_secret of this UserUserMetadata.
        :type client_secret: str
        """

        self._client_secret = client_secret

    @property
    def punits(self):
        """Gets the punits of this UserUserMetadata.


        :return: The punits of this UserUserMetadata.
        :rtype: float
        """
        return self._punits

    @punits.setter
    def punits(self, punits):
        """Sets the punits of this UserUserMetadata.


        :param punits: The punits of this UserUserMetadata.
        :type punits: float
        """

        self._punits = punits
