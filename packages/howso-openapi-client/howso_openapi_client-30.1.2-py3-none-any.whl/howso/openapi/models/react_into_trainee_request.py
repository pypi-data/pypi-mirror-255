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


class ReactIntoTraineeRequest(object):
    """
    Auto-generated OpenAPI type.

    Request body for react into trainee.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'contributions': 'bool',
        'contributions_robust': 'bool',
        'residuals': 'bool',
        'residuals_robust': 'bool',
        'mda': 'bool',
        'mda_permutation': 'bool',
        'mda_robust': 'bool',
        'mda_robust_permutation': 'bool',
        'action_feature': 'str',
        'context_features': 'list[str]',
        'hyperparameter_param_path': 'list[str]',
        'num_robust_influence_samples': 'int',
        'num_robust_influence_samples_per_case': 'int',
        'num_robust_residual_samples': 'int',
        'num_samples': 'int',
        'sample_model_fraction': 'float',
        'sub_model_size': 'int',
        'use_case_weights': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'contributions': 'contributions',
        'contributions_robust': 'contributions_robust',
        'residuals': 'residuals',
        'residuals_robust': 'residuals_robust',
        'mda': 'mda',
        'mda_permutation': 'mda_permutation',
        'mda_robust': 'mda_robust',
        'mda_robust_permutation': 'mda_robust_permutation',
        'action_feature': 'action_feature',
        'context_features': 'context_features',
        'hyperparameter_param_path': 'hyperparameter_param_path',
        'num_robust_influence_samples': 'num_robust_influence_samples',
        'num_robust_influence_samples_per_case': 'num_robust_influence_samples_per_case',
        'num_robust_residual_samples': 'num_robust_residual_samples',
        'num_samples': 'num_samples',
        'sample_model_fraction': 'sample_model_fraction',
        'sub_model_size': 'sub_model_size',
        'use_case_weights': 'use_case_weights',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, contributions=None, contributions_robust=None, residuals=None, residuals_robust=None, mda=None, mda_permutation=None, mda_robust=None, mda_robust_permutation=None, action_feature=None, context_features=None, hyperparameter_param_path=None, num_robust_influence_samples=None, num_robust_influence_samples_per_case=None, num_robust_residual_samples=None, num_samples=None, sample_model_fraction=None, sub_model_size=None, use_case_weights=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """ReactIntoTraineeRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._contributions = None
        self._contributions_robust = None
        self._residuals = None
        self._residuals_robust = None
        self._mda = None
        self._mda_permutation = None
        self._mda_robust = None
        self._mda_robust_permutation = None
        self._action_feature = None
        self._context_features = None
        self._hyperparameter_param_path = None
        self._num_robust_influence_samples = None
        self._num_robust_influence_samples_per_case = None
        self._num_robust_residual_samples = None
        self._num_samples = None
        self._sample_model_fraction = None
        self._sub_model_size = None
        self._use_case_weights = None
        self._weight_feature = None

        if contributions is not None:
            self.contributions = contributions
        if contributions_robust is not None:
            self.contributions_robust = contributions_robust
        if residuals is not None:
            self.residuals = residuals
        if residuals_robust is not None:
            self.residuals_robust = residuals_robust
        if mda is not None:
            self.mda = mda
        if mda_permutation is not None:
            self.mda_permutation = mda_permutation
        if mda_robust is not None:
            self.mda_robust = mda_robust
        if mda_robust_permutation is not None:
            self.mda_robust_permutation = mda_robust_permutation
        if action_feature is not None:
            self.action_feature = action_feature
        if context_features is not None:
            self.context_features = context_features
        if hyperparameter_param_path is not None:
            self.hyperparameter_param_path = hyperparameter_param_path
        if num_robust_influence_samples is not None:
            self.num_robust_influence_samples = num_robust_influence_samples
        if num_robust_influence_samples_per_case is not None:
            self.num_robust_influence_samples_per_case = num_robust_influence_samples_per_case
        if num_robust_residual_samples is not None:
            self.num_robust_residual_samples = num_robust_residual_samples
        if num_samples is not None:
            self.num_samples = num_samples
        if sample_model_fraction is not None:
            self.sample_model_fraction = sample_model_fraction
        if sub_model_size is not None:
            self.sub_model_size = sub_model_size
        if use_case_weights is not None:
            self.use_case_weights = use_case_weights
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def contributions(self):
        """Get the contributions of this ReactIntoTraineeRequest.

        For each context_feature, use the full set of all other context_features to compute the mean absolute delta between prediction of action_feature with and without the context_feature in the model. False removes cached values. 

        :return: The contributions of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._contributions

    @contributions.setter
    def contributions(self, contributions):
        """Set the contributions of this ReactIntoTraineeRequest.

        For each context_feature, use the full set of all other context_features to compute the mean absolute delta between prediction of action_feature with and without the context_feature in the model. False removes cached values. 

        :param contributions: The contributions of this ReactIntoTraineeRequest.
        :type contributions: bool
        """

        self._contributions = contributions

    @property
    def contributions_robust(self):
        """Get the contributions_robust of this ReactIntoTraineeRequest.

        For each context_feature, use the robust (power set/permutation) set of all other context_features to compute the mean absolute delta between prediction of action_feature with and without the context_feature in the model. False removes cached values. 

        :return: The contributions_robust of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._contributions_robust

    @contributions_robust.setter
    def contributions_robust(self, contributions_robust):
        """Set the contributions_robust of this ReactIntoTraineeRequest.

        For each context_feature, use the robust (power set/permutation) set of all other context_features to compute the mean absolute delta between prediction of action_feature with and without the context_feature in the model. False removes cached values. 

        :param contributions_robust: The contributions_robust of this ReactIntoTraineeRequest.
        :type contributions_robust: bool
        """

        self._contributions_robust = contributions_robust

    @property
    def residuals(self):
        """Get the residuals of this ReactIntoTraineeRequest.

        When True, for each context_feature use the full set of all other context_features to predict the feature. Computes and caches MAE (mean absolute error), R^2, RMSE (root mean squared error), and Spearman Coefficient for continuous features and MAE, accuracy, precision and recall for nominal features. When False, removes previously computed values from the model. 

        :return: The residuals of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._residuals

    @residuals.setter
    def residuals(self, residuals):
        """Set the residuals of this ReactIntoTraineeRequest.

        When True, for each context_feature use the full set of all other context_features to predict the feature. Computes and caches MAE (mean absolute error), R^2, RMSE (root mean squared error), and Spearman Coefficient for continuous features and MAE, accuracy, precision and recall for nominal features. When False, removes previously computed values from the model. 

        :param residuals: The residuals of this ReactIntoTraineeRequest.
        :type residuals: bool
        """

        self._residuals = residuals

    @property
    def residuals_robust(self):
        """Get the residuals_robust of this ReactIntoTraineeRequest.

        When True, for each context_feature compute and cache the same stats as residuals but using the robust (power set/permutations) set of all other context features to predict the feature. When False, removes previously computed values from the model. 

        :return: The residuals_robust of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._residuals_robust

    @residuals_robust.setter
    def residuals_robust(self, residuals_robust):
        """Set the residuals_robust of this ReactIntoTraineeRequest.

        When True, for each context_feature compute and cache the same stats as residuals but using the robust (power set/permutations) set of all other context features to predict the feature. When False, removes previously computed values from the model. 

        :param residuals_robust: The residuals_robust of this ReactIntoTraineeRequest.
        :type residuals_robust: bool
        """

        self._residuals_robust = residuals_robust

    @property
    def mda(self):
        """Get the mda of this ReactIntoTraineeRequest.

        When True, computes Mean Decrease in Accuracy for each context feature at predicting action_feature. Drop each feature and use the full set of remaining context features for each prediction. When False, removes previously computed values from the model. 

        :return: The mda of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._mda

    @mda.setter
    def mda(self, mda):
        """Set the mda of this ReactIntoTraineeRequest.

        When True, computes Mean Decrease in Accuracy for each context feature at predicting action_feature. Drop each feature and use the full set of remaining context features for each prediction. When False, removes previously computed values from the model. 

        :param mda: The mda of this ReactIntoTraineeRequest.
        :type mda: bool
        """

        self._mda = mda

    @property
    def mda_permutation(self):
        """Get the mda_permutation of this ReactIntoTraineeRequest.

        When True, computes the Mean Decrease in Accuracy by scrambling each feature and using the full set of remaining context features for each prediction. When False, removes previously computed values from the model. 

        :return: The mda_permutation of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._mda_permutation

    @mda_permutation.setter
    def mda_permutation(self, mda_permutation):
        """Set the mda_permutation of this ReactIntoTraineeRequest.

        When True, computes the Mean Decrease in Accuracy by scrambling each feature and using the full set of remaining context features for each prediction. When False, removes previously computed values from the model. 

        :param mda_permutation: The mda_permutation of this ReactIntoTraineeRequest.
        :type mda_permutation: bool
        """

        self._mda_permutation = mda_permutation

    @property
    def mda_robust(self):
        """Get the mda_robust of this ReactIntoTraineeRequest.

        When True, computes the Mean Decrease in Accuracy by dropping each feature and using the robust (power set/permutations) set of remaining context features for each prediction. When False, removes previously computed values from the model. 

        :return: The mda_robust of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._mda_robust

    @mda_robust.setter
    def mda_robust(self, mda_robust):
        """Set the mda_robust of this ReactIntoTraineeRequest.

        When True, computes the Mean Decrease in Accuracy by dropping each feature and using the robust (power set/permutations) set of remaining context features for each prediction. When False, removes previously computed values from the model. 

        :param mda_robust: The mda_robust of this ReactIntoTraineeRequest.
        :type mda_robust: bool
        """

        self._mda_robust = mda_robust

    @property
    def mda_robust_permutation(self):
        """Get the mda_robust_permutation of this ReactIntoTraineeRequest.

        When True, computes the Mean Decrease in Accuracy by scrambling each feature and using the robust (power set/permutations) set of remaining context features for each prediction. When False, removes previously computed values from the model. 

        :return: The mda_robust_permutation of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._mda_robust_permutation

    @mda_robust_permutation.setter
    def mda_robust_permutation(self, mda_robust_permutation):
        """Set the mda_robust_permutation of this ReactIntoTraineeRequest.

        When True, computes the Mean Decrease in Accuracy by scrambling each feature and using the robust (power set/permutations) set of remaining context features for each prediction. When False, removes previously computed values from the model. 

        :param mda_robust_permutation: The mda_robust_permutation of this ReactIntoTraineeRequest.
        :type mda_robust_permutation: bool
        """

        self._mda_robust_permutation = mda_robust_permutation

    @property
    def action_feature(self):
        """Get the action_feature of this ReactIntoTraineeRequest.

        Name of target feature for which to do computations. Default is whatever the model was analyzed for, i.e., action feature for MDA and contributions, or \".targetless\" if analyzed for targetless. This parameter is required for MDA or contributions computations. 

        :return: The action_feature of this ReactIntoTraineeRequest.
        :rtype: str
        """
        return self._action_feature

    @action_feature.setter
    def action_feature(self, action_feature):
        """Set the action_feature of this ReactIntoTraineeRequest.

        Name of target feature for which to do computations. Default is whatever the model was analyzed for, i.e., action feature for MDA and contributions, or \".targetless\" if analyzed for targetless. This parameter is required for MDA or contributions computations. 

        :param action_feature: The action_feature of this ReactIntoTraineeRequest.
        :type action_feature: str
        """

        self._action_feature = action_feature

    @property
    def context_features(self):
        """Get the context_features of this ReactIntoTraineeRequest.

        List of features names to use as contexts for computations. Defaults to all non-unique features if not specified. 

        :return: The context_features of this ReactIntoTraineeRequest.
        :rtype: list[str]
        """
        return self._context_features

    @context_features.setter
    def context_features(self, context_features):
        """Set the context_features of this ReactIntoTraineeRequest.

        List of features names to use as contexts for computations. Defaults to all non-unique features if not specified. 

        :param context_features: The context_features of this ReactIntoTraineeRequest.
        :type context_features: list[str]
        """

        self._context_features = context_features

    @property
    def hyperparameter_param_path(self):
        """Get the hyperparameter_param_path of this ReactIntoTraineeRequest.

        Full path for hyperparameters to use for computation. If specified for any residual computations, takes precedence over action_feature parameter. 

        :return: The hyperparameter_param_path of this ReactIntoTraineeRequest.
        :rtype: list[str]
        """
        return self._hyperparameter_param_path

    @hyperparameter_param_path.setter
    def hyperparameter_param_path(self, hyperparameter_param_path):
        """Set the hyperparameter_param_path of this ReactIntoTraineeRequest.

        Full path for hyperparameters to use for computation. If specified for any residual computations, takes precedence over action_feature parameter. 

        :param hyperparameter_param_path: The hyperparameter_param_path of this ReactIntoTraineeRequest.
        :type hyperparameter_param_path: list[str]
        """

        self._hyperparameter_param_path = hyperparameter_param_path

    @property
    def num_robust_influence_samples(self):
        """Get the num_robust_influence_samples of this ReactIntoTraineeRequest.

        Total sample size of model to use (using sampling with replacement) for robust contribution computation. Defaults to 300. 

        :return: The num_robust_influence_samples of this ReactIntoTraineeRequest.
        :rtype: int
        """
        return self._num_robust_influence_samples

    @num_robust_influence_samples.setter
    def num_robust_influence_samples(self, num_robust_influence_samples):
        """Set the num_robust_influence_samples of this ReactIntoTraineeRequest.

        Total sample size of model to use (using sampling with replacement) for robust contribution computation. Defaults to 300. 

        :param num_robust_influence_samples: The num_robust_influence_samples of this ReactIntoTraineeRequest.
        :type num_robust_influence_samples: int
        """

        self._num_robust_influence_samples = num_robust_influence_samples

    @property
    def num_robust_influence_samples_per_case(self):
        """Get the num_robust_influence_samples_per_case of this ReactIntoTraineeRequest.

        Specifies the number of robust samples to use for each case for robust contribution computations. Defaults to 300 + 2 * (number of features). 

        :return: The num_robust_influence_samples_per_case of this ReactIntoTraineeRequest.
        :rtype: int
        """
        return self._num_robust_influence_samples_per_case

    @num_robust_influence_samples_per_case.setter
    def num_robust_influence_samples_per_case(self, num_robust_influence_samples_per_case):
        """Set the num_robust_influence_samples_per_case of this ReactIntoTraineeRequest.

        Specifies the number of robust samples to use for each case for robust contribution computations. Defaults to 300 + 2 * (number of features). 

        :param num_robust_influence_samples_per_case: The num_robust_influence_samples_per_case of this ReactIntoTraineeRequest.
        :type num_robust_influence_samples_per_case: int
        """

        self._num_robust_influence_samples_per_case = num_robust_influence_samples_per_case

    @property
    def num_robust_residual_samples(self):
        """Get the num_robust_residual_samples of this ReactIntoTraineeRequest.

        Total sample size of model to use (using sampling with replacement) for robust mda and residual computation. Defaults to 1000 * (1 + log(number of features)).  Note: robust mda will be updated to use num_robust_influence_samples in a future release. 

        :return: The num_robust_residual_samples of this ReactIntoTraineeRequest.
        :rtype: int
        """
        return self._num_robust_residual_samples

    @num_robust_residual_samples.setter
    def num_robust_residual_samples(self, num_robust_residual_samples):
        """Set the num_robust_residual_samples of this ReactIntoTraineeRequest.

        Total sample size of model to use (using sampling with replacement) for robust mda and residual computation. Defaults to 1000 * (1 + log(number of features)).  Note: robust mda will be updated to use num_robust_influence_samples in a future release. 

        :param num_robust_residual_samples: The num_robust_residual_samples of this ReactIntoTraineeRequest.
        :type num_robust_residual_samples: int
        """

        self._num_robust_residual_samples = num_robust_residual_samples

    @property
    def num_samples(self):
        """Get the num_samples of this ReactIntoTraineeRequest.

        Total sample size of model to use (using sampling with replacement) for all non-robust computation. Defaults to 1000. If specified overrides sample_model_fraction. 

        :return: The num_samples of this ReactIntoTraineeRequest.
        :rtype: int
        """
        return self._num_samples

    @num_samples.setter
    def num_samples(self, num_samples):
        """Set the num_samples of this ReactIntoTraineeRequest.

        Total sample size of model to use (using sampling with replacement) for all non-robust computation. Defaults to 1000. If specified overrides sample_model_fraction. 

        :param num_samples: The num_samples of this ReactIntoTraineeRequest.
        :type num_samples: int
        """

        self._num_samples = num_samples

    @property
    def sample_model_fraction(self):
        """Get the sample_model_fraction of this ReactIntoTraineeRequest.

        A value between 0.0 - 1.0, percent of model to use in sampling (using sampling without replacement). Applicable only to non-robust computation. Ignored if num_samples is specified. Higher values provide better accuracy at the cost of compute time. 

        :return: The sample_model_fraction of this ReactIntoTraineeRequest.
        :rtype: float
        """
        return self._sample_model_fraction

    @sample_model_fraction.setter
    def sample_model_fraction(self, sample_model_fraction):
        """Set the sample_model_fraction of this ReactIntoTraineeRequest.

        A value between 0.0 - 1.0, percent of model to use in sampling (using sampling without replacement). Applicable only to non-robust computation. Ignored if num_samples is specified. Higher values provide better accuracy at the cost of compute time. 

        :param sample_model_fraction: The sample_model_fraction of this ReactIntoTraineeRequest.
        :type sample_model_fraction: float
        """
        if (self.local_vars_configuration.client_side_validation and
                sample_model_fraction is not None and sample_model_fraction > 1):  # noqa: E501
            raise ValueError("Invalid value for `sample_model_fraction`, must be a value less than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                sample_model_fraction is not None and sample_model_fraction < 0):  # noqa: E501
            raise ValueError("Invalid value for `sample_model_fraction`, must be a value greater than or equal to `0`")  # noqa: E501

        self._sample_model_fraction = sample_model_fraction

    @property
    def sub_model_size(self):
        """Get the sub_model_size of this ReactIntoTraineeRequest.

        If specified will calculate residuals only on a sub model of the specified size from the full model. Applicable only to models > 1000 cases. 

        :return: The sub_model_size of this ReactIntoTraineeRequest.
        :rtype: int
        """
        return self._sub_model_size

    @sub_model_size.setter
    def sub_model_size(self, sub_model_size):
        """Set the sub_model_size of this ReactIntoTraineeRequest.

        If specified will calculate residuals only on a sub model of the specified size from the full model. Applicable only to models > 1000 cases. 

        :param sub_model_size: The sub_model_size of this ReactIntoTraineeRequest.
        :type sub_model_size: int
        """

        self._sub_model_size = sub_model_size

    @property
    def use_case_weights(self):
        """Get the use_case_weights of this ReactIntoTraineeRequest.

        When True, will scale influence weights by each case's weight_feature weight. 

        :return: The use_case_weights of this ReactIntoTraineeRequest.
        :rtype: bool
        """
        return self._use_case_weights

    @use_case_weights.setter
    def use_case_weights(self, use_case_weights):
        """Set the use_case_weights of this ReactIntoTraineeRequest.

        When True, will scale influence weights by each case's weight_feature weight. 

        :param use_case_weights: The use_case_weights of this ReactIntoTraineeRequest.
        :type use_case_weights: bool
        """

        self._use_case_weights = use_case_weights

    @property
    def weight_feature(self):
        """Get the weight_feature of this ReactIntoTraineeRequest.

        The name of the feature whose values to use as case weights. When left unspecified uses the internally managed case weight. 

        :return: The weight_feature of this ReactIntoTraineeRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this ReactIntoTraineeRequest.

        The name of the feature whose values to use as case weights. When left unspecified uses the internally managed case weight. 

        :param weight_feature: The weight_feature of this ReactIntoTraineeRequest.
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
        if not isinstance(other, ReactIntoTraineeRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactIntoTraineeRequest):
            return True

        return self.to_dict() != other.to_dict()
