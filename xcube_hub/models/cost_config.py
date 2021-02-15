# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub import util
from xcube_hub.models.cubegen_config import CubeGenConfig
from xcube_hub.models.cubegen_config_cube_config import CubeGenConfigCubeConfig
from xcube_hub.models.cubegen_config_input_configs import CubeGenConfigInputConfigs
from xcube_hub.models.cubegen_config_output_config import CubeGenConfigOutputConfig


class CostConfig(CubeGenConfig):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, input_configs: List[CubeGenConfigInputConfigs] = None,
                 cube_config: CubeGenConfigCubeConfig = None,
                 output_config: CubeGenConfigOutputConfig = None):  # noqa: E501
        """CostConfig - a model defined in Swagger

        :param input_configs: The input_configs of this CubeGenConfig.  # noqa: E501
        :type input_configs: List[CubeGenConfigInputConfigs]
        :param cube_config: The cube_configs of this CubeGenConfig.  # noqa: E501
        :type cube_config: CubeGenConfigCubeConfig
        :param output_config: The output_config of this CubeGenConfig.  # noqa: E501
        :type output_config: CubeGenConfigOutputConfig
        """

        super().__init__(input_configs=input_configs, cube_config=cube_config, output_config=output_config)

    @classmethod
    def from_dict(cls, dikt) -> 'CostConfig':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CostConfig of this CostConfig.  # noqa: E501
        :rtype: CostConfig
        """
        return util.deserialize_model(dikt, cls)
