# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub.models.api_response import ApiResponse  # noqa: F401,E501
from xcube_hub.models.user import User  # noqa: F401,E501
from xcube_hub import util


class ApiUserResponse(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, message: str = None, output: object = None, result: User = None):  # noqa: E501
        """ApiUserResponse - a model defined in Swagger

        :param message: The message of this ApiUserResponse.  # noqa: E501
        :type message: str
        :param output: The output of this ApiUserResponse.  # noqa: E501
        :type output: object
        :param result: The result of this ApiUserResponse.  # noqa: E501
        :type result: User
        """
        self.swagger_types = {
            'message': str,
            'output': object,
            'result': User
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
    def from_dict(cls, dikt) -> 'ApiUserResponse':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ApiUserResponse of this ApiUserResponse.  # noqa: E501
        :rtype: ApiUserResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def message(self) -> str:
        """Gets the message of this ApiUserResponse.


        :return: The message of this ApiUserResponse.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this ApiUserResponse.


        :param message: The message of this ApiUserResponse.
        :type message: str
        """
        if message is None:
            raise ValueError("Invalid value for `message`, must not be `None`")  # noqa: E501

        self._message = message

    @property
    def output(self) -> object:
        """Gets the output of this ApiUserResponse.


        :return: The output of this ApiUserResponse.
        :rtype: object
        """
        return self._output

    @output.setter
    def output(self, output: object):
        """Sets the output of this ApiUserResponse.


        :param output: The output of this ApiUserResponse.
        :type output: object
        """

        self._output = output

    @property
    def result(self) -> User:
        """Gets the result of this ApiUserResponse.


        :return: The result of this ApiUserResponse.
        :rtype: User
        """
        return self._result

    @result.setter
    def result(self, result: User):
        """Sets the result of this ApiUserResponse.


        :param result: The result of this ApiUserResponse.
        :type result: User
        """
        if result is None:
            raise ValueError("Invalid value for `result`, must not be `None`")  # noqa: E501

        self._result = result
