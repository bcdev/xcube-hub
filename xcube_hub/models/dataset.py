# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub.models.variable import Variable
from xcube_hub import util

from xcube_hub.models.variable import Variable  # noqa: E501

class Dataset(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, name=None, variables=None):  # noqa: E501
        """Dataset - a model defined in OpenAPI

        :param id: The id of this Dataset.  # noqa: E501
        :type id: str
        :param name: The name of this Dataset.  # noqa: E501
        :type name: str
        :param variables: The variables of this Dataset.  # noqa: E501
        :type variables: List[Variable]
        """
        self.openapi_types = {
            'id': str,
            'name': str,
            'variables': List[Variable]
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'variables': 'variables'
        }

        self._id = id
        self._name = name
        self._variables = variables

    @classmethod
    def from_dict(cls, dikt) -> 'Dataset':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Dataset of this Dataset.  # noqa: E501
        :rtype: Dataset
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this Dataset.


        :return: The id of this Dataset.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Dataset.


        :param id: The id of this Dataset.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def name(self):
        """Gets the name of this Dataset.


        :return: The name of this Dataset.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Dataset.


        :param name: The name of this Dataset.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def variables(self):
        """Gets the variables of this Dataset.


        :return: The variables of this Dataset.
        :rtype: List[Variable]
        """
        return self._variables

    @variables.setter
    def variables(self, variables):
        """Sets the variables of this Dataset.


        :param variables: The variables of this Dataset.
        :type variables: List[Variable]
        """
        if variables is None:
            raise ValueError("Invalid value for `variables`, must not be `None`")  # noqa: E501

        self._variables = variables
