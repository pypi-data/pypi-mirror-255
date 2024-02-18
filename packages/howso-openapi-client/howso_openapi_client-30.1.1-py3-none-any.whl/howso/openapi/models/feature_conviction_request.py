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


class FeatureConvictionRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of a feature conviction request.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'features': 'list[str]',
        'action_features': 'list[str]',
        'familiarity_conviction_addition': 'bool',
        'familiarity_conviction_removal': 'bool',
        'use_case_weights': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'features': 'features',
        'action_features': 'action_features',
        'familiarity_conviction_addition': 'familiarity_conviction_addition',
        'familiarity_conviction_removal': 'familiarity_conviction_removal',
        'use_case_weights': 'use_case_weights',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, features=None, action_features=None, familiarity_conviction_addition=True, familiarity_conviction_removal=None, use_case_weights=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """FeatureConvictionRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._features = None
        self._action_features = None
        self._familiarity_conviction_addition = None
        self._familiarity_conviction_removal = None
        self._use_case_weights = None
        self._weight_feature = None

        if features is not None:
            self.features = features
        if action_features is not None:
            self.action_features = action_features
        if familiarity_conviction_addition is not None:
            self.familiarity_conviction_addition = familiarity_conviction_addition
        if familiarity_conviction_removal is not None:
            self.familiarity_conviction_removal = familiarity_conviction_removal
        if use_case_weights is not None:
            self.use_case_weights = use_case_weights
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def features(self):
        """Get the features of this FeatureConvictionRequest.

        A list of feature names to calculate convictions. At least 2 features are required to get familiarity conviction and at least 3 features to get prediction conviction and prediction contribution. If not specified all features will be used. 

        :return: The features of this FeatureConvictionRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this FeatureConvictionRequest.

        A list of feature names to calculate convictions. At least 2 features are required to get familiarity conviction and at least 3 features to get prediction conviction and prediction contribution. If not specified all features will be used. 

        :param features: The features of this FeatureConvictionRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def action_features(self):
        """Get the action_features of this FeatureConvictionRequest.

        A list of feature names to be treated as action features during conviction calculation in order to determine the conviction of each feature against the set of action_features. If not specified, conviction is computed for each feature against the rest of the features as a whole. 

        :return: The action_features of this FeatureConvictionRequest.
        :rtype: list[str]
        """
        return self._action_features

    @action_features.setter
    def action_features(self, action_features):
        """Set the action_features of this FeatureConvictionRequest.

        A list of feature names to be treated as action features during conviction calculation in order to determine the conviction of each feature against the set of action_features. If not specified, conviction is computed for each feature against the rest of the features as a whole. 

        :param action_features: The action_features of this FeatureConvictionRequest.
        :type action_features: list[str]
        """

        self._action_features = action_features

    @property
    def familiarity_conviction_addition(self):
        """Get the familiarity_conviction_addition of this FeatureConvictionRequest.

        When true, calculate and output the familiarity conviction of adding the features.

        :return: The familiarity_conviction_addition of this FeatureConvictionRequest.
        :rtype: bool
        """
        return self._familiarity_conviction_addition

    @familiarity_conviction_addition.setter
    def familiarity_conviction_addition(self, familiarity_conviction_addition):
        """Set the familiarity_conviction_addition of this FeatureConvictionRequest.

        When true, calculate and output the familiarity conviction of adding the features.

        :param familiarity_conviction_addition: The familiarity_conviction_addition of this FeatureConvictionRequest.
        :type familiarity_conviction_addition: bool
        """

        self._familiarity_conviction_addition = familiarity_conviction_addition

    @property
    def familiarity_conviction_removal(self):
        """Get the familiarity_conviction_removal of this FeatureConvictionRequest.

        When true, calculate and output the familiarity conviction of removing the features.

        :return: The familiarity_conviction_removal of this FeatureConvictionRequest.
        :rtype: bool
        """
        return self._familiarity_conviction_removal

    @familiarity_conviction_removal.setter
    def familiarity_conviction_removal(self, familiarity_conviction_removal):
        """Set the familiarity_conviction_removal of this FeatureConvictionRequest.

        When true, calculate and output the familiarity conviction of removing the features.

        :param familiarity_conviction_removal: The familiarity_conviction_removal of this FeatureConvictionRequest.
        :type familiarity_conviction_removal: bool
        """

        self._familiarity_conviction_removal = familiarity_conviction_removal

    @property
    def use_case_weights(self):
        """Get the use_case_weights of this FeatureConvictionRequest.

        If set to True will scale influence weights by each case's `weight_feature` weight.

        :return: The use_case_weights of this FeatureConvictionRequest.
        :rtype: bool
        """
        return self._use_case_weights

    @use_case_weights.setter
    def use_case_weights(self, use_case_weights):
        """Set the use_case_weights of this FeatureConvictionRequest.

        If set to True will scale influence weights by each case's `weight_feature` weight.

        :param use_case_weights: The use_case_weights of this FeatureConvictionRequest.
        :type use_case_weights: bool
        """

        self._use_case_weights = use_case_weights

    @property
    def weight_feature(self):
        """Get the weight_feature of this FeatureConvictionRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :return: The weight_feature of this FeatureConvictionRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this FeatureConvictionRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :param weight_feature: The weight_feature of this FeatureConvictionRequest.
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
        if not isinstance(other, FeatureConvictionRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureConvictionRequest):
            return True

        return self.to_dict() != other.to_dict()
