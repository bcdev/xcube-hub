# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class CubeGenConfigOutputConfig(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, store_id: str=None, store_params: object=None):  # noqa: E501
        """CubeGenConfigOutputConfig - a model defined in Swagger

        :param store_id: The store_id of this CubeGenConfigOutputConfig.  # noqa: E501
        :type store_id: str
        :param store_params: The store_params of this CubeGenConfigOutputConfig.  # noqa: E501
        :type store_params: object
        """
        self.swagger_types = {
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
    def from_dict(cls, dikt) -> 'CubeGenConfigOutputConfig':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CubeGenConfig_output_config of this CubeGenConfigOutputConfig.  # noqa: E501
        :rtype: CubeGenConfigOutputConfig
        """
        return util.deserialize_model(dikt, cls)

    @property
    def store_id(self) -> str:
        """Gets the store_id of this CubeGenConfigOutputConfig.


        :return: The store_id of this CubeGenConfigOutputConfig.
        :rtype: str
        """
        return self._store_id

    @store_id.setter
    def store_id(self, store_id: str):
        """Sets the store_id of this CubeGenConfigOutputConfig.


        :param store_id: The store_id of this CubeGenConfigOutputConfig.
        :type store_id: str
        """
        if store_id is None:
            raise ValueError("Invalid value for `store_id`, must not be `None`")  # noqa: E501

        self._store_id = store_id

    @property
    def store_params(self) -> object:
        """Gets the store_params of this CubeGenConfigOutputConfig.


        :return: The store_params of this CubeGenConfigOutputConfig.
        :rtype: object
        """
        return self._store_params

    @store_params.setter
    def store_params(self, store_params: object):
        """Sets the store_params of this CubeGenConfigOutputConfig.


        :param store_params: The store_params of this CubeGenConfigOutputConfig.
        :type store_params: object
        """
        if store_params is None:
            raise ValueError("Invalid value for `store_params`, must not be `None`")  # noqa: E501

        self._store_params = store_params
