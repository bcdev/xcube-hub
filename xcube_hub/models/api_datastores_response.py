# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub.models.api_datastores_response_all_of import ApiDatastoresResponseAllOf
from xcube_hub.models.api_response import ApiResponse
from xcube_hub.models.datastore import Datastore
from xcube_hub import util

from xcube_hub.models.api_datastores_response_all_of import ApiDatastoresResponseAllOf  # noqa: E501
from xcube_hub.models.api_response import ApiResponse  # noqa: E501
from xcube_hub.models.datastore import Datastore  # noqa: E501

class ApiDatastoresResponse(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, message=None, output=None, result=None):  # noqa: E501
        """ApiDatastoresResponse - a model defined in OpenAPI

        :param message: The message of this ApiDatastoresResponse.  # noqa: E501
        :type message: str
        :param output: The output of this ApiDatastoresResponse.  # noqa: E501
        :type output: object
        :param result: The result of this ApiDatastoresResponse.  # noqa: E501
        :type result: Datastore
        """
        self.openapi_types = {
            'message': str,
            'output': object,
            'result': Datastore
        }

        self.attribute_map = {
            'message': 'message',
            'output': 'output',
            'result': 'result'
        }

        self._message = message
        self._output = output
        self._result = result

    @classmethod
    def from_dict(cls, dikt) -> 'ApiDatastoresResponse':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ApiDatastoresResponse of this ApiDatastoresResponse.  # noqa: E501
        :rtype: ApiDatastoresResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def message(self):
        """Gets the message of this ApiDatastoresResponse.


        :return: The message of this ApiDatastoresResponse.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this ApiDatastoresResponse.


        :param message: The message of this ApiDatastoresResponse.
        :type message: str
        """
        if message is None:
            raise ValueError("Invalid value for `message`, must not be `None`")  # noqa: E501

        self._message = message

    @property
    def output(self):
        """Gets the output of this ApiDatastoresResponse.


        :return: The output of this ApiDatastoresResponse.
        :rtype: object
        """
        return self._output

    @output.setter
    def output(self, output):
        """Sets the output of this ApiDatastoresResponse.


        :param output: The output of this ApiDatastoresResponse.
        :type output: object
        """

        self._output = output

    @property
    def result(self):
        """Gets the result of this ApiDatastoresResponse.


        :return: The result of this ApiDatastoresResponse.
        :rtype: Datastore
        """
        return self._result

    @result.setter
    def result(self, result):
        """Sets the result of this ApiDatastoresResponse.


        :param result: The result of this ApiDatastoresResponse.
        :type result: Datastore
        """
        if result is None:
            raise ValueError("Invalid value for `result`, must not be `None`")  # noqa: E501

        self._result = result
