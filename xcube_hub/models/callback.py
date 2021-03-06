# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class Callback(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, state=None, sender=None):
        """Callback - a model defined in OpenAPI

        :param state: The state of this Callback.  # noqa: E501
        :type state: object
        :param sender: The state of this Callback.  # noqa: E501
        :type sender: str
        """
        self.openapi_types = {
            'state': object,
            'sender': str,
        }

        self.attribute_map = {
            'state': 'state',
            'sender': 'sender',
        }

        self._state = state
        self._sender = sender

    @classmethod
    def from_dict(cls, dikt) -> 'Callback':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Callback of this Callback.  # noqa: E501
        :rtype: Callback
        """
        return util.deserialize_model(dikt, cls)

    @property
    def state(self):
        """Gets the state of this Callback.


        :return: The state of this Callback.
        :rtype: object
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this Callback.


        :param state: The state of this Callback.
        :type state: object
        """
        if state is None:
            raise ValueError("Invalid value for `state`, must not be `None`")  # noqa: E501

        self._state = state

    @property
    def sender(self):
        """Gets the state of this Callback.


        :return: The state of this Callback.
        :rtype: str
        """
        return self._sender

    @sender.setter
    def sender(self, sender):
        """Sets the state of this Callback.


        :param sender: The state of this Callback.
        :type sender: str
        """
        if sender is None:
            raise ValueError("Invalid value for `sender`, must not be `None`")  # noqa: E501

        self._sender = sender
