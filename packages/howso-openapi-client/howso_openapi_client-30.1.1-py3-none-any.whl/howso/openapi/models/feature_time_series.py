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


class FeatureTimeSeries(object):
    """
    Auto-generated OpenAPI type.

    Time series options for a feature. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'type': 'str',
        'order': 'float',
        'derived_orders': 'float',
        'delta_min': 'list[float]',
        'delta_max': 'list[float]',
        'lags': 'list[int]',
        'num_lags': 'float',
        'rate_min': 'list[float]',
        'rate_max': 'list[float]',
        'series_has_terminators': 'bool',
        'stop_on_terminator': 'bool',
        'time_feature': 'bool',
        'universal': 'bool'
    }

    attribute_map = {
        'type': 'type',
        'order': 'order',
        'derived_orders': 'derived_orders',
        'delta_min': 'delta_min',
        'delta_max': 'delta_max',
        'lags': 'lags',
        'num_lags': 'num_lags',
        'rate_min': 'rate_min',
        'rate_max': 'rate_max',
        'series_has_terminators': 'series_has_terminators',
        'stop_on_terminator': 'stop_on_terminator',
        'time_feature': 'time_feature',
        'universal': 'universal'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, type=None, order=None, derived_orders=None, delta_min=None, delta_max=None, lags=None, num_lags=None, rate_min=None, rate_max=None, series_has_terminators=None, stop_on_terminator=None, time_feature=None, universal=None, local_vars_configuration=None):  # noqa: E501
        """FeatureTimeSeries - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._type = None
        self._order = None
        self._derived_orders = None
        self._delta_min = None
        self._delta_max = None
        self._lags = None
        self._num_lags = None
        self._rate_min = None
        self._rate_max = None
        self._series_has_terminators = None
        self._stop_on_terminator = None
        self._time_feature = None
        self._universal = None

        self.type = type
        if order is not None:
            self.order = order
        if derived_orders is not None:
            self.derived_orders = derived_orders
        if delta_min is not None:
            self.delta_min = delta_min
        if delta_max is not None:
            self.delta_max = delta_max
        if lags is not None:
            self.lags = lags
        if num_lags is not None:
            self.num_lags = num_lags
        if rate_min is not None:
            self.rate_min = rate_min
        if rate_max is not None:
            self.rate_max = rate_max
        if series_has_terminators is not None:
            self.series_has_terminators = series_has_terminators
        if stop_on_terminator is not None:
            self.stop_on_terminator = stop_on_terminator
        if time_feature is not None:
            self.time_feature = time_feature
        if universal is not None:
            self.universal = universal

    @property
    def type(self):
        """Get the type of this FeatureTimeSeries.

        When `rate` is specified, uses the difference of the current value from its previous value divided by the change in time since the previous value. When `delta` is specified, uses the difference of the current value from its previous value regardless of the elapsed time. Set to `delta` if feature has `time_feature` set to true. 

        :return: The type of this FeatureTimeSeries.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Set the type of this FeatureTimeSeries.

        When `rate` is specified, uses the difference of the current value from its previous value divided by the change in time since the previous value. When `delta` is specified, uses the difference of the current value from its previous value regardless of the elapsed time. Set to `delta` if feature has `time_feature` set to true. 

        :param type: The type of this FeatureTimeSeries.
        :type type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        allowed_values = ["rate", "delta"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def order(self):
        """Get the order of this FeatureTimeSeries.

        If provided, will generate the specified number of derivatives and boundary values. 

        :return: The order of this FeatureTimeSeries.
        :rtype: float
        """
        return self._order

    @order.setter
    def order(self, order):
        """Set the order of this FeatureTimeSeries.

        If provided, will generate the specified number of derivatives and boundary values. 

        :param order: The order of this FeatureTimeSeries.
        :type order: float
        """
        if (self.local_vars_configuration.client_side_validation and
                order is not None and order < 0):  # noqa: E501
            raise ValueError("Invalid value for `order`, must be a value greater than or equal to `0`")  # noqa: E501

        self._order = order

    @property
    def derived_orders(self):
        """Get the derived_orders of this FeatureTimeSeries.

        The number of orders of derivatives that should be derived instead of synthesized. Ignored if order is not provided. 

        :return: The derived_orders of this FeatureTimeSeries.
        :rtype: float
        """
        return self._derived_orders

    @derived_orders.setter
    def derived_orders(self, derived_orders):
        """Set the derived_orders of this FeatureTimeSeries.

        The number of orders of derivatives that should be derived instead of synthesized. Ignored if order is not provided. 

        :param derived_orders: The derived_orders of this FeatureTimeSeries.
        :type derived_orders: float
        """

        self._derived_orders = derived_orders

    @property
    def delta_min(self):
        """Get the delta_min of this FeatureTimeSeries.

        If specified, ensures that the smallest difference between features values is not smaller than this specified value. A null value means no min boundary. The length of the list must match the number of derivatives as specified by `order`. Only applicable when time series type is set to `delta`. 

        :return: The delta_min of this FeatureTimeSeries.
        :rtype: list[float]
        """
        return self._delta_min

    @delta_min.setter
    def delta_min(self, delta_min):
        """Set the delta_min of this FeatureTimeSeries.

        If specified, ensures that the smallest difference between features values is not smaller than this specified value. A null value means no min boundary. The length of the list must match the number of derivatives as specified by `order`. Only applicable when time series type is set to `delta`. 

        :param delta_min: The delta_min of this FeatureTimeSeries.
        :type delta_min: list[float]
        """

        self._delta_min = delta_min

    @property
    def delta_max(self):
        """Get the delta_max of this FeatureTimeSeries.

        If specified, ensures that the largest difference between feature values is not larger than this specified value. A null value means no max boundary. The length of the list must match the number of derivatives as specified by `order`. Only applicable when time series type is set to `delta`. 

        :return: The delta_max of this FeatureTimeSeries.
        :rtype: list[float]
        """
        return self._delta_max

    @delta_max.setter
    def delta_max(self, delta_max):
        """Set the delta_max of this FeatureTimeSeries.

        If specified, ensures that the largest difference between feature values is not larger than this specified value. A null value means no max boundary. The length of the list must match the number of derivatives as specified by `order`. Only applicable when time series type is set to `delta`. 

        :param delta_max: The delta_max of this FeatureTimeSeries.
        :type delta_max: list[float]
        """

        self._delta_max = delta_max

    @property
    def lags(self):
        """Get the lags of this FeatureTimeSeries.

        If specified, generates lag features containing previous values using the enumerated lag offsets. Takes precedence over `num_lags`. If neither `num_lags` nor `lags` is specified for a feature, then a single lag feature is generated. 

        :return: The lags of this FeatureTimeSeries.
        :rtype: list[int]
        """
        return self._lags

    @lags.setter
    def lags(self, lags):
        """Set the lags of this FeatureTimeSeries.

        If specified, generates lag features containing previous values using the enumerated lag offsets. Takes precedence over `num_lags`. If neither `num_lags` nor `lags` is specified for a feature, then a single lag feature is generated. 

        :param lags: The lags of this FeatureTimeSeries.
        :type lags: list[int]
        """

        self._lags = lags

    @property
    def num_lags(self):
        """Get the num_lags of this FeatureTimeSeries.

        If specified, generates the specified amount of lag features containing previous values. If `lags` is specified, then this parameter will be ignored. If neither `num_lags` nor `lags` is specified for a feature, then a single lag feature is generated. 

        :return: The num_lags of this FeatureTimeSeries.
        :rtype: float
        """
        return self._num_lags

    @num_lags.setter
    def num_lags(self, num_lags):
        """Set the num_lags of this FeatureTimeSeries.

        If specified, generates the specified amount of lag features containing previous values. If `lags` is specified, then this parameter will be ignored. If neither `num_lags` nor `lags` is specified for a feature, then a single lag feature is generated. 

        :param num_lags: The num_lags of this FeatureTimeSeries.
        :type num_lags: float
        """

        self._num_lags = num_lags

    @property
    def rate_min(self):
        """Get the rate_min of this FeatureTimeSeries.

        If specified, ensures that the rate or delta (the difference quotient, the discrete version of derivative) for this feature won't be less than the value provided. A null value means no min boundary. The value must be in epoch format for the time feature. The length of the list must match the number of derivatives as specified by `order`. Only applicable when time series type is set to `rate`. 

        :return: The rate_min of this FeatureTimeSeries.
        :rtype: list[float]
        """
        return self._rate_min

    @rate_min.setter
    def rate_min(self, rate_min):
        """Set the rate_min of this FeatureTimeSeries.

        If specified, ensures that the rate or delta (the difference quotient, the discrete version of derivative) for this feature won't be less than the value provided. A null value means no min boundary. The value must be in epoch format for the time feature. The length of the list must match the number of derivatives as specified by `order`. Only applicable when time series type is set to `rate`. 

        :param rate_min: The rate_min of this FeatureTimeSeries.
        :type rate_min: list[float]
        """

        self._rate_min = rate_min

    @property
    def rate_max(self):
        """Get the rate_max of this FeatureTimeSeries.

        If specified, ensures that the rate or delta (the difference quotient, the discrete version of derivative) for this feature won't be more than the value provided. A null value means no max boundary. The value must be in epoch format for the time feature. The length of the list must match the number of derivatives as specified by `order`. Only applicable when time series type is set to `rate`. 

        :return: The rate_max of this FeatureTimeSeries.
        :rtype: list[float]
        """
        return self._rate_max

    @rate_max.setter
    def rate_max(self, rate_max):
        """Set the rate_max of this FeatureTimeSeries.

        If specified, ensures that the rate or delta (the difference quotient, the discrete version of derivative) for this feature won't be more than the value provided. A null value means no max boundary. The value must be in epoch format for the time feature. The length of the list must match the number of derivatives as specified by `order`. Only applicable when time series type is set to `rate`. 

        :param rate_max: The rate_max of this FeatureTimeSeries.
        :type rate_max: list[float]
        """

        self._rate_max = rate_max

    @property
    def series_has_terminators(self):
        """Get the series_has_terminators of this FeatureTimeSeries.

        When true, requires that the model identify and learn values that explicitly denote the end of a series. Only applicable to id features for a series. 

        :return: The series_has_terminators of this FeatureTimeSeries.
        :rtype: bool
        """
        return self._series_has_terminators

    @series_has_terminators.setter
    def series_has_terminators(self, series_has_terminators):
        """Set the series_has_terminators of this FeatureTimeSeries.

        When true, requires that the model identify and learn values that explicitly denote the end of a series. Only applicable to id features for a series. 

        :param series_has_terminators: The series_has_terminators of this FeatureTimeSeries.
        :type series_has_terminators: bool
        """

        self._series_has_terminators = series_has_terminators

    @property
    def stop_on_terminator(self):
        """Get the stop_on_terminator of this FeatureTimeSeries.

        When true, requires that a series ends on a terminator value. Only applicable to id features for a series. 

        :return: The stop_on_terminator of this FeatureTimeSeries.
        :rtype: bool
        """
        return self._stop_on_terminator

    @stop_on_terminator.setter
    def stop_on_terminator(self, stop_on_terminator):
        """Set the stop_on_terminator of this FeatureTimeSeries.

        When true, requires that a series ends on a terminator value. Only applicable to id features for a series. 

        :param stop_on_terminator: The stop_on_terminator of this FeatureTimeSeries.
        :type stop_on_terminator: bool
        """

        self._stop_on_terminator = stop_on_terminator

    @property
    def time_feature(self):
        """Get the time_feature of this FeatureTimeSeries.

        When true, the feature will be treated as the time feature for time series modeling. Additionally, time features must use type `delta`. 

        :return: The time_feature of this FeatureTimeSeries.
        :rtype: bool
        """
        return self._time_feature

    @time_feature.setter
    def time_feature(self, time_feature):
        """Set the time_feature of this FeatureTimeSeries.

        When true, the feature will be treated as the time feature for time series modeling. Additionally, time features must use type `delta`. 

        :param time_feature: The time_feature of this FeatureTimeSeries.
        :type time_feature: bool
        """

        self._time_feature = time_feature

    @property
    def universal(self):
        """Get the universal of this FeatureTimeSeries.

        Controls whether future values of independent time series are considered. Applicable only to the time feature. When false, the time feature is not universal and allows using future data from other series in decisions; this is applicable when the time is not globally relevant and is independent for each time series. When true, universally excludes using any data with from the future from all series; this is applicable when time is globally relevant and there are events that may affect all time series. If there is any possibility of global relevancy of time, it is generally recommended to set this value to true, which is the default. 

        :return: The universal of this FeatureTimeSeries.
        :rtype: bool
        """
        return self._universal

    @universal.setter
    def universal(self, universal):
        """Set the universal of this FeatureTimeSeries.

        Controls whether future values of independent time series are considered. Applicable only to the time feature. When false, the time feature is not universal and allows using future data from other series in decisions; this is applicable when the time is not globally relevant and is independent for each time series. When true, universally excludes using any data with from the future from all series; this is applicable when time is globally relevant and there are events that may affect all time series. If there is any possibility of global relevancy of time, it is generally recommended to set this value to true, which is the default. 

        :param universal: The universal of this FeatureTimeSeries.
        :type universal: bool
        """

        self._universal = universal

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
        if not isinstance(other, FeatureTimeSeries):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureTimeSeries):
            return True

        return self.to_dict() != other.to_dict()
