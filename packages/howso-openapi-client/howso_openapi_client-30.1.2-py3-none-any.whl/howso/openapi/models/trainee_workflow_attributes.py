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


class TraineeWorkflowAttributes(object):
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
        'default_hyperparameter_map': 'TraineeHyperparameters',
        'hyperparameter_map': 'dict[str, object]',
        'auto_analyze_enabled': 'bool',
        'auto_analyze_limit_size': 'int',
        'analyze_growth_factor': 'float',
        'analyze_threshold': 'int'
    }

    attribute_map = {
        'default_hyperparameter_map': 'default_hyperparameter_map',
        'hyperparameter_map': 'hyperparameter_map',
        'auto_analyze_enabled': 'auto_analyze_enabled',
        'auto_analyze_limit_size': 'auto_analyze_limit_size',
        'analyze_growth_factor': 'analyze_growth_factor',
        'analyze_threshold': 'analyze_threshold'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, default_hyperparameter_map=None, hyperparameter_map=None, auto_analyze_enabled=None, auto_analyze_limit_size=None, analyze_growth_factor=None, analyze_threshold=None, local_vars_configuration=None):  # noqa: E501
        """TraineeWorkflowAttributes - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._default_hyperparameter_map = None
        self._hyperparameter_map = None
        self._auto_analyze_enabled = None
        self._auto_analyze_limit_size = None
        self._analyze_growth_factor = None
        self._analyze_threshold = None

        if default_hyperparameter_map is not None:
            self.default_hyperparameter_map = default_hyperparameter_map
        if hyperparameter_map is not None:
            self.hyperparameter_map = hyperparameter_map
        if auto_analyze_enabled is not None:
            self.auto_analyze_enabled = auto_analyze_enabled
        if auto_analyze_limit_size is not None:
            self.auto_analyze_limit_size = auto_analyze_limit_size
        if analyze_growth_factor is not None:
            self.analyze_growth_factor = analyze_growth_factor
        if analyze_threshold is not None:
            self.analyze_threshold = analyze_threshold

    @property
    def default_hyperparameter_map(self):
        """Get the default_hyperparameter_map of this TraineeWorkflowAttributes.


        :return: The default_hyperparameter_map of this TraineeWorkflowAttributes.
        :rtype: TraineeHyperparameters
        """
        return self._default_hyperparameter_map

    @default_hyperparameter_map.setter
    def default_hyperparameter_map(self, default_hyperparameter_map):
        """Set the default_hyperparameter_map of this TraineeWorkflowAttributes.


        :param default_hyperparameter_map: The default_hyperparameter_map of this TraineeWorkflowAttributes.
        :type default_hyperparameter_map: TraineeHyperparameters
        """

        self._default_hyperparameter_map = default_hyperparameter_map

    @property
    def hyperparameter_map(self):
        """Get the hyperparameter_map of this TraineeWorkflowAttributes.


        :return: The hyperparameter_map of this TraineeWorkflowAttributes.
        :rtype: dict[str, object]
        """
        return self._hyperparameter_map

    @hyperparameter_map.setter
    def hyperparameter_map(self, hyperparameter_map):
        """Set the hyperparameter_map of this TraineeWorkflowAttributes.


        :param hyperparameter_map: The hyperparameter_map of this TraineeWorkflowAttributes.
        :type hyperparameter_map: dict[str, object]
        """

        self._hyperparameter_map = hyperparameter_map

    @property
    def auto_analyze_enabled(self):
        """Get the auto_analyze_enabled of this TraineeWorkflowAttributes.

        When True, the train operation returns when it's time for the model to be analyzed again.

        :return: The auto_analyze_enabled of this TraineeWorkflowAttributes.
        :rtype: bool
        """
        return self._auto_analyze_enabled

    @auto_analyze_enabled.setter
    def auto_analyze_enabled(self, auto_analyze_enabled):
        """Set the auto_analyze_enabled of this TraineeWorkflowAttributes.

        When True, the train operation returns when it's time for the model to be analyzed again.

        :param auto_analyze_enabled: The auto_analyze_enabled of this TraineeWorkflowAttributes.
        :type auto_analyze_enabled: bool
        """

        self._auto_analyze_enabled = auto_analyze_enabled

    @property
    def auto_analyze_limit_size(self):
        """Get the auto_analyze_limit_size of this TraineeWorkflowAttributes.

        The size of of the model at which to stop doing auto-analysis. Value of 0 means no limit.

        :return: The auto_analyze_limit_size of this TraineeWorkflowAttributes.
        :rtype: int
        """
        return self._auto_analyze_limit_size

    @auto_analyze_limit_size.setter
    def auto_analyze_limit_size(self, auto_analyze_limit_size):
        """Set the auto_analyze_limit_size of this TraineeWorkflowAttributes.

        The size of of the model at which to stop doing auto-analysis. Value of 0 means no limit.

        :param auto_analyze_limit_size: The auto_analyze_limit_size of this TraineeWorkflowAttributes.
        :type auto_analyze_limit_size: int
        """

        self._auto_analyze_limit_size = auto_analyze_limit_size

    @property
    def analyze_growth_factor(self):
        """Get the analyze_growth_factor of this TraineeWorkflowAttributes.

        The factor by which to increase the analyze threshold every time the model grows to the current threshold size.

        :return: The analyze_growth_factor of this TraineeWorkflowAttributes.
        :rtype: float
        """
        return self._analyze_growth_factor

    @analyze_growth_factor.setter
    def analyze_growth_factor(self, analyze_growth_factor):
        """Set the analyze_growth_factor of this TraineeWorkflowAttributes.

        The factor by which to increase the analyze threshold every time the model grows to the current threshold size.

        :param analyze_growth_factor: The analyze_growth_factor of this TraineeWorkflowAttributes.
        :type analyze_growth_factor: float
        """

        self._analyze_growth_factor = analyze_growth_factor

    @property
    def analyze_threshold(self):
        """Get the analyze_threshold of this TraineeWorkflowAttributes.

        The threshold for the number of cases at which the model should be re-analyzed.

        :return: The analyze_threshold of this TraineeWorkflowAttributes.
        :rtype: int
        """
        return self._analyze_threshold

    @analyze_threshold.setter
    def analyze_threshold(self, analyze_threshold):
        """Set the analyze_threshold of this TraineeWorkflowAttributes.

        The threshold for the number of cases at which the model should be re-analyzed.

        :param analyze_threshold: The analyze_threshold of this TraineeWorkflowAttributes.
        :type analyze_threshold: int
        """

        self._analyze_threshold = analyze_threshold

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
        if not isinstance(other, TraineeWorkflowAttributes):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TraineeWorkflowAttributes):
            return True

        return self.to_dict() != other.to_dict()
