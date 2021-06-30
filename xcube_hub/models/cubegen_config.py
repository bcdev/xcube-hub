# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub.models.cubegen_config_code_config import CubegenConfigCodeConfig
from xcube_hub import util

from xcube_hub.models.cubegen_config_cube_config import CubegenConfigCubeConfig  # noqa: E501
from xcube_hub.models.cubegen_config_input_configs import CubegenConfigInputConfigs  # noqa: E501
from xcube_hub.models.cubegen_config_output_config import CubegenConfigOutputConfig  # noqa: E501


class CubegenConfig(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, input_configs=None, cube_config=None, output_config=None, code_config=None):  # noqa: E501
        """CubegenConfig - a model defined in OpenAPI

        :param input_configs: The input_configs of this CubegenConfig.  # noqa: E501
        :type input_configs: List[CubegenConfigInputConfigs]
        :param cube_config: The cube_config of this CubegenConfig.  # noqa: E501
        :type cube_config: CubegenConfigCubeConfig
        :param output_config: The output_config of this CubegenConfig.  # noqa: E501
        :type output_config: CubegenConfigOutputConfig
        :param code_config: The code_config of this CubegenConfig.  # noqa: E501
        :type code_config: CubegenConfigCodeConfig
        """
        self.openapi_types = {
            'input_configs': List[CubegenConfigInputConfigs],
            'cube_config': CubegenConfigCubeConfig,
            'output_config': CubegenConfigOutputConfig,
            'code_config': CubegenConfigCodeConfig,
        }

        self.attribute_map = {
            'input_configs': 'input_configs',
            'cube_config': 'cube_config',
            'output_config': 'output_config',
            'code_config': 'code_config',
        }

        self._input_configs = input_configs
        self._cube_config = cube_config
        self._output_config = output_config
        self._code_config = code_config

    @classmethod
    def from_dict(cls, dikt) -> 'CubegenConfig':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CubegenConfig of this CubegenConfig.  # noqa: E501
        :rtype: CubegenConfig
        """
        return util.deserialize_model(dikt, cls)

    @property
    def input_configs(self):
        """Gets the input_configs of this CubegenConfig.


        :return: The input_configs of this CubegenConfig.
        :rtype: List[CubegenConfigInputConfigs]
        """
        return self._input_configs

    @input_configs.setter
    def input_configs(self, input_configs):
        """Sets the input_configs of this CubegenConfig.


        :param input_configs: The input_configs of this CubegenConfig.
        :type input_configs: List[CubegenConfigInputConfigs]
        """
        if input_configs is None:
            raise ValueError("Invalid value for `input_configs`, must not be `None`")  # noqa: E501

        self._input_configs = input_configs

    @property
    def cube_config(self):
        """Gets the cube_config of this CubegenConfig.


        :return: The cube_config of this CubegenConfig.
        :rtype: CubegenConfigCubeConfig
        """
        return self._cube_config

    @cube_config.setter
    def cube_config(self, cube_config):
        """Sets the cube_config of this CubegenConfig.


        :param cube_config: The cube_config of this CubegenConfig.
        :type cube_config: CubegenConfigCubeConfig
        """
        if cube_config is None:
            raise ValueError("Invalid value for `cube_config`, must not be `None`")  # noqa: E501

        self._cube_config = cube_config

    @property
    def output_config(self):
        """Gets the output_config of this CubegenConfig.


        :return: The output_config of this CubegenConfig.
        :rtype: CubegenConfigOutputConfig
        """
        return self._output_config

    @output_config.setter
    def output_config(self, output_config):
        """Sets the output_config of this CubegenConfig.


        :param output_config: The output_config of this CubegenConfig.
        :type output_config: CubegenConfigOutputConfig
        """
        if output_config is None:
            raise ValueError("Invalid value for `output_config`, must not be `None`")  # noqa: E501

        self._output_config = output_config

    @property
    def code_config(self):
        """Gets the code_config of this CubegenConfig.


        :return: The code_config of this CubegenConfig.
        :rtype: CubegenConfigCodeConfig
        """
        return self._code_config

    @code_config.setter
    def code_config(self, code_config):
        """Sets the code_config of this CubegenConfig.


        :param code_config: The code_config of this CubegenConfig.
        :type code_config: CubegenConfigCodeConfig
        """

        self._code_config = code_config
