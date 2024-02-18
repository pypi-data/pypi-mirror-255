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


class CaseRemoveRequest(object):
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
        'num_cases': 'int',
        'case_indices': 'list[list[object]]',
        'condition': 'dict[str, object]',
        'condition_session': 'str',
        'distribute_weight_feature': 'str',
        'precision': 'str',
        'preserve_session_data': 'bool'
    }

    attribute_map = {
        'num_cases': 'num_cases',
        'case_indices': 'case_indices',
        'condition': 'condition',
        'condition_session': 'condition_session',
        'distribute_weight_feature': 'distribute_weight_feature',
        'precision': 'precision',
        'preserve_session_data': 'preserve_session_data'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, num_cases=None, case_indices=None, condition=None, condition_session=None, distribute_weight_feature=None, precision=None, preserve_session_data=False, local_vars_configuration=None):  # noqa: E501
        """CaseRemoveRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._num_cases = None
        self._case_indices = None
        self._condition = None
        self._condition_session = None
        self._distribute_weight_feature = None
        self._precision = None
        self._preserve_session_data = None

        self.num_cases = num_cases
        if case_indices is not None:
            self.case_indices = case_indices
        if condition is not None:
            self.condition = condition
        if condition_session is not None:
            self.condition_session = condition_session
        if distribute_weight_feature is not None:
            self.distribute_weight_feature = distribute_weight_feature
        if precision is not None:
            self.precision = precision
        if preserve_session_data is not None:
            self.preserve_session_data = preserve_session_data

    @property
    def num_cases(self):
        """Get the num_cases of this CaseRemoveRequest.

        The number of cases to move or remove. This is ignored if case_indices is specified.

        :return: The num_cases of this CaseRemoveRequest.
        :rtype: int
        """
        return self._num_cases

    @num_cases.setter
    def num_cases(self, num_cases):
        """Set the num_cases of this CaseRemoveRequest.

        The number of cases to move or remove. This is ignored if case_indices is specified.

        :param num_cases: The num_cases of this CaseRemoveRequest.
        :type num_cases: int
        """
        if self.local_vars_configuration.client_side_validation and num_cases is None:  # noqa: E501
            raise ValueError("Invalid value for `num_cases`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                num_cases is not None and num_cases < 1):  # noqa: E501
            raise ValueError("Invalid value for `num_cases`, must be a value greater than or equal to `1`")  # noqa: E501

        self._num_cases = num_cases

    @property
    def case_indices(self):
        """Get the case_indices of this CaseRemoveRequest.

        List of tuples containing the session id and index, where index is the original 0-based index of the case as it was trained into the session. This explicitly specifies the cases to retrieve. 

        :return: The case_indices of this CaseRemoveRequest.
        :rtype: list[list[object]]
        """
        return self._case_indices

    @case_indices.setter
    def case_indices(self, case_indices):
        """Set the case_indices of this CaseRemoveRequest.

        List of tuples containing the session id and index, where index is the original 0-based index of the case as it was trained into the session. This explicitly specifies the cases to retrieve. 

        :param case_indices: The case_indices of this CaseRemoveRequest.
        :type case_indices: list[list[object]]
        """

        self._case_indices = case_indices

    @property
    def condition(self):
        """Get the condition of this CaseRemoveRequest.

        The condition map to select the cases to remove that meet all the provided conditions. The dictionary keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. This is ignored if case_indices is specified. 

        :return: The condition of this CaseRemoveRequest.
        :rtype: dict[str, object]
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Set the condition of this CaseRemoveRequest.

        The condition map to select the cases to remove that meet all the provided conditions. The dictionary keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. This is ignored if case_indices is specified. 

        :param condition: The condition of this CaseRemoveRequest.
        :type condition: dict[str, object]
        """

        self._condition = condition

    @property
    def condition_session(self):
        """Get the condition_session of this CaseRemoveRequest.

        If specified, ignores the condition and operates on cases for the specified session id. This is ignored if case_indices is specified.

        :return: The condition_session of this CaseRemoveRequest.
        :rtype: str
        """
        return self._condition_session

    @condition_session.setter
    def condition_session(self, condition_session):
        """Set the condition_session of this CaseRemoveRequest.

        If specified, ignores the condition and operates on cases for the specified session id. This is ignored if case_indices is specified.

        :param condition_session: The condition_session of this CaseRemoveRequest.
        :type condition_session: str
        """

        self._condition_session = condition_session

    @property
    def distribute_weight_feature(self):
        """Get the distribute_weight_feature of this CaseRemoveRequest.

        When specified, will distribute the removed cases' weights from this feature into their neighbors.

        :return: The distribute_weight_feature of this CaseRemoveRequest.
        :rtype: str
        """
        return self._distribute_weight_feature

    @distribute_weight_feature.setter
    def distribute_weight_feature(self, distribute_weight_feature):
        """Set the distribute_weight_feature of this CaseRemoveRequest.

        When specified, will distribute the removed cases' weights from this feature into their neighbors.

        :param distribute_weight_feature: The distribute_weight_feature of this CaseRemoveRequest.
        :type distribute_weight_feature: str
        """

        self._distribute_weight_feature = distribute_weight_feature

    @property
    def precision(self):
        """Get the precision of this CaseRemoveRequest.

        Exact matching or fuzzy matching. This is ignored if case_indices is specified.

        :return: The precision of this CaseRemoveRequest.
        :rtype: str
        """
        return self._precision

    @precision.setter
    def precision(self, precision):
        """Set the precision of this CaseRemoveRequest.

        Exact matching or fuzzy matching. This is ignored if case_indices is specified.

        :param precision: The precision of this CaseRemoveRequest.
        :type precision: str
        """
        allowed_values = ["exact", "similar"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and precision not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `precision` ({0}), must be one of {1}"  # noqa: E501
                .format(precision, allowed_values)
            )

        self._precision = precision

    @property
    def preserve_session_data(self):
        """Get the preserve_session_data of this CaseRemoveRequest.

        When True, will remove cases without cleaning up session data.

        :return: The preserve_session_data of this CaseRemoveRequest.
        :rtype: bool
        """
        return self._preserve_session_data

    @preserve_session_data.setter
    def preserve_session_data(self, preserve_session_data):
        """Set the preserve_session_data of this CaseRemoveRequest.

        When True, will remove cases without cleaning up session data.

        :param preserve_session_data: The preserve_session_data of this CaseRemoveRequest.
        :type preserve_session_data: bool
        """

        self._preserve_session_data = preserve_session_data

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
        if not isinstance(other, CaseRemoveRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CaseRemoveRequest):
            return True

        return self.to_dict() != other.to_dict()
