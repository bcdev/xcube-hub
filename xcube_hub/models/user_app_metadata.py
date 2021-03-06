# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class UserAppMetadata(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
    Do not edit the class manually.
    """

    def __init__(self, geodb_role=None):  # noqa: E501
        """UserAppMetadata - a model defined in OpenAPI
        :param geodb_role: The geodb_role of this UserAppMetadata.  # noqa: E501
        :type geodb_role: str
        """
        self.openapi_types = {
            'geodb_role': str
        }

        self.attribute_map = {
            'geodb_role': 'geodb_role'
        }

        self._geodb_role = geodb_role

    @classmethod
    def from_dict(cls, dikt) -> 'UserAppMetadata':
        """Returns the dict as a model
        :param dikt: A dict.
        :type: dict
        :return: The User_app_metadata of this UserAppMetadata.  # noqa: E501
        :rtype: UserAppMetadata
        """
        return util.deserialize_model(dikt, cls)

    @property
    def geodb_role(self):
        """Gets the geodb_role of this UserAppMetadata.
        :return: The geodb_role of this UserAppMetadata.
        :rtype: str
        """
        return self._geodb_role

    @geodb_role.setter
    def geodb_role(self, geodb_role):
        """Sets the geodb_role of this UserAppMetadata.
        :param geodb_role: The geodb_role of this UserAppMetadata.
        :type geodb_role: str
        """

        self._geodb_role = geodb_role
