import datetime
import hashlib
import os
import re
import secrets
import uuid
from typing import Optional, Sequence, Any

import connexion
import six
from kubernetes import client

from xcube_hub import typing_utils, api


def _deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if klass in six.integer_types or klass in (float, str, bool, bytearray):
        return _deserialize_primitive(data, klass)
    elif klass == object:
        return _deserialize_object(data)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif typing_utils.is_generic(klass):
        if typing_utils.is_list(klass):
            return _deserialize_list(data, klass.__args__[0])
        if typing_utils.is_dict(klass):
            return _deserialize_dict(data, klass.__args__[1])
    else:
        return deserialize_model(data, klass)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    :rtype: int | long | float | str | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        value = six.u(data)
    except TypeError:
        value = data
    return value


def _deserialize_object(value):
    """Return an original value.

    :return: object.
    """
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass()

    if not instance.openapi_types:
        return data

    for attr, attr_type in six.iteritems(instance.openapi_types):
        if data is not None \
                and instance.attribute_map[attr] in data \
                and isinstance(data, (list, dict)):
            value = data[instance.attribute_map[attr]]
            setattr(instance, attr, _deserialize(value, attr_type))

    return instance


def _deserialize_list(data, boxed_type):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list
    :param boxed_type: class literal.

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, boxed_type)
            for sub_data in data]


def _deserialize_dict(data, boxed_type):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict
    :param boxed_type: class literal.

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, boxed_type)
            for k, v in six.iteritems(data)}


def maybe_raise_for_env(env_var: str, default: Optional[Any] = None, typ=str) -> Any:
    val = os.getenv(env_var, default=default)

    if val is None:
        raise api.ApiError(400, f"Environment Variable {env_var} does not exist.")

    try:
        val = typ(val)
    except (TypeError, ValueError) as e:
        raise api.ApiError(400, str(e))

    return val


def raise_for_invalid_username(username: str) -> bool:
    valid = True
    if len(username) > 63:
        valid = False

    pattern = re.compile("[a-z0-9]([-a-z0-9]*[a-z0-9])?")
    if not pattern.fullmatch(username):
        valid = False

    if not valid:
        raise api.ApiError(400, "Invalid user name.")

    return valid


def load_env_by_regex(regex: Optional[str] = None) -> Sequence[client.V1EnvVar]:
    p = re.compile(regex or '')

    return [client.V1EnvVar(name=k, value=v) for k, v in os.environ.items() if regex is None or p.match(k)]


# noinspection InsecureHash
def create_user_id_from_email(email: str):
    res = hashlib.md5(email.encode())
    return 'a' + res.hexdigest()


def generate_temp_password(secrets_length: int = 32):
    return secrets.token_urlsafe(secrets_length)


def create_secret(secrets_length: int = 32):
    client_id = uuid.uuid4().hex
    client_secret = generate_temp_password(secrets_length)
    return client_id, client_secret


def strap_token():
    return connexion.request.headers["Authorization"].replace("Bearer ", "")
