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


class ReactDetails(object):
    """
    Auto-generated OpenAPI type.

    Returns explanation and audit data for a given reaction for the specified audit data flags. Local and regional models are used to determine explanations:     Local model -  only the most similar cases used to directly determine the prediction value, used to compute affects of cases directly                     responsible for the predicted output.     Regional model - the most similar cases to the prediction, represented by the maximum of either 30 or the local model size. Used in                     situations where relying on a small local model may produce noisy results. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'robust_residuals': 'bool',
        'robust_influences': 'bool',
        'influential_cases': 'bool',
        'derivation_parameters': 'bool',
        'influential_cases_familiarity_convictions': 'bool',
        'influential_cases_raw_weights': 'bool',
        'most_similar_cases': 'bool',
        'num_most_similar_cases': 'float',
        'num_most_similar_case_indices': 'float',
        'num_robust_influence_samples_per_case': 'float',
        'boundary_cases': 'bool',
        'num_boundary_cases': 'float',
        'boundary_cases_familiarity_convictions': 'bool',
        'features': 'list[str]',
        'feature_residuals': 'bool',
        'feature_mda': 'bool',
        'feature_mda_ex_post': 'bool',
        'feature_contributions': 'bool',
        'case_feature_contributions': 'bool',
        'case_feature_residuals': 'bool',
        'case_mda': 'bool',
        'case_contributions': 'bool',
        'global_case_feature_residual_convictions': 'bool',
        'local_case_feature_residual_convictions': 'bool',
        'outlying_feature_values': 'bool',
        'categorical_action_probabilities': 'bool',
        'hypothetical_values': 'dict[str, object]',
        'distance_ratio': 'bool',
        'distance_contribution': 'bool',
        'similarity_conviction': 'bool',
        'observational_errors': 'bool'
    }

    attribute_map = {
        'robust_residuals': 'robust_residuals',
        'robust_influences': 'robust_influences',
        'influential_cases': 'influential_cases',
        'derivation_parameters': 'derivation_parameters',
        'influential_cases_familiarity_convictions': 'influential_cases_familiarity_convictions',
        'influential_cases_raw_weights': 'influential_cases_raw_weights',
        'most_similar_cases': 'most_similar_cases',
        'num_most_similar_cases': 'num_most_similar_cases',
        'num_most_similar_case_indices': 'num_most_similar_case_indices',
        'num_robust_influence_samples_per_case': 'num_robust_influence_samples_per_case',
        'boundary_cases': 'boundary_cases',
        'num_boundary_cases': 'num_boundary_cases',
        'boundary_cases_familiarity_convictions': 'boundary_cases_familiarity_convictions',
        'features': 'features',
        'feature_residuals': 'feature_residuals',
        'feature_mda': 'feature_mda',
        'feature_mda_ex_post': 'feature_mda_ex_post',
        'feature_contributions': 'feature_contributions',
        'case_feature_contributions': 'case_feature_contributions',
        'case_feature_residuals': 'case_feature_residuals',
        'case_mda': 'case_mda',
        'case_contributions': 'case_contributions',
        'global_case_feature_residual_convictions': 'global_case_feature_residual_convictions',
        'local_case_feature_residual_convictions': 'local_case_feature_residual_convictions',
        'outlying_feature_values': 'outlying_feature_values',
        'categorical_action_probabilities': 'categorical_action_probabilities',
        'hypothetical_values': 'hypothetical_values',
        'distance_ratio': 'distance_ratio',
        'distance_contribution': 'distance_contribution',
        'similarity_conviction': 'similarity_conviction',
        'observational_errors': 'observational_errors'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, robust_residuals=None, robust_influences=None, influential_cases=None, derivation_parameters=None, influential_cases_familiarity_convictions=None, influential_cases_raw_weights=None, most_similar_cases=None, num_most_similar_cases=None, num_most_similar_case_indices=None, num_robust_influence_samples_per_case=None, boundary_cases=None, num_boundary_cases=None, boundary_cases_familiarity_convictions=None, features=None, feature_residuals=None, feature_mda=None, feature_mda_ex_post=None, feature_contributions=None, case_feature_contributions=None, case_feature_residuals=None, case_mda=None, case_contributions=None, global_case_feature_residual_convictions=None, local_case_feature_residual_convictions=None, outlying_feature_values=None, categorical_action_probabilities=None, hypothetical_values=None, distance_ratio=None, distance_contribution=None, similarity_conviction=None, observational_errors=None, local_vars_configuration=None):  # noqa: E501
        """ReactDetails - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._robust_residuals = None
        self._robust_influences = None
        self._influential_cases = None
        self._derivation_parameters = None
        self._influential_cases_familiarity_convictions = None
        self._influential_cases_raw_weights = None
        self._most_similar_cases = None
        self._num_most_similar_cases = None
        self._num_most_similar_case_indices = None
        self._num_robust_influence_samples_per_case = None
        self._boundary_cases = None
        self._num_boundary_cases = None
        self._boundary_cases_familiarity_convictions = None
        self._features = None
        self._feature_residuals = None
        self._feature_mda = None
        self._feature_mda_ex_post = None
        self._feature_contributions = None
        self._case_feature_contributions = None
        self._case_feature_residuals = None
        self._case_mda = None
        self._case_contributions = None
        self._global_case_feature_residual_convictions = None
        self._local_case_feature_residual_convictions = None
        self._outlying_feature_values = None
        self._categorical_action_probabilities = None
        self._hypothetical_values = None
        self._distance_ratio = None
        self._distance_contribution = None
        self._similarity_conviction = None
        self._observational_errors = None

        if robust_residuals is not None:
            self.robust_residuals = robust_residuals
        if robust_influences is not None:
            self.robust_influences = robust_influences
        if influential_cases is not None:
            self.influential_cases = influential_cases
        if derivation_parameters is not None:
            self.derivation_parameters = derivation_parameters
        if influential_cases_familiarity_convictions is not None:
            self.influential_cases_familiarity_convictions = influential_cases_familiarity_convictions
        if influential_cases_raw_weights is not None:
            self.influential_cases_raw_weights = influential_cases_raw_weights
        if most_similar_cases is not None:
            self.most_similar_cases = most_similar_cases
        if num_most_similar_cases is not None:
            self.num_most_similar_cases = num_most_similar_cases
        if num_most_similar_case_indices is not None:
            self.num_most_similar_case_indices = num_most_similar_case_indices
        if num_robust_influence_samples_per_case is not None:
            self.num_robust_influence_samples_per_case = num_robust_influence_samples_per_case
        if boundary_cases is not None:
            self.boundary_cases = boundary_cases
        if num_boundary_cases is not None:
            self.num_boundary_cases = num_boundary_cases
        if boundary_cases_familiarity_convictions is not None:
            self.boundary_cases_familiarity_convictions = boundary_cases_familiarity_convictions
        if features is not None:
            self.features = features
        if feature_residuals is not None:
            self.feature_residuals = feature_residuals
        if feature_mda is not None:
            self.feature_mda = feature_mda
        if feature_mda_ex_post is not None:
            self.feature_mda_ex_post = feature_mda_ex_post
        if feature_contributions is not None:
            self.feature_contributions = feature_contributions
        if case_feature_contributions is not None:
            self.case_feature_contributions = case_feature_contributions
        if case_feature_residuals is not None:
            self.case_feature_residuals = case_feature_residuals
        if case_mda is not None:
            self.case_mda = case_mda
        if case_contributions is not None:
            self.case_contributions = case_contributions
        if global_case_feature_residual_convictions is not None:
            self.global_case_feature_residual_convictions = global_case_feature_residual_convictions
        if local_case_feature_residual_convictions is not None:
            self.local_case_feature_residual_convictions = local_case_feature_residual_convictions
        if outlying_feature_values is not None:
            self.outlying_feature_values = outlying_feature_values
        if categorical_action_probabilities is not None:
            self.categorical_action_probabilities = categorical_action_probabilities
        if hypothetical_values is not None:
            self.hypothetical_values = hypothetical_values
        if distance_ratio is not None:
            self.distance_ratio = distance_ratio
        if distance_contribution is not None:
            self.distance_contribution = distance_contribution
        if similarity_conviction is not None:
            self.similarity_conviction = similarity_conviction
        if observational_errors is not None:
            self.observational_errors = observational_errors

    @property
    def robust_residuals(self):
        """Get the robust_residuals of this ReactDetails.

        When false, uses leave-one-out for features (or cases, as needed) for all residual computations. When true, uses uniform sampling from the power set of all combinations of features (or cases, as needed) instead. Default behavior is false. 

        :return: The robust_residuals of this ReactDetails.
        :rtype: bool
        """
        return self._robust_residuals

    @robust_residuals.setter
    def robust_residuals(self, robust_residuals):
        """Set the robust_residuals of this ReactDetails.

        When false, uses leave-one-out for features (or cases, as needed) for all residual computations. When true, uses uniform sampling from the power set of all combinations of features (or cases, as needed) instead. Default behavior is false. 

        :param robust_residuals: The robust_residuals of this ReactDetails.
        :type robust_residuals: bool
        """

        self._robust_residuals = robust_residuals

    @property
    def robust_influences(self):
        """Get the robust_influences of this ReactDetails.

        When true, uses leave-one-out for features (or cases, as needed) for all MDA and contribution computations. When true, uses uniform sampling from the power set of all combinations of features (or cases, as needed) instead. Default behavior is true. 

        :return: The robust_influences of this ReactDetails.
        :rtype: bool
        """
        return self._robust_influences

    @robust_influences.setter
    def robust_influences(self, robust_influences):
        """Set the robust_influences of this ReactDetails.

        When true, uses leave-one-out for features (or cases, as needed) for all MDA and contribution computations. When true, uses uniform sampling from the power set of all combinations of features (or cases, as needed) instead. Default behavior is true. 

        :param robust_influences: The robust_influences of this ReactDetails.
        :type robust_influences: bool
        """

        self._robust_influences = robust_influences

    @property
    def influential_cases(self):
        """Get the influential_cases of this ReactDetails.

        When true, outputs the most influential cases and their influence weights based on the surprisal of each case relative to the context being predicted among the cases. Uses only the context features of the reacted case. 

        :return: The influential_cases of this ReactDetails.
        :rtype: bool
        """
        return self._influential_cases

    @influential_cases.setter
    def influential_cases(self, influential_cases):
        """Set the influential_cases of this ReactDetails.

        When true, outputs the most influential cases and their influence weights based on the surprisal of each case relative to the context being predicted among the cases. Uses only the context features of the reacted case. 

        :param influential_cases: The influential_cases of this ReactDetails.
        :type influential_cases: bool
        """

        self._influential_cases = influential_cases

    @property
    def derivation_parameters(self):
        """Get the derivation_parameters of this ReactDetails.

        If True, outputs a dictionary of the parameters used in the react call. These include k, p, distance_transform, feature_weights, feature_deviations, nominal_class_counts, and use_irw. 

        :return: The derivation_parameters of this ReactDetails.
        :rtype: bool
        """
        return self._derivation_parameters

    @derivation_parameters.setter
    def derivation_parameters(self, derivation_parameters):
        """Set the derivation_parameters of this ReactDetails.

        If True, outputs a dictionary of the parameters used in the react call. These include k, p, distance_transform, feature_weights, feature_deviations, nominal_class_counts, and use_irw. 

        :param derivation_parameters: The derivation_parameters of this ReactDetails.
        :type derivation_parameters: bool
        """

        self._derivation_parameters = derivation_parameters

    @property
    def influential_cases_familiarity_convictions(self):
        """Get the influential_cases_familiarity_convictions of this ReactDetails.

        When true, outputs familiarity conviction of addition for each of the influential cases.

        :return: The influential_cases_familiarity_convictions of this ReactDetails.
        :rtype: bool
        """
        return self._influential_cases_familiarity_convictions

    @influential_cases_familiarity_convictions.setter
    def influential_cases_familiarity_convictions(self, influential_cases_familiarity_convictions):
        """Set the influential_cases_familiarity_convictions of this ReactDetails.

        When true, outputs familiarity conviction of addition for each of the influential cases.

        :param influential_cases_familiarity_convictions: The influential_cases_familiarity_convictions of this ReactDetails.
        :type influential_cases_familiarity_convictions: bool
        """

        self._influential_cases_familiarity_convictions = influential_cases_familiarity_convictions

    @property
    def influential_cases_raw_weights(self):
        """Get the influential_cases_raw_weights of this ReactDetails.

        When true, outputs the surprisal for each of the influential cases. 

        :return: The influential_cases_raw_weights of this ReactDetails.
        :rtype: bool
        """
        return self._influential_cases_raw_weights

    @influential_cases_raw_weights.setter
    def influential_cases_raw_weights(self, influential_cases_raw_weights):
        """Set the influential_cases_raw_weights of this ReactDetails.

        When true, outputs the surprisal for each of the influential cases. 

        :param influential_cases_raw_weights: The influential_cases_raw_weights of this ReactDetails.
        :type influential_cases_raw_weights: bool
        """

        self._influential_cases_raw_weights = influential_cases_raw_weights

    @property
    def most_similar_cases(self):
        """Get the most_similar_cases of this ReactDetails.

        When true, outputs an automatically determined (when 'num_most_similar_cases' is not specified) relevant number of similar cases, which will first include the influential cases. Uses only the context features of the reacted case. 

        :return: The most_similar_cases of this ReactDetails.
        :rtype: bool
        """
        return self._most_similar_cases

    @most_similar_cases.setter
    def most_similar_cases(self, most_similar_cases):
        """Set the most_similar_cases of this ReactDetails.

        When true, outputs an automatically determined (when 'num_most_similar_cases' is not specified) relevant number of similar cases, which will first include the influential cases. Uses only the context features of the reacted case. 

        :param most_similar_cases: The most_similar_cases of this ReactDetails.
        :type most_similar_cases: bool
        """

        self._most_similar_cases = most_similar_cases

    @property
    def num_most_similar_cases(self):
        """Get the num_most_similar_cases of this ReactDetails.

        When defined, outputs this manually specified number of most similar cases, which will first include the influential cases. Takes precedence over 'most_similar_cases' parameter. 

        :return: The num_most_similar_cases of this ReactDetails.
        :rtype: float
        """
        return self._num_most_similar_cases

    @num_most_similar_cases.setter
    def num_most_similar_cases(self, num_most_similar_cases):
        """Set the num_most_similar_cases of this ReactDetails.

        When defined, outputs this manually specified number of most similar cases, which will first include the influential cases. Takes precedence over 'most_similar_cases' parameter. 

        :param num_most_similar_cases: The num_most_similar_cases of this ReactDetails.
        :type num_most_similar_cases: float
        """
        if (self.local_vars_configuration.client_side_validation and
                num_most_similar_cases is not None and num_most_similar_cases > 1000):  # noqa: E501
            raise ValueError("Invalid value for `num_most_similar_cases`, must be a value less than or equal to `1000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                num_most_similar_cases is not None and num_most_similar_cases < 1):  # noqa: E501
            raise ValueError("Invalid value for `num_most_similar_cases`, must be a value greater than or equal to `1`")  # noqa: E501

        self._num_most_similar_cases = num_most_similar_cases

    @property
    def num_most_similar_case_indices(self):
        """Get the num_most_similar_case_indices of this ReactDetails.

        When defined, outputs the specified number of most similar case indices when 'distance_ratio' is also set to true. 

        :return: The num_most_similar_case_indices of this ReactDetails.
        :rtype: float
        """
        return self._num_most_similar_case_indices

    @num_most_similar_case_indices.setter
    def num_most_similar_case_indices(self, num_most_similar_case_indices):
        """Set the num_most_similar_case_indices of this ReactDetails.

        When defined, outputs the specified number of most similar case indices when 'distance_ratio' is also set to true. 

        :param num_most_similar_case_indices: The num_most_similar_case_indices of this ReactDetails.
        :type num_most_similar_case_indices: float
        """
        if (self.local_vars_configuration.client_side_validation and
                num_most_similar_case_indices is not None and num_most_similar_case_indices > 1000):  # noqa: E501
            raise ValueError("Invalid value for `num_most_similar_case_indices`, must be a value less than or equal to `1000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                num_most_similar_case_indices is not None and num_most_similar_case_indices < 1):  # noqa: E501
            raise ValueError("Invalid value for `num_most_similar_case_indices`, must be a value greater than or equal to `1`")  # noqa: E501

        self._num_most_similar_case_indices = num_most_similar_case_indices

    @property
    def num_robust_influence_samples_per_case(self):
        """Get the num_robust_influence_samples_per_case of this ReactDetails.

        Specifies the number of robust samples to use for each case. Applicable only for computing robust feature contributions or robust case feature contributions. Defaults to 2000 when unspecified. Higher values will take longer but provide more stable results. 

        :return: The num_robust_influence_samples_per_case of this ReactDetails.
        :rtype: float
        """
        return self._num_robust_influence_samples_per_case

    @num_robust_influence_samples_per_case.setter
    def num_robust_influence_samples_per_case(self, num_robust_influence_samples_per_case):
        """Set the num_robust_influence_samples_per_case of this ReactDetails.

        Specifies the number of robust samples to use for each case. Applicable only for computing robust feature contributions or robust case feature contributions. Defaults to 2000 when unspecified. Higher values will take longer but provide more stable results. 

        :param num_robust_influence_samples_per_case: The num_robust_influence_samples_per_case of this ReactDetails.
        :type num_robust_influence_samples_per_case: float
        """
        if (self.local_vars_configuration.client_side_validation and
                num_robust_influence_samples_per_case is not None and num_robust_influence_samples_per_case > 1000000):  # noqa: E501
            raise ValueError("Invalid value for `num_robust_influence_samples_per_case`, must be a value less than or equal to `1000000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                num_robust_influence_samples_per_case is not None and num_robust_influence_samples_per_case < 1):  # noqa: E501
            raise ValueError("Invalid value for `num_robust_influence_samples_per_case`, must be a value greater than or equal to `1`")  # noqa: E501

        self._num_robust_influence_samples_per_case = num_robust_influence_samples_per_case

    @property
    def boundary_cases(self):
        """Get the boundary_cases of this ReactDetails.

        When true, outputs an automatically determined (when 'num_boundary_cases' is not specified) relevant number of boundary cases. Uses both context and action features of the reacted case to determine the counterfactual boundary based on action features, which maximize the dissimilarity of action features while maximizing the similarity of context features. If action features aren't specified, uses familiarity conviction to determine the boundary instead. 

        :return: The boundary_cases of this ReactDetails.
        :rtype: bool
        """
        return self._boundary_cases

    @boundary_cases.setter
    def boundary_cases(self, boundary_cases):
        """Set the boundary_cases of this ReactDetails.

        When true, outputs an automatically determined (when 'num_boundary_cases' is not specified) relevant number of boundary cases. Uses both context and action features of the reacted case to determine the counterfactual boundary based on action features, which maximize the dissimilarity of action features while maximizing the similarity of context features. If action features aren't specified, uses familiarity conviction to determine the boundary instead. 

        :param boundary_cases: The boundary_cases of this ReactDetails.
        :type boundary_cases: bool
        """

        self._boundary_cases = boundary_cases

    @property
    def num_boundary_cases(self):
        """Get the num_boundary_cases of this ReactDetails.

        When defined, outputs this manually specified number of boundary cases. Takes precedence over 'boundary_cases' parameter. 

        :return: The num_boundary_cases of this ReactDetails.
        :rtype: float
        """
        return self._num_boundary_cases

    @num_boundary_cases.setter
    def num_boundary_cases(self, num_boundary_cases):
        """Set the num_boundary_cases of this ReactDetails.

        When defined, outputs this manually specified number of boundary cases. Takes precedence over 'boundary_cases' parameter. 

        :param num_boundary_cases: The num_boundary_cases of this ReactDetails.
        :type num_boundary_cases: float
        """
        if (self.local_vars_configuration.client_side_validation and
                num_boundary_cases is not None and num_boundary_cases > 1000):  # noqa: E501
            raise ValueError("Invalid value for `num_boundary_cases`, must be a value less than or equal to `1000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                num_boundary_cases is not None and num_boundary_cases < 1):  # noqa: E501
            raise ValueError("Invalid value for `num_boundary_cases`, must be a value greater than or equal to `1`")  # noqa: E501

        self._num_boundary_cases = num_boundary_cases

    @property
    def boundary_cases_familiarity_convictions(self):
        """Get the boundary_cases_familiarity_convictions of this ReactDetails.

        When true, outputs familiarity conviction of addition for each of the boundary cases.

        :return: The boundary_cases_familiarity_convictions of this ReactDetails.
        :rtype: bool
        """
        return self._boundary_cases_familiarity_convictions

    @boundary_cases_familiarity_convictions.setter
    def boundary_cases_familiarity_convictions(self, boundary_cases_familiarity_convictions):
        """Set the boundary_cases_familiarity_convictions of this ReactDetails.

        When true, outputs familiarity conviction of addition for each of the boundary cases.

        :param boundary_cases_familiarity_convictions: The boundary_cases_familiarity_convictions of this ReactDetails.
        :type boundary_cases_familiarity_convictions: bool
        """

        self._boundary_cases_familiarity_convictions = boundary_cases_familiarity_convictions

    @property
    def features(self):
        """Get the features of this ReactDetails.

        A list of feature names that specifies for what features will per-feature details be computed (residuals, contributions, mda, etc.). This should generally preserve compute, but will not when computing details robustly. Details will be computed for all context and action features if this is not specified. 

        :return: The features of this ReactDetails.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this ReactDetails.

        A list of feature names that specifies for what features will per-feature details be computed (residuals, contributions, mda, etc.). This should generally preserve compute, but will not when computing details robustly. Details will be computed for all context and action features if this is not specified. 

        :param features: The features of this ReactDetails.
        :type features: list[str]
        """

        self._features = features

    @property
    def feature_residuals(self):
        """Get the feature_residuals of this ReactDetails.

        When true, outputs feature residuals for all (context and action) features locally around the prediction. Uses only the context features of the reacted case to determine that area. Relies on 'robust_residuals' parameter to determine whether to do standard or robust computation. 

        :return: The feature_residuals of this ReactDetails.
        :rtype: bool
        """
        return self._feature_residuals

    @feature_residuals.setter
    def feature_residuals(self, feature_residuals):
        """Set the feature_residuals of this ReactDetails.

        When true, outputs feature residuals for all (context and action) features locally around the prediction. Uses only the context features of the reacted case to determine that area. Relies on 'robust_residuals' parameter to determine whether to do standard or robust computation. 

        :param feature_residuals: The feature_residuals of this ReactDetails.
        :type feature_residuals: bool
        """

        self._feature_residuals = feature_residuals

    @property
    def feature_mda(self):
        """Get the feature_mda of this ReactDetails.

        When true, outputs each context feature's mean decrease in accuracy of predicting the action feature given the context. Uses only the context features of the reacted case to determine that area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. 

        :return: The feature_mda of this ReactDetails.
        :rtype: bool
        """
        return self._feature_mda

    @feature_mda.setter
    def feature_mda(self, feature_mda):
        """Set the feature_mda of this ReactDetails.

        When true, outputs each context feature's mean decrease in accuracy of predicting the action feature given the context. Uses only the context features of the reacted case to determine that area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. 

        :param feature_mda: The feature_mda of this ReactDetails.
        :type feature_mda: bool
        """

        self._feature_mda = feature_mda

    @property
    def feature_mda_ex_post(self):
        """Get the feature_mda_ex_post of this ReactDetails.

        When true, outputs each context feature's mean decrease in accuracy of predicting the action feature as an explanation given that the specified prediction was already made as specified by the action value. Uses both context and action features of the reacted case to determine that area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. 

        :return: The feature_mda_ex_post of this ReactDetails.
        :rtype: bool
        """
        return self._feature_mda_ex_post

    @feature_mda_ex_post.setter
    def feature_mda_ex_post(self, feature_mda_ex_post):
        """Set the feature_mda_ex_post of this ReactDetails.

        When true, outputs each context feature's mean decrease in accuracy of predicting the action feature as an explanation given that the specified prediction was already made as specified by the action value. Uses both context and action features of the reacted case to determine that area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. 

        :param feature_mda_ex_post: The feature_mda_ex_post of this ReactDetails.
        :type feature_mda_ex_post: bool
        """

        self._feature_mda_ex_post = feature_mda_ex_post

    @property
    def feature_contributions(self):
        """Get the feature_contributions of this ReactDetails.

        When true, outputs each context feature's absolute and directional differences between the predicted action feature value and the predicted action feature value if each context were not in the model for all context features in the local model area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. Directional feature contributions are returned under the key 'directional_feature_contributions'. 

        :return: The feature_contributions of this ReactDetails.
        :rtype: bool
        """
        return self._feature_contributions

    @feature_contributions.setter
    def feature_contributions(self, feature_contributions):
        """Set the feature_contributions of this ReactDetails.

        When true, outputs each context feature's absolute and directional differences between the predicted action feature value and the predicted action feature value if each context were not in the model for all context features in the local model area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. Directional feature contributions are returned under the key 'directional_feature_contributions'. 

        :param feature_contributions: The feature_contributions of this ReactDetails.
        :type feature_contributions: bool
        """

        self._feature_contributions = feature_contributions

    @property
    def case_feature_contributions(self):
        """Get the case_feature_contributions of this ReactDetails.

        When true, outputs each context feature's absolute and directional differences between the predicted action feature value and the predicted action feature value if each context feature were not in the model for all context features in this case, using only the values from this specific case. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. Directional case feature contributions are returned under the 'case_directional_feature_contributions' key. 

        :return: The case_feature_contributions of this ReactDetails.
        :rtype: bool
        """
        return self._case_feature_contributions

    @case_feature_contributions.setter
    def case_feature_contributions(self, case_feature_contributions):
        """Set the case_feature_contributions of this ReactDetails.

        When true, outputs each context feature's absolute and directional differences between the predicted action feature value and the predicted action feature value if each context feature were not in the model for all context features in this case, using only the values from this specific case. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. Directional case feature contributions are returned under the 'case_directional_feature_contributions' key. 

        :param case_feature_contributions: The case_feature_contributions of this ReactDetails.
        :type case_feature_contributions: bool
        """

        self._case_feature_contributions = case_feature_contributions

    @property
    def case_feature_residuals(self):
        """Get the case_feature_residuals of this ReactDetails.

        When true, outputs feature residuals for all (context and action) features for just the specified case. Uses leave-one-out for each feature, while using the others to predict the left out feature with their corresponding values from this case. Relies on 'robust_residuals' parameter to determine whether to do standard or robust computation. 

        :return: The case_feature_residuals of this ReactDetails.
        :rtype: bool
        """
        return self._case_feature_residuals

    @case_feature_residuals.setter
    def case_feature_residuals(self, case_feature_residuals):
        """Set the case_feature_residuals of this ReactDetails.

        When true, outputs feature residuals for all (context and action) features for just the specified case. Uses leave-one-out for each feature, while using the others to predict the left out feature with their corresponding values from this case. Relies on 'robust_residuals' parameter to determine whether to do standard or robust computation. 

        :param case_feature_residuals: The case_feature_residuals of this ReactDetails.
        :type case_feature_residuals: bool
        """

        self._case_feature_residuals = case_feature_residuals

    @property
    def case_mda(self):
        """Get the case_mda of this ReactDetails.

        When true, outputs each influential case's mean decrease in accuracy of predicting the action feature in the local model area, as if each individual case were included versus not included. Uses only the context features of the reacted case to determine that area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. 

        :return: The case_mda of this ReactDetails.
        :rtype: bool
        """
        return self._case_mda

    @case_mda.setter
    def case_mda(self, case_mda):
        """Set the case_mda of this ReactDetails.

        When true, outputs each influential case's mean decrease in accuracy of predicting the action feature in the local model area, as if each individual case were included versus not included. Uses only the context features of the reacted case to determine that area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. 

        :param case_mda: The case_mda of this ReactDetails.
        :type case_mda: bool
        """

        self._case_mda = case_mda

    @property
    def case_contributions(self):
        """Get the case_contributions of this ReactDetails.

        When true, outputs each influential case's differences between the predicted action feature value and the predicted action feature value if each individual case were not included. Uses only the context features of the reacted case to determine that area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. 

        :return: The case_contributions of this ReactDetails.
        :rtype: bool
        """
        return self._case_contributions

    @case_contributions.setter
    def case_contributions(self, case_contributions):
        """Set the case_contributions of this ReactDetails.

        When true, outputs each influential case's differences between the predicted action feature value and the predicted action feature value if each individual case were not included. Uses only the context features of the reacted case to determine that area. Relies on 'robust_influences' parameter to determine whether to do standard or robust computation. 

        :param case_contributions: The case_contributions of this ReactDetails.
        :type case_contributions: bool
        """

        self._case_contributions = case_contributions

    @property
    def global_case_feature_residual_convictions(self):
        """Get the global_case_feature_residual_convictions of this ReactDetails.

        When true, outputs this case's feature residual convictions for the global model. Computed as: global model feature residual divided by case feature residual. Relies on 'robust_residuals' parameter to determine whether to do standard or robust computation. 

        :return: The global_case_feature_residual_convictions of this ReactDetails.
        :rtype: bool
        """
        return self._global_case_feature_residual_convictions

    @global_case_feature_residual_convictions.setter
    def global_case_feature_residual_convictions(self, global_case_feature_residual_convictions):
        """Set the global_case_feature_residual_convictions of this ReactDetails.

        When true, outputs this case's feature residual convictions for the global model. Computed as: global model feature residual divided by case feature residual. Relies on 'robust_residuals' parameter to determine whether to do standard or robust computation. 

        :param global_case_feature_residual_convictions: The global_case_feature_residual_convictions of this ReactDetails.
        :type global_case_feature_residual_convictions: bool
        """

        self._global_case_feature_residual_convictions = global_case_feature_residual_convictions

    @property
    def local_case_feature_residual_convictions(self):
        """Get the local_case_feature_residual_convictions of this ReactDetails.

        When true, outputs this case's feature residual convictions for the region around the prediction. Uses only the context features of the reacted case to determine that region. Computed as: region feature residual divided by case feature residual. Relies on 'robust_residuals' parameter to determine whether to do standard or robust computation. 

        :return: The local_case_feature_residual_convictions of this ReactDetails.
        :rtype: bool
        """
        return self._local_case_feature_residual_convictions

    @local_case_feature_residual_convictions.setter
    def local_case_feature_residual_convictions(self, local_case_feature_residual_convictions):
        """Set the local_case_feature_residual_convictions of this ReactDetails.

        When true, outputs this case's feature residual convictions for the region around the prediction. Uses only the context features of the reacted case to determine that region. Computed as: region feature residual divided by case feature residual. Relies on 'robust_residuals' parameter to determine whether to do standard or robust computation. 

        :param local_case_feature_residual_convictions: The local_case_feature_residual_convictions of this ReactDetails.
        :type local_case_feature_residual_convictions: bool
        """

        self._local_case_feature_residual_convictions = local_case_feature_residual_convictions

    @property
    def outlying_feature_values(self):
        """Get the outlying_feature_values of this ReactDetails.

        When true, outputs the reacted case's context feature values that are outside the min or max of the corresponding feature values of all the cases in the local model area. Uses only the context features of the reacted case to determine that area. 

        :return: The outlying_feature_values of this ReactDetails.
        :rtype: bool
        """
        return self._outlying_feature_values

    @outlying_feature_values.setter
    def outlying_feature_values(self, outlying_feature_values):
        """Set the outlying_feature_values of this ReactDetails.

        When true, outputs the reacted case's context feature values that are outside the min or max of the corresponding feature values of all the cases in the local model area. Uses only the context features of the reacted case to determine that area. 

        :param outlying_feature_values: The outlying_feature_values of this ReactDetails.
        :type outlying_feature_values: bool
        """

        self._outlying_feature_values = outlying_feature_values

    @property
    def categorical_action_probabilities(self):
        """Get the categorical_action_probabilities of this ReactDetails.

        When true, outputs probabilities for each class for the action. Applicable only to categorical action features. 

        :return: The categorical_action_probabilities of this ReactDetails.
        :rtype: bool
        """
        return self._categorical_action_probabilities

    @categorical_action_probabilities.setter
    def categorical_action_probabilities(self, categorical_action_probabilities):
        """Set the categorical_action_probabilities of this ReactDetails.

        When true, outputs probabilities for each class for the action. Applicable only to categorical action features. 

        :param categorical_action_probabilities: The categorical_action_probabilities of this ReactDetails.
        :type categorical_action_probabilities: bool
        """

        self._categorical_action_probabilities = categorical_action_probabilities

    @property
    def hypothetical_values(self):
        """Get the hypothetical_values of this ReactDetails.

        A dictionary of feature name to feature value. If specified, shows how a prediction could change in a what-if scenario where the influential cases' context feature values are replaced with the specified values. Iterates over all influential cases, predicting the action features each one using the updated hypothetical values. Outputs the predicted arithmetic over the influential cases for each action feature. 

        :return: The hypothetical_values of this ReactDetails.
        :rtype: dict[str, object]
        """
        return self._hypothetical_values

    @hypothetical_values.setter
    def hypothetical_values(self, hypothetical_values):
        """Set the hypothetical_values of this ReactDetails.

        A dictionary of feature name to feature value. If specified, shows how a prediction could change in a what-if scenario where the influential cases' context feature values are replaced with the specified values. Iterates over all influential cases, predicting the action features each one using the updated hypothetical values. Outputs the predicted arithmetic over the influential cases for each action feature. 

        :param hypothetical_values: The hypothetical_values of this ReactDetails.
        :type hypothetical_values: dict[str, object]
        """

        self._hypothetical_values = hypothetical_values

    @property
    def distance_ratio(self):
        """Get the distance_ratio of this ReactDetails.

        When true, outputs the ratio of distance (relative surprisal) between this reacted case and its nearest case to the minimum distance (relative surprisal) in between the closest two cases in the local area. All distances are computed using only the specified context features. 

        :return: The distance_ratio of this ReactDetails.
        :rtype: bool
        """
        return self._distance_ratio

    @distance_ratio.setter
    def distance_ratio(self, distance_ratio):
        """Set the distance_ratio of this ReactDetails.

        When true, outputs the ratio of distance (relative surprisal) between this reacted case and its nearest case to the minimum distance (relative surprisal) in between the closest two cases in the local area. All distances are computed using only the specified context features. 

        :param distance_ratio: The distance_ratio of this ReactDetails.
        :type distance_ratio: bool
        """

        self._distance_ratio = distance_ratio

    @property
    def distance_contribution(self):
        """Get the distance_contribution of this ReactDetails.

        When true, outputs the distance contribution (expected total surprisal contribution) for the reacted case. Uses both context and action feature values. 

        :return: The distance_contribution of this ReactDetails.
        :rtype: bool
        """
        return self._distance_contribution

    @distance_contribution.setter
    def distance_contribution(self, distance_contribution):
        """Set the distance_contribution of this ReactDetails.

        When true, outputs the distance contribution (expected total surprisal contribution) for the reacted case. Uses both context and action feature values. 

        :param distance_contribution: The distance_contribution of this ReactDetails.
        :type distance_contribution: bool
        """

        self._distance_contribution = distance_contribution

    @property
    def similarity_conviction(self):
        """Get the similarity_conviction of this ReactDetails.

        When true, outputs similarity conviction for the reacted case. Uses both context and action feature values as the case values for all computations. This is defined as expected (local) distance contribution divided by reacted case distance contribution. 

        :return: The similarity_conviction of this ReactDetails.
        :rtype: bool
        """
        return self._similarity_conviction

    @similarity_conviction.setter
    def similarity_conviction(self, similarity_conviction):
        """Set the similarity_conviction of this ReactDetails.

        When true, outputs similarity conviction for the reacted case. Uses both context and action feature values as the case values for all computations. This is defined as expected (local) distance contribution divided by reacted case distance contribution. 

        :param similarity_conviction: The similarity_conviction of this ReactDetails.
        :type similarity_conviction: bool
        """

        self._similarity_conviction = similarity_conviction

    @property
    def observational_errors(self):
        """Get the observational_errors of this ReactDetails.

        When true, outputs observational errors for all features as defined in feature attributes. 

        :return: The observational_errors of this ReactDetails.
        :rtype: bool
        """
        return self._observational_errors

    @observational_errors.setter
    def observational_errors(self, observational_errors):
        """Set the observational_errors of this ReactDetails.

        When true, outputs observational errors for all features as defined in feature attributes. 

        :param observational_errors: The observational_errors of this ReactDetails.
        :type observational_errors: bool
        """

        self._observational_errors = observational_errors

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
        if not isinstance(other, ReactDetails):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactDetails):
            return True

        return self.to_dict() != other.to_dict()
