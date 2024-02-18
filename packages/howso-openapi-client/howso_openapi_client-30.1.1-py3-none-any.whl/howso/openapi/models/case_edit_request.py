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


class CaseEditRequest(object):
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
        'features': 'list[str]',
        'feature_values': 'list[object]',
        'case_indices': 'list[list[object]]',
        'condition': 'dict[str, object]',
        'condition_session': 'str',
        'num_cases': 'float',
        'precision': 'str'
    }

    attribute_map = {
        'features': 'features',
        'feature_values': 'feature_values',
        'case_indices': 'case_indices',
        'condition': 'condition',
        'condition_session': 'condition_session',
        'num_cases': 'num_cases',
        'precision': 'precision'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, features=None, feature_values=None, case_indices=None, condition=None, condition_session=None, num_cases=None, precision=None, local_vars_configuration=None):  # noqa: E501
        """CaseEditRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._features = None
        self._feature_values = None
        self._case_indices = None
        self._condition = None
        self._condition_session = None
        self._num_cases = None
        self._precision = None

        if features is not None:
            self.features = features
        if feature_values is not None:
            self.feature_values = feature_values
        if case_indices is not None:
            self.case_indices = case_indices
        if condition is not None:
            self.condition = condition
        if condition_session is not None:
            self.condition_session = condition_session
        if num_cases is not None:
            self.num_cases = num_cases
        if precision is not None:
            self.precision = precision

    @property
    def features(self):
        """Get the features of this CaseEditRequest.

        The names of the features to edit.

        :return: The features of this CaseEditRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this CaseEditRequest.

        The names of the features to edit.

        :param features: The features of this CaseEditRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def feature_values(self):
        """Get the feature_values of this CaseEditRequest.

        The feature values to edit the case with.

        :return: The feature_values of this CaseEditRequest.
        :rtype: list[object]
        """
        return self._feature_values

    @feature_values.setter
    def feature_values(self, feature_values):
        """Set the feature_values of this CaseEditRequest.

        The feature values to edit the case with.

        :param feature_values: The feature_values of this CaseEditRequest.
        :type feature_values: list[object]
        """

        self._feature_values = feature_values

    @property
    def case_indices(self):
        """Get the case_indices of this CaseEditRequest.

        List of tuples containing the session id and index, where index is the original 0-based index of the case as it was trained into the session. This explicitly specifies the cases to edit. When specified, `condition` and `condition_session` are ignored. 

        :return: The case_indices of this CaseEditRequest.
        :rtype: list[list[object]]
        """
        return self._case_indices

    @case_indices.setter
    def case_indices(self, case_indices):
        """Set the case_indices of this CaseEditRequest.

        List of tuples containing the session id and index, where index is the original 0-based index of the case as it was trained into the session. This explicitly specifies the cases to edit. When specified, `condition` and `condition_session` are ignored. 

        :param case_indices: The case_indices of this CaseEditRequest.
        :type case_indices: list[list[object]]
        """

        self._case_indices = case_indices

    @property
    def condition(self):
        """Get the condition of this CaseEditRequest.

        A condition map to select which cases to edit. The dictionary keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :return: The condition of this CaseEditRequest.
        :rtype: dict[str, object]
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Set the condition of this CaseEditRequest.

        A condition map to select which cases to edit. The dictionary keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :param condition: The condition of this CaseEditRequest.
        :type condition: dict[str, object]
        """

        self._condition = condition

    @property
    def condition_session(self):
        """Get the condition_session of this CaseEditRequest.

        If specified, ignores the condition and operates on cases for the specified session id.

        :return: The condition_session of this CaseEditRequest.
        :rtype: str
        """
        return self._condition_session

    @condition_session.setter
    def condition_session(self, condition_session):
        """Set the condition_session of this CaseEditRequest.

        If specified, ignores the condition and operates on cases for the specified session id.

        :param condition_session: The condition_session of this CaseEditRequest.
        :type condition_session: str
        """

        self._condition_session = condition_session

    @property
    def num_cases(self):
        """Get the num_cases of this CaseEditRequest.

        The maximum number of cases to edit. If not specified, the limit will be k cases if precision is \"similar\", or no limit if precision is \"exact\". 

        :return: The num_cases of this CaseEditRequest.
        :rtype: float
        """
        return self._num_cases

    @num_cases.setter
    def num_cases(self, num_cases):
        """Set the num_cases of this CaseEditRequest.

        The maximum number of cases to edit. If not specified, the limit will be k cases if precision is \"similar\", or no limit if precision is \"exact\". 

        :param num_cases: The num_cases of this CaseEditRequest.
        :type num_cases: float
        """

        self._num_cases = num_cases

    @property
    def precision(self):
        """Get the precision of this CaseEditRequest.

        Exact matching or fuzzy matching.

        :return: The precision of this CaseEditRequest.
        :rtype: str
        """
        return self._precision

    @precision.setter
    def precision(self, precision):
        """Set the precision of this CaseEditRequest.

        Exact matching or fuzzy matching.

        :param precision: The precision of this CaseEditRequest.
        :type precision: str
        """
        allowed_values = ["exact", "similar"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and precision not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `precision` ({0}), must be one of {1}"  # noqa: E501
                .format(precision, allowed_values)
            )

        self._precision = precision

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
        if not isinstance(other, CaseEditRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CaseEditRequest):
            return True

        return self.to_dict() != other.to_dict()
