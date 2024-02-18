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


class PairwiseDistancesRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of the pairwise distances metric request.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'from_case_indices': 'list[list[object]]',
        'from_values': 'list[list[object]]',
        'to_case_indices': 'list[list[object]]',
        'to_values': 'list[list[object]]',
        'features': 'list[str]',
        'action_feature': 'str',
        'use_case_weights': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'from_case_indices': 'from_case_indices',
        'from_values': 'from_values',
        'to_case_indices': 'to_case_indices',
        'to_values': 'to_values',
        'features': 'features',
        'action_feature': 'action_feature',
        'use_case_weights': 'use_case_weights',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, from_case_indices=None, from_values=None, to_case_indices=None, to_values=None, features=None, action_feature=None, use_case_weights=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """PairwiseDistancesRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._from_case_indices = None
        self._from_values = None
        self._to_case_indices = None
        self._to_values = None
        self._features = None
        self._action_feature = None
        self._use_case_weights = None
        self._weight_feature = None

        if from_case_indices is not None:
            self.from_case_indices = from_case_indices
        if from_values is not None:
            self.from_values = from_values
        if to_case_indices is not None:
            self.to_case_indices = to_case_indices
        if to_values is not None:
            self.to_values = to_values
        if features is not None:
            self.features = features
        if action_feature is not None:
            self.action_feature = action_feature
        if use_case_weights is not None:
            self.use_case_weights = use_case_weights
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def from_case_indices(self):
        """Get the from_case_indices of this PairwiseDistancesRequest.

        List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. If specified must be either length of 1 or match length of `to_values` or `to_case_indices`. 

        :return: The from_case_indices of this PairwiseDistancesRequest.
        :rtype: list[list[object]]
        """
        return self._from_case_indices

    @from_case_indices.setter
    def from_case_indices(self, from_case_indices):
        """Set the from_case_indices of this PairwiseDistancesRequest.

        List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. If specified must be either length of 1 or match length of `to_values` or `to_case_indices`. 

        :param from_case_indices: The from_case_indices of this PairwiseDistancesRequest.
        :type from_case_indices: list[list[object]]
        """
        if (self.local_vars_configuration.client_side_validation and
                from_case_indices is not None and len(from_case_indices) < 1):
            raise ValueError("Invalid value for `from_case_indices`, number of items must be greater than or equal to `1`")  # noqa: E501

        self._from_case_indices = from_case_indices

    @property
    def from_values(self):
        """Get the from_values of this PairwiseDistancesRequest.

        A 2d-list of case values. If specified must be either length of 1 or match length of `to_values` or `to_case_indices`.

        :return: The from_values of this PairwiseDistancesRequest.
        :rtype: list[list[object]]
        """
        return self._from_values

    @from_values.setter
    def from_values(self, from_values):
        """Set the from_values of this PairwiseDistancesRequest.

        A 2d-list of case values. If specified must be either length of 1 or match length of `to_values` or `to_case_indices`.

        :param from_values: The from_values of this PairwiseDistancesRequest.
        :type from_values: list[list[object]]
        """
        if (self.local_vars_configuration.client_side_validation and
                from_values is not None and len(from_values) < 1):
            raise ValueError("Invalid value for `from_values`, number of items must be greater than or equal to `1`")  # noqa: E501

        self._from_values = from_values

    @property
    def to_case_indices(self):
        """Get the to_case_indices of this PairwiseDistancesRequest.

        List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. If specified must be either length of 1 or match length of `from_values` or `from_case_indices`. 

        :return: The to_case_indices of this PairwiseDistancesRequest.
        :rtype: list[list[object]]
        """
        return self._to_case_indices

    @to_case_indices.setter
    def to_case_indices(self, to_case_indices):
        """Set the to_case_indices of this PairwiseDistancesRequest.

        List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. If specified must be either length of 1 or match length of `from_values` or `from_case_indices`. 

        :param to_case_indices: The to_case_indices of this PairwiseDistancesRequest.
        :type to_case_indices: list[list[object]]
        """
        if (self.local_vars_configuration.client_side_validation and
                to_case_indices is not None and len(to_case_indices) < 1):
            raise ValueError("Invalid value for `to_case_indices`, number of items must be greater than or equal to `1`")  # noqa: E501

        self._to_case_indices = to_case_indices

    @property
    def to_values(self):
        """Get the to_values of this PairwiseDistancesRequest.

        A 2d-list of case values. If specified must be either length of 1 or match length of `from_values` or `from_case_indices`.

        :return: The to_values of this PairwiseDistancesRequest.
        :rtype: list[list[object]]
        """
        return self._to_values

    @to_values.setter
    def to_values(self, to_values):
        """Set the to_values of this PairwiseDistancesRequest.

        A 2d-list of case values. If specified must be either length of 1 or match length of `from_values` or `from_case_indices`.

        :param to_values: The to_values of this PairwiseDistancesRequest.
        :type to_values: list[list[object]]
        """
        if (self.local_vars_configuration.client_side_validation and
                to_values is not None and len(to_values) < 1):
            raise ValueError("Invalid value for `to_values`, number of items must be greater than or equal to `1`")  # noqa: E501

        self._to_values = to_values

    @property
    def features(self):
        """Get the features of this PairwiseDistancesRequest.

        List of feature names to use when computing pairwise distances. If unspecified uses all features. 

        :return: The features of this PairwiseDistancesRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this PairwiseDistancesRequest.

        List of feature names to use when computing pairwise distances. If unspecified uses all features. 

        :param features: The features of this PairwiseDistancesRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def action_feature(self):
        """Get the action_feature of this PairwiseDistancesRequest.

        The action feature. If specified, uses targeted hyperparameters used to predict this `action_feature`, otherwise uses targetless hyperparameters. 

        :return: The action_feature of this PairwiseDistancesRequest.
        :rtype: str
        """
        return self._action_feature

    @action_feature.setter
    def action_feature(self, action_feature):
        """Set the action_feature of this PairwiseDistancesRequest.

        The action feature. If specified, uses targeted hyperparameters used to predict this `action_feature`, otherwise uses targetless hyperparameters. 

        :param action_feature: The action_feature of this PairwiseDistancesRequest.
        :type action_feature: str
        """

        self._action_feature = action_feature

    @property
    def use_case_weights(self):
        """Get the use_case_weights of this PairwiseDistancesRequest.

        If set to True, will scale influence weights by each case's `weight_feature` weight. 

        :return: The use_case_weights of this PairwiseDistancesRequest.
        :rtype: bool
        """
        return self._use_case_weights

    @use_case_weights.setter
    def use_case_weights(self, use_case_weights):
        """Set the use_case_weights of this PairwiseDistancesRequest.

        If set to True, will scale influence weights by each case's `weight_feature` weight. 

        :param use_case_weights: The use_case_weights of this PairwiseDistancesRequest.
        :type use_case_weights: bool
        """

        self._use_case_weights = use_case_weights

    @property
    def weight_feature(self):
        """Get the weight_feature of this PairwiseDistancesRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :return: The weight_feature of this PairwiseDistancesRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this PairwiseDistancesRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :param weight_feature: The weight_feature of this PairwiseDistancesRequest.
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
        if not isinstance(other, PairwiseDistancesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PairwiseDistancesRequest):
            return True

        return self.to_dict() != other.to_dict()
