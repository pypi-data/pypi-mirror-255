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


class FeatureResidualsRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of a feature residuals request. 
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
        'robust_hyperparameters': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'action_feature': 'action_feature',
        'robust': 'robust',
        'robust_hyperparameters': 'robust_hyperparameters',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, action_feature=None, robust=None, robust_hyperparameters=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """FeatureResidualsRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_feature = None
        self._robust = None
        self._robust_hyperparameters = None
        self._weight_feature = None

        if action_feature is not None:
            self.action_feature = action_feature
        if robust is not None:
            self.robust = robust
        if robust_hyperparameters is not None:
            self.robust_hyperparameters = robust_hyperparameters
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def action_feature(self):
        """Get the action_feature of this FeatureResidualsRequest.

        When specified, will attempt to return residuals that were computed for this specified action_feature. Note: \".targetless\" is the action feature used during targetless analysis. 

        :return: The action_feature of this FeatureResidualsRequest.
        :rtype: str
        """
        return self._action_feature

    @action_feature.setter
    def action_feature(self, action_feature):
        """Set the action_feature of this FeatureResidualsRequest.

        When specified, will attempt to return residuals that were computed for this specified action_feature. Note: \".targetless\" is the action feature used during targetless analysis. 

        :param action_feature: The action_feature of this FeatureResidualsRequest.
        :type action_feature: str
        """

        self._action_feature = action_feature

    @property
    def robust(self):
        """Get the robust of this FeatureResidualsRequest.

        When specified, will attempt to return residuals that were computed with the specified robust or non-robust type. 

        :return: The robust of this FeatureResidualsRequest.
        :rtype: bool
        """
        return self._robust

    @robust.setter
    def robust(self, robust):
        """Set the robust of this FeatureResidualsRequest.

        When specified, will attempt to return residuals that were computed with the specified robust or non-robust type. 

        :param robust: The robust of this FeatureResidualsRequest.
        :type robust: bool
        """

        self._robust = robust

    @property
    def robust_hyperparameters(self):
        """Get the robust_hyperparameters of this FeatureResidualsRequest.

        When specified, will attempt to return residuals that were computed using hyperparameters with the specified robust or non-robust type. 

        :return: The robust_hyperparameters of this FeatureResidualsRequest.
        :rtype: bool
        """
        return self._robust_hyperparameters

    @robust_hyperparameters.setter
    def robust_hyperparameters(self, robust_hyperparameters):
        """Set the robust_hyperparameters of this FeatureResidualsRequest.

        When specified, will attempt to return residuals that were computed using hyperparameters with the specified robust or non-robust type. 

        :param robust_hyperparameters: The robust_hyperparameters of this FeatureResidualsRequest.
        :type robust_hyperparameters: bool
        """

        self._robust_hyperparameters = robust_hyperparameters

    @property
    def weight_feature(self):
        """Get the weight_feature of this FeatureResidualsRequest.

        When specified, will attempt to return residuals that were computed using this weight_feature. 

        :return: The weight_feature of this FeatureResidualsRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this FeatureResidualsRequest.

        When specified, will attempt to return residuals that were computed using this weight_feature. 

        :param weight_feature: The weight_feature of this FeatureResidualsRequest.
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
        if not isinstance(other, FeatureResidualsRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureResidualsRequest):
            return True

        return self.to_dict() != other.to_dict()
