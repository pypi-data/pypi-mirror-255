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


class TraineeHyperparameters(object):
    """
    Auto-generated OpenAPI type.

    A set of Trainee hyperparameters.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'k': 'float',
        'p': 'float',
        'dt': 'float',
        'all_feature_residuals_cached': 'bool',
        'use_deviations': 'bool',
        'feature_deviations': 'dict[str, float]',
        'feature_domain_attributes': 'dict[str, object]',
        'feature_weights': 'dict[str, float]',
        'param_path': 'list[str]'
    }

    attribute_map = {
        'k': 'k',
        'p': 'p',
        'dt': 'dt',
        'all_feature_residuals_cached': 'allFeatureResidualsCached',
        'use_deviations': 'useDeviations',
        'feature_deviations': 'featureDeviations',
        'feature_domain_attributes': 'featureDomainAttributes',
        'feature_weights': 'featureWeights',
        'param_path': 'paramPath'
    }

    nullable_attributes = [
        'all_feature_residuals_cached', 
        'use_deviations', 
        'feature_deviations', 
        'feature_domain_attributes', 
        'feature_weights', 
        'param_path', 
    ]

    discriminator = None

    def __init__(self, k=None, p=None, dt=None, all_feature_residuals_cached=None, use_deviations=None, feature_deviations=None, feature_domain_attributes=None, feature_weights=None, param_path=None, local_vars_configuration=None):  # noqa: E501
        """TraineeHyperparameters - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._k = None
        self._p = None
        self._dt = None
        self._all_feature_residuals_cached = None
        self._use_deviations = None
        self._feature_deviations = None
        self._feature_domain_attributes = None
        self._feature_weights = None
        self._param_path = None

        if k is not None:
            self.k = k
        if p is not None:
            self.p = p
        if dt is not None:
            self.dt = dt
        self.all_feature_residuals_cached = all_feature_residuals_cached
        self.use_deviations = use_deviations
        self.feature_deviations = feature_deviations
        self.feature_domain_attributes = feature_domain_attributes
        self.feature_weights = feature_weights
        self.param_path = param_path

    @property
    def k(self):
        """Get the k of this TraineeHyperparameters.


        :return: The k of this TraineeHyperparameters.
        :rtype: float
        """
        return self._k

    @k.setter
    def k(self, k):
        """Set the k of this TraineeHyperparameters.


        :param k: The k of this TraineeHyperparameters.
        :type k: float
        """

        self._k = k

    @property
    def p(self):
        """Get the p of this TraineeHyperparameters.


        :return: The p of this TraineeHyperparameters.
        :rtype: float
        """
        return self._p

    @p.setter
    def p(self, p):
        """Set the p of this TraineeHyperparameters.


        :param p: The p of this TraineeHyperparameters.
        :type p: float
        """

        self._p = p

    @property
    def dt(self):
        """Get the dt of this TraineeHyperparameters.


        :return: The dt of this TraineeHyperparameters.
        :rtype: float
        """
        return self._dt

    @dt.setter
    def dt(self, dt):
        """Set the dt of this TraineeHyperparameters.


        :param dt: The dt of this TraineeHyperparameters.
        :type dt: float
        """

        self._dt = dt

    @property
    def all_feature_residuals_cached(self):
        """Get the all_feature_residuals_cached of this TraineeHyperparameters.


        :return: The all_feature_residuals_cached of this TraineeHyperparameters.
        :rtype: bool
        """
        return self._all_feature_residuals_cached

    @all_feature_residuals_cached.setter
    def all_feature_residuals_cached(self, all_feature_residuals_cached):
        """Set the all_feature_residuals_cached of this TraineeHyperparameters.


        :param all_feature_residuals_cached: The all_feature_residuals_cached of this TraineeHyperparameters.
        :type all_feature_residuals_cached: bool
        """

        self._all_feature_residuals_cached = all_feature_residuals_cached

    @property
    def use_deviations(self):
        """Get the use_deviations of this TraineeHyperparameters.


        :return: The use_deviations of this TraineeHyperparameters.
        :rtype: bool
        """
        return self._use_deviations

    @use_deviations.setter
    def use_deviations(self, use_deviations):
        """Set the use_deviations of this TraineeHyperparameters.


        :param use_deviations: The use_deviations of this TraineeHyperparameters.
        :type use_deviations: bool
        """

        self._use_deviations = use_deviations

    @property
    def feature_deviations(self):
        """Get the feature_deviations of this TraineeHyperparameters.

        A map of feature names to deviations.

        :return: The feature_deviations of this TraineeHyperparameters.
        :rtype: dict[str, float]
        """
        return self._feature_deviations

    @feature_deviations.setter
    def feature_deviations(self, feature_deviations):
        """Set the feature_deviations of this TraineeHyperparameters.

        A map of feature names to deviations.

        :param feature_deviations: The feature_deviations of this TraineeHyperparameters.
        :type feature_deviations: dict[str, float]
        """

        self._feature_deviations = feature_deviations

    @property
    def feature_domain_attributes(self):
        """Get the feature_domain_attributes of this TraineeHyperparameters.


        :return: The feature_domain_attributes of this TraineeHyperparameters.
        :rtype: dict[str, object]
        """
        return self._feature_domain_attributes

    @feature_domain_attributes.setter
    def feature_domain_attributes(self, feature_domain_attributes):
        """Set the feature_domain_attributes of this TraineeHyperparameters.


        :param feature_domain_attributes: The feature_domain_attributes of this TraineeHyperparameters.
        :type feature_domain_attributes: dict[str, object]
        """

        self._feature_domain_attributes = feature_domain_attributes

    @property
    def feature_weights(self):
        """Get the feature_weights of this TraineeHyperparameters.

        A map of feature names to feature weights.

        :return: The feature_weights of this TraineeHyperparameters.
        :rtype: dict[str, float]
        """
        return self._feature_weights

    @feature_weights.setter
    def feature_weights(self, feature_weights):
        """Set the feature_weights of this TraineeHyperparameters.

        A map of feature names to feature weights.

        :param feature_weights: The feature_weights of this TraineeHyperparameters.
        :type feature_weights: dict[str, float]
        """

        self._feature_weights = feature_weights

    @property
    def param_path(self):
        """Get the param_path of this TraineeHyperparameters.


        :return: The param_path of this TraineeHyperparameters.
        :rtype: list[str]
        """
        return self._param_path

    @param_path.setter
    def param_path(self, param_path):
        """Set the param_path of this TraineeHyperparameters.


        :param param_path: The param_path of this TraineeHyperparameters.
        :type param_path: list[str]
        """

        self._param_path = param_path

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
        if not isinstance(other, TraineeHyperparameters):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TraineeHyperparameters):
            return True

        return self.to_dict() != other.to_dict()
