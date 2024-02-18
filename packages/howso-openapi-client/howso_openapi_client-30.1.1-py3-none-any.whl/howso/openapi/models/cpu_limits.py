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


class CPULimits(object):
    """
    Auto-generated OpenAPI type.

    The requested CPU to provision for a compute instance.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'minimum': 'int',
        'maximum': 'int'
    }

    attribute_map = {
        'minimum': 'minimum',
        'maximum': 'maximum'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, minimum=None, maximum=None, local_vars_configuration=None):  # noqa: E501
        """CPULimits - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._minimum = None
        self._maximum = None

        if minimum is not None:
            self.minimum = minimum
        if maximum is not None:
            self.maximum = maximum

    @property
    def minimum(self):
        """Get the minimum of this CPULimits.

        The minimum CPUs to provision (in millicores). The compute instance will be guaranteed to receive at least this amount of CPU resources. If the system does not have enough CPU resources available the compute instance will fail to be provisioned. 

        :return: The minimum of this CPULimits.
        :rtype: int
        """
        return self._minimum

    @minimum.setter
    def minimum(self, minimum):
        """Set the minimum of this CPULimits.

        The minimum CPUs to provision (in millicores). The compute instance will be guaranteed to receive at least this amount of CPU resources. If the system does not have enough CPU resources available the compute instance will fail to be provisioned. 

        :param minimum: The minimum of this CPULimits.
        :type minimum: int
        """

        self._minimum = minimum

    @property
    def maximum(self):
        """Get the maximum of this CPULimits.

        The maximum CPUs to provision (in millicores). The compute instance will be allowed to scale to use more CPU resources up to this limit if available. Upon exceeding this limit the compute instance CPU will be throttled. 

        :return: The maximum of this CPULimits.
        :rtype: int
        """
        return self._maximum

    @maximum.setter
    def maximum(self, maximum):
        """Set the maximum of this CPULimits.

        The maximum CPUs to provision (in millicores). The compute instance will be allowed to scale to use more CPU resources up to this limit if available. Upon exceeding this limit the compute instance CPU will be throttled. 

        :param maximum: The maximum of this CPULimits.
        :type maximum: int
        """

        self._maximum = maximum

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
        if not isinstance(other, CPULimits):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CPULimits):
            return True

        return self.to_dict() != other.to_dict()
