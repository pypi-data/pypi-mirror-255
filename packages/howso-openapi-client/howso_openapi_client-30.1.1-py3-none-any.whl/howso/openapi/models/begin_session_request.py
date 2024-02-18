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


class BeginSessionRequest(object):
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
        'name': 'str',
        'metadata': 'dict[str, object]'
    }

    attribute_map = {
        'name': 'name',
        'metadata': 'metadata'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, name=None, metadata=None, local_vars_configuration=None):  # noqa: E501
        """BeginSessionRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._metadata = None

        self.name = name
        if metadata is not None:
            self.metadata = metadata

    @property
    def name(self):
        """Get the name of this BeginSessionRequest.

        The name given to the session.

        :return: The name of this BeginSessionRequest.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set the name of this BeginSessionRequest.

        The name given to the session.

        :param name: The name of this BeginSessionRequest.
        :type name: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 128):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `128`")  # noqa: E501

        self._name = name

    @property
    def metadata(self):
        """Get the metadata of this BeginSessionRequest.

        Any key-value pair to store custom metadata for the session.

        :return: The metadata of this BeginSessionRequest.
        :rtype: dict[str, object]
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Set the metadata of this BeginSessionRequest.

        Any key-value pair to store custom metadata for the session.

        :param metadata: The metadata of this BeginSessionRequest.
        :type metadata: dict[str, object]
        """

        self._metadata = metadata

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
        if not isinstance(other, BeginSessionRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BeginSessionRequest):
            return True

        return self.to_dict() != other.to_dict()
