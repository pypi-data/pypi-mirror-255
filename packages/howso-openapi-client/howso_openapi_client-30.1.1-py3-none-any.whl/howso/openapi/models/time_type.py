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


class TimeType(object):
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
        'data_type': 'str',
        'timezone': 'str'
    }

    attribute_map = {
        'data_type': 'data_type',
        'timezone': 'timezone'
    }

    nullable_attributes = [
        'timezone', 
    ]

    discriminator = None

    def __init__(self, data_type=None, timezone=None, local_vars_configuration=None):  # noqa: E501
        """TimeType - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._data_type = None
        self._timezone = None

        self.data_type = data_type
        self.timezone = timezone

    @property
    def data_type(self):
        """Get the data_type of this TimeType.

        The name of the data type.

        :return: The data_type of this TimeType.
        :rtype: str
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Set the data_type of this TimeType.

        The name of the data type.

        :param data_type: The data_type of this TimeType.
        :type data_type: str
        """
        if self.local_vars_configuration.client_side_validation and data_type is None:  # noqa: E501
            raise ValueError("Invalid value for `data_type`, must not be `None`")  # noqa: E501

        self._data_type = data_type

    @property
    def timezone(self):
        """Get the timezone of this TimeType.

        The standardized timezone name.

        :return: The timezone of this TimeType.
        :rtype: str
        """
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        """Set the timezone of this TimeType.

        The standardized timezone name.

        :param timezone: The timezone of this TimeType.
        :type timezone: str
        """

        self._timezone = timezone

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
        if not isinstance(other, TimeType):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TimeType):
            return True

        return self.to_dict() != other.to_dict()
