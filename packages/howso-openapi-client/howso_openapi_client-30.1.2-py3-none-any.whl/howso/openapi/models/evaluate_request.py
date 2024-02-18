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


class EvaluateRequest(object):
    """
    Auto-generated OpenAPI type.

    Request body for evaluate
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'features_to_code_map': 'dict[str, str]',
        'aggregation_code': 'str'
    }

    attribute_map = {
        'features_to_code_map': 'features_to_code_map',
        'aggregation_code': 'aggregation_code'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, features_to_code_map=None, aggregation_code=None, local_vars_configuration=None):  # noqa: E501
        """EvaluateRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._features_to_code_map = None
        self._aggregation_code = None

        self.features_to_code_map = features_to_code_map
        if aggregation_code is not None:
            self.aggregation_code = aggregation_code

    @property
    def features_to_code_map(self):
        """Get the features_to_code_map of this EvaluateRequest.

        Map of feature name to custom code string 

        :return: The features_to_code_map of this EvaluateRequest.
        :rtype: dict[str, str]
        """
        return self._features_to_code_map

    @features_to_code_map.setter
    def features_to_code_map(self, features_to_code_map):
        """Set the features_to_code_map of this EvaluateRequest.

        Map of feature name to custom code string 

        :param features_to_code_map: The features_to_code_map of this EvaluateRequest.
        :type features_to_code_map: dict[str, str]
        """
        if self.local_vars_configuration.client_side_validation and features_to_code_map is None:  # noqa: E501
            raise ValueError("Invalid value for `features_to_code_map`, must not be `None`")  # noqa: E501

        self._features_to_code_map = features_to_code_map

    @property
    def aggregation_code(self):
        """Get the aggregation_code of this EvaluateRequest.


        :return: The aggregation_code of this EvaluateRequest.
        :rtype: str
        """
        return self._aggregation_code

    @aggregation_code.setter
    def aggregation_code(self, aggregation_code):
        """Set the aggregation_code of this EvaluateRequest.


        :param aggregation_code: The aggregation_code of this EvaluateRequest.
        :type aggregation_code: str
        """

        self._aggregation_code = aggregation_code

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
        if not isinstance(other, EvaluateRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, EvaluateRequest):
            return True

        return self.to_dict() != other.to_dict()
