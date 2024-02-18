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


class ReactIntoFeaturesResponse(object):
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
        'warnings': 'list[Warning]'
    }

    attribute_map = {
        'warnings': 'warnings'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, warnings=None, local_vars_configuration=None):  # noqa: E501
        """ReactIntoFeaturesResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._warnings = None

        if warnings is not None:
            self.warnings = warnings

    @property
    def warnings(self):
        """Get the warnings of this ReactIntoFeaturesResponse.


        :return: The warnings of this ReactIntoFeaturesResponse.
        :rtype: list[Warning]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Set the warnings of this ReactIntoFeaturesResponse.


        :param warnings: The warnings of this ReactIntoFeaturesResponse.
        :type warnings: list[Warning]
        """

        self._warnings = warnings

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
        if not isinstance(other, ReactIntoFeaturesResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactIntoFeaturesResponse):
            return True

        return self.to_dict() != other.to_dict()
