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


class PlatformVersion(object):
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
        'api': 'str',
        'client': 'str',
        'platform': 'str',
        'replicated': 'str'
    }

    attribute_map = {
        'api': 'api',
        'client': 'client',
        'platform': 'platform',
        'replicated': 'replicated'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, api=None, client=None, platform=None, replicated=None, local_vars_configuration=None):  # noqa: E501
        """PlatformVersion - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._api = None
        self._client = None
        self._platform = None
        self._replicated = None

        if api is not None:
            self.api = api
        if client is not None:
            self.client = client
        if platform is not None:
            self.platform = platform
        if replicated is not None:
            self.replicated = replicated

    @property
    def api(self):
        """Get the api of this PlatformVersion.

        The API version.

        :return: The api of this PlatformVersion.
        :rtype: str
        """
        return self._api

    @api.setter
    def api(self, api):
        """Set the api of this PlatformVersion.

        The API version.

        :param api: The api of this PlatformVersion.
        :type api: str
        """

        self._api = api

    @property
    def client(self):
        """Get the client of this PlatformVersion.

        The version of the locally installed client.

        :return: The client of this PlatformVersion.
        :rtype: str
        """
        return self._client

    @client.setter
    def client(self, client):
        """Set the client of this PlatformVersion.

        The version of the locally installed client.

        :param client: The client of this PlatformVersion.
        :type client: str
        """

        self._client = client

    @property
    def platform(self):
        """Get the platform of this PlatformVersion.

        The platform release version.

        :return: The platform of this PlatformVersion.
        :rtype: str
        """
        return self._platform

    @platform.setter
    def platform(self, platform):
        """Set the platform of this PlatformVersion.

        The platform release version.

        :param platform: The platform of this PlatformVersion.
        :type platform: str
        """

        self._platform = platform

    @property
    def replicated(self):
        """Get the replicated of this PlatformVersion.

        The Replicated version.

        :return: The replicated of this PlatformVersion.
        :rtype: str
        """
        return self._replicated

    @replicated.setter
    def replicated(self, replicated):
        """Set the replicated of this PlatformVersion.

        The Replicated version.

        :param replicated: The replicated of this PlatformVersion.
        :type replicated: str
        """

        self._replicated = replicated

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
        if not isinstance(other, PlatformVersion):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PlatformVersion):
            return True

        return self.to_dict() != other.to_dict()
