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


class EvaluateResponse(object):
    """
    Auto-generated OpenAPI type.

    The response body for evaluate
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'aggregated': 'object',
        'evaluated': 'dict[str, list[object]]'
    }

    attribute_map = {
        'aggregated': 'aggregated',
        'evaluated': 'evaluated'
    }

    nullable_attributes = [
        'aggregated', 
    ]

    discriminator = None

    def __init__(self, aggregated=None, evaluated=None, local_vars_configuration=None):  # noqa: E501
        """EvaluateResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._aggregated = None
        self._evaluated = None

        self.aggregated = aggregated
        if evaluated is not None:
            self.evaluated = evaluated

    @property
    def aggregated(self):
        """Get the aggregated of this EvaluateResponse.


        :return: The aggregated of this EvaluateResponse.
        :rtype: object
        """
        return self._aggregated

    @aggregated.setter
    def aggregated(self, aggregated):
        """Set the aggregated of this EvaluateResponse.


        :param aggregated: The aggregated of this EvaluateResponse.
        :type aggregated: object
        """

        self._aggregated = aggregated

    @property
    def evaluated(self):
        """Get the evaluated of this EvaluateResponse.

        Map of feature name to list of values derived from custom code 

        :return: The evaluated of this EvaluateResponse.
        :rtype: dict[str, list[object]]
        """
        return self._evaluated

    @evaluated.setter
    def evaluated(self, evaluated):
        """Set the evaluated of this EvaluateResponse.

        Map of feature name to list of values derived from custom code 

        :param evaluated: The evaluated of this EvaluateResponse.
        :type evaluated: dict[str, list[object]]
        """

        self._evaluated = evaluated

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
        if not isinstance(other, EvaluateResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, EvaluateResponse):
            return True

        return self.to_dict() != other.to_dict()
