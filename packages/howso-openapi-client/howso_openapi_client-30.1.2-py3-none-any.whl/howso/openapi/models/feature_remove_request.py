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


class FeatureRemoveRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of a feature removal request. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'feature': 'str',
        'condition': 'object',
        'condition_session': 'str'
    }

    attribute_map = {
        'feature': 'feature',
        'condition': 'condition',
        'condition_session': 'condition_session'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, feature=None, condition=None, condition_session=None, local_vars_configuration=None):  # noqa: E501
        """FeatureRemoveRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._feature = None
        self._condition = None
        self._condition_session = None

        self.feature = feature
        if condition is not None:
            self.condition = condition
        if condition_session is not None:
            self.condition_session = condition_session

    @property
    def feature(self):
        """Get the feature of this FeatureRemoveRequest.

        The name of the feature.

        :return: The feature of this FeatureRemoveRequest.
        :rtype: str
        """
        return self._feature

    @feature.setter
    def feature(self, feature):
        """Set the feature of this FeatureRemoveRequest.

        The name of the feature.

        :param feature: The feature of this FeatureRemoveRequest.
        :type feature: str
        """
        if self.local_vars_configuration.client_side_validation and feature is None:  # noqa: E501
            raise ValueError("Invalid value for `feature`, must not be `None`")  # noqa: E501

        self._feature = feature

    @property
    def condition(self):
        """Get the condition of this FeatureRemoveRequest.

        A condition map where features will only be modified when certain criteria is met. If no value is provided, the feature will be modified in all cases of the model and feature metadata will be updated. If an empty object is provided, the feature will be modified in all cases of the model but the feature metadata will not be updated. The object keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :return: The condition of this FeatureRemoveRequest.
        :rtype: object
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Set the condition of this FeatureRemoveRequest.

        A condition map where features will only be modified when certain criteria is met. If no value is provided, the feature will be modified in all cases of the model and feature metadata will be updated. If an empty object is provided, the feature will be modified in all cases of the model but the feature metadata will not be updated. The object keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :param condition: The condition of this FeatureRemoveRequest.
        :type condition: object
        """

        self._condition = condition

    @property
    def condition_session(self):
        """Get the condition_session of this FeatureRemoveRequest.

        If specified, ignores the condition and operates on cases for the specified session id.

        :return: The condition_session of this FeatureRemoveRequest.
        :rtype: str
        """
        return self._condition_session

    @condition_session.setter
    def condition_session(self, condition_session):
        """Set the condition_session of this FeatureRemoveRequest.

        If specified, ignores the condition and operates on cases for the specified session id.

        :param condition_session: The condition_session of this FeatureRemoveRequest.
        :type condition_session: str
        """

        self._condition_session = condition_session

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
        if not isinstance(other, FeatureRemoveRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureRemoveRequest):
            return True

        return self.to_dict() != other.to_dict()
