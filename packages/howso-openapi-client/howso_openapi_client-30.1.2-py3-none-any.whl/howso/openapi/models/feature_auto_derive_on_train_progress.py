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


class FeatureAutoDeriveOnTrainProgress(object):
    """
    Auto-generated OpenAPI type.

    Derive feature by creating two new continuous features: `.series_progress` and `.series_progress_delta`. Series progress values range from 0 to 1.0 for each case in the series. Series progress delta values are the delta value of the progress for each case. Both of these features are used to determine when to stop series synthesis. 
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
        'series_id_features': 'list[str]'
    }

    attribute_map = {
        'derive_type': 'derive_type',
        'series_id_features': 'series_id_features'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, derive_type=None, series_id_features=None, local_vars_configuration=None):  # noqa: E501
        """FeatureAutoDeriveOnTrainProgress - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._derive_type = None
        self._series_id_features = None

        self.derive_type = derive_type
        self.series_id_features = series_id_features

    @property
    def derive_type(self):
        """Get the derive_type of this FeatureAutoDeriveOnTrainProgress.

        The train derive operation type.

        :return: The derive_type of this FeatureAutoDeriveOnTrainProgress.
        :rtype: str
        """
        return self._derive_type

    @derive_type.setter
    def derive_type(self, derive_type):
        """Set the derive_type of this FeatureAutoDeriveOnTrainProgress.

        The train derive operation type.

        :param derive_type: The derive_type of this FeatureAutoDeriveOnTrainProgress.
        :type derive_type: str
        """
        if self.local_vars_configuration.client_side_validation and derive_type is None:  # noqa: E501
            raise ValueError("Invalid value for `derive_type`, must not be `None`")  # noqa: E501

        self._derive_type = derive_type

    @property
    def series_id_features(self):
        """Get the series_id_features of this FeatureAutoDeriveOnTrainProgress.

        Feature name(s) of series for which to derive this feature. A series is the conjunction of all the features specified by this attribute. 

        :return: The series_id_features of this FeatureAutoDeriveOnTrainProgress.
        :rtype: list[str]
        """
        return self._series_id_features

    @series_id_features.setter
    def series_id_features(self, series_id_features):
        """Set the series_id_features of this FeatureAutoDeriveOnTrainProgress.

        Feature name(s) of series for which to derive this feature. A series is the conjunction of all the features specified by this attribute. 

        :param series_id_features: The series_id_features of this FeatureAutoDeriveOnTrainProgress.
        :type series_id_features: list[str]
        """
        if self.local_vars_configuration.client_side_validation and series_id_features is None:  # noqa: E501
            raise ValueError("Invalid value for `series_id_features`, must not be `None`")  # noqa: E501

        self._series_id_features = series_id_features

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
        if not isinstance(other, FeatureAutoDeriveOnTrainProgress):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureAutoDeriveOnTrainProgress):
            return True

        return self.to_dict() != other.to_dict()
