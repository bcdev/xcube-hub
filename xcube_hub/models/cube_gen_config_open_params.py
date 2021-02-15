# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class CubeGenConfigOpenParams(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, tile_size: List[float]=None):  # noqa: E501
        """CubeGenConfigOpenParams - a model defined in Swagger

        :param tile_size: The tile_size of this CubeGenConfigOpenParams.  # noqa: E501
        :type tile_size: List[float]
        """
        self.swagger_types = {
            'tile_size': List[float]
        }

        self.attribute_map = {
            'tile_size': 'tile_size'
        }
        self._tile_size = tile_size

    @classmethod
    def from_dict(cls, dikt) -> 'CubeGenConfigOpenParams':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CubeGenConfig_open_params of this CubeGenConfigOpenParams.  # noqa: E501
        :rtype: CubeGenConfigOpenParams
        """
        return util.deserialize_model(dikt, cls)

    @property
    def tile_size(self) -> List[float]:
        """Gets the tile_size of this CubeGenConfigOpenParams.


        :return: The tile_size of this CubeGenConfigOpenParams.
        :rtype: List[float]
        """
        return self._tile_size

    @tile_size.setter
    def tile_size(self, tile_size: List[float]):
        """Sets the tile_size of this CubeGenConfigOpenParams.


        :param tile_size: The tile_size of this CubeGenConfigOpenParams.
        :type tile_size: List[float]
        """

        self._tile_size = tile_size