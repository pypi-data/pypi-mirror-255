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


class AnalyzeRequest(object):
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
        'action_features': 'list[str]',
        'context_features': 'list[str]',
        'k_folds': 'int',
        'num_samples': 'int',
        'dt_values': 'list[float]',
        'k_values': 'list[int]',
        'p_values': 'list[float]',
        'bypass_hyperparameter_analysis': 'bool',
        'bypass_calculate_feature_residuals': 'bool',
        'bypass_calculate_feature_weights': 'bool',
        'targeted_model': 'str',
        'analyze_level': 'int',
        'num_analysis_samples': 'int',
        'analysis_sub_model_size': 'int',
        'use_deviations': 'bool',
        'inverse_residuals_as_weights': 'bool',
        'use_case_weights': 'bool',
        'weight_feature': 'str',
        'experimental_options': 'dict[str, object]'
    }

    attribute_map = {
        'action_features': 'action_features',
        'context_features': 'context_features',
        'k_folds': 'k_folds',
        'num_samples': 'num_samples',
        'dt_values': 'dt_values',
        'k_values': 'k_values',
        'p_values': 'p_values',
        'bypass_hyperparameter_analysis': 'bypass_hyperparameter_analysis',
        'bypass_calculate_feature_residuals': 'bypass_calculate_feature_residuals',
        'bypass_calculate_feature_weights': 'bypass_calculate_feature_weights',
        'targeted_model': 'targeted_model',
        'analyze_level': 'analyze_level',
        'num_analysis_samples': 'num_analysis_samples',
        'analysis_sub_model_size': 'analysis_sub_model_size',
        'use_deviations': 'use_deviations',
        'inverse_residuals_as_weights': 'inverse_residuals_as_weights',
        'use_case_weights': 'use_case_weights',
        'weight_feature': 'weight_feature',
        'experimental_options': 'experimental_options'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, action_features=None, context_features=None, k_folds=None, num_samples=None, dt_values=None, k_values=None, p_values=None, bypass_hyperparameter_analysis=None, bypass_calculate_feature_residuals=None, bypass_calculate_feature_weights=None, targeted_model=None, analyze_level=None, num_analysis_samples=None, analysis_sub_model_size=None, use_deviations=None, inverse_residuals_as_weights=None, use_case_weights=None, weight_feature=None, experimental_options=None, local_vars_configuration=None):  # noqa: E501
        """AnalyzeRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_features = None
        self._context_features = None
        self._k_folds = None
        self._num_samples = None
        self._dt_values = None
        self._k_values = None
        self._p_values = None
        self._bypass_hyperparameter_analysis = None
        self._bypass_calculate_feature_residuals = None
        self._bypass_calculate_feature_weights = None
        self._targeted_model = None
        self._analyze_level = None
        self._num_analysis_samples = None
        self._analysis_sub_model_size = None
        self._use_deviations = None
        self._inverse_residuals_as_weights = None
        self._use_case_weights = None
        self._weight_feature = None
        self._experimental_options = None

        if action_features is not None:
            self.action_features = action_features
        if context_features is not None:
            self.context_features = context_features
        if k_folds is not None:
            self.k_folds = k_folds
        if num_samples is not None:
            self.num_samples = num_samples
        if dt_values is not None:
            self.dt_values = dt_values
        if k_values is not None:
            self.k_values = k_values
        if p_values is not None:
            self.p_values = p_values
        if bypass_hyperparameter_analysis is not None:
            self.bypass_hyperparameter_analysis = bypass_hyperparameter_analysis
        if bypass_calculate_feature_residuals is not None:
            self.bypass_calculate_feature_residuals = bypass_calculate_feature_residuals
        if bypass_calculate_feature_weights is not None:
            self.bypass_calculate_feature_weights = bypass_calculate_feature_weights
        if targeted_model is not None:
            self.targeted_model = targeted_model
        if analyze_level is not None:
            self.analyze_level = analyze_level
        if num_analysis_samples is not None:
            self.num_analysis_samples = num_analysis_samples
        if analysis_sub_model_size is not None:
            self.analysis_sub_model_size = analysis_sub_model_size
        if use_deviations is not None:
            self.use_deviations = use_deviations
        if inverse_residuals_as_weights is not None:
            self.inverse_residuals_as_weights = inverse_residuals_as_weights
        if use_case_weights is not None:
            self.use_case_weights = use_case_weights
        if weight_feature is not None:
            self.weight_feature = weight_feature
        if experimental_options is not None:
            self.experimental_options = experimental_options

    @property
    def action_features(self):
        """Get the action_features of this AnalyzeRequest.

        A list of action feature names. 

        :return: The action_features of this AnalyzeRequest.
        :rtype: list[str]
        """
        return self._action_features

    @action_features.setter
    def action_features(self, action_features):
        """Set the action_features of this AnalyzeRequest.

        A list of action feature names. 

        :param action_features: The action_features of this AnalyzeRequest.
        :type action_features: list[str]
        """

        self._action_features = action_features

    @property
    def context_features(self):
        """Get the context_features of this AnalyzeRequest.

        A list of context feature names. 

        :return: The context_features of this AnalyzeRequest.
        :rtype: list[str]
        """
        return self._context_features

    @context_features.setter
    def context_features(self, context_features):
        """Set the context_features of this AnalyzeRequest.

        A list of context feature names. 

        :param context_features: The context_features of this AnalyzeRequest.
        :type context_features: list[str]
        """

        self._context_features = context_features

    @property
    def k_folds(self):
        """Get the k_folds of this AnalyzeRequest.

        Number of cross validation folds to do. Value of 1 does hold-one-out instead of k-fold.

        :return: The k_folds of this AnalyzeRequest.
        :rtype: int
        """
        return self._k_folds

    @k_folds.setter
    def k_folds(self, k_folds):
        """Set the k_folds of this AnalyzeRequest.

        Number of cross validation folds to do. Value of 1 does hold-one-out instead of k-fold.

        :param k_folds: The k_folds of this AnalyzeRequest.
        :type k_folds: int
        """

        self._k_folds = k_folds

    @property
    def num_samples(self):
        """Get the num_samples of this AnalyzeRequest.

        Number of samples used in calculating feature residuals. 

        :return: The num_samples of this AnalyzeRequest.
        :rtype: int
        """
        return self._num_samples

    @num_samples.setter
    def num_samples(self, num_samples):
        """Set the num_samples of this AnalyzeRequest.

        Number of samples used in calculating feature residuals. 

        :param num_samples: The num_samples of this AnalyzeRequest.
        :type num_samples: int
        """

        self._num_samples = num_samples

    @property
    def dt_values(self):
        """Get the dt_values of this AnalyzeRequest.

        Optional list of distance transform value hyperparameters to analyze with.

        :return: The dt_values of this AnalyzeRequest.
        :rtype: list[float]
        """
        return self._dt_values

    @dt_values.setter
    def dt_values(self, dt_values):
        """Set the dt_values of this AnalyzeRequest.

        Optional list of distance transform value hyperparameters to analyze with.

        :param dt_values: The dt_values of this AnalyzeRequest.
        :type dt_values: list[float]
        """

        self._dt_values = dt_values

    @property
    def k_values(self):
        """Get the k_values of this AnalyzeRequest.

        Optional list of k value hyperparameters to analyze with. 

        :return: The k_values of this AnalyzeRequest.
        :rtype: list[int]
        """
        return self._k_values

    @k_values.setter
    def k_values(self, k_values):
        """Set the k_values of this AnalyzeRequest.

        Optional list of k value hyperparameters to analyze with. 

        :param k_values: The k_values of this AnalyzeRequest.
        :type k_values: list[int]
        """

        self._k_values = k_values

    @property
    def p_values(self):
        """Get the p_values of this AnalyzeRequest.

        Optional list of p value hyperparameters to analyze with. 

        :return: The p_values of this AnalyzeRequest.
        :rtype: list[float]
        """
        return self._p_values

    @p_values.setter
    def p_values(self, p_values):
        """Set the p_values of this AnalyzeRequest.

        Optional list of p value hyperparameters to analyze with. 

        :param p_values: The p_values of this AnalyzeRequest.
        :type p_values: list[float]
        """

        self._p_values = p_values

    @property
    def bypass_hyperparameter_analysis(self):
        """Get the bypass_hyperparameter_analysis of this AnalyzeRequest.

        If true, bypass hyperparameter analysis. 

        :return: The bypass_hyperparameter_analysis of this AnalyzeRequest.
        :rtype: bool
        """
        return self._bypass_hyperparameter_analysis

    @bypass_hyperparameter_analysis.setter
    def bypass_hyperparameter_analysis(self, bypass_hyperparameter_analysis):
        """Set the bypass_hyperparameter_analysis of this AnalyzeRequest.

        If true, bypass hyperparameter analysis. 

        :param bypass_hyperparameter_analysis: The bypass_hyperparameter_analysis of this AnalyzeRequest.
        :type bypass_hyperparameter_analysis: bool
        """

        self._bypass_hyperparameter_analysis = bypass_hyperparameter_analysis

    @property
    def bypass_calculate_feature_residuals(self):
        """Get the bypass_calculate_feature_residuals of this AnalyzeRequest.

        If true, bypass calculation of feature residuals. 

        :return: The bypass_calculate_feature_residuals of this AnalyzeRequest.
        :rtype: bool
        """
        return self._bypass_calculate_feature_residuals

    @bypass_calculate_feature_residuals.setter
    def bypass_calculate_feature_residuals(self, bypass_calculate_feature_residuals):
        """Set the bypass_calculate_feature_residuals of this AnalyzeRequest.

        If true, bypass calculation of feature residuals. 

        :param bypass_calculate_feature_residuals: The bypass_calculate_feature_residuals of this AnalyzeRequest.
        :type bypass_calculate_feature_residuals: bool
        """

        self._bypass_calculate_feature_residuals = bypass_calculate_feature_residuals

    @property
    def bypass_calculate_feature_weights(self):
        """Get the bypass_calculate_feature_weights of this AnalyzeRequest.

        If true, bypass calculation of feature weights. 

        :return: The bypass_calculate_feature_weights of this AnalyzeRequest.
        :rtype: bool
        """
        return self._bypass_calculate_feature_weights

    @bypass_calculate_feature_weights.setter
    def bypass_calculate_feature_weights(self, bypass_calculate_feature_weights):
        """Set the bypass_calculate_feature_weights of this AnalyzeRequest.

        If true, bypass calculation of feature weights. 

        :param bypass_calculate_feature_weights: The bypass_calculate_feature_weights of this AnalyzeRequest.
        :type bypass_calculate_feature_weights: bool
        """

        self._bypass_calculate_feature_weights = bypass_calculate_feature_weights

    @property
    def targeted_model(self):
        """Get the targeted_model of this AnalyzeRequest.

        Optional value, defaults to single_targeted single_targeted: analyze hyperparameters for the specified action_features omni_targeted: analyze hyperparameters for each context feature as an action feature, ignores action_features parameter targetless: analyze hyperparameters for all context features as possible action features, ignores action_features parameter 

        :return: The targeted_model of this AnalyzeRequest.
        :rtype: str
        """
        return self._targeted_model

    @targeted_model.setter
    def targeted_model(self, targeted_model):
        """Set the targeted_model of this AnalyzeRequest.

        Optional value, defaults to single_targeted single_targeted: analyze hyperparameters for the specified action_features omni_targeted: analyze hyperparameters for each context feature as an action feature, ignores action_features parameter targetless: analyze hyperparameters for all context features as possible action features, ignores action_features parameter 

        :param targeted_model: The targeted_model of this AnalyzeRequest.
        :type targeted_model: str
        """
        allowed_values = ["single_targeted", "omni_targeted", "targetless"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and targeted_model not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `targeted_model` ({0}), must be one of {1}"  # noqa: E501
                .format(targeted_model, allowed_values)
            )

        self._targeted_model = targeted_model

    @property
    def analyze_level(self):
        """Get the analyze_level of this AnalyzeRequest.

        Optional value, if specified will analyze for the following flows:   1: predictions/accuracy (hyperparameters)   2: data synth (cache: global residuals)   3: standard explanations (cache: case prediction conviction)   4: full analysis (cache: model feature prediction conviction) 

        :return: The analyze_level of this AnalyzeRequest.
        :rtype: int
        """
        return self._analyze_level

    @analyze_level.setter
    def analyze_level(self, analyze_level):
        """Set the analyze_level of this AnalyzeRequest.

        Optional value, if specified will analyze for the following flows:   1: predictions/accuracy (hyperparameters)   2: data synth (cache: global residuals)   3: standard explanations (cache: case prediction conviction)   4: full analysis (cache: model feature prediction conviction) 

        :param analyze_level: The analyze_level of this AnalyzeRequest.
        :type analyze_level: int
        """

        self._analyze_level = analyze_level

    @property
    def num_analysis_samples(self):
        """Get the num_analysis_samples of this AnalyzeRequest.

        Optional. Number of cases to sample during analysis. Only applies for k_folds = 1. 

        :return: The num_analysis_samples of this AnalyzeRequest.
        :rtype: int
        """
        return self._num_analysis_samples

    @num_analysis_samples.setter
    def num_analysis_samples(self, num_analysis_samples):
        """Set the num_analysis_samples of this AnalyzeRequest.

        Optional. Number of cases to sample during analysis. Only applies for k_folds = 1. 

        :param num_analysis_samples: The num_analysis_samples of this AnalyzeRequest.
        :type num_analysis_samples: int
        """

        self._num_analysis_samples = num_analysis_samples

    @property
    def analysis_sub_model_size(self):
        """Get the analysis_sub_model_size of this AnalyzeRequest.

        Optional. Number of samples to use for analysis. The rest will be randomly held-out and not included in calculations. 

        :return: The analysis_sub_model_size of this AnalyzeRequest.
        :rtype: int
        """
        return self._analysis_sub_model_size

    @analysis_sub_model_size.setter
    def analysis_sub_model_size(self, analysis_sub_model_size):
        """Set the analysis_sub_model_size of this AnalyzeRequest.

        Optional. Number of samples to use for analysis. The rest will be randomly held-out and not included in calculations. 

        :param analysis_sub_model_size: The analysis_sub_model_size of this AnalyzeRequest.
        :type analysis_sub_model_size: int
        """

        self._analysis_sub_model_size = analysis_sub_model_size

    @property
    def use_deviations(self):
        """Get the use_deviations of this AnalyzeRequest.

        Optional flag, when true uses deviations for LK metric in queries.

        :return: The use_deviations of this AnalyzeRequest.
        :rtype: bool
        """
        return self._use_deviations

    @use_deviations.setter
    def use_deviations(self, use_deviations):
        """Set the use_deviations of this AnalyzeRequest.

        Optional flag, when true uses deviations for LK metric in queries.

        :param use_deviations: The use_deviations of this AnalyzeRequest.
        :type use_deviations: bool
        """

        self._use_deviations = use_deviations

    @property
    def inverse_residuals_as_weights(self):
        """Get the inverse_residuals_as_weights of this AnalyzeRequest.

        Compute and use inverse of residuals as feature weights.

        :return: The inverse_residuals_as_weights of this AnalyzeRequest.
        :rtype: bool
        """
        return self._inverse_residuals_as_weights

    @inverse_residuals_as_weights.setter
    def inverse_residuals_as_weights(self, inverse_residuals_as_weights):
        """Set the inverse_residuals_as_weights of this AnalyzeRequest.

        Compute and use inverse of residuals as feature weights.

        :param inverse_residuals_as_weights: The inverse_residuals_as_weights of this AnalyzeRequest.
        :type inverse_residuals_as_weights: bool
        """

        self._inverse_residuals_as_weights = inverse_residuals_as_weights

    @property
    def use_case_weights(self):
        """Get the use_case_weights of this AnalyzeRequest.

        Optional. When True, will scale influence weights by each case's `weight_feature` weight. 

        :return: The use_case_weights of this AnalyzeRequest.
        :rtype: bool
        """
        return self._use_case_weights

    @use_case_weights.setter
    def use_case_weights(self, use_case_weights):
        """Set the use_case_weights of this AnalyzeRequest.

        Optional. When True, will scale influence weights by each case's `weight_feature` weight. 

        :param use_case_weights: The use_case_weights of this AnalyzeRequest.
        :type use_case_weights: bool
        """

        self._use_case_weights = use_case_weights

    @property
    def weight_feature(self):
        """Get the weight_feature of this AnalyzeRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :return: The weight_feature of this AnalyzeRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this AnalyzeRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :param weight_feature: The weight_feature of this AnalyzeRequest.
        :type weight_feature: str
        """

        self._weight_feature = weight_feature

    @property
    def experimental_options(self):
        """Get the experimental_options of this AnalyzeRequest.

        Additional experimental analyze parameters.

        :return: The experimental_options of this AnalyzeRequest.
        :rtype: dict[str, object]
        """
        return self._experimental_options

    @experimental_options.setter
    def experimental_options(self, experimental_options):
        """Set the experimental_options of this AnalyzeRequest.

        Additional experimental analyze parameters.

        :param experimental_options: The experimental_options of this AnalyzeRequest.
        :type experimental_options: dict[str, object]
        """

        self._experimental_options = experimental_options

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
        if not isinstance(other, AnalyzeRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AnalyzeRequest):
            return True

        return self.to_dict() != other.to_dict()
