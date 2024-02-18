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


class RemoveSeriesStoreRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of a remove series store request.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'series': 'str'
    }

    attribute_map = {
        'series': 'series'
    }

    nullable_attributes = [
        'series', 
    ]

    discriminator = None

    def __init__(self, series=None, local_vars_configuration=None):  # noqa: E501
        """RemoveSeriesStoreRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._series = None

        self.series = series

    @property
    def series(self):
        """Get the series of this RemoveSeriesStoreRequest.

        The name of a series to remove.

        :return: The series of this RemoveSeriesStoreRequest.
        :rtype: str
        """
        return self._series

    @series.setter
    def series(self, series):
        """Set the series of this RemoveSeriesStoreRequest.

        The name of a series to remove.

        :param series: The series of this RemoveSeriesStoreRequest.
        :type series: str
        """

        self._series = series

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
        if not isinstance(other, RemoveSeriesStoreRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, RemoveSeriesStoreRequest):
            return True

        return self.to_dict() != other.to_dict()
