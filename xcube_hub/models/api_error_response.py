# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub.models.api_response import ApiResponse  # noqa: F401,E501
from xcube_hub import util


class ApiErrorResponse(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, message: str=None, output: object=None, traceback: object=None):  # noqa: E501
        """ApiErrorResponse - a model defined in Swagger

        :param message: The message of this ApiErrorResponse.  # noqa: E501
        :type message: str
        :param output: The output of this ApiErrorResponse.  # noqa: E501
        :type output: object
        :param traceback: The traceback of this ApiErrorResponse.  # noqa: E501
        :type traceback: object
        """
        self.swagger_types = {
            'message': str,
            'output': object,
            'traceback': object
        }

        self.attribute_map = {
            'message': 'message',
            'output': 'output',
            'traceback': 'traceback'
        }
        self._message = message
        self._output = output
        self._traceback = traceback

    @classmethod
    def from_dict(cls, dikt) -> 'ApiErrorResponse':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ApiErrorResponse of this ApiErrorResponse.  # noqa: E501
        :rtype: ApiErrorResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def message(self) -> str:
        """Gets the message of this ApiErrorResponse.


        :return: The message of this ApiErrorResponse.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this ApiErrorResponse.


        :param message: The message of this ApiErrorResponse.
        :type message: str
        """
        if message is None:
            raise ValueError("Invalid value for `message`, must not be `None`")  # noqa: E501

        self._message = message

    @property
    def output(self) -> object:
        """Gets the output of this ApiErrorResponse.


        :return: The output of this ApiErrorResponse.
        :rtype: object
        """
        return self._output

    @output.setter
    def output(self, output: object):
        """Sets the output of this ApiErrorResponse.


        :param output: The output of this ApiErrorResponse.
        :type output: object
        """

        self._output = output

    @property
    def traceback(self) -> object:
        """Gets the traceback of this ApiErrorResponse.


        :return: The traceback of this ApiErrorResponse.
        :rtype: object
        """
        return self._traceback

    @traceback.setter
    def traceback(self, traceback: object):
        """Sets the traceback of this ApiErrorResponse.


        :param traceback: The traceback of this ApiErrorResponse.
        :type traceback: object
        """

        self._traceback = traceback