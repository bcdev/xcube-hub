# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class Callback(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, status: str=None, message: str=None, values: object=None, total_work: float=None, worked: float=None):  # noqa: E501
        """Callback - a model defined in Swagger

        :param status: The status of this Callback.  # noqa: E501
        :type status: str
        :param message: The message of this Callback.  # noqa: E501
        :type message: str
        :param values: The values of this Callback.  # noqa: E501
        :type values: object
        :param total_work: The total_work of this Callback.  # noqa: E501
        :type total_work: float
        :param worked: The worked of this Callback.  # noqa: E501
        :type worked: float
        """
        self.swagger_types = {
            'status': str,
            'message': str,
            'values': object,
            'total_work': float,
            'worked': float
        }

        self.attribute_map = {
            'status': 'status',
            'message': 'message',
            'values': 'values',
            'total_work': 'total_work',
            'worked': 'worked'
        }
        self._status = status
        self._message = message
        self._values = values
        self._total_work = total_work
        self._worked = worked

    @classmethod
    def from_dict(cls, dikt) -> 'Callback':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Callback of this Callback.  # noqa: E501
        :rtype: Callback
        """
        return util.deserialize_model(dikt, cls)

    @property
    def status(self) -> str:
        """Gets the status of this Callback.


        :return: The status of this Callback.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status: str):
        """Sets the status of this Callback.


        :param status: The status of this Callback.
        :type status: str
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501

        self._status = status

    @property
    def message(self) -> str:
        """Gets the message of this Callback.


        :return: The message of this Callback.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this Callback.


        :param message: The message of this Callback.
        :type message: str
        """
        if message is None:
            raise ValueError("Invalid value for `message`, must not be `None`")  # noqa: E501

        self._message = message

    @property
    def values(self) -> object:
        """Gets the values of this Callback.


        :return: The values of this Callback.
        :rtype: object
        """
        return self._values

    @values.setter
    def values(self, values: object):
        """Sets the values of this Callback.


        :param values: The values of this Callback.
        :type values: object
        """

        self._values = values

    @property
    def total_work(self) -> float:
        """Gets the total_work of this Callback.


        :return: The total_work of this Callback.
        :rtype: float
        """
        return self._total_work

    @total_work.setter
    def total_work(self, total_work: float):
        """Sets the total_work of this Callback.


        :param total_work: The total_work of this Callback.
        :type total_work: float
        """

        self._total_work = total_work

    @property
    def worked(self) -> float:
        """Gets the worked of this Callback.


        :return: The worked of this Callback.
        :rtype: float
        """
        return self._worked

    @worked.setter
    def worked(self, worked: float):
        """Sets the worked of this Callback.


        :param worked: The worked of this Callback.
        :type worked: float
        """

        self._worked = worked