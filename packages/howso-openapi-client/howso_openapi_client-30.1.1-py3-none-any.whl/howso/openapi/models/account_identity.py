# coding: utf-8

"""
Howso API

OpenAPI implementation for interacting with the Howso API. 
"""

try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from howso.openapi.configuration import Configuration


class AccountIdentity(object):
    """
    Auto-generated OpenAPI type.

    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'uuid': 'str',
        'username': 'str',
        'full_name': 'str'
    }

    attribute_map = {
        'uuid': 'uuid',
        'username': 'username',
        'full_name': 'full_name'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, uuid=None, username=None, full_name=None, local_vars_configuration=None):  # noqa: E501
        """AccountIdentity - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._uuid = None
        self._username = None
        self._full_name = None

        if uuid is not None:
            self.uuid = uuid
        if username is not None:
            self.username = username
        if full_name is not None:
            self.full_name = full_name

    @property
    def uuid(self):
        """Get the uuid of this AccountIdentity.

        The user's UUID.

        :return: The uuid of this AccountIdentity.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        """Set the uuid of this AccountIdentity.

        The user's UUID.

        :param uuid: The uuid of this AccountIdentity.
        :type uuid: str
        """

        self._uuid = uuid

    @property
    def username(self):
        """Get the username of this AccountIdentity.

        The user's username.

        :return: The username of this AccountIdentity.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """Set the username of this AccountIdentity.

        The user's username.

        :param username: The username of this AccountIdentity.
        :type username: str
        """

        self._username = username

    @property
    def full_name(self):
        """Get the full_name of this AccountIdentity.

        The user's full name.

        :return: The full_name of this AccountIdentity.
        :rtype: str
        """
        return self._full_name

    @full_name.setter
    def full_name(self, full_name):
        """Set the full_name of this AccountIdentity.

        The user's full name.

        :param full_name: The full_name of this AccountIdentity.
        :type full_name: str
        """

        self._full_name = full_name

    def to_dict(self, serialize=False, exclude_null=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                elif 'exclude_null' in args:
                    return x.to_dict(serialize, exclude_null)
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            elif value is None and (exclude_null or attr not in self.nullable_attributes):
                continue
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AccountIdentity):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AccountIdentity):
            return True

        return self.to_dict() != other.to_dict()
