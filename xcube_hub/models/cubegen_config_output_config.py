# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class CubegenConfigOutputConfig(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, store_id=None, store_params=None):  # noqa: E501
        """CubegenConfigOutputConfig - a model defined in OpenAPI

        :param store_id: The store_id of this CubegenConfigOutputConfig.  # noqa: E501
        :type store_id: str
        :param store_params: The store_params of this CubegenConfigOutputConfig.  # noqa: E501
        :type store_params: object
        """
        self.openapi_types = {
            'store_id': str,
            'store_params': object
        }

        self.attribute_map = {
            'store_id': 'store_id',
            'store_params': 'store_params'
        }

        self._store_id = store_id
        self._store_params = store_params

    @classmethod
    def from_dict(cls, dikt) -> 'CubegenConfigOutputConfig':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CubegenConfig_output_config of this CubegenConfigOutputConfig.  # noqa: E501
        :rtype: CubegenConfigOutputConfig
        """
        return util.deserialize_model(dikt, cls)

    @property
    def store_id(self):
        """Gets the store_id of this CubegenConfigOutputConfig.


        :return: The store_id of this CubegenConfigOutputConfig.
        :rtype: str
        """
        return self._store_id

    @store_id.setter
    def store_id(self, store_id):
        """Sets the store_id of this CubegenConfigOutputConfig.


        :param store_id: The store_id of this CubegenConfigOutputConfig.
        :type store_id: str
        """
        if store_id is None:
            raise ValueError("Invalid value for `store_id`, must not be `None`")  # noqa: E501

        self._store_id = store_id

    @property
    def store_params(self):
        """Gets the store_params of this CubegenConfigOutputConfig.


        :return: The store_params of this CubegenConfigOutputConfig.
        :rtype: object
        """
        return self._store_params

    @store_params.setter
    def store_params(self, store_params):
        """Sets the store_params of this CubegenConfigOutputConfig.


        :param store_params: The store_params of this CubegenConfigOutputConfig.
        :type store_params: object
        """
        if store_params is None:
            raise ValueError("Invalid value for `store_params`, must not be `None`")  # noqa: E501

        self._store_params = store_params
