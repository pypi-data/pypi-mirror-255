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


class ReactSeriesResponseContent(object):
    """
    Auto-generated OpenAPI type.

    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'boundary_cases': 'list[list[object]]',
        'categorical_action_probabilities': 'list[dict[str, object]]',
        'derivation_parameters': 'list[DerivationParameters]',
        'feature_residuals': 'list[dict[str, object]]',
        'outlying_feature_values': 'list[dict[str, DetailsResponseOutlyingFeatureValuesInnerValue]]',
        'influential_cases': 'list[list[object]]',
        'most_similar_cases': 'list[list[object]]',
        'observational_errors': 'list[dict[str, float]]',
        'feature_mda': 'list[dict[str, float]]',
        'feature_mda_ex_post': 'list[dict[str, float]]',
        'feature_contributions': 'list[dict[str, float]]',
        'case_feature_contributions': 'list[dict[str, float]]',
        'case_mda': 'list[list[dict[str, object]]]',
        'case_contributions': 'list[list[dict[str, object]]]',
        'case_feature_residuals': 'list[dict[str, float]]',
        'local_case_feature_residual_convictions': 'list[dict[str, float]]',
        'global_case_feature_residual_convictions': 'list[dict[str, float]]',
        'hypothetical_values': 'list[dict[str, object]]',
        'distance_ratio': 'list[float]',
        'distance_ratio_parts': 'list[DetailsResponseDistanceRatioPartsInner]',
        'distance_contribution': 'list[float]',
        'similarity_conviction': 'list[float]',
        'most_similar_case_indices': 'list[list[dict[str, object]]]',
        'action_features': 'list[str]',
        'series': 'list[list[list[object]]]'
    }

    attribute_map = {
        'boundary_cases': 'boundary_cases',
        'categorical_action_probabilities': 'categorical_action_probabilities',
        'derivation_parameters': 'derivation_parameters',
        'feature_residuals': 'feature_residuals',
        'outlying_feature_values': 'outlying_feature_values',
        'influential_cases': 'influential_cases',
        'most_similar_cases': 'most_similar_cases',
        'observational_errors': 'observational_errors',
        'feature_mda': 'feature_mda',
        'feature_mda_ex_post': 'feature_mda_ex_post',
        'feature_contributions': 'feature_contributions',
        'case_feature_contributions': 'case_feature_contributions',
        'case_mda': 'case_mda',
        'case_contributions': 'case_contributions',
        'case_feature_residuals': 'case_feature_residuals',
        'local_case_feature_residual_convictions': 'local_case_feature_residual_convictions',
        'global_case_feature_residual_convictions': 'global_case_feature_residual_convictions',
        'hypothetical_values': 'hypothetical_values',
        'distance_ratio': 'distance_ratio',
        'distance_ratio_parts': 'distance_ratio_parts',
        'distance_contribution': 'distance_contribution',
        'similarity_conviction': 'similarity_conviction',
        'most_similar_case_indices': 'most_similar_case_indices',
        'action_features': 'action_features',
        'series': 'series'
    }

    nullable_attributes = [
        'action_features', 
        'series', 
    ]

    discriminator = None

    def __init__(self, boundary_cases=None, categorical_action_probabilities=None, derivation_parameters=None, feature_residuals=None, outlying_feature_values=None, influential_cases=None, most_similar_cases=None, observational_errors=None, feature_mda=None, feature_mda_ex_post=None, feature_contributions=None, case_feature_contributions=None, case_mda=None, case_contributions=None, case_feature_residuals=None, local_case_feature_residual_convictions=None, global_case_feature_residual_convictions=None, hypothetical_values=None, distance_ratio=None, distance_ratio_parts=None, distance_contribution=None, similarity_conviction=None, most_similar_case_indices=None, action_features=None, series=None, local_vars_configuration=None):  # noqa: E501
        """ReactSeriesResponseContent - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._boundary_cases = None
        self._categorical_action_probabilities = None
        self._derivation_parameters = None
        self._feature_residuals = None
        self._outlying_feature_values = None
        self._influential_cases = None
        self._most_similar_cases = None
        self._observational_errors = None
        self._feature_mda = None
        self._feature_mda_ex_post = None
        self._feature_contributions = None
        self._case_feature_contributions = None
        self._case_mda = None
        self._case_contributions = None
        self._case_feature_residuals = None
        self._local_case_feature_residual_convictions = None
        self._global_case_feature_residual_convictions = None
        self._hypothetical_values = None
        self._distance_ratio = None
        self._distance_ratio_parts = None
        self._distance_contribution = None
        self._similarity_conviction = None
        self._most_similar_case_indices = None
        self._action_features = None
        self._series = None

        if boundary_cases is not None:
            self.boundary_cases = boundary_cases
        if categorical_action_probabilities is not None:
            self.categorical_action_probabilities = categorical_action_probabilities
        if derivation_parameters is not None:
            self.derivation_parameters = derivation_parameters
        if feature_residuals is not None:
            self.feature_residuals = feature_residuals
        if outlying_feature_values is not None:
            self.outlying_feature_values = outlying_feature_values
        if influential_cases is not None:
            self.influential_cases = influential_cases
        if most_similar_cases is not None:
            self.most_similar_cases = most_similar_cases
        if observational_errors is not None:
            self.observational_errors = observational_errors
        if feature_mda is not None:
            self.feature_mda = feature_mda
        if feature_mda_ex_post is not None:
            self.feature_mda_ex_post = feature_mda_ex_post
        if feature_contributions is not None:
            self.feature_contributions = feature_contributions
        if case_feature_contributions is not None:
            self.case_feature_contributions = case_feature_contributions
        if case_mda is not None:
            self.case_mda = case_mda
        if case_contributions is not None:
            self.case_contributions = case_contributions
        if case_feature_residuals is not None:
            self.case_feature_residuals = case_feature_residuals
        if local_case_feature_residual_convictions is not None:
            self.local_case_feature_residual_convictions = local_case_feature_residual_convictions
        if global_case_feature_residual_convictions is not None:
            self.global_case_feature_residual_convictions = global_case_feature_residual_convictions
        if hypothetical_values is not None:
            self.hypothetical_values = hypothetical_values
        if distance_ratio is not None:
            self.distance_ratio = distance_ratio
        if distance_ratio_parts is not None:
            self.distance_ratio_parts = distance_ratio_parts
        if distance_contribution is not None:
            self.distance_contribution = distance_contribution
        if similarity_conviction is not None:
            self.similarity_conviction = similarity_conviction
        if most_similar_case_indices is not None:
            self.most_similar_case_indices = most_similar_case_indices
        self.action_features = action_features
        self.series = series

    @property
    def boundary_cases(self):
        """Get the boundary_cases of this ReactSeriesResponseContent.


        :return: The boundary_cases of this ReactSeriesResponseContent.
        :rtype: list[list[object]]
        """
        return self._boundary_cases

    @boundary_cases.setter
    def boundary_cases(self, boundary_cases):
        """Set the boundary_cases of this ReactSeriesResponseContent.


        :param boundary_cases: The boundary_cases of this ReactSeriesResponseContent.
        :type boundary_cases: list[list[object]]
        """

        self._boundary_cases = boundary_cases

    @property
    def categorical_action_probabilities(self):
        """Get the categorical_action_probabilities of this ReactSeriesResponseContent.


        :return: The categorical_action_probabilities of this ReactSeriesResponseContent.
        :rtype: list[dict[str, object]]
        """
        return self._categorical_action_probabilities

    @categorical_action_probabilities.setter
    def categorical_action_probabilities(self, categorical_action_probabilities):
        """Set the categorical_action_probabilities of this ReactSeriesResponseContent.


        :param categorical_action_probabilities: The categorical_action_probabilities of this ReactSeriesResponseContent.
        :type categorical_action_probabilities: list[dict[str, object]]
        """

        self._categorical_action_probabilities = categorical_action_probabilities

    @property
    def derivation_parameters(self):
        """Get the derivation_parameters of this ReactSeriesResponseContent.


        :return: The derivation_parameters of this ReactSeriesResponseContent.
        :rtype: list[DerivationParameters]
        """
        return self._derivation_parameters

    @derivation_parameters.setter
    def derivation_parameters(self, derivation_parameters):
        """Set the derivation_parameters of this ReactSeriesResponseContent.


        :param derivation_parameters: The derivation_parameters of this ReactSeriesResponseContent.
        :type derivation_parameters: list[DerivationParameters]
        """

        self._derivation_parameters = derivation_parameters

    @property
    def feature_residuals(self):
        """Get the feature_residuals of this ReactSeriesResponseContent.


        :return: The feature_residuals of this ReactSeriesResponseContent.
        :rtype: list[dict[str, object]]
        """
        return self._feature_residuals

    @feature_residuals.setter
    def feature_residuals(self, feature_residuals):
        """Set the feature_residuals of this ReactSeriesResponseContent.


        :param feature_residuals: The feature_residuals of this ReactSeriesResponseContent.
        :type feature_residuals: list[dict[str, object]]
        """

        self._feature_residuals = feature_residuals

    @property
    def outlying_feature_values(self):
        """Get the outlying_feature_values of this ReactSeriesResponseContent.


        :return: The outlying_feature_values of this ReactSeriesResponseContent.
        :rtype: list[dict[str, DetailsResponseOutlyingFeatureValuesInnerValue]]
        """
        return self._outlying_feature_values

    @outlying_feature_values.setter
    def outlying_feature_values(self, outlying_feature_values):
        """Set the outlying_feature_values of this ReactSeriesResponseContent.


        :param outlying_feature_values: The outlying_feature_values of this ReactSeriesResponseContent.
        :type outlying_feature_values: list[dict[str, DetailsResponseOutlyingFeatureValuesInnerValue]]
        """

        self._outlying_feature_values = outlying_feature_values

    @property
    def influential_cases(self):
        """Get the influential_cases of this ReactSeriesResponseContent.


        :return: The influential_cases of this ReactSeriesResponseContent.
        :rtype: list[list[object]]
        """
        return self._influential_cases

    @influential_cases.setter
    def influential_cases(self, influential_cases):
        """Set the influential_cases of this ReactSeriesResponseContent.


        :param influential_cases: The influential_cases of this ReactSeriesResponseContent.
        :type influential_cases: list[list[object]]
        """

        self._influential_cases = influential_cases

    @property
    def most_similar_cases(self):
        """Get the most_similar_cases of this ReactSeriesResponseContent.


        :return: The most_similar_cases of this ReactSeriesResponseContent.
        :rtype: list[list[object]]
        """
        return self._most_similar_cases

    @most_similar_cases.setter
    def most_similar_cases(self, most_similar_cases):
        """Set the most_similar_cases of this ReactSeriesResponseContent.


        :param most_similar_cases: The most_similar_cases of this ReactSeriesResponseContent.
        :type most_similar_cases: list[list[object]]
        """

        self._most_similar_cases = most_similar_cases

    @property
    def observational_errors(self):
        """Get the observational_errors of this ReactSeriesResponseContent.

        Observational errors for all features as defined in feature attributes.

        :return: The observational_errors of this ReactSeriesResponseContent.
        :rtype: list[dict[str, float]]
        """
        return self._observational_errors

    @observational_errors.setter
    def observational_errors(self, observational_errors):
        """Set the observational_errors of this ReactSeriesResponseContent.

        Observational errors for all features as defined in feature attributes.

        :param observational_errors: The observational_errors of this ReactSeriesResponseContent.
        :type observational_errors: list[dict[str, float]]
        """

        self._observational_errors = observational_errors

    @property
    def feature_mda(self):
        """Get the feature_mda of this ReactSeriesResponseContent.


        :return: The feature_mda of this ReactSeriesResponseContent.
        :rtype: list[dict[str, float]]
        """
        return self._feature_mda

    @feature_mda.setter
    def feature_mda(self, feature_mda):
        """Set the feature_mda of this ReactSeriesResponseContent.


        :param feature_mda: The feature_mda of this ReactSeriesResponseContent.
        :type feature_mda: list[dict[str, float]]
        """

        self._feature_mda = feature_mda

    @property
    def feature_mda_ex_post(self):
        """Get the feature_mda_ex_post of this ReactSeriesResponseContent.


        :return: The feature_mda_ex_post of this ReactSeriesResponseContent.
        :rtype: list[dict[str, float]]
        """
        return self._feature_mda_ex_post

    @feature_mda_ex_post.setter
    def feature_mda_ex_post(self, feature_mda_ex_post):
        """Set the feature_mda_ex_post of this ReactSeriesResponseContent.


        :param feature_mda_ex_post: The feature_mda_ex_post of this ReactSeriesResponseContent.
        :type feature_mda_ex_post: list[dict[str, float]]
        """

        self._feature_mda_ex_post = feature_mda_ex_post

    @property
    def feature_contributions(self):
        """Get the feature_contributions of this ReactSeriesResponseContent.


        :return: The feature_contributions of this ReactSeriesResponseContent.
        :rtype: list[dict[str, float]]
        """
        return self._feature_contributions

    @feature_contributions.setter
    def feature_contributions(self, feature_contributions):
        """Set the feature_contributions of this ReactSeriesResponseContent.


        :param feature_contributions: The feature_contributions of this ReactSeriesResponseContent.
        :type feature_contributions: list[dict[str, float]]
        """

        self._feature_contributions = feature_contributions

    @property
    def case_feature_contributions(self):
        """Get the case_feature_contributions of this ReactSeriesResponseContent.


        :return: The case_feature_contributions of this ReactSeriesResponseContent.
        :rtype: list[dict[str, float]]
        """
        return self._case_feature_contributions

    @case_feature_contributions.setter
    def case_feature_contributions(self, case_feature_contributions):
        """Set the case_feature_contributions of this ReactSeriesResponseContent.


        :param case_feature_contributions: The case_feature_contributions of this ReactSeriesResponseContent.
        :type case_feature_contributions: list[dict[str, float]]
        """

        self._case_feature_contributions = case_feature_contributions

    @property
    def case_mda(self):
        """Get the case_mda of this ReactSeriesResponseContent.


        :return: The case_mda of this ReactSeriesResponseContent.
        :rtype: list[list[dict[str, object]]]
        """
        return self._case_mda

    @case_mda.setter
    def case_mda(self, case_mda):
        """Set the case_mda of this ReactSeriesResponseContent.


        :param case_mda: The case_mda of this ReactSeriesResponseContent.
        :type case_mda: list[list[dict[str, object]]]
        """

        self._case_mda = case_mda

    @property
    def case_contributions(self):
        """Get the case_contributions of this ReactSeriesResponseContent.


        :return: The case_contributions of this ReactSeriesResponseContent.
        :rtype: list[list[dict[str, object]]]
        """
        return self._case_contributions

    @case_contributions.setter
    def case_contributions(self, case_contributions):
        """Set the case_contributions of this ReactSeriesResponseContent.


        :param case_contributions: The case_contributions of this ReactSeriesResponseContent.
        :type case_contributions: list[list[dict[str, object]]]
        """

        self._case_contributions = case_contributions

    @property
    def case_feature_residuals(self):
        """Get the case_feature_residuals of this ReactSeriesResponseContent.


        :return: The case_feature_residuals of this ReactSeriesResponseContent.
        :rtype: list[dict[str, float]]
        """
        return self._case_feature_residuals

    @case_feature_residuals.setter
    def case_feature_residuals(self, case_feature_residuals):
        """Set the case_feature_residuals of this ReactSeriesResponseContent.


        :param case_feature_residuals: The case_feature_residuals of this ReactSeriesResponseContent.
        :type case_feature_residuals: list[dict[str, float]]
        """

        self._case_feature_residuals = case_feature_residuals

    @property
    def local_case_feature_residual_convictions(self):
        """Get the local_case_feature_residual_convictions of this ReactSeriesResponseContent.


        :return: The local_case_feature_residual_convictions of this ReactSeriesResponseContent.
        :rtype: list[dict[str, float]]
        """
        return self._local_case_feature_residual_convictions

    @local_case_feature_residual_convictions.setter
    def local_case_feature_residual_convictions(self, local_case_feature_residual_convictions):
        """Set the local_case_feature_residual_convictions of this ReactSeriesResponseContent.


        :param local_case_feature_residual_convictions: The local_case_feature_residual_convictions of this ReactSeriesResponseContent.
        :type local_case_feature_residual_convictions: list[dict[str, float]]
        """

        self._local_case_feature_residual_convictions = local_case_feature_residual_convictions

    @property
    def global_case_feature_residual_convictions(self):
        """Get the global_case_feature_residual_convictions of this ReactSeriesResponseContent.


        :return: The global_case_feature_residual_convictions of this ReactSeriesResponseContent.
        :rtype: list[dict[str, float]]
        """
        return self._global_case_feature_residual_convictions

    @global_case_feature_residual_convictions.setter
    def global_case_feature_residual_convictions(self, global_case_feature_residual_convictions):
        """Set the global_case_feature_residual_convictions of this ReactSeriesResponseContent.


        :param global_case_feature_residual_convictions: The global_case_feature_residual_convictions of this ReactSeriesResponseContent.
        :type global_case_feature_residual_convictions: list[dict[str, float]]
        """

        self._global_case_feature_residual_convictions = global_case_feature_residual_convictions

    @property
    def hypothetical_values(self):
        """Get the hypothetical_values of this ReactSeriesResponseContent.


        :return: The hypothetical_values of this ReactSeriesResponseContent.
        :rtype: list[dict[str, object]]
        """
        return self._hypothetical_values

    @hypothetical_values.setter
    def hypothetical_values(self, hypothetical_values):
        """Set the hypothetical_values of this ReactSeriesResponseContent.


        :param hypothetical_values: The hypothetical_values of this ReactSeriesResponseContent.
        :type hypothetical_values: list[dict[str, object]]
        """

        self._hypothetical_values = hypothetical_values

    @property
    def distance_ratio(self):
        """Get the distance_ratio of this ReactSeriesResponseContent.


        :return: The distance_ratio of this ReactSeriesResponseContent.
        :rtype: list[float]
        """
        return self._distance_ratio

    @distance_ratio.setter
    def distance_ratio(self, distance_ratio):
        """Set the distance_ratio of this ReactSeriesResponseContent.


        :param distance_ratio: The distance_ratio of this ReactSeriesResponseContent.
        :type distance_ratio: list[float]
        """

        self._distance_ratio = distance_ratio

    @property
    def distance_ratio_parts(self):
        """Get the distance_ratio_parts of this ReactSeriesResponseContent.


        :return: The distance_ratio_parts of this ReactSeriesResponseContent.
        :rtype: list[DetailsResponseDistanceRatioPartsInner]
        """
        return self._distance_ratio_parts

    @distance_ratio_parts.setter
    def distance_ratio_parts(self, distance_ratio_parts):
        """Set the distance_ratio_parts of this ReactSeriesResponseContent.


        :param distance_ratio_parts: The distance_ratio_parts of this ReactSeriesResponseContent.
        :type distance_ratio_parts: list[DetailsResponseDistanceRatioPartsInner]
        """

        self._distance_ratio_parts = distance_ratio_parts

    @property
    def distance_contribution(self):
        """Get the distance_contribution of this ReactSeriesResponseContent.


        :return: The distance_contribution of this ReactSeriesResponseContent.
        :rtype: list[float]
        """
        return self._distance_contribution

    @distance_contribution.setter
    def distance_contribution(self, distance_contribution):
        """Set the distance_contribution of this ReactSeriesResponseContent.


        :param distance_contribution: The distance_contribution of this ReactSeriesResponseContent.
        :type distance_contribution: list[float]
        """

        self._distance_contribution = distance_contribution

    @property
    def similarity_conviction(self):
        """Get the similarity_conviction of this ReactSeriesResponseContent.


        :return: The similarity_conviction of this ReactSeriesResponseContent.
        :rtype: list[float]
        """
        return self._similarity_conviction

    @similarity_conviction.setter
    def similarity_conviction(self, similarity_conviction):
        """Set the similarity_conviction of this ReactSeriesResponseContent.


        :param similarity_conviction: The similarity_conviction of this ReactSeriesResponseContent.
        :type similarity_conviction: list[float]
        """

        self._similarity_conviction = similarity_conviction

    @property
    def most_similar_case_indices(self):
        """Get the most_similar_case_indices of this ReactSeriesResponseContent.


        :return: The most_similar_case_indices of this ReactSeriesResponseContent.
        :rtype: list[list[dict[str, object]]]
        """
        return self._most_similar_case_indices

    @most_similar_case_indices.setter
    def most_similar_case_indices(self, most_similar_case_indices):
        """Set the most_similar_case_indices of this ReactSeriesResponseContent.


        :param most_similar_case_indices: The most_similar_case_indices of this ReactSeriesResponseContent.
        :type most_similar_case_indices: list[list[dict[str, object]]]
        """

        self._most_similar_case_indices = most_similar_case_indices

    @property
    def action_features(self):
        """Get the action_features of this ReactSeriesResponseContent.

        The list of all action features, specified and derived.

        :return: The action_features of this ReactSeriesResponseContent.
        :rtype: list[str]
        """
        return self._action_features

    @action_features.setter
    def action_features(self, action_features):
        """Set the action_features of this ReactSeriesResponseContent.

        The list of all action features, specified and derived.

        :param action_features: The action_features of this ReactSeriesResponseContent.
        :type action_features: list[str]
        """

        self._action_features = action_features

    @property
    def series(self):
        """Get the series of this ReactSeriesResponseContent.

        List of series, where each series is a 2d list of values (rows of data the series), where the values are in the same order as 'action_features'. 

        :return: The series of this ReactSeriesResponseContent.
        :rtype: list[list[list[object]]]
        """
        return self._series

    @series.setter
    def series(self, series):
        """Set the series of this ReactSeriesResponseContent.

        List of series, where each series is a 2d list of values (rows of data the series), where the values are in the same order as 'action_features'. 

        :param series: The series of this ReactSeriesResponseContent.
        :type series: list[list[list[object]]]
        """

        self._series = series

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
        if not isinstance(other, ReactSeriesResponseContent):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactSeriesResponseContent):
            return True

        return self.to_dict() != other.to_dict()
