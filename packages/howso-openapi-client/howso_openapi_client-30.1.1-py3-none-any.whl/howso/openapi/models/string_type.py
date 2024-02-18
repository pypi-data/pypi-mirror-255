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


class StringType(object):
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
        'length': 'int',
        'encoding': 'str'
    }

    attribute_map = {
        'data_type': 'data_type',
        'length': 'length',
        'encoding': 'encoding'
    }

    nullable_attributes = [
        'length', 
        'encoding', 
    ]

    discriminator = None

    def __init__(self, data_type=None, length=None, encoding=None, local_vars_configuration=None):  # noqa: E501
        """StringType - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._data_type = None
        self._length = None
        self._encoding = None

        self.data_type = data_type
        self.length = length
        self.encoding = encoding

    @property
    def data_type(self):
        """Get the data_type of this StringType.

        The name of the data type.

        :return: The data_type of this StringType.
        :rtype: str
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Set the data_type of this StringType.

        The name of the data type.

        :param data_type: The data_type of this StringType.
        :type data_type: str
        """
        if self.local_vars_configuration.client_side_validation and data_type is None:  # noqa: E501
            raise ValueError("Invalid value for `data_type`, must not be `None`")  # noqa: E501

        self._data_type = data_type

    @property
    def length(self):
        """Get the length of this StringType.

        The maximum allowed length of the string.

        :return: The length of this StringType.
        :rtype: int
        """
        return self._length

    @length.setter
    def length(self, length):
        """Set the length of this StringType.

        The maximum allowed length of the string.

        :param length: The length of this StringType.
        :type length: int
        """
        if (self.local_vars_configuration.client_side_validation and
                length is not None and length < 1):  # noqa: E501
            raise ValueError("Invalid value for `length`, must be a value greater than or equal to `1`")  # noqa: E501

        self._length = length

    @property
    def encoding(self):
        """Get the encoding of this StringType.

        The string encoding type.

        :return: The encoding of this StringType.
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """Set the encoding of this StringType.

        The string encoding type.

        :param encoding: The encoding of this StringType.
        :type encoding: str
        """

        self._encoding = encoding

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
        if not isinstance(other, StringType):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, StringType):
            return True

        return self.to_dict() != other.to_dict()
