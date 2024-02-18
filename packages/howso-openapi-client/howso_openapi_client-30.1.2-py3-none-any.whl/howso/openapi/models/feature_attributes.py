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


class FeatureAttributes(object):
    """
    Auto-generated OpenAPI type.

    The mapping of attributes for a single feature. 
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
        'auto_derive_on_train': 'FeatureAutoDeriveOnTrain',
        'bounds': 'FeatureBounds',
        'cycle_length': 'int',
        'data_type': 'str',
        'date_time_format': 'str',
        'decimal_places': 'int',
        'dependent_features': 'list[str]',
        'derived_feature_code': 'str',
        'id_feature': 'bool',
        'locale': 'str',
        'non_sensitive': 'bool',
        'null_is_dependent': 'bool',
        'observational_error': 'float',
        'original_type': 'FeatureOriginalType',
        'original_format': 'dict[str, object]',
        'post_process': 'str',
        'significant_digits': 'int',
        'subtype': 'str',
        'time_delta_format': 'str',
        'time_series': 'FeatureTimeSeries',
        'unique': 'bool'
    }

    attribute_map = {
        'type': 'type',
        'auto_derive_on_train': 'auto_derive_on_train',
        'bounds': 'bounds',
        'cycle_length': 'cycle_length',
        'data_type': 'data_type',
        'date_time_format': 'date_time_format',
        'decimal_places': 'decimal_places',
        'dependent_features': 'dependent_features',
        'derived_feature_code': 'derived_feature_code',
        'id_feature': 'id_feature',
        'locale': 'locale',
        'non_sensitive': 'non_sensitive',
        'null_is_dependent': 'null_is_dependent',
        'observational_error': 'observational_error',
        'original_type': 'original_type',
        'original_format': 'original_format',
        'post_process': 'post_process',
        'significant_digits': 'significant_digits',
        'subtype': 'subtype',
        'time_delta_format': 'time_delta_format',
        'time_series': 'time_series',
        'unique': 'unique'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, type=None, auto_derive_on_train=None, bounds=None, cycle_length=None, data_type=None, date_time_format=None, decimal_places=None, dependent_features=None, derived_feature_code=None, id_feature=None, locale=None, non_sensitive=None, null_is_dependent=None, observational_error=None, original_type=None, original_format=None, post_process=None, significant_digits=None, subtype=None, time_delta_format=None, time_series=None, unique=None, local_vars_configuration=None):  # noqa: E501
        """FeatureAttributes - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._type = None
        self._auto_derive_on_train = None
        self._bounds = None
        self._cycle_length = None
        self._data_type = None
        self._date_time_format = None
        self._decimal_places = None
        self._dependent_features = None
        self._derived_feature_code = None
        self._id_feature = None
        self._locale = None
        self._non_sensitive = None
        self._null_is_dependent = None
        self._observational_error = None
        self._original_type = None
        self._original_format = None
        self._post_process = None
        self._significant_digits = None
        self._subtype = None
        self._time_delta_format = None
        self._time_series = None
        self._unique = None

        self.type = type
        if auto_derive_on_train is not None:
            self.auto_derive_on_train = auto_derive_on_train
        if bounds is not None:
            self.bounds = bounds
        if cycle_length is not None:
            self.cycle_length = cycle_length
        if data_type is not None:
            self.data_type = data_type
        if date_time_format is not None:
            self.date_time_format = date_time_format
        if decimal_places is not None:
            self.decimal_places = decimal_places
        if dependent_features is not None:
            self.dependent_features = dependent_features
        if derived_feature_code is not None:
            self.derived_feature_code = derived_feature_code
        if id_feature is not None:
            self.id_feature = id_feature
        if locale is not None:
            self.locale = locale
        if non_sensitive is not None:
            self.non_sensitive = non_sensitive
        if null_is_dependent is not None:
            self.null_is_dependent = null_is_dependent
        if observational_error is not None:
            self.observational_error = observational_error
        if original_type is not None:
            self.original_type = original_type
        if original_format is not None:
            self.original_format = original_format
        if post_process is not None:
            self.post_process = post_process
        if significant_digits is not None:
            self.significant_digits = significant_digits
        if subtype is not None:
            self.subtype = subtype
        if time_delta_format is not None:
            self.time_delta_format = time_delta_format
        if time_series is not None:
            self.time_series = time_series
        if unique is not None:
            self.unique = unique

    @property
    def type(self):
        """Get the type of this FeatureAttributes.

        The type of the feature.  - continuous: A continuous numeric value. (e.g. Temperature or humidity) - nominal: A numeric or string value with no ordering. (e.g. The name of a fruit) - ordinal: A nominal numeric value with ordering. (e.g. Rating scale, 1-5 stars) 

        :return: The type of this FeatureAttributes.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Set the type of this FeatureAttributes.

        The type of the feature.  - continuous: A continuous numeric value. (e.g. Temperature or humidity) - nominal: A numeric or string value with no ordering. (e.g. The name of a fruit) - ordinal: A nominal numeric value with ordering. (e.g. Rating scale, 1-5 stars) 

        :param type: The type of this FeatureAttributes.
        :type type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        allowed_values = ["continuous", "nominal", "ordinal"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def auto_derive_on_train(self):
        """Get the auto_derive_on_train of this FeatureAttributes.


        :return: The auto_derive_on_train of this FeatureAttributes.
        :rtype: FeatureAutoDeriveOnTrain
        """
        return self._auto_derive_on_train

    @auto_derive_on_train.setter
    def auto_derive_on_train(self, auto_derive_on_train):
        """Set the auto_derive_on_train of this FeatureAttributes.


        :param auto_derive_on_train: The auto_derive_on_train of this FeatureAttributes.
        :type auto_derive_on_train: FeatureAutoDeriveOnTrain
        """

        self._auto_derive_on_train = auto_derive_on_train

    @property
    def bounds(self):
        """Get the bounds of this FeatureAttributes.


        :return: The bounds of this FeatureAttributes.
        :rtype: FeatureBounds
        """
        return self._bounds

    @bounds.setter
    def bounds(self, bounds):
        """Set the bounds of this FeatureAttributes.


        :param bounds: The bounds of this FeatureAttributes.
        :type bounds: FeatureBounds
        """

        self._bounds = bounds

    @property
    def cycle_length(self):
        """Get the cycle_length of this FeatureAttributes.

        Cyclic features start at 0 and have a range of [0, cycle_length). The `cycle_length` is the maximum value (exclusive) of the cycle. Values exceeding the cycle length are normalized to the original cycle (e.g., cycles with length 360 for degrees will evaluate a 370 as 10 and 360 as 0). Negative values are not supported in cyclic features. Only applicable to continuous or ordinal features.  Examples: - degrees: values should be 0-359, cycle_length = 360 - days: values should be 0-6, cycle_length = 7 - hours: values should be 0-23, cycle_length = 24 

        :return: The cycle_length of this FeatureAttributes.
        :rtype: int
        """
        return self._cycle_length

    @cycle_length.setter
    def cycle_length(self, cycle_length):
        """Set the cycle_length of this FeatureAttributes.

        Cyclic features start at 0 and have a range of [0, cycle_length). The `cycle_length` is the maximum value (exclusive) of the cycle. Values exceeding the cycle length are normalized to the original cycle (e.g., cycles with length 360 for degrees will evaluate a 370 as 10 and 360 as 0). Negative values are not supported in cyclic features. Only applicable to continuous or ordinal features.  Examples: - degrees: values should be 0-359, cycle_length = 360 - days: values should be 0-6, cycle_length = 7 - hours: values should be 0-23, cycle_length = 24 

        :param cycle_length: The cycle_length of this FeatureAttributes.
        :type cycle_length: int
        """
        if (self.local_vars_configuration.client_side_validation and
                cycle_length is not None and cycle_length < 0):  # noqa: E501
            raise ValueError("Invalid value for `cycle_length`, must be a value greater than or equal to `0`")  # noqa: E501

        self._cycle_length = cycle_length

    @property
    def data_type(self):
        """Get the data_type of this FeatureAttributes.

        Specify the data type for features with a type of nominal or continuous. Default is `string` for nominals and `number` for continuous.  Valid values include:  - `string`, `number`, `json`, `amalgam`, `yaml`: Valid for both nominal and continuous.  - `string_mixable`: Valid only when type is continuous (predicted values may result in interpolated strings   containing a combination of characters from multiple original values).  - `boolean`: Valid only for nominals. 

        :return: The data_type of this FeatureAttributes.
        :rtype: str
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Set the data_type of this FeatureAttributes.

        Specify the data type for features with a type of nominal or continuous. Default is `string` for nominals and `number` for continuous.  Valid values include:  - `string`, `number`, `json`, `amalgam`, `yaml`: Valid for both nominal and continuous.  - `string_mixable`: Valid only when type is continuous (predicted values may result in interpolated strings   containing a combination of characters from multiple original values).  - `boolean`: Valid only for nominals. 

        :param data_type: The data_type of this FeatureAttributes.
        :type data_type: str
        """
        allowed_values = ["string", "number", "boolean", "string_mixable", "json", "yaml", "amalgam"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and data_type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `data_type` ({0}), must be one of {1}"  # noqa: E501
                .format(data_type, allowed_values)
            )

        self._data_type = data_type

    @property
    def date_time_format(self):
        """Get the date_time_format of this FeatureAttributes.

        If specified, feature values should match the date format specified by this string. Only applicable to continuous features. 

        :return: The date_time_format of this FeatureAttributes.
        :rtype: str
        """
        return self._date_time_format

    @date_time_format.setter
    def date_time_format(self, date_time_format):
        """Set the date_time_format of this FeatureAttributes.

        If specified, feature values should match the date format specified by this string. Only applicable to continuous features. 

        :param date_time_format: The date_time_format of this FeatureAttributes.
        :type date_time_format: str
        """

        self._date_time_format = date_time_format

    @property
    def decimal_places(self):
        """Get the decimal_places of this FeatureAttributes.

        Decimal places to round to, default is no rounding. If `significant_digits` is also specified, the number will be rounded to the specified number of significant digits first, then rounded to the number of decimal points as specified by this parameter. 

        :return: The decimal_places of this FeatureAttributes.
        :rtype: int
        """
        return self._decimal_places

    @decimal_places.setter
    def decimal_places(self, decimal_places):
        """Set the decimal_places of this FeatureAttributes.

        Decimal places to round to, default is no rounding. If `significant_digits` is also specified, the number will be rounded to the specified number of significant digits first, then rounded to the number of decimal points as specified by this parameter. 

        :param decimal_places: The decimal_places of this FeatureAttributes.
        :type decimal_places: int
        """

        self._decimal_places = decimal_places

    @property
    def dependent_features(self):
        """Get the dependent_features of this FeatureAttributes.

        A list of other feature names that this feature either depends on or features that depend on this feature. Should be used when there are multi-type value features that tightly depend on values based on other multi-type value features. 

        :return: The dependent_features of this FeatureAttributes.
        :rtype: list[str]
        """
        return self._dependent_features

    @dependent_features.setter
    def dependent_features(self, dependent_features):
        """Set the dependent_features of this FeatureAttributes.

        A list of other feature names that this feature either depends on or features that depend on this feature. Should be used when there are multi-type value features that tightly depend on values based on other multi-type value features. 

        :param dependent_features: The dependent_features of this FeatureAttributes.
        :type dependent_features: list[str]
        """

        self._dependent_features = dependent_features

    @property
    def derived_feature_code(self):
        """Get the derived_feature_code of this FeatureAttributes.

        Code defining how the value for this feature could be derived if this feature is specified as a `derived_context_feature` or a `derived_action_feature` during react flows. For `react_series`, the data referenced is the accumulated series data (as a list of rows), and for non-series reacts, the data is the one single row. Each row is comprised of all the combined context and action features. Referencing data in these rows uses 0-based indexing, where the current row index is 0, the previous row's is 1, etc. The specified code may do simple logic and numeric operations on feature values referenced via feature name and row offset.  Examples: - ``\"#x 1\"``: Use the value for feature 'x' from the previously processed row (offset of 1, one lag value). - ``\"(- #y 0 #x 1)\"``: Feature 'y' value from current (offset 0) row  minus feature 'x' value from previous (offset 1) row. 

        :return: The derived_feature_code of this FeatureAttributes.
        :rtype: str
        """
        return self._derived_feature_code

    @derived_feature_code.setter
    def derived_feature_code(self, derived_feature_code):
        """Set the derived_feature_code of this FeatureAttributes.

        Code defining how the value for this feature could be derived if this feature is specified as a `derived_context_feature` or a `derived_action_feature` during react flows. For `react_series`, the data referenced is the accumulated series data (as a list of rows), and for non-series reacts, the data is the one single row. Each row is comprised of all the combined context and action features. Referencing data in these rows uses 0-based indexing, where the current row index is 0, the previous row's is 1, etc. The specified code may do simple logic and numeric operations on feature values referenced via feature name and row offset.  Examples: - ``\"#x 1\"``: Use the value for feature 'x' from the previously processed row (offset of 1, one lag value). - ``\"(- #y 0 #x 1)\"``: Feature 'y' value from current (offset 0) row  minus feature 'x' value from previous (offset 1) row. 

        :param derived_feature_code: The derived_feature_code of this FeatureAttributes.
        :type derived_feature_code: str
        """

        self._derived_feature_code = derived_feature_code

    @property
    def id_feature(self):
        """Get the id_feature of this FeatureAttributes.

        Set to true for nominal features containing nominal IDs, specifying that his feature should be used to compute case weights for id based privacy. For time series, this feature will be used as the id for each time series generation. 

        :return: The id_feature of this FeatureAttributes.
        :rtype: bool
        """
        return self._id_feature

    @id_feature.setter
    def id_feature(self, id_feature):
        """Set the id_feature of this FeatureAttributes.

        Set to true for nominal features containing nominal IDs, specifying that his feature should be used to compute case weights for id based privacy. For time series, this feature will be used as the id for each time series generation. 

        :param id_feature: The id_feature of this FeatureAttributes.
        :type id_feature: bool
        """

        self._id_feature = id_feature

    @property
    def locale(self):
        """Get the locale of this FeatureAttributes.

        The date time format locale. If unspecified, uses platform default locale. 

        :return: The locale of this FeatureAttributes.
        :rtype: str
        """
        return self._locale

    @locale.setter
    def locale(self, locale):
        """Set the locale of this FeatureAttributes.

        The date time format locale. If unspecified, uses platform default locale. 

        :param locale: The locale of this FeatureAttributes.
        :type locale: str
        """

        self._locale = locale

    @property
    def non_sensitive(self):
        """Get the non_sensitive of this FeatureAttributes.

        Flag a categorical nominal feature as non-sensitive. It is recommended that all nominal features be represented with either an `int-id` subtype or another available nominal subtype using the `subtype` attribute. However, if the nominal feature is non-sensitive, setting this parameter to true will bypass the `subtype` requirement. Only applicable to nominal features. 

        :return: The non_sensitive of this FeatureAttributes.
        :rtype: bool
        """
        return self._non_sensitive

    @non_sensitive.setter
    def non_sensitive(self, non_sensitive):
        """Set the non_sensitive of this FeatureAttributes.

        Flag a categorical nominal feature as non-sensitive. It is recommended that all nominal features be represented with either an `int-id` subtype or another available nominal subtype using the `subtype` attribute. However, if the nominal feature is non-sensitive, setting this parameter to true will bypass the `subtype` requirement. Only applicable to nominal features. 

        :param non_sensitive: The non_sensitive of this FeatureAttributes.
        :type non_sensitive: bool
        """

        self._non_sensitive = non_sensitive

    @property
    def null_is_dependent(self):
        """Get the null_is_dependent of this FeatureAttributes.

        Modify how dependent features with nulls are treated during a react, specifically when they use null as a context value. Only applicable to dependent features. When false (default), the feature will be treated as a non-dependent context feature. When true for nominal types, treats null as an individual dependent class value, only cases that also have nulls as this feature's value will be considered. When true for continuous types, only the cases with the same dependent feature values as the cases that also have nulls as this feature's value will be considered. 

        :return: The null_is_dependent of this FeatureAttributes.
        :rtype: bool
        """
        return self._null_is_dependent

    @null_is_dependent.setter
    def null_is_dependent(self, null_is_dependent):
        """Set the null_is_dependent of this FeatureAttributes.

        Modify how dependent features with nulls are treated during a react, specifically when they use null as a context value. Only applicable to dependent features. When false (default), the feature will be treated as a non-dependent context feature. When true for nominal types, treats null as an individual dependent class value, only cases that also have nulls as this feature's value will be considered. When true for continuous types, only the cases with the same dependent feature values as the cases that also have nulls as this feature's value will be considered. 

        :param null_is_dependent: The null_is_dependent of this FeatureAttributes.
        :type null_is_dependent: bool
        """

        self._null_is_dependent = null_is_dependent

    @property
    def observational_error(self):
        """Get the observational_error of this FeatureAttributes.

        Specify the observed error value for this feature. Use when the error value is already known. Defaults to 0.

        :return: The observational_error of this FeatureAttributes.
        :rtype: float
        """
        return self._observational_error

    @observational_error.setter
    def observational_error(self, observational_error):
        """Set the observational_error of this FeatureAttributes.

        Specify the observed error value for this feature. Use when the error value is already known. Defaults to 0.

        :param observational_error: The observational_error of this FeatureAttributes.
        :type observational_error: float
        """

        self._observational_error = observational_error

    @property
    def original_type(self):
        """Get the original_type of this FeatureAttributes.


        :return: The original_type of this FeatureAttributes.
        :rtype: FeatureOriginalType
        """
        return self._original_type

    @original_type.setter
    def original_type(self, original_type):
        """Set the original_type of this FeatureAttributes.


        :param original_type: The original_type of this FeatureAttributes.
        :type original_type: FeatureOriginalType
        """

        self._original_type = original_type

    @property
    def original_format(self):
        """Get the original_format of this FeatureAttributes.

        Original data formats used by clients. Automatically populated by clients to store client language specific context about features. 

        :return: The original_format of this FeatureAttributes.
        :rtype: dict[str, object]
        """
        return self._original_format

    @original_format.setter
    def original_format(self, original_format):
        """Set the original_format of this FeatureAttributes.

        Original data formats used by clients. Automatically populated by clients to store client language specific context about features. 

        :param original_format: The original_format of this FeatureAttributes.
        :type original_format: dict[str, object]
        """

        self._original_format = original_format

    @property
    def post_process(self):
        """Get the post_process of this FeatureAttributes.

        Custom Amalgam code that is called on resulting values of this feature during react operations.

        :return: The post_process of this FeatureAttributes.
        :rtype: str
        """
        return self._post_process

    @post_process.setter
    def post_process(self, post_process):
        """Set the post_process of this FeatureAttributes.

        Custom Amalgam code that is called on resulting values of this feature during react operations.

        :param post_process: The post_process of this FeatureAttributes.
        :type post_process: str
        """

        self._post_process = post_process

    @property
    def significant_digits(self):
        """Get the significant_digits of this FeatureAttributes.

        Round to the specified significant digits, default is no rounding. 

        :return: The significant_digits of this FeatureAttributes.
        :rtype: int
        """
        return self._significant_digits

    @significant_digits.setter
    def significant_digits(self, significant_digits):
        """Set the significant_digits of this FeatureAttributes.

        Round to the specified significant digits, default is no rounding. 

        :param significant_digits: The significant_digits of this FeatureAttributes.
        :type significant_digits: int
        """

        self._significant_digits = significant_digits

    @property
    def subtype(self):
        """Get the subtype of this FeatureAttributes.

        The type used in novel nominal substitution.

        :return: The subtype of this FeatureAttributes.
        :rtype: str
        """
        return self._subtype

    @subtype.setter
    def subtype(self, subtype):
        """Set the subtype of this FeatureAttributes.

        The type used in novel nominal substitution.

        :param subtype: The subtype of this FeatureAttributes.
        :type subtype: str
        """

        self._subtype = subtype

    @property
    def time_delta_format(self):
        """Get the time_delta_format of this FeatureAttributes.

        Format of the delta for date time features, default is 'seconds'. Valid values are: milliseconds, seconds, minutes, hours, days, weeks, years. 

        :return: The time_delta_format of this FeatureAttributes.
        :rtype: str
        """
        return self._time_delta_format

    @time_delta_format.setter
    def time_delta_format(self, time_delta_format):
        """Set the time_delta_format of this FeatureAttributes.

        Format of the delta for date time features, default is 'seconds'. Valid values are: milliseconds, seconds, minutes, hours, days, weeks, years. 

        :param time_delta_format: The time_delta_format of this FeatureAttributes.
        :type time_delta_format: str
        """
        allowed_values = ["milliseconds", "seconds", "minutes", "hours", "days", "weeks", "years"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and time_delta_format not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `time_delta_format` ({0}), must be one of {1}"  # noqa: E501
                .format(time_delta_format, allowed_values)
            )

        self._time_delta_format = time_delta_format

    @property
    def time_series(self):
        """Get the time_series of this FeatureAttributes.


        :return: The time_series of this FeatureAttributes.
        :rtype: FeatureTimeSeries
        """
        return self._time_series

    @time_series.setter
    def time_series(self, time_series):
        """Set the time_series of this FeatureAttributes.


        :param time_series: The time_series of this FeatureAttributes.
        :type time_series: FeatureTimeSeries
        """

        self._time_series = time_series

    @property
    def unique(self):
        """Get the unique of this FeatureAttributes.

        Flag feature as only having unique values. Only applicable to nominals features.

        :return: The unique of this FeatureAttributes.
        :rtype: bool
        """
        return self._unique

    @unique.setter
    def unique(self, unique):
        """Set the unique of this FeatureAttributes.

        Flag feature as only having unique values. Only applicable to nominals features.

        :param unique: The unique of this FeatureAttributes.
        :type unique: bool
        """

        self._unique = unique

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
        if not isinstance(other, FeatureAttributes):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureAttributes):
            return True

        return self.to_dict() != other.to_dict()
