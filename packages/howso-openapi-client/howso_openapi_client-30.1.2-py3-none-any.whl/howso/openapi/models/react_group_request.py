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


class ReactGroupRequest(object):
    """
    Auto-generated OpenAPI type.

    Request body for react group.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'new_cases': 'list[list[list[object]]]',
        'trainees_to_compare': 'list[str]',
        'features': 'list[str]',
        'familiarity_conviction_addition': 'bool',
        'familiarity_conviction_removal': 'bool',
        'kl_divergence_addition': 'bool',
        'kl_divergence_removal': 'bool',
        'p_value_of_addition': 'bool',
        'p_value_of_removal': 'bool',
        'distance_contributions': 'bool',
        'use_case_weights': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'new_cases': 'new_cases',
        'trainees_to_compare': 'trainees_to_compare',
        'features': 'features',
        'familiarity_conviction_addition': 'familiarity_conviction_addition',
        'familiarity_conviction_removal': 'familiarity_conviction_removal',
        'kl_divergence_addition': 'kl_divergence_addition',
        'kl_divergence_removal': 'kl_divergence_removal',
        'p_value_of_addition': 'p_value_of_addition',
        'p_value_of_removal': 'p_value_of_removal',
        'distance_contributions': 'distance_contributions',
        'use_case_weights': 'use_case_weights',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, new_cases=None, trainees_to_compare=None, features=None, familiarity_conviction_addition=None, familiarity_conviction_removal=None, kl_divergence_addition=None, kl_divergence_removal=None, p_value_of_addition=None, p_value_of_removal=None, distance_contributions=None, use_case_weights=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """ReactGroupRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._new_cases = None
        self._trainees_to_compare = None
        self._features = None
        self._familiarity_conviction_addition = None
        self._familiarity_conviction_removal = None
        self._kl_divergence_addition = None
        self._kl_divergence_removal = None
        self._p_value_of_addition = None
        self._p_value_of_removal = None
        self._distance_contributions = None
        self._use_case_weights = None
        self._weight_feature = None

        if new_cases is not None:
            self.new_cases = new_cases
        if trainees_to_compare is not None:
            self.trainees_to_compare = trainees_to_compare
        if features is not None:
            self.features = features
        if familiarity_conviction_addition is not None:
            self.familiarity_conviction_addition = familiarity_conviction_addition
        if familiarity_conviction_removal is not None:
            self.familiarity_conviction_removal = familiarity_conviction_removal
        if kl_divergence_addition is not None:
            self.kl_divergence_addition = kl_divergence_addition
        if kl_divergence_removal is not None:
            self.kl_divergence_removal = kl_divergence_removal
        if p_value_of_addition is not None:
            self.p_value_of_addition = p_value_of_addition
        if p_value_of_removal is not None:
            self.p_value_of_removal = p_value_of_removal
        if distance_contributions is not None:
            self.distance_contributions = distance_contributions
        if use_case_weights is not None:
            self.use_case_weights = use_case_weights
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def new_cases(self):
        """Get the new_cases of this ReactGroupRequest.

        One or more groupings of cases to compare against.

        :return: The new_cases of this ReactGroupRequest.
        :rtype: list[list[list[object]]]
        """
        return self._new_cases

    @new_cases.setter
    def new_cases(self, new_cases):
        """Set the new_cases of this ReactGroupRequest.

        One or more groupings of cases to compare against.

        :param new_cases: The new_cases of this ReactGroupRequest.
        :type new_cases: list[list[list[object]]]
        """
        if (self.local_vars_configuration.client_side_validation and
                new_cases is not None and len(new_cases) < 1):
            raise ValueError("Invalid value for `new_cases`, number of items must be greater than or equal to `1`")  # noqa: E501

        self._new_cases = new_cases

    @property
    def trainees_to_compare(self):
        """Get the trainees_to_compare of this ReactGroupRequest.

        IDs of other trainees to compare the cases of to this trainee. If specified ignores \"new_cases\" parameter. 

        :return: The trainees_to_compare of this ReactGroupRequest.
        :rtype: list[str]
        """
        return self._trainees_to_compare

    @trainees_to_compare.setter
    def trainees_to_compare(self, trainees_to_compare):
        """Set the trainees_to_compare of this ReactGroupRequest.

        IDs of other trainees to compare the cases of to this trainee. If specified ignores \"new_cases\" parameter. 

        :param trainees_to_compare: The trainees_to_compare of this ReactGroupRequest.
        :type trainees_to_compare: list[str]
        """

        self._trainees_to_compare = trainees_to_compare

    @property
    def features(self):
        """Get the features of this ReactGroupRequest.

        The features to use when calculating convictions.

        :return: The features of this ReactGroupRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this ReactGroupRequest.

        The features to use when calculating convictions.

        :param features: The features of this ReactGroupRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def familiarity_conviction_addition(self):
        """Get the familiarity_conviction_addition of this ReactGroupRequest.

        Calculate and output the familiarity conviction of adding the cases.

        :return: The familiarity_conviction_addition of this ReactGroupRequest.
        :rtype: bool
        """
        return self._familiarity_conviction_addition

    @familiarity_conviction_addition.setter
    def familiarity_conviction_addition(self, familiarity_conviction_addition):
        """Set the familiarity_conviction_addition of this ReactGroupRequest.

        Calculate and output the familiarity conviction of adding the cases.

        :param familiarity_conviction_addition: The familiarity_conviction_addition of this ReactGroupRequest.
        :type familiarity_conviction_addition: bool
        """

        self._familiarity_conviction_addition = familiarity_conviction_addition

    @property
    def familiarity_conviction_removal(self):
        """Get the familiarity_conviction_removal of this ReactGroupRequest.

        Calculate and output the familiarity conviction of removing the cases.

        :return: The familiarity_conviction_removal of this ReactGroupRequest.
        :rtype: bool
        """
        return self._familiarity_conviction_removal

    @familiarity_conviction_removal.setter
    def familiarity_conviction_removal(self, familiarity_conviction_removal):
        """Set the familiarity_conviction_removal of this ReactGroupRequest.

        Calculate and output the familiarity conviction of removing the cases.

        :param familiarity_conviction_removal: The familiarity_conviction_removal of this ReactGroupRequest.
        :type familiarity_conviction_removal: bool
        """

        self._familiarity_conviction_removal = familiarity_conviction_removal

    @property
    def kl_divergence_addition(self):
        """Get the kl_divergence_addition of this ReactGroupRequest.

        Calculate and output the KL divergence of adding the cases.

        :return: The kl_divergence_addition of this ReactGroupRequest.
        :rtype: bool
        """
        return self._kl_divergence_addition

    @kl_divergence_addition.setter
    def kl_divergence_addition(self, kl_divergence_addition):
        """Set the kl_divergence_addition of this ReactGroupRequest.

        Calculate and output the KL divergence of adding the cases.

        :param kl_divergence_addition: The kl_divergence_addition of this ReactGroupRequest.
        :type kl_divergence_addition: bool
        """

        self._kl_divergence_addition = kl_divergence_addition

    @property
    def kl_divergence_removal(self):
        """Get the kl_divergence_removal of this ReactGroupRequest.

        Calculate and output the KL divergence of removing the cases.

        :return: The kl_divergence_removal of this ReactGroupRequest.
        :rtype: bool
        """
        return self._kl_divergence_removal

    @kl_divergence_removal.setter
    def kl_divergence_removal(self, kl_divergence_removal):
        """Set the kl_divergence_removal of this ReactGroupRequest.

        Calculate and output the KL divergence of removing the cases.

        :param kl_divergence_removal: The kl_divergence_removal of this ReactGroupRequest.
        :type kl_divergence_removal: bool
        """

        self._kl_divergence_removal = kl_divergence_removal

    @property
    def p_value_of_addition(self):
        """Get the p_value_of_addition of this ReactGroupRequest.

        When true, output p value of addition.

        :return: The p_value_of_addition of this ReactGroupRequest.
        :rtype: bool
        """
        return self._p_value_of_addition

    @p_value_of_addition.setter
    def p_value_of_addition(self, p_value_of_addition):
        """Set the p_value_of_addition of this ReactGroupRequest.

        When true, output p value of addition.

        :param p_value_of_addition: The p_value_of_addition of this ReactGroupRequest.
        :type p_value_of_addition: bool
        """

        self._p_value_of_addition = p_value_of_addition

    @property
    def p_value_of_removal(self):
        """Get the p_value_of_removal of this ReactGroupRequest.

        When true, output p value of removal.

        :return: The p_value_of_removal of this ReactGroupRequest.
        :rtype: bool
        """
        return self._p_value_of_removal

    @p_value_of_removal.setter
    def p_value_of_removal(self, p_value_of_removal):
        """Set the p_value_of_removal of this ReactGroupRequest.

        When true, output p value of removal.

        :param p_value_of_removal: The p_value_of_removal of this ReactGroupRequest.
        :type p_value_of_removal: bool
        """

        self._p_value_of_removal = p_value_of_removal

    @property
    def distance_contributions(self):
        """Get the distance_contributions of this ReactGroupRequest.

        When true, calculate and output distance contribution ratios for each case.

        :return: The distance_contributions of this ReactGroupRequest.
        :rtype: bool
        """
        return self._distance_contributions

    @distance_contributions.setter
    def distance_contributions(self, distance_contributions):
        """Set the distance_contributions of this ReactGroupRequest.

        When true, calculate and output distance contribution ratios for each case.

        :param distance_contributions: The distance_contributions of this ReactGroupRequest.
        :type distance_contributions: bool
        """

        self._distance_contributions = distance_contributions

    @property
    def use_case_weights(self):
        """Get the use_case_weights of this ReactGroupRequest.

        If set to True will scale influence weights by each case's `weight_feature` weight.

        :return: The use_case_weights of this ReactGroupRequest.
        :rtype: bool
        """
        return self._use_case_weights

    @use_case_weights.setter
    def use_case_weights(self, use_case_weights):
        """Set the use_case_weights of this ReactGroupRequest.

        If set to True will scale influence weights by each case's `weight_feature` weight.

        :param use_case_weights: The use_case_weights of this ReactGroupRequest.
        :type use_case_weights: bool
        """

        self._use_case_weights = use_case_weights

    @property
    def weight_feature(self):
        """Get the weight_feature of this ReactGroupRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :return: The weight_feature of this ReactGroupRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this ReactGroupRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :param weight_feature: The weight_feature of this ReactGroupRequest.
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
        if not isinstance(other, ReactGroupRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactGroupRequest):
            return True

        return self.to_dict() != other.to_dict()
