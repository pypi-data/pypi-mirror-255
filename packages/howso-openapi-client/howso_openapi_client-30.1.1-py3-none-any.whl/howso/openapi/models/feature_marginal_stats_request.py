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


class FeatureMarginalStatsRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of a feature marginal stats request. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'weight_feature': 'str',
        'condition': 'dict[str, object]',
        'num_cases': 'float',
        'precision': 'str'
    }

    attribute_map = {
        'weight_feature': 'weight_feature',
        'condition': 'condition',
        'num_cases': 'num_cases',
        'precision': 'precision'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, weight_feature=None, condition=None, num_cases=None, precision=None, local_vars_configuration=None):  # noqa: E501
        """FeatureMarginalStatsRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._weight_feature = None
        self._condition = None
        self._num_cases = None
        self._precision = None

        if weight_feature is not None:
            self.weight_feature = weight_feature
        if condition is not None:
            self.condition = condition
        if num_cases is not None:
            self.num_cases = num_cases
        if precision is not None:
            self.precision = precision

    @property
    def weight_feature(self):
        """Get the weight_feature of this FeatureMarginalStatsRequest.

        When specified, will attempt to return stats that were computed using this weight_feature. 

        :return: The weight_feature of this FeatureMarginalStatsRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this FeatureMarginalStatsRequest.

        When specified, will attempt to return stats that were computed using this weight_feature. 

        :param weight_feature: The weight_feature of this FeatureMarginalStatsRequest.
        :type weight_feature: str
        """

        self._weight_feature = weight_feature

    @property
    def condition(self):
        """Get the condition of this FeatureMarginalStatsRequest.

        The condition map to select the cases that meet all the provided conditions. The dictionary keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :return: The condition of this FeatureMarginalStatsRequest.
        :rtype: dict[str, object]
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Set the condition of this FeatureMarginalStatsRequest.

        The condition map to select the cases that meet all the provided conditions. The dictionary keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :param condition: The condition of this FeatureMarginalStatsRequest.
        :type condition: dict[str, object]
        """

        self._condition = condition

    @property
    def num_cases(self):
        """Get the num_cases of this FeatureMarginalStatsRequest.

        The maximum number of cases to use. If not specified, the limit will be k cases if precision is \"similar\", or no limit if precision is \"exact\". 

        :return: The num_cases of this FeatureMarginalStatsRequest.
        :rtype: float
        """
        return self._num_cases

    @num_cases.setter
    def num_cases(self, num_cases):
        """Set the num_cases of this FeatureMarginalStatsRequest.

        The maximum number of cases to use. If not specified, the limit will be k cases if precision is \"similar\", or no limit if precision is \"exact\". 

        :param num_cases: The num_cases of this FeatureMarginalStatsRequest.
        :type num_cases: float
        """

        self._num_cases = num_cases

    @property
    def precision(self):
        """Get the precision of this FeatureMarginalStatsRequest.

        Exact matching or fuzzy matching.

        :return: The precision of this FeatureMarginalStatsRequest.
        :rtype: str
        """
        return self._precision

    @precision.setter
    def precision(self, precision):
        """Set the precision of this FeatureMarginalStatsRequest.

        Exact matching or fuzzy matching.

        :param precision: The precision of this FeatureMarginalStatsRequest.
        :type precision: str
        """
        allowed_values = ["exact", "similar"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and precision not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `precision` ({0}), must be one of {1}"  # noqa: E501
                .format(precision, allowed_values)
            )

        self._precision = precision

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
        if not isinstance(other, FeatureMarginalStatsRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureMarginalStatsRequest):
            return True

        return self.to_dict() != other.to_dict()
