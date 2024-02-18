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


class AutoAblationParams(object):
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
        'auto_ablation_enabled': 'bool',
        'auto_ablation_weight_feature': 'str',
        'minimum_model_size': 'float',
        'influence_weight_entropy_threshold': 'float',
        'exact_prediction_features': 'list[str]',
        'tolerance_prediction_threshold_map': 'dict[str, list[float]]',
        'relative_prediction_threshold_map': 'dict[str, float]',
        'residual_prediction_features': 'list[str]',
        'conviction_upper_threshold': 'float',
        'conviction_lower_threshold': 'float'
    }

    attribute_map = {
        'auto_ablation_enabled': 'auto_ablation_enabled',
        'auto_ablation_weight_feature': 'auto_ablation_weight_feature',
        'minimum_model_size': 'minimum_model_size',
        'influence_weight_entropy_threshold': 'influence_weight_entropy_threshold',
        'exact_prediction_features': 'exact_prediction_features',
        'tolerance_prediction_threshold_map': 'tolerance_prediction_threshold_map',
        'relative_prediction_threshold_map': 'relative_prediction_threshold_map',
        'residual_prediction_features': 'residual_prediction_features',
        'conviction_upper_threshold': 'conviction_upper_threshold',
        'conviction_lower_threshold': 'conviction_lower_threshold'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, auto_ablation_enabled=False, auto_ablation_weight_feature='.case_weight', minimum_model_size=1000, influence_weight_entropy_threshold=0.6, exact_prediction_features=None, tolerance_prediction_threshold_map=None, relative_prediction_threshold_map=None, residual_prediction_features=None, conviction_upper_threshold=None, conviction_lower_threshold=None, local_vars_configuration=None):  # noqa: E501
        """AutoAblationParams - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._auto_ablation_enabled = None
        self._auto_ablation_weight_feature = None
        self._minimum_model_size = None
        self._influence_weight_entropy_threshold = None
        self._exact_prediction_features = None
        self._tolerance_prediction_threshold_map = None
        self._relative_prediction_threshold_map = None
        self._residual_prediction_features = None
        self._conviction_upper_threshold = None
        self._conviction_lower_threshold = None

        if auto_ablation_enabled is not None:
            self.auto_ablation_enabled = auto_ablation_enabled
        if auto_ablation_weight_feature is not None:
            self.auto_ablation_weight_feature = auto_ablation_weight_feature
        if minimum_model_size is not None:
            self.minimum_model_size = minimum_model_size
        if influence_weight_entropy_threshold is not None:
            self.influence_weight_entropy_threshold = influence_weight_entropy_threshold
        if exact_prediction_features is not None:
            self.exact_prediction_features = exact_prediction_features
        if tolerance_prediction_threshold_map is not None:
            self.tolerance_prediction_threshold_map = tolerance_prediction_threshold_map
        if relative_prediction_threshold_map is not None:
            self.relative_prediction_threshold_map = relative_prediction_threshold_map
        if residual_prediction_features is not None:
            self.residual_prediction_features = residual_prediction_features
        if conviction_upper_threshold is not None:
            self.conviction_upper_threshold = conviction_upper_threshold
        if conviction_lower_threshold is not None:
            self.conviction_lower_threshold = conviction_lower_threshold

    @property
    def auto_ablation_enabled(self):
        """Get the auto_ablation_enabled of this AutoAblationParams.

        When true, auto ablation is enabled.

        :return: The auto_ablation_enabled of this AutoAblationParams.
        :rtype: bool
        """
        return self._auto_ablation_enabled

    @auto_ablation_enabled.setter
    def auto_ablation_enabled(self, auto_ablation_enabled):
        """Set the auto_ablation_enabled of this AutoAblationParams.

        When true, auto ablation is enabled.

        :param auto_ablation_enabled: The auto_ablation_enabled of this AutoAblationParams.
        :type auto_ablation_enabled: bool
        """

        self._auto_ablation_enabled = auto_ablation_enabled

    @property
    def auto_ablation_weight_feature(self):
        """Get the auto_ablation_weight_feature of this AutoAblationParams.

        The name of the weight feature used when ablating.

        :return: The auto_ablation_weight_feature of this AutoAblationParams.
        :rtype: str
        """
        return self._auto_ablation_weight_feature

    @auto_ablation_weight_feature.setter
    def auto_ablation_weight_feature(self, auto_ablation_weight_feature):
        """Set the auto_ablation_weight_feature of this AutoAblationParams.

        The name of the weight feature used when ablating.

        :param auto_ablation_weight_feature: The auto_ablation_weight_feature of this AutoAblationParams.
        :type auto_ablation_weight_feature: str
        """

        self._auto_ablation_weight_feature = auto_ablation_weight_feature

    @property
    def minimum_model_size(self):
        """Get the minimum_model_size of this AutoAblationParams.

        The minimum number of cases at which the model should.

        :return: The minimum_model_size of this AutoAblationParams.
        :rtype: float
        """
        return self._minimum_model_size

    @minimum_model_size.setter
    def minimum_model_size(self, minimum_model_size):
        """Set the minimum_model_size of this AutoAblationParams.

        The minimum number of cases at which the model should.

        :param minimum_model_size: The minimum_model_size of this AutoAblationParams.
        :type minimum_model_size: float
        """

        self._minimum_model_size = minimum_model_size

    @property
    def influence_weight_entropy_threshold(self):
        """Get the influence_weight_entropy_threshold of this AutoAblationParams.

        The influence weight entropy quantile that a case must be beneath in order to be trained.

        :return: The influence_weight_entropy_threshold of this AutoAblationParams.
        :rtype: float
        """
        return self._influence_weight_entropy_threshold

    @influence_weight_entropy_threshold.setter
    def influence_weight_entropy_threshold(self, influence_weight_entropy_threshold):
        """Set the influence_weight_entropy_threshold of this AutoAblationParams.

        The influence weight entropy quantile that a case must be beneath in order to be trained.

        :param influence_weight_entropy_threshold: The influence_weight_entropy_threshold of this AutoAblationParams.
        :type influence_weight_entropy_threshold: float
        """

        self._influence_weight_entropy_threshold = influence_weight_entropy_threshold

    @property
    def exact_prediction_features(self):
        """Get the exact_prediction_features of this AutoAblationParams.

        A list of feature names for which cases will be ablated if the feature prediction equals the case value.

        :return: The exact_prediction_features of this AutoAblationParams.
        :rtype: list[str]
        """
        return self._exact_prediction_features

    @exact_prediction_features.setter
    def exact_prediction_features(self, exact_prediction_features):
        """Set the exact_prediction_features of this AutoAblationParams.

        A list of feature names for which cases will be ablated if the feature prediction equals the case value.

        :param exact_prediction_features: The exact_prediction_features of this AutoAblationParams.
        :type exact_prediction_features: list[str]
        """

        self._exact_prediction_features = exact_prediction_features

    @property
    def tolerance_prediction_threshold_map(self):
        """Get the tolerance_prediction_threshold_map of this AutoAblationParams.

        A map of feature names to tuples of [MIN, MAX] for which cases will be ablated if the feature prediction is within (case value - MIN, case_value + MAX).

        :return: The tolerance_prediction_threshold_map of this AutoAblationParams.
        :rtype: dict[str, list[float]]
        """
        return self._tolerance_prediction_threshold_map

    @tolerance_prediction_threshold_map.setter
    def tolerance_prediction_threshold_map(self, tolerance_prediction_threshold_map):
        """Set the tolerance_prediction_threshold_map of this AutoAblationParams.

        A map of feature names to tuples of [MIN, MAX] for which cases will be ablated if the feature prediction is within (case value - MIN, case_value + MAX).

        :param tolerance_prediction_threshold_map: The tolerance_prediction_threshold_map of this AutoAblationParams.
        :type tolerance_prediction_threshold_map: dict[str, list[float]]
        """

        self._tolerance_prediction_threshold_map = tolerance_prediction_threshold_map

    @property
    def relative_prediction_threshold_map(self):
        """Get the relative_prediction_threshold_map of this AutoAblationParams.

        A map of feature names to relative percentages for which cases will be ablated if the feature prediction is within the relative error of the case value.

        :return: The relative_prediction_threshold_map of this AutoAblationParams.
        :rtype: dict[str, float]
        """
        return self._relative_prediction_threshold_map

    @relative_prediction_threshold_map.setter
    def relative_prediction_threshold_map(self, relative_prediction_threshold_map):
        """Set the relative_prediction_threshold_map of this AutoAblationParams.

        A map of feature names to relative percentages for which cases will be ablated if the feature prediction is within the relative error of the case value.

        :param relative_prediction_threshold_map: The relative_prediction_threshold_map of this AutoAblationParams.
        :type relative_prediction_threshold_map: dict[str, float]
        """

        self._relative_prediction_threshold_map = relative_prediction_threshold_map

    @property
    def residual_prediction_features(self):
        """Get the residual_prediction_features of this AutoAblationParams.

        A list of feature names for which cases will be ablated if the feature prediction is within the residual of the case value.

        :return: The residual_prediction_features of this AutoAblationParams.
        :rtype: list[str]
        """
        return self._residual_prediction_features

    @residual_prediction_features.setter
    def residual_prediction_features(self, residual_prediction_features):
        """Set the residual_prediction_features of this AutoAblationParams.

        A list of feature names for which cases will be ablated if the feature prediction is within the residual of the case value.

        :param residual_prediction_features: The residual_prediction_features of this AutoAblationParams.
        :type residual_prediction_features: list[str]
        """

        self._residual_prediction_features = residual_prediction_features

    @property
    def conviction_upper_threshold(self):
        """Get the conviction_upper_threshold of this AutoAblationParams.

        The conviction value below which cases will be ablated.

        :return: The conviction_upper_threshold of this AutoAblationParams.
        :rtype: float
        """
        return self._conviction_upper_threshold

    @conviction_upper_threshold.setter
    def conviction_upper_threshold(self, conviction_upper_threshold):
        """Set the conviction_upper_threshold of this AutoAblationParams.

        The conviction value below which cases will be ablated.

        :param conviction_upper_threshold: The conviction_upper_threshold of this AutoAblationParams.
        :type conviction_upper_threshold: float
        """

        self._conviction_upper_threshold = conviction_upper_threshold

    @property
    def conviction_lower_threshold(self):
        """Get the conviction_lower_threshold of this AutoAblationParams.

        The conviction value above which cases will be ablated.

        :return: The conviction_lower_threshold of this AutoAblationParams.
        :rtype: float
        """
        return self._conviction_lower_threshold

    @conviction_lower_threshold.setter
    def conviction_lower_threshold(self, conviction_lower_threshold):
        """Set the conviction_lower_threshold of this AutoAblationParams.

        The conviction value above which cases will be ablated.

        :param conviction_lower_threshold: The conviction_lower_threshold of this AutoAblationParams.
        :type conviction_lower_threshold: float
        """

        self._conviction_lower_threshold = conviction_lower_threshold

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
        if not isinstance(other, AutoAblationParams):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AutoAblationParams):
            return True

        return self.to_dict() != other.to_dict()
