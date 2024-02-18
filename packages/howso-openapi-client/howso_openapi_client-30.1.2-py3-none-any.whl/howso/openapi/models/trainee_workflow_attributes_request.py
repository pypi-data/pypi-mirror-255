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


class TraineeWorkflowAttributesRequest(object):
    """
    Auto-generated OpenAPI type.

    Parameters that get passed to get_internal_parameters.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'action_feature': 'str',
        'context_features': 'list[str]',
        'mode': 'str',
        'weight_feature': 'str'
    }

    attribute_map = {
        'action_feature': 'action_feature',
        'context_features': 'context_features',
        'mode': 'mode',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, action_feature=None, context_features=None, mode=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """TraineeWorkflowAttributesRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_feature = None
        self._context_features = None
        self._mode = None
        self._weight_feature = None

        if action_feature is not None:
            self.action_feature = action_feature
        if context_features is not None:
            self.context_features = context_features
        if mode is not None:
            self.mode = mode
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def action_feature(self):
        """Get the action_feature of this TraineeWorkflowAttributesRequest.

        The action feature used to determine the desired hyperparameters.

        :return: The action_feature of this TraineeWorkflowAttributesRequest.
        :rtype: str
        """
        return self._action_feature

    @action_feature.setter
    def action_feature(self, action_feature):
        """Set the action_feature of this TraineeWorkflowAttributesRequest.

        The action feature used to determine the desired hyperparameters.

        :param action_feature: The action_feature of this TraineeWorkflowAttributesRequest.
        :type action_feature: str
        """

        self._action_feature = action_feature

    @property
    def context_features(self):
        """Get the context_features of this TraineeWorkflowAttributesRequest.

        The context features used to determine the desired hyperparameters.

        :return: The context_features of this TraineeWorkflowAttributesRequest.
        :rtype: list[str]
        """
        return self._context_features

    @context_features.setter
    def context_features(self, context_features):
        """Set the context_features of this TraineeWorkflowAttributesRequest.

        The context features used to determine the desired hyperparameters.

        :param context_features: The context_features of this TraineeWorkflowAttributesRequest.
        :type context_features: list[str]
        """

        self._context_features = context_features

    @property
    def mode(self):
        """Get the mode of this TraineeWorkflowAttributesRequest.

        The mode of calculation (robust or full) used to determine the desired hyperparameters.

        :return: The mode of this TraineeWorkflowAttributesRequest.
        :rtype: str
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Set the mode of this TraineeWorkflowAttributesRequest.

        The mode of calculation (robust or full) used to determine the desired hyperparameters.

        :param mode: The mode of this TraineeWorkflowAttributesRequest.
        :type mode: str
        """
        allowed_values = ["robust", "full"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and mode not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `mode` ({0}), must be one of {1}"  # noqa: E501
                .format(mode, allowed_values)
            )

        self._mode = mode

    @property
    def weight_feature(self):
        """Get the weight_feature of this TraineeWorkflowAttributesRequest.

        The weight feature used to determine the desired hyperparameters.

        :return: The weight_feature of this TraineeWorkflowAttributesRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this TraineeWorkflowAttributesRequest.

        The weight feature used to determine the desired hyperparameters.

        :param weight_feature: The weight_feature of this TraineeWorkflowAttributesRequest.
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
        if not isinstance(other, TraineeWorkflowAttributesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TraineeWorkflowAttributesRequest):
            return True

        return self.to_dict() != other.to_dict()
