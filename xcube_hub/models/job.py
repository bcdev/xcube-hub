# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub.models.job_status import JobStatus  # noqa: F401,E501
from xcube_hub import util


class Job(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, job_id: str=None, status: JobStatus=None):  # noqa: E501
        """Job - a model defined in Swagger

        :param job_id: The job_id of this Job.  # noqa: E501
        :type job_id: str
        :param status: The status of this Job.  # noqa: E501
        :type status: JobStatus
        """
        self.swagger_types = {
            'job_id': str,
            'status': JobStatus
        }

        self.attribute_map = {
            'job_id': 'job_id',
            'status': 'status'
        }
        self._job_id = job_id
        self._status = status

    @classmethod
    def from_dict(cls, dikt) -> 'Job':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Job of this Job.  # noqa: E501
        :rtype: Job
        """
        return util.deserialize_model(dikt, cls)

    @property
    def job_id(self) -> str:
        """Gets the job_id of this Job.


        :return: The job_id of this Job.
        :rtype: str
        """
        return self._job_id

    @job_id.setter
    def job_id(self, job_id: str):
        """Sets the job_id of this Job.


        :param job_id: The job_id of this Job.
        :type job_id: str
        """
        if job_id is None:
            raise ValueError("Invalid value for `job_id`, must not be `None`")  # noqa: E501

        self._job_id = job_id

    @property
    def status(self) -> JobStatus:
        """Gets the status of this Job.


        :return: The status of this Job.
        :rtype: JobStatus
        """
        return self._status

    @status.setter
    def status(self, status: JobStatus):
        """Sets the status of this Job.


        :param status: The status of this Job.
        :type status: JobStatus
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501

        self._status = status
