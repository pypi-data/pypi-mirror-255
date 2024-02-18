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


class CasesRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of a case request. 
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
        'session': 'str',
        'indicate_imputed': 'bool',
        'case_indices': 'list[list[object]]',
        'condition': 'dict[str, object]',
        'num_cases': 'float',
        'precision': 'str'
    }

    attribute_map = {
        'features': 'features',
        'session': 'session',
        'indicate_imputed': 'indicate_imputed',
        'case_indices': 'case_indices',
        'condition': 'condition',
        'num_cases': 'num_cases',
        'precision': 'precision'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, features=None, session=None, indicate_imputed=None, case_indices=None, condition=None, num_cases=None, precision=None, local_vars_configuration=None):  # noqa: E501
        """CasesRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._features = None
        self._session = None
        self._indicate_imputed = None
        self._case_indices = None
        self._condition = None
        self._num_cases = None
        self._precision = None

        if features is not None:
            self.features = features
        if session is not None:
            self.session = session
        if indicate_imputed is not None:
            self.indicate_imputed = indicate_imputed
        if case_indices is not None:
            self.case_indices = case_indices
        if condition is not None:
            self.condition = condition
        if num_cases is not None:
            self.num_cases = num_cases
        if precision is not None:
            self.precision = precision

    @property
    def features(self):
        """Get the features of this CasesRequest.

        Features to return.  If not specified, the trainee's default feature set will be used. 

        :return: The features of this CasesRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this CasesRequest.

        Features to return.  If not specified, the trainee's default feature set will be used. 

        :param features: The features of this CasesRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def session(self):
        """Get the session of this CasesRequest.

        If specified, cases for this specific session will be returned in the order they were trained. 

        :return: The session of this CasesRequest.
        :rtype: str
        """
        return self._session

    @session.setter
    def session(self, session):
        """Set the session of this CasesRequest.

        If specified, cases for this specific session will be returned in the order they were trained. 

        :param session: The session of this CasesRequest.
        :type session: str
        """

        self._session = session

    @property
    def indicate_imputed(self):
        """Get the indicate_imputed of this CasesRequest.

        If true, the response will include the list of imputed features. 

        :return: The indicate_imputed of this CasesRequest.
        :rtype: bool
        """
        return self._indicate_imputed

    @indicate_imputed.setter
    def indicate_imputed(self, indicate_imputed):
        """Set the indicate_imputed of this CasesRequest.

        If true, the response will include the list of imputed features. 

        :param indicate_imputed: The indicate_imputed of this CasesRequest.
        :type indicate_imputed: bool
        """

        self._indicate_imputed = indicate_imputed

    @property
    def case_indices(self):
        """Get the case_indices of this CasesRequest.

        List of tuples containing the session id and index, where index is the original 0-based index of the case as it was trained into the session. This explicitly specifies the cases to retrieve. 

        :return: The case_indices of this CasesRequest.
        :rtype: list[list[object]]
        """
        return self._case_indices

    @case_indices.setter
    def case_indices(self, case_indices):
        """Set the case_indices of this CasesRequest.

        List of tuples containing the session id and index, where index is the original 0-based index of the case as it was trained into the session. This explicitly specifies the cases to retrieve. 

        :param case_indices: The case_indices of this CasesRequest.
        :type case_indices: list[list[object]]
        """

        self._case_indices = case_indices

    @property
    def condition(self):
        """Get the condition of this CasesRequest.

        The condition map to select the cases to remove that meet all the provided conditions. The dictionary keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :return: The condition of this CasesRequest.
        :rtype: dict[str, object]
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Set the condition of this CasesRequest.

        The condition map to select the cases to remove that meet all the provided conditions. The dictionary keys are the feature name and values are one of:   - None   - A value, must match exactly.   - An array of two numeric values, specifying an inclusive range. Only applicable to continuous and numeric ordinal features.   - An array of string values, must match any of these values exactly. Only applicable to nominal and string ordinal features. 

        :param condition: The condition of this CasesRequest.
        :type condition: dict[str, object]
        """

        self._condition = condition

    @property
    def num_cases(self):
        """Get the num_cases of this CasesRequest.

        The maximum number of cases to retrieve. If not specified, the limit will be k cases if precision is \"similar\", or no limit if precision is \"exact\". 

        :return: The num_cases of this CasesRequest.
        :rtype: float
        """
        return self._num_cases

    @num_cases.setter
    def num_cases(self, num_cases):
        """Set the num_cases of this CasesRequest.

        The maximum number of cases to retrieve. If not specified, the limit will be k cases if precision is \"similar\", or no limit if precision is \"exact\". 

        :param num_cases: The num_cases of this CasesRequest.
        :type num_cases: float
        """

        self._num_cases = num_cases

    @property
    def precision(self):
        """Get the precision of this CasesRequest.

        Exact matching or fuzzy matching.

        :return: The precision of this CasesRequest.
        :rtype: str
        """
        return self._precision

    @precision.setter
    def precision(self, precision):
        """Set the precision of this CasesRequest.

        Exact matching or fuzzy matching.

        :param precision: The precision of this CasesRequest.
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
        if not isinstance(other, CasesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CasesRequest):
            return True

        return self.to_dict() != other.to_dict()
