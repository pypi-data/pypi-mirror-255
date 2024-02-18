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


class FeatureAddRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of an add feature request. 
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
        'condition_session': 'str',
        'feature_value': 'object',
        'feature_attributes': 'FeatureAttributes',
        'overwrite': 'bool'
    }

    attribute_map = {
        'feature': 'feature',
        'condition': 'condition',
        'condition_session': 'condition_session',
        'feature_value': 'feature_value',
        'feature_attributes': 'feature_attributes',
        'overwrite': 'overwrite'
    }

    nullable_attributes = [
        'feature_value', 
    ]

    discriminator = None

    def __init__(self, feature=None, condition=None, condition_session=None, feature_value=None, feature_attributes=None, overwrite=True, local_vars_configuration=None):  # noqa: E501
        """FeatureAddRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._feature = None
        self._condition = None
        self._condition_session = None
        self._feature_value = None
        self._feature_attributes = None
        self._overwrite = None

        self.feature = feature
        if condition is not None:
            self.condition = condition
        if condition_session is not None:
            self.condition_session = condition_session
        self.feature_value = feature_value
        if feature_attributes is not None:
            self.feature_attributes = feature_attributes
        if overwrite is not None:
            self.overwrite = overwrite

    @property
    def feature(self):
        """Get the feature of this FeatureAddRequest.

        The name of the feature.

        :return: The feature of this FeatureAddRequest.
        :rtype: str
        """
        return self._feature

    @feature.setter
    def feature(self, feature):
        """Set the feature of this FeatureAddRequest.

        The name of the feature.

        :param feature: The feature of this FeatureAddRequest.
        :type feature: str
        """
        if self.local_vars_configuration.client_side_validation and feature is None:  # noqa: E501
            raise ValueError("Invalid value for `feature`, must not be `None`")  # noqa: E501

        self._feature = feature

    @property
    def condition(self):
        """Get the condition of this FeatureAddRequest.

        A condition map where features will only be modified when certain criteria is met. If no value is provided, the feature will be modified in all cases of the model and feature metadata will be updated. If an empty object is provided, the feature will be modified in all cases of the model but the feature metadata will not be updated. The object keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :return: The condition of this FeatureAddRequest.
        :rtype: object
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Set the condition of this FeatureAddRequest.

        A condition map where features will only be modified when certain criteria is met. If no value is provided, the feature will be modified in all cases of the model and feature metadata will be updated. If an empty object is provided, the feature will be modified in all cases of the model but the feature metadata will not be updated. The object keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :param condition: The condition of this FeatureAddRequest.
        :type condition: object
        """

        self._condition = condition

    @property
    def condition_session(self):
        """Get the condition_session of this FeatureAddRequest.

        If specified, ignores the condition and operates on cases for the specified session id.

        :return: The condition_session of this FeatureAddRequest.
        :rtype: str
        """
        return self._condition_session

    @condition_session.setter
    def condition_session(self, condition_session):
        """Set the condition_session of this FeatureAddRequest.

        If specified, ignores the condition and operates on cases for the specified session id.

        :param condition_session: The condition_session of this FeatureAddRequest.
        :type condition_session: str
        """

        self._condition_session = condition_session

    @property
    def feature_value(self):
        """Get the feature_value of this FeatureAddRequest.

        A value to apply to the feature for all cases trained the session/trainee. 

        :return: The feature_value of this FeatureAddRequest.
        :rtype: object
        """
        return self._feature_value

    @feature_value.setter
    def feature_value(self, feature_value):
        """Set the feature_value of this FeatureAddRequest.

        A value to apply to the feature for all cases trained the session/trainee. 

        :param feature_value: The feature_value of this FeatureAddRequest.
        :type feature_value: object
        """

        self._feature_value = feature_value

    @property
    def feature_attributes(self):
        """Get the feature_attributes of this FeatureAddRequest.


        :return: The feature_attributes of this FeatureAddRequest.
        :rtype: FeatureAttributes
        """
        return self._feature_attributes

    @feature_attributes.setter
    def feature_attributes(self, feature_attributes):
        """Set the feature_attributes of this FeatureAddRequest.


        :param feature_attributes: The feature_attributes of this FeatureAddRequest.
        :type feature_attributes: FeatureAttributes
        """

        self._feature_attributes = feature_attributes

    @property
    def overwrite(self):
        """Get the overwrite of this FeatureAddRequest.

        Whether to overwrite the feature if it exists.

        :return: The overwrite of this FeatureAddRequest.
        :rtype: bool
        """
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite):
        """Set the overwrite of this FeatureAddRequest.

        Whether to overwrite the feature if it exists.

        :param overwrite: The overwrite of this FeatureAddRequest.
        :type overwrite: bool
        """

        self._overwrite = overwrite

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
        if not isinstance(other, FeatureAddRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureAddRequest):
            return True

        return self.to_dict() != other.to_dict()
