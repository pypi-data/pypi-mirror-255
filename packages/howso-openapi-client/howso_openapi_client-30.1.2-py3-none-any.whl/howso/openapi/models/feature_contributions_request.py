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


class FeatureContributionsRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of a feature contributions request. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'action_feature': 'str',
        'robust': 'bool',
        'directional': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'action_feature': 'action_feature',
        'robust': 'robust',
        'directional': 'directional',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, action_feature=None, robust=None, directional=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """FeatureContributionsRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_feature = None
        self._robust = None
        self._directional = None
        self._weight_feature = None

        self.action_feature = action_feature
        if robust is not None:
            self.robust = robust
        if directional is not None:
            self.directional = directional
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def action_feature(self):
        """Get the action_feature of this FeatureContributionsRequest.

        When specified, will attempt to return contributions that were computed for this specified action_feature. 

        :return: The action_feature of this FeatureContributionsRequest.
        :rtype: str
        """
        return self._action_feature

    @action_feature.setter
    def action_feature(self, action_feature):
        """Set the action_feature of this FeatureContributionsRequest.

        When specified, will attempt to return contributions that were computed for this specified action_feature. 

        :param action_feature: The action_feature of this FeatureContributionsRequest.
        :type action_feature: str
        """
        if self.local_vars_configuration.client_side_validation and action_feature is None:  # noqa: E501
            raise ValueError("Invalid value for `action_feature`, must not be `None`")  # noqa: E501

        self._action_feature = action_feature

    @property
    def robust(self):
        """Get the robust of this FeatureContributionsRequest.

        When specified, will attempt to return contributions that were computed with the specified robust or non-robust type. 

        :return: The robust of this FeatureContributionsRequest.
        :rtype: bool
        """
        return self._robust

    @robust.setter
    def robust(self, robust):
        """Set the robust of this FeatureContributionsRequest.

        When specified, will attempt to return contributions that were computed with the specified robust or non-robust type. 

        :param robust: The robust of this FeatureContributionsRequest.
        :type robust: bool
        """

        self._robust = robust

    @property
    def directional(self):
        """Get the directional of this FeatureContributionsRequest.

        If false returns absolute feature contributions. If true, returns directional feature contributions. 

        :return: The directional of this FeatureContributionsRequest.
        :rtype: bool
        """
        return self._directional

    @directional.setter
    def directional(self, directional):
        """Set the directional of this FeatureContributionsRequest.

        If false returns absolute feature contributions. If true, returns directional feature contributions. 

        :param directional: The directional of this FeatureContributionsRequest.
        :type directional: bool
        """

        self._directional = directional

    @property
    def weight_feature(self):
        """Get the weight_feature of this FeatureContributionsRequest.

        When specified, will attempt to return contributions that were computed using this weight_feature. 

        :return: The weight_feature of this FeatureContributionsRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this FeatureContributionsRequest.

        When specified, will attempt to return contributions that were computed using this weight_feature. 

        :param weight_feature: The weight_feature of this FeatureContributionsRequest.
        :type weight_feature: str
        """

        self._weight_feature = weight_feature

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
        if not isinstance(other, FeatureContributionsRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureContributionsRequest):
            return True

        return self.to_dict() != other.to_dict()
