# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class ServiceInformation(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, name: str=None, description: str=None, version: str=None, server_start_time: datetime=None, server_current_time: datetime=None, server_pid: int=None, chart_version: str=None, mock_services: str=None, run_local: bool=None):  # noqa: E501
        """ServiceInformation - a model defined in Swagger

        :param name: The name of this ServiceInformation.  # noqa: E501
        :type name: str
        :param description: The description of this ServiceInformation.  # noqa: E501
        :type description: str
        :param version: The version of this ServiceInformation.  # noqa: E501
        :type version: str
        :param server_start_time: The server_start_time of this ServiceInformation.  # noqa: E501
        :type server_start_time: datetime
        :param server_current_time: The server_current_time of this ServiceInformation.  # noqa: E501
        :type server_current_time: datetime
        :param server_pid: The server_pid of this ServiceInformation.  # noqa: E501
        :type server_pid: int
        :param chart_version: The chart_version of this ServiceInformation.  # noqa: E501
        :type chart_version: str
        :param mock_services: The mock_services of this ServiceInformation.  # noqa: E501
        :type mock_services: str
        :param run_local: The run_local of this ServiceInformation.  # noqa: E501
        :type run_local: bool
        """
        self.swagger_types = {
            'name': str,
            'description': str,
            'version': str,
            'server_start_time': datetime,
            'server_current_time': datetime,
            'server_pid': int,
            'chart_version': str,
            'mock_services': str,
            'run_local': bool
        }

        self.attribute_map = {
            'name': 'name',
            'description': 'description',
            'version': 'version',
            'server_start_time': 'serverStartTime',
            'server_current_time': 'serverCurrentTime',
            'server_pid': 'serverPID',
            'chart_version': 'chartVersion',
            'mock_services': 'mockServices',
            'run_local': 'runLocal'
        }
        self._name = name
        self._description = description
        self._version = version
        self._server_start_time = server_start_time
        self._server_current_time = server_current_time
        self._server_pid = server_pid
        self._chart_version = chart_version
        self._mock_services = mock_services
        self._run_local = run_local

    @classmethod
    def from_dict(cls, dikt) -> 'ServiceInformation':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ServiceInformation of this ServiceInformation.  # noqa: E501
        :rtype: ServiceInformation
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self) -> str:
        """Gets the name of this ServiceInformation.


        :return: The name of this ServiceInformation.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this ServiceInformation.


        :param name: The name of this ServiceInformation.
        :type name: str
        """

        self._name = name

    @property
    def description(self) -> str:
        """Gets the description of this ServiceInformation.


        :return: The description of this ServiceInformation.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this ServiceInformation.


        :param description: The description of this ServiceInformation.
        :type description: str
        """

        self._description = description

    @property
    def version(self) -> str:
        """Gets the version of this ServiceInformation.


        :return: The version of this ServiceInformation.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version: str):
        """Sets the version of this ServiceInformation.


        :param version: The version of this ServiceInformation.
        :type version: str
        """

        self._version = version

    @property
    def server_start_time(self) -> datetime:
        """Gets the server_start_time of this ServiceInformation.


        :return: The server_start_time of this ServiceInformation.
        :rtype: datetime
        """
        return self._server_start_time

    @server_start_time.setter
    def server_start_time(self, server_start_time: datetime):
        """Sets the server_start_time of this ServiceInformation.


        :param server_start_time: The server_start_time of this ServiceInformation.
        :type server_start_time: datetime
        """

        self._server_start_time = server_start_time

    @property
    def server_current_time(self) -> datetime:
        """Gets the server_current_time of this ServiceInformation.


        :return: The server_current_time of this ServiceInformation.
        :rtype: datetime
        """
        return self._server_current_time

    @server_current_time.setter
    def server_current_time(self, server_current_time: datetime):
        """Sets the server_current_time of this ServiceInformation.


        :param server_current_time: The server_current_time of this ServiceInformation.
        :type server_current_time: datetime
        """

        self._server_current_time = server_current_time

    @property
    def server_pid(self) -> int:
        """Gets the server_pid of this ServiceInformation.


        :return: The server_pid of this ServiceInformation.
        :rtype: int
        """
        return self._server_pid

    @server_pid.setter
    def server_pid(self, server_pid: int):
        """Sets the server_pid of this ServiceInformation.


        :param server_pid: The server_pid of this ServiceInformation.
        :type server_pid: int
        """

        self._server_pid = server_pid

    @property
    def chart_version(self) -> str:
        """Gets the chart_version of this ServiceInformation.


        :return: The chart_version of this ServiceInformation.
        :rtype: str
        """
        return self._chart_version

    @chart_version.setter
    def chart_version(self, chart_version: str):
        """Sets the chart_version of this ServiceInformation.


        :param chart_version: The chart_version of this ServiceInformation.
        :type chart_version: str
        """

        self._chart_version = chart_version

    @property
    def mock_services(self) -> str:
        """Gets the mock_services of this ServiceInformation.


        :return: The mock_services of this ServiceInformation.
        :rtype: str
        """
        return self._mock_services

    @mock_services.setter
    def mock_services(self, mock_services: str):
        """Sets the mock_services of this ServiceInformation.


        :param mock_services: The mock_services of this ServiceInformation.
        :type mock_services: str
        """

        self._mock_services = mock_services

    @property
    def run_local(self) -> bool:
        """Gets the run_local of this ServiceInformation.


        :return: The run_local of this ServiceInformation.
        :rtype: bool
        """
        return self._run_local

    @run_local.setter
    def run_local(self, run_local: bool):
        """Sets the run_local of this ServiceInformation.


        :param run_local: The run_local of this ServiceInformation.
        :type run_local: bool
        """

        self._run_local = run_local
