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


class ReactIntoFeaturesRequest(object):
    """
    Auto-generated OpenAPI type.

    Request body for react into features.
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
        'familiarity_conviction_addition': 'str',
        'familiarity_conviction_removal': 'str',
        'influence_weight_entropy': 'str',
        'p_value_of_addition': 'str',
        'p_value_of_removal': 'str',
        'distance_contribution': 'str',
        'similarity_conviction': 'str',
        'use_case_weights': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'features': 'features',
        'familiarity_conviction_addition': 'familiarity_conviction_addition',
        'familiarity_conviction_removal': 'familiarity_conviction_removal',
        'influence_weight_entropy': 'influence_weight_entropy',
        'p_value_of_addition': 'p_value_of_addition',
        'p_value_of_removal': 'p_value_of_removal',
        'distance_contribution': 'distance_contribution',
        'similarity_conviction': 'similarity_conviction',
        'use_case_weights': 'use_case_weights',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, features=None, familiarity_conviction_addition=None, familiarity_conviction_removal=None, influence_weight_entropy=None, p_value_of_addition=None, p_value_of_removal=None, distance_contribution=None, similarity_conviction=None, use_case_weights=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """ReactIntoFeaturesRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._features = None
        self._familiarity_conviction_addition = None
        self._familiarity_conviction_removal = None
        self._influence_weight_entropy = None
        self._p_value_of_addition = None
        self._p_value_of_removal = None
        self._distance_contribution = None
        self._similarity_conviction = None
        self._use_case_weights = None
        self._weight_feature = None

        if features is not None:
            self.features = features
        if familiarity_conviction_addition is not None:
            self.familiarity_conviction_addition = familiarity_conviction_addition
        if familiarity_conviction_removal is not None:
            self.familiarity_conviction_removal = familiarity_conviction_removal
        if influence_weight_entropy is not None:
            self.influence_weight_entropy = influence_weight_entropy
        if p_value_of_addition is not None:
            self.p_value_of_addition = p_value_of_addition
        if p_value_of_removal is not None:
            self.p_value_of_removal = p_value_of_removal
        if distance_contribution is not None:
            self.distance_contribution = distance_contribution
        if similarity_conviction is not None:
            self.similarity_conviction = similarity_conviction
        if use_case_weights is not None:
            self.use_case_weights = use_case_weights
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def features(self):
        """Get the features of this ReactIntoFeaturesRequest.

        The features to use when calculating convictions.

        :return: The features of this ReactIntoFeaturesRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this ReactIntoFeaturesRequest.

        The features to use when calculating convictions.

        :param features: The features of this ReactIntoFeaturesRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def familiarity_conviction_addition(self):
        """Get the familiarity_conviction_addition of this ReactIntoFeaturesRequest.

        The name of the feature to store conviction of addition values.

        :return: The familiarity_conviction_addition of this ReactIntoFeaturesRequest.
        :rtype: str
        """
        return self._familiarity_conviction_addition

    @familiarity_conviction_addition.setter
    def familiarity_conviction_addition(self, familiarity_conviction_addition):
        """Set the familiarity_conviction_addition of this ReactIntoFeaturesRequest.

        The name of the feature to store conviction of addition values.

        :param familiarity_conviction_addition: The familiarity_conviction_addition of this ReactIntoFeaturesRequest.
        :type familiarity_conviction_addition: str
        """

        self._familiarity_conviction_addition = familiarity_conviction_addition

    @property
    def familiarity_conviction_removal(self):
        """Get the familiarity_conviction_removal of this ReactIntoFeaturesRequest.

        The name of the feature to store conviction of removal values.

        :return: The familiarity_conviction_removal of this ReactIntoFeaturesRequest.
        :rtype: str
        """
        return self._familiarity_conviction_removal

    @familiarity_conviction_removal.setter
    def familiarity_conviction_removal(self, familiarity_conviction_removal):
        """Set the familiarity_conviction_removal of this ReactIntoFeaturesRequest.

        The name of the feature to store conviction of removal values.

        :param familiarity_conviction_removal: The familiarity_conviction_removal of this ReactIntoFeaturesRequest.
        :type familiarity_conviction_removal: str
        """

        self._familiarity_conviction_removal = familiarity_conviction_removal

    @property
    def influence_weight_entropy(self):
        """Get the influence_weight_entropy of this ReactIntoFeaturesRequest.

        The name of the feature to store influence weight entropy values.

        :return: The influence_weight_entropy of this ReactIntoFeaturesRequest.
        :rtype: str
        """
        return self._influence_weight_entropy

    @influence_weight_entropy.setter
    def influence_weight_entropy(self, influence_weight_entropy):
        """Set the influence_weight_entropy of this ReactIntoFeaturesRequest.

        The name of the feature to store influence weight entropy values.

        :param influence_weight_entropy: The influence_weight_entropy of this ReactIntoFeaturesRequest.
        :type influence_weight_entropy: str
        """

        self._influence_weight_entropy = influence_weight_entropy

    @property
    def p_value_of_addition(self):
        """Get the p_value_of_addition of this ReactIntoFeaturesRequest.

        The name of the feature to store p value of addition values.

        :return: The p_value_of_addition of this ReactIntoFeaturesRequest.
        :rtype: str
        """
        return self._p_value_of_addition

    @p_value_of_addition.setter
    def p_value_of_addition(self, p_value_of_addition):
        """Set the p_value_of_addition of this ReactIntoFeaturesRequest.

        The name of the feature to store p value of addition values.

        :param p_value_of_addition: The p_value_of_addition of this ReactIntoFeaturesRequest.
        :type p_value_of_addition: str
        """

        self._p_value_of_addition = p_value_of_addition

    @property
    def p_value_of_removal(self):
        """Get the p_value_of_removal of this ReactIntoFeaturesRequest.

        The name of the feature to store p value of removal values.

        :return: The p_value_of_removal of this ReactIntoFeaturesRequest.
        :rtype: str
        """
        return self._p_value_of_removal

    @p_value_of_removal.setter
    def p_value_of_removal(self, p_value_of_removal):
        """Set the p_value_of_removal of this ReactIntoFeaturesRequest.

        The name of the feature to store p value of removal values.

        :param p_value_of_removal: The p_value_of_removal of this ReactIntoFeaturesRequest.
        :type p_value_of_removal: str
        """

        self._p_value_of_removal = p_value_of_removal

    @property
    def distance_contribution(self):
        """Get the distance_contribution of this ReactIntoFeaturesRequest.

        The name of the feature to store distance contribution ratios for each case.

        :return: The distance_contribution of this ReactIntoFeaturesRequest.
        :rtype: str
        """
        return self._distance_contribution

    @distance_contribution.setter
    def distance_contribution(self, distance_contribution):
        """Set the distance_contribution of this ReactIntoFeaturesRequest.

        The name of the feature to store distance contribution ratios for each case.

        :param distance_contribution: The distance_contribution of this ReactIntoFeaturesRequest.
        :type distance_contribution: str
        """

        self._distance_contribution = distance_contribution

    @property
    def similarity_conviction(self):
        """Get the similarity_conviction of this ReactIntoFeaturesRequest.

        The name of the feature to store similarity conviction values for each case.

        :return: The similarity_conviction of this ReactIntoFeaturesRequest.
        :rtype: str
        """
        return self._similarity_conviction

    @similarity_conviction.setter
    def similarity_conviction(self, similarity_conviction):
        """Set the similarity_conviction of this ReactIntoFeaturesRequest.

        The name of the feature to store similarity conviction values for each case.

        :param similarity_conviction: The similarity_conviction of this ReactIntoFeaturesRequest.
        :type similarity_conviction: str
        """

        self._similarity_conviction = similarity_conviction

    @property
    def use_case_weights(self):
        """Get the use_case_weights of this ReactIntoFeaturesRequest.

        If set to True will scale influence weights by each case's `weight_feature` weight.

        :return: The use_case_weights of this ReactIntoFeaturesRequest.
        :rtype: bool
        """
        return self._use_case_weights

    @use_case_weights.setter
    def use_case_weights(self, use_case_weights):
        """Set the use_case_weights of this ReactIntoFeaturesRequest.

        If set to True will scale influence weights by each case's `weight_feature` weight.

        :param use_case_weights: The use_case_weights of this ReactIntoFeaturesRequest.
        :type use_case_weights: bool
        """

        self._use_case_weights = use_case_weights

    @property
    def weight_feature(self):
        """Get the weight_feature of this ReactIntoFeaturesRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :return: The weight_feature of this ReactIntoFeaturesRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this ReactIntoFeaturesRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :param weight_feature: The weight_feature of this ReactIntoFeaturesRequest.
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
        if not isinstance(other, ReactIntoFeaturesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactIntoFeaturesRequest):
            return True

        return self.to_dict() != other.to_dict()
