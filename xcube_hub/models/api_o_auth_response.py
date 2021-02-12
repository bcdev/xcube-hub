# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from xcube_hub.models.base_model_ import Model
from xcube_hub import util


class ApiOAuthResponse(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, access_token: str=None, token_type: str=None):  # noqa: E501
        """ApiOAuthResponse - a model defined in Swagger

        :param access_token: The access_token of this ApiOAuthResponse.  # noqa: E501
        :type access_token: str
        :param token_type: The token_type of this ApiOAuthResponse.  # noqa: E501
        :type token_type: str
        """
        self.swagger_types = {
            'access_token': str,
            'token_type': str
        }

        self.attribute_map = {
            'access_token': 'access_token',
            'token_type': 'token_type'
        }
        self._access_token = access_token
        self._token_type = token_type

    @classmethod
    def from_dict(cls, dikt) -> 'ApiOAuthResponse':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ApiOAuthResponse of this ApiOAuthResponse.  # noqa: E501
        :rtype: ApiOAuthResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def access_token(self) -> str:
        """Gets the access_token of this ApiOAuthResponse.


        :return: The access_token of this ApiOAuthResponse.
        :rtype: str
        """
        return self._access_token

    @access_token.setter
    def access_token(self, access_token: str):
        """Sets the access_token of this ApiOAuthResponse.


        :param access_token: The access_token of this ApiOAuthResponse.
        :type access_token: str
        """
        if access_token is None:
            raise ValueError("Invalid value for `access_token`, must not be `None`")  # noqa: E501

        self._access_token = access_token

    @property
    def token_type(self) -> str:
        """Gets the token_type of this ApiOAuthResponse.


        :return: The token_type of this ApiOAuthResponse.
        :rtype: str
        """
        return self._token_type

    @token_type.setter
    def token_type(self, token_type: str):
        """Sets the token_type of this ApiOAuthResponse.


        :param token_type: The token_type of this ApiOAuthResponse.
        :type token_type: str
        """
        if token_type is None:
            raise ValueError("Invalid value for `token_type`, must not be `None`")  # noqa: E501

        self._token_type = token_type
