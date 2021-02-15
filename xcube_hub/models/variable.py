# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class Variable(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, id: str = None, name: str = None, units: str = None, dtype: str = None,
                 spatial_res: float = None, temporal_res: str = None, description: str = None):  # noqa: E501
        """Variable - a model defined in Swagger

        :param id: The id of this Variable.  # noqa: E501
        :type id: str
        :param name: The name of this Variable.  # noqa: E501
        :type name: str
        :param units: The units of this Variable.  # noqa: E501
        :type units: str
        :param dtype: The dtype of this Variable.  # noqa: E501
        :type dtype: str
        :param spatial_res: The spatial_res of this Variable.  # noqa: E501
        :type spatial_res: float
        :param temporal_res: The temporal_res of this Variable.  # noqa: E501
        :type temporal_res: str
        :param description: The description of this Variable.  # noqa: E501
        :type description: str
        """
        self.swagger_types = {
            'id': str,
            'name': str,
            'units': str,
            'dtype': str,
            'spatial_res': float,
            'temporal_res': str,
            'description': str
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'units': 'units',
            'dtype': 'dtype',
            'spatial_res': 'spatialRes',
            'temporal_res': 'temporalRes',
            'description': 'description'
        }
        self._id = id
        self._name = name
        self._units = units
        self._dtype = dtype
        self._spatial_res = spatial_res
        self._temporal_res = temporal_res
        self._description = description

    @classmethod
    def from_dict(cls, dikt) -> 'Variable':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Variable of this Variable.  # noqa: E501
        :rtype: Variable
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """Gets the id of this Variable.


        :return: The id of this Variable.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this Variable.


        :param id: The id of this Variable.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def name(self) -> str:
        """Gets the name of this Variable.


        :return: The name of this Variable.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Variable.


        :param name: The name of this Variable.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def units(self) -> str:
        """Gets the units of this Variable.


        :return: The units of this Variable.
        :rtype: str
        """
        return self._units

    @units.setter
    def units(self, units: str):
        """Sets the units of this Variable.


        :param units: The units of this Variable.
        :type units: str
        """
        if units is None:
            raise ValueError("Invalid value for `units`, must not be `None`")  # noqa: E501

        self._units = units

    @property
    def dtype(self) -> str:
        """Gets the dtype of this Variable.


        :return: The dtype of this Variable.
        :rtype: str
        """
        return self._dtype

    @dtype.setter
    def dtype(self, dtype: str):
        """Sets the dtype of this Variable.


        :param dtype: The dtype of this Variable.
        :type dtype: str
        """
        if dtype is None:
            raise ValueError("Invalid value for `dtype`, must not be `None`")  # noqa: E501

        self._dtype = dtype

    @property
    def spatial_res(self) -> float:
        """Gets the spatial_res of this Variable.


        :return: The spatial_res of this Variable.
        :rtype: float
        """
        return self._spatial_res

    @spatial_res.setter
    def spatial_res(self, spatial_res: float):
        """Sets the spatial_res of this Variable.


        :param spatial_res: The spatial_res of this Variable.
        :type spatial_res: float
        """
        if spatial_res is None:
            raise ValueError("Invalid value for `spatial_res`, must not be `None`")  # noqa: E501

        self._spatial_res = spatial_res

    @property
    def temporal_res(self) -> str:
        """Gets the temporal_res of this Variable.


        :return: The temporal_res of this Variable.
        :rtype: str
        """
        return self._temporal_res

    @temporal_res.setter
    def temporal_res(self, temporal_res: str):
        """Sets the temporal_res of this Variable.


        :param temporal_res: The temporal_res of this Variable.
        :type temporal_res: str
        """
        if temporal_res is None:
            raise ValueError("Invalid value for `temporal_res`, must not be `None`")  # noqa: E501

        self._temporal_res = temporal_res

    @property
    def description(self) -> str:
        """Gets the description of this Variable.


        :return: The description of this Variable.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this Variable.


        :param description: The description of this Variable.
        :type description: str
        """
        if description is None:
            raise ValueError("Invalid value for `description`, must not be `None`")  # noqa: E501

        self._description = description
