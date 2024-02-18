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


class DerivationParameters(object):
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
        'k': 'float',
        'p': 'float',
        'distance_transform': 'float',
        'feature_weights': 'dict[str, float]',
        'feature_deviations': 'dict[str, float]',
        'nominal_class_counts': 'dict[str, float]',
        'use_irw': 'bool'
    }

    attribute_map = {
        'k': 'k',
        'p': 'p',
        'distance_transform': 'distance_transform',
        'feature_weights': 'feature_weights',
        'feature_deviations': 'feature_deviations',
        'nominal_class_counts': 'nominal_class_counts',
        'use_irw': 'use_irw'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, k=None, p=None, distance_transform=None, feature_weights=None, feature_deviations=None, nominal_class_counts=None, use_irw=None, local_vars_configuration=None):  # noqa: E501
        """DerivationParameters - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._k = None
        self._p = None
        self._distance_transform = None
        self._feature_weights = None
        self._feature_deviations = None
        self._nominal_class_counts = None
        self._use_irw = None

        if k is not None:
            self.k = k
        if p is not None:
            self.p = p
        if distance_transform is not None:
            self.distance_transform = distance_transform
        if feature_weights is not None:
            self.feature_weights = feature_weights
        if feature_deviations is not None:
            self.feature_deviations = feature_deviations
        if nominal_class_counts is not None:
            self.nominal_class_counts = nominal_class_counts
        if use_irw is not None:
            self.use_irw = use_irw

    @property
    def k(self):
        """Get the k of this DerivationParameters.

        The number of cases used for the local model.

        :return: The k of this DerivationParameters.
        :rtype: float
        """
        return self._k

    @k.setter
    def k(self, k):
        """Set the k of this DerivationParameters.

        The number of cases used for the local model.

        :param k: The k of this DerivationParameters.
        :type k: float
        """

        self._k = k

    @property
    def p(self):
        """Get the p of this DerivationParameters.

        The parameter for the Lebesgue space.

        :return: The p of this DerivationParameters.
        :rtype: float
        """
        return self._p

    @p.setter
    def p(self, p):
        """Set the p of this DerivationParameters.

        The parameter for the Lebesgue space.

        :param p: The p of this DerivationParameters.
        :type p: float
        """

        self._p = p

    @property
    def distance_transform(self):
        """Get the distance_transform of this DerivationParameters.

        The value used as an exponent to convert distances to raw influence weights.

        :return: The distance_transform of this DerivationParameters.
        :rtype: float
        """
        return self._distance_transform

    @distance_transform.setter
    def distance_transform(self, distance_transform):
        """Set the distance_transform of this DerivationParameters.

        The value used as an exponent to convert distances to raw influence weights.

        :param distance_transform: The distance_transform of this DerivationParameters.
        :type distance_transform: float
        """

        self._distance_transform = distance_transform

    @property
    def feature_weights(self):
        """Get the feature_weights of this DerivationParameters.

        The weights for each feature used in the distance metric.

        :return: The feature_weights of this DerivationParameters.
        :rtype: dict[str, float]
        """
        return self._feature_weights

    @feature_weights.setter
    def feature_weights(self, feature_weights):
        """Set the feature_weights of this DerivationParameters.

        The weights for each feature used in the distance metric.

        :param feature_weights: The feature_weights of this DerivationParameters.
        :type feature_weights: dict[str, float]
        """

        self._feature_weights = feature_weights

    @property
    def feature_deviations(self):
        """Get the feature_deviations of this DerivationParameters.

        The deviations for each feature used in the distance metric.

        :return: The feature_deviations of this DerivationParameters.
        :rtype: dict[str, float]
        """
        return self._feature_deviations

    @feature_deviations.setter
    def feature_deviations(self, feature_deviations):
        """Set the feature_deviations of this DerivationParameters.

        The deviations for each feature used in the distance metric.

        :param feature_deviations: The feature_deviations of this DerivationParameters.
        :type feature_deviations: dict[str, float]
        """

        self._feature_deviations = feature_deviations

    @property
    def nominal_class_counts(self):
        """Get the nominal_class_counts of this DerivationParameters.

        The number of unique values for each nominal feature.

        :return: The nominal_class_counts of this DerivationParameters.
        :rtype: dict[str, float]
        """
        return self._nominal_class_counts

    @nominal_class_counts.setter
    def nominal_class_counts(self, nominal_class_counts):
        """Set the nominal_class_counts of this DerivationParameters.

        The number of unique values for each nominal feature.

        :param nominal_class_counts: The nominal_class_counts of this DerivationParameters.
        :type nominal_class_counts: dict[str, float]
        """

        self._nominal_class_counts = nominal_class_counts

    @property
    def use_irw(self):
        """Get the use_irw of this DerivationParameters.

        A flag indicating if feature weights were derived using inverse residual weighting.

        :return: The use_irw of this DerivationParameters.
        :rtype: bool
        """
        return self._use_irw

    @use_irw.setter
    def use_irw(self, use_irw):
        """Set the use_irw of this DerivationParameters.

        A flag indicating if feature weights were derived using inverse residual weighting.

        :param use_irw: The use_irw of this DerivationParameters.
        :type use_irw: bool
        """

        self._use_irw = use_irw

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
        if not isinstance(other, DerivationParameters):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DerivationParameters):
            return True

        return self.to_dict() != other.to_dict()
