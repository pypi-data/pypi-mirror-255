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


class FeatureConviction(object):
    """
    Auto-generated OpenAPI type.

    The feature familiarity conviction values. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'familiarity_conviction_addition': 'dict[str, float]',
        'familiarity_conviction_removal': 'dict[str, float]'
    }

    attribute_map = {
        'familiarity_conviction_addition': 'familiarity_conviction_addition',
        'familiarity_conviction_removal': 'familiarity_conviction_removal'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, familiarity_conviction_addition=None, familiarity_conviction_removal=None, local_vars_configuration=None):  # noqa: E501
        """FeatureConviction - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._familiarity_conviction_addition = None
        self._familiarity_conviction_removal = None

        if familiarity_conviction_addition is not None:
            self.familiarity_conviction_addition = familiarity_conviction_addition
        if familiarity_conviction_removal is not None:
            self.familiarity_conviction_removal = familiarity_conviction_removal

    @property
    def familiarity_conviction_addition(self):
        """Get the familiarity_conviction_addition of this FeatureConviction.

        A dictionary of feature name to conviction value where each value is the familiarity conviction of adding the feature to the Model. 

        :return: The familiarity_conviction_addition of this FeatureConviction.
        :rtype: dict[str, float]
        """
        return self._familiarity_conviction_addition

    @familiarity_conviction_addition.setter
    def familiarity_conviction_addition(self, familiarity_conviction_addition):
        """Set the familiarity_conviction_addition of this FeatureConviction.

        A dictionary of feature name to conviction value where each value is the familiarity conviction of adding the feature to the Model. 

        :param familiarity_conviction_addition: The familiarity_conviction_addition of this FeatureConviction.
        :type familiarity_conviction_addition: dict[str, float]
        """

        self._familiarity_conviction_addition = familiarity_conviction_addition

    @property
    def familiarity_conviction_removal(self):
        """Get the familiarity_conviction_removal of this FeatureConviction.

        A dictionary of feature name to conviction value where each value is the familiarity conviction of removing the feature from the Model. 

        :return: The familiarity_conviction_removal of this FeatureConviction.
        :rtype: dict[str, float]
        """
        return self._familiarity_conviction_removal

    @familiarity_conviction_removal.setter
    def familiarity_conviction_removal(self, familiarity_conviction_removal):
        """Set the familiarity_conviction_removal of this FeatureConviction.

        A dictionary of feature name to conviction value where each value is the familiarity conviction of removing the feature from the Model. 

        :param familiarity_conviction_removal: The familiarity_conviction_removal of this FeatureConviction.
        :type familiarity_conviction_removal: dict[str, float]
        """

        self._familiarity_conviction_removal = familiarity_conviction_removal

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
        if not isinstance(other, FeatureConviction):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureConviction):
            return True

        return self.to_dict() != other.to_dict()
