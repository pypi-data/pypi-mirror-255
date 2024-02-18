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


class TraineeResources(object):
    """
    Auto-generated OpenAPI type.

    The alloted resources for a Trainee.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'cpu': 'CPULimits',
        'memory': 'MemoryLimits',
        'replicas': 'int'
    }

    attribute_map = {
        'cpu': 'cpu',
        'memory': 'memory',
        'replicas': 'replicas'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, cpu=None, memory=None, replicas=1, local_vars_configuration=None):  # noqa: E501
        """TraineeResources - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._cpu = None
        self._memory = None
        self._replicas = None

        if cpu is not None:
            self.cpu = cpu
        if memory is not None:
            self.memory = memory
        if replicas is not None:
            self.replicas = replicas

    @property
    def cpu(self):
        """Get the cpu of this TraineeResources.


        :return: The cpu of this TraineeResources.
        :rtype: CPULimits
        """
        return self._cpu

    @cpu.setter
    def cpu(self, cpu):
        """Set the cpu of this TraineeResources.


        :param cpu: The cpu of this TraineeResources.
        :type cpu: CPULimits
        """

        self._cpu = cpu

    @property
    def memory(self):
        """Get the memory of this TraineeResources.


        :return: The memory of this TraineeResources.
        :rtype: MemoryLimits
        """
        return self._memory

    @memory.setter
    def memory(self, memory):
        """Set the memory of this TraineeResources.


        :param memory: The memory of this TraineeResources.
        :type memory: MemoryLimits
        """

        self._memory = memory

    @property
    def replicas(self):
        """Get the replicas of this TraineeResources.

        The number of compute instance replicas to create.

        :return: The replicas of this TraineeResources.
        :rtype: int
        """
        return self._replicas

    @replicas.setter
    def replicas(self, replicas):
        """Set the replicas of this TraineeResources.

        The number of compute instance replicas to create.

        :param replicas: The replicas of this TraineeResources.
        :type replicas: int
        """
        if (self.local_vars_configuration.client_side_validation and
                replicas is not None and replicas > 1):  # noqa: E501
            raise ValueError("Invalid value for `replicas`, must be a value less than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                replicas is not None and replicas < 1):  # noqa: E501
            raise ValueError("Invalid value for `replicas`, must be a value greater than or equal to `1`")  # noqa: E501

        self._replicas = replicas

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
        if not isinstance(other, TraineeResources):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TraineeResources):
            return True

        return self.to_dict() != other.to_dict()
