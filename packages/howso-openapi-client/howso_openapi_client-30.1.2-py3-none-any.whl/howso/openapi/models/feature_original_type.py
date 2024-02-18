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


class FeatureOriginalType(object):
    """
    Auto-generated OpenAPI type.

    Original data type details. Used by clients to determine how to serialize and deserialize feature data.
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
        'encoding': 'str',
        'format': 'str',
        'size': 'int',
        'unsigned': 'bool',
        'timezone': 'str',
        'unit': 'str'
    }

    attribute_map = {
        'data_type': 'data_type',
        'length': 'length',
        'encoding': 'encoding',
        'format': 'format',
        'size': 'size',
        'unsigned': 'unsigned',
        'timezone': 'timezone',
        'unit': 'unit'
    }

    nullable_attributes = [
        'length', 
        'encoding', 
        'timezone', 
    ]

    discriminator_value_class_map = {
        'boolean': 'BooleanType',
        'date': 'DateType',
        'datetime': 'DatetimeType',
        'integer': 'IntegerType',
        'numeric': 'NumericType',
        'object': 'ObjectType',
        'string': 'StringType',
        'time': 'TimeType',
        'timedelta': 'TimedeltaType'
    }

    discriminator = 'data_type'

    def __init__(self, data_type=None, length=None, encoding=None, format=None, size=None, unsigned=False, timezone=None, unit='seconds', local_vars_configuration=None):  # noqa: E501
        """FeatureOriginalType - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._data_type = None
        self._length = None
        self._encoding = None
        self._format = None
        self._size = None
        self._unsigned = None
        self._timezone = None
        self._unit = None

        self.data_type = data_type
        self.length = length
        self.encoding = encoding
        if format is not None:
            self.format = format
        if size is not None:
            self.size = size
        if unsigned is not None:
            self.unsigned = unsigned
        self.timezone = timezone
        if unit is not None:
            self.unit = unit

    @property
    def data_type(self):
        """Get the data_type of this FeatureOriginalType.

        The name of the data type.

        :return: The data_type of this FeatureOriginalType.
        :rtype: str
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Set the data_type of this FeatureOriginalType.

        The name of the data type.

        :param data_type: The data_type of this FeatureOriginalType.
        :type data_type: str
        """
        if self.local_vars_configuration.client_side_validation and data_type is None:  # noqa: E501
            raise ValueError("Invalid value for `data_type`, must not be `None`")  # noqa: E501

        self._data_type = data_type

    @property
    def length(self):
        """Get the length of this FeatureOriginalType.

        The maximum allowed length of the string.

        :return: The length of this FeatureOriginalType.
        :rtype: int
        """
        return self._length

    @length.setter
    def length(self, length):
        """Set the length of this FeatureOriginalType.

        The maximum allowed length of the string.

        :param length: The length of this FeatureOriginalType.
        :type length: int
        """
        if (self.local_vars_configuration.client_side_validation and
                length is not None and length < 1):  # noqa: E501
            raise ValueError("Invalid value for `length`, must be a value greater than or equal to `1`")  # noqa: E501

        self._length = length

    @property
    def encoding(self):
        """Get the encoding of this FeatureOriginalType.

        The string encoding type.

        :return: The encoding of this FeatureOriginalType.
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """Set the encoding of this FeatureOriginalType.

        The string encoding type.

        :param encoding: The encoding of this FeatureOriginalType.
        :type encoding: str
        """

        self._encoding = encoding

    @property
    def format(self):
        """Get the format of this FeatureOriginalType.

        The format of the number.

        :return: The format of this FeatureOriginalType.
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """Set the format of this FeatureOriginalType.

        The format of the number.

        :param format: The format of this FeatureOriginalType.
        :type format: str
        """
        allowed_values = ["decimal"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and format not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `format` ({0}), must be one of {1}"  # noqa: E501
                .format(format, allowed_values)
            )

        self._format = format

    @property
    def size(self):
        """Get the size of this FeatureOriginalType.

        The size of the integer (in bytes).

        :return: The size of this FeatureOriginalType.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Set the size of this FeatureOriginalType.

        The size of the integer (in bytes).

        :param size: The size of this FeatureOriginalType.
        :type size: int
        """

        self._size = size

    @property
    def unsigned(self):
        """Get the unsigned of this FeatureOriginalType.

        If the integer is unsigned.

        :return: The unsigned of this FeatureOriginalType.
        :rtype: bool
        """
        return self._unsigned

    @unsigned.setter
    def unsigned(self, unsigned):
        """Set the unsigned of this FeatureOriginalType.

        If the integer is unsigned.

        :param unsigned: The unsigned of this FeatureOriginalType.
        :type unsigned: bool
        """

        self._unsigned = unsigned

    @property
    def timezone(self):
        """Get the timezone of this FeatureOriginalType.

        The standardized timezone name.

        :return: The timezone of this FeatureOriginalType.
        :rtype: str
        """
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        """Set the timezone of this FeatureOriginalType.

        The standardized timezone name.

        :param timezone: The timezone of this FeatureOriginalType.
        :type timezone: str
        """

        self._timezone = timezone

    @property
    def unit(self):
        """Get the unit of this FeatureOriginalType.

        The unit of the time delta.

        :return: The unit of this FeatureOriginalType.
        :rtype: str
        """
        return self._unit

    @unit.setter
    def unit(self, unit):
        """Set the unit of this FeatureOriginalType.

        The unit of the time delta.

        :param unit: The unit of this FeatureOriginalType.
        :type unit: str
        """
        allowed_values = ["days", "seconds", "nanoseconds"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and unit not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `unit` ({0}), must be one of {1}"  # noqa: E501
                .format(unit, allowed_values)
            )

        self._unit = unit

    @classmethod
    def get_real_child_model(cls, data):  # pragma: no cover
        """Returns the real base class specified by the discriminator"""
        discriminator_key = cls.attribute_map[cls.discriminator]
        discriminator_value = data[discriminator_key]
        return cls.discriminator_value_class_map.get(discriminator_value)

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
        if not isinstance(other, FeatureOriginalType):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureOriginalType):
            return True

        return self.to_dict() != other.to_dict()
