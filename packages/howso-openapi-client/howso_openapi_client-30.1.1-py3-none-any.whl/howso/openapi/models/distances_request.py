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


class DistancesRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of the distances metric request.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'features': 'list[str]',
        'action_feature': 'str',
        'case_indices': 'list[list[object]]',
        'feature_values': 'list[object]',
        'use_case_weights': 'bool',
        'weight_feature': 'str',
        'row_offset': 'int',
        'row_count': 'int',
        'column_offset': 'int',
        'column_count': 'int'
    }

    attribute_map = {
        'features': 'features',
        'action_feature': 'action_feature',
        'case_indices': 'case_indices',
        'feature_values': 'feature_values',
        'use_case_weights': 'use_case_weights',
        'weight_feature': 'weight_feature',
        'row_offset': 'row_offset',
        'row_count': 'row_count',
        'column_offset': 'column_offset',
        'column_count': 'column_count'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, features=None, action_feature=None, case_indices=None, feature_values=None, use_case_weights=None, weight_feature=None, row_offset=0, row_count=500, column_offset=0, column_count=500, local_vars_configuration=None):  # noqa: E501
        """DistancesRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._features = None
        self._action_feature = None
        self._case_indices = None
        self._feature_values = None
        self._use_case_weights = None
        self._weight_feature = None
        self._row_offset = None
        self._row_count = None
        self._column_offset = None
        self._column_count = None

        if features is not None:
            self.features = features
        if action_feature is not None:
            self.action_feature = action_feature
        if case_indices is not None:
            self.case_indices = case_indices
        if feature_values is not None:
            self.feature_values = feature_values
        if use_case_weights is not None:
            self.use_case_weights = use_case_weights
        if weight_feature is not None:
            self.weight_feature = weight_feature
        self.row_offset = row_offset
        self.row_count = row_count
        self.column_offset = column_offset
        self.column_count = column_count

    @property
    def features(self):
        """Get the features of this DistancesRequest.

        List of feature names to use when computing distances. If unspecified uses all features. 

        :return: The features of this DistancesRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this DistancesRequest.

        List of feature names to use when computing distances. If unspecified uses all features. 

        :param features: The features of this DistancesRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def action_feature(self):
        """Get the action_feature of this DistancesRequest.

        The action feature. If specified, uses targeted hyperparameters used to predict this `action_feature`, otherwise uses targetless hyperparameters. 

        :return: The action_feature of this DistancesRequest.
        :rtype: str
        """
        return self._action_feature

    @action_feature.setter
    def action_feature(self, action_feature):
        """Set the action_feature of this DistancesRequest.

        The action feature. If specified, uses targeted hyperparameters used to predict this `action_feature`, otherwise uses targetless hyperparameters. 

        :param action_feature: The action_feature of this DistancesRequest.
        :type action_feature: str
        """

        self._action_feature = action_feature

    @property
    def case_indices(self):
        """Get the case_indices of this DistancesRequest.

        List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. If specified, returns distances for all of these cases. Ignored if `feature_values` is provided. If neither `feature_values` nor `case_indices` is specified, uses full dataset. 

        :return: The case_indices of this DistancesRequest.
        :rtype: list[list[object]]
        """
        return self._case_indices

    @case_indices.setter
    def case_indices(self, case_indices):
        """Set the case_indices of this DistancesRequest.

        List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. If specified, returns distances for all of these cases. Ignored if `feature_values` is provided. If neither `feature_values` nor `case_indices` is specified, uses full dataset. 

        :param case_indices: The case_indices of this DistancesRequest.
        :type case_indices: list[list[object]]
        """
        if (self.local_vars_configuration.client_side_validation and
                case_indices is not None and len(case_indices) > 2000):
            raise ValueError("Invalid value for `case_indices`, number of items must be less than or equal to `2000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                case_indices is not None and len(case_indices) < 2):
            raise ValueError("Invalid value for `case_indices`, number of items must be greater than or equal to `2`")  # noqa: E501

        self._case_indices = case_indices

    @property
    def feature_values(self):
        """Get the feature_values of this DistancesRequest.

        List of values, if specified, returns distances of the local model relative to these values, ignores `case_indices` parameter. 

        :return: The feature_values of this DistancesRequest.
        :rtype: list[object]
        """
        return self._feature_values

    @feature_values.setter
    def feature_values(self, feature_values):
        """Set the feature_values of this DistancesRequest.

        List of values, if specified, returns distances of the local model relative to these values, ignores `case_indices` parameter. 

        :param feature_values: The feature_values of this DistancesRequest.
        :type feature_values: list[object]
        """

        self._feature_values = feature_values

    @property
    def use_case_weights(self):
        """Get the use_case_weights of this DistancesRequest.

        If set to True, will scale influence weights by each case's `weight_feature` weight. 

        :return: The use_case_weights of this DistancesRequest.
        :rtype: bool
        """
        return self._use_case_weights

    @use_case_weights.setter
    def use_case_weights(self, use_case_weights):
        """Set the use_case_weights of this DistancesRequest.

        If set to True, will scale influence weights by each case's `weight_feature` weight. 

        :param use_case_weights: The use_case_weights of this DistancesRequest.
        :type use_case_weights: bool
        """

        self._use_case_weights = use_case_weights

    @property
    def weight_feature(self):
        """Get the weight_feature of this DistancesRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :return: The weight_feature of this DistancesRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this DistancesRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :param weight_feature: The weight_feature of this DistancesRequest.
        :type weight_feature: str
        """

        self._weight_feature = weight_feature

    @property
    def row_offset(self):
        """Get the row_offset of this DistancesRequest.

        The row starting offset. Used for paging of results.

        :return: The row_offset of this DistancesRequest.
        :rtype: int
        """
        return self._row_offset

    @row_offset.setter
    def row_offset(self, row_offset):
        """Set the row_offset of this DistancesRequest.

        The row starting offset. Used for paging of results.

        :param row_offset: The row_offset of this DistancesRequest.
        :type row_offset: int
        """
        if self.local_vars_configuration.client_side_validation and row_offset is None:  # noqa: E501
            raise ValueError("Invalid value for `row_offset`, must not be `None`")  # noqa: E501

        self._row_offset = row_offset

    @property
    def row_count(self):
        """Get the row_count of this DistancesRequest.

        The number of rows to include in the page.

        :return: The row_count of this DistancesRequest.
        :rtype: int
        """
        return self._row_count

    @row_count.setter
    def row_count(self, row_count):
        """Set the row_count of this DistancesRequest.

        The number of rows to include in the page.

        :param row_count: The row_count of this DistancesRequest.
        :type row_count: int
        """
        if self.local_vars_configuration.client_side_validation and row_count is None:  # noqa: E501
            raise ValueError("Invalid value for `row_count`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                row_count is not None and row_count > 2000):  # noqa: E501
            raise ValueError("Invalid value for `row_count`, must be a value less than or equal to `2000`")  # noqa: E501

        self._row_count = row_count

    @property
    def column_offset(self):
        """Get the column_offset of this DistancesRequest.

        The column starting offset. Used for paging of results.

        :return: The column_offset of this DistancesRequest.
        :rtype: int
        """
        return self._column_offset

    @column_offset.setter
    def column_offset(self, column_offset):
        """Set the column_offset of this DistancesRequest.

        The column starting offset. Used for paging of results.

        :param column_offset: The column_offset of this DistancesRequest.
        :type column_offset: int
        """
        if self.local_vars_configuration.client_side_validation and column_offset is None:  # noqa: E501
            raise ValueError("Invalid value for `column_offset`, must not be `None`")  # noqa: E501

        self._column_offset = column_offset

    @property
    def column_count(self):
        """Get the column_count of this DistancesRequest.

        The number of columns to include in the page.

        :return: The column_count of this DistancesRequest.
        :rtype: int
        """
        return self._column_count

    @column_count.setter
    def column_count(self, column_count):
        """Set the column_count of this DistancesRequest.

        The number of columns to include in the page.

        :param column_count: The column_count of this DistancesRequest.
        :type column_count: int
        """
        if self.local_vars_configuration.client_side_validation and column_count is None:  # noqa: E501
            raise ValueError("Invalid value for `column_count`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                column_count is not None and column_count > 2000):  # noqa: E501
            raise ValueError("Invalid value for `column_count`, must be a value less than or equal to `2000`")  # noqa: E501

        self._column_count = column_count

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
        if not isinstance(other, DistancesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DistancesRequest):
            return True

        return self.to_dict() != other.to_dict()
