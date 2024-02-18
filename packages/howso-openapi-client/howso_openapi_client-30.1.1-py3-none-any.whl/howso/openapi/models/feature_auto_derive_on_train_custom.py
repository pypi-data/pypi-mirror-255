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


class FeatureAutoDeriveOnTrainCustom(object):
    """
    Auto-generated OpenAPI type.

    Derive feature using the specified `code`. For each series, where each series is defined by `series_id_features`, the rows are processed in order, after being sorted by `ordered_by_features`. If series is not specified, processes the entire dataset. Referencing data in rows uses 0-based indexing, where the current row index is 0, the previous row's is 1, etc. Specified code may do simple logic and numeric operations on feature values referenced via feature name and row offset.  Examples: - ``\"#x 1\"`` : Use the value for feature 'x' from the previously processed row (offset of 1, one lag value). - ``\"(- #y 0 #x 1)\"`` : Feature 'y' value from current (offset 0) row  minus feature 'x' value from previous (offset 1) row. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'derive_type': 'str',
        'code': 'str',
        'series_id_features': 'list[str]',
        'ordered_by_features': 'list[str]'
    }

    attribute_map = {
        'derive_type': 'derive_type',
        'code': 'code',
        'series_id_features': 'series_id_features',
        'ordered_by_features': 'ordered_by_features'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, derive_type=None, code=None, series_id_features=None, ordered_by_features=None, local_vars_configuration=None):  # noqa: E501
        """FeatureAutoDeriveOnTrainCustom - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._derive_type = None
        self._code = None
        self._series_id_features = None
        self._ordered_by_features = None

        self.derive_type = derive_type
        self.code = code
        if series_id_features is not None:
            self.series_id_features = series_id_features
        if ordered_by_features is not None:
            self.ordered_by_features = ordered_by_features

    @property
    def derive_type(self):
        """Get the derive_type of this FeatureAutoDeriveOnTrainCustom.

        The train derive operation type.

        :return: The derive_type of this FeatureAutoDeriveOnTrainCustom.
        :rtype: str
        """
        return self._derive_type

    @derive_type.setter
    def derive_type(self, derive_type):
        """Set the derive_type of this FeatureAutoDeriveOnTrainCustom.

        The train derive operation type.

        :param derive_type: The derive_type of this FeatureAutoDeriveOnTrainCustom.
        :type derive_type: str
        """
        if self.local_vars_configuration.client_side_validation and derive_type is None:  # noqa: E501
            raise ValueError("Invalid value for `derive_type`, must not be `None`")  # noqa: E501

        self._derive_type = derive_type

    @property
    def code(self):
        """Get the code of this FeatureAutoDeriveOnTrainCustom.

        Amalgam code describing how feature could be derived.

        :return: The code of this FeatureAutoDeriveOnTrainCustom.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Set the code of this FeatureAutoDeriveOnTrainCustom.

        Amalgam code describing how feature could be derived.

        :param code: The code of this FeatureAutoDeriveOnTrainCustom.
        :type code: str
        """
        if self.local_vars_configuration.client_side_validation and code is None:  # noqa: E501
            raise ValueError("Invalid value for `code`, must not be `None`")  # noqa: E501

        self._code = code

    @property
    def series_id_features(self):
        """Get the series_id_features of this FeatureAutoDeriveOnTrainCustom.

        Feature name(s) of series for which to derive this feature. A series is the conjunction of all the features specified by this attribute. 

        :return: The series_id_features of this FeatureAutoDeriveOnTrainCustom.
        :rtype: list[str]
        """
        return self._series_id_features

    @series_id_features.setter
    def series_id_features(self, series_id_features):
        """Set the series_id_features of this FeatureAutoDeriveOnTrainCustom.

        Feature name(s) of series for which to derive this feature. A series is the conjunction of all the features specified by this attribute. 

        :param series_id_features: The series_id_features of this FeatureAutoDeriveOnTrainCustom.
        :type series_id_features: list[str]
        """

        self._series_id_features = series_id_features

    @property
    def ordered_by_features(self):
        """Get the ordered_by_features of this FeatureAutoDeriveOnTrainCustom.

        Feature name(s) by which to order the series specified by `series_id_features`. Series values are order by the order of feature names specified by this attribute. 

        :return: The ordered_by_features of this FeatureAutoDeriveOnTrainCustom.
        :rtype: list[str]
        """
        return self._ordered_by_features

    @ordered_by_features.setter
    def ordered_by_features(self, ordered_by_features):
        """Set the ordered_by_features of this FeatureAutoDeriveOnTrainCustom.

        Feature name(s) by which to order the series specified by `series_id_features`. Series values are order by the order of feature names specified by this attribute. 

        :param ordered_by_features: The ordered_by_features of this FeatureAutoDeriveOnTrainCustom.
        :type ordered_by_features: list[str]
        """

        self._ordered_by_features = ordered_by_features

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
        if not isinstance(other, FeatureAutoDeriveOnTrainCustom):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureAutoDeriveOnTrainCustom):
            return True

        return self.to_dict() != other.to_dict()
