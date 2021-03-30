# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util
from xcube_hub.models.subscription import Subscription


class UserUserMetadata(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
    Do not edit the class manually.
    """

    def __init__(self, client_id=None, client_secret=None, subscriptions=None):
        """UserUserMetadata - a model defined in OpenAPI
        :param client_id: The client_id of this UserUserMetadata.  # noqa: E501
        :type client_id: str
        :param client_secret: The client_secret of this UserUserMetadata.  # noqa: E501
        :type client_secret: str
        """
        self.openapi_types = {
            'client_id': str,
            'client_secret': str,
            'subscriptions': Dict[str, Subscription]
        }

        self.attribute_map = {
            'client_id': 'client_id',
            'client_secret': 'client_secret',
            'subscriptions': 'subscriptions',
        }

        self._client_id = client_id
        self._client_secret = client_secret
        self._subscriptions = subscriptions

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
    def subscriptions(self):
        """Gets the subscriptions of this UserUserMetadata.
        :return: The subscriptions of this UserUserMetadata.
        :rtype: float
        """
        return self._subscriptions

    @subscriptions.setter
    def subscriptions(self, subscriptions):
        """Sets the subscriptions of this UserUserMetadata.
        :param subscriptions: The punits of this UserUserMetadata.
        :type subscriptions: float
        """

        self._subscriptions = subscriptions
