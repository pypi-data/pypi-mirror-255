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


class ApiVersion(object):
    """
    Auto-generated OpenAPI type.

    API version information. 
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
        'client': 'str'
    }

    attribute_map = {
        'api': 'api',
        'client': 'client'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, api=None, client=None, local_vars_configuration=None):  # noqa: E501
        """ApiVersion - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._api = None
        self._client = None

        if api is not None:
            self.api = api
        if client is not None:
            self.client = client

    @property
    def api(self):
        """Get the api of this ApiVersion.

        The API version.

        :return: The api of this ApiVersion.
        :rtype: str
        """
        return self._api

    @api.setter
    def api(self, api):
        """Set the api of this ApiVersion.

        The API version.

        :param api: The api of this ApiVersion.
        :type api: str
        """

        self._api = api

    @property
    def client(self):
        """Get the client of this ApiVersion.

        The version of the locally installed client.

        :return: The client of this ApiVersion.
        :rtype: str
        """
        return self._client

    @client.setter
    def client(self, client):
        """Set the client of this ApiVersion.

        The version of the locally installed client.

        :param client: The client of this ApiVersion.
        :type client: str
        """

        self._client = client

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
        if not isinstance(other, ApiVersion):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ApiVersion):
            return True

        return self.to_dict() != other.to_dict()
