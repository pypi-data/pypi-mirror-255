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


class TrainRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of a train request. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'cases': 'list[list[object]]',
        'features': 'list[str]',
        'derived_features': 'list[str]',
        'input_is_substituted': 'bool',
        'accumulate_weight_feature': 'str',
        'series': 'str',
        'train_weights_only': 'bool',
        'run_async': 'bool'
    }

    attribute_map = {
        'cases': 'cases',
        'features': 'features',
        'derived_features': 'derived_features',
        'input_is_substituted': 'input_is_substituted',
        'accumulate_weight_feature': 'accumulate_weight_feature',
        'series': 'series',
        'train_weights_only': 'train_weights_only',
        'run_async': 'run_async'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, cases=None, features=None, derived_features=None, input_is_substituted=None, accumulate_weight_feature=None, series=None, train_weights_only=None, run_async=None, local_vars_configuration=None):  # noqa: E501
        """TrainRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._cases = None
        self._features = None
        self._derived_features = None
        self._input_is_substituted = None
        self._accumulate_weight_feature = None
        self._series = None
        self._train_weights_only = None
        self._run_async = None

        self.cases = cases
        if features is not None:
            self.features = features
        if derived_features is not None:
            self.derived_features = derived_features
        if input_is_substituted is not None:
            self.input_is_substituted = input_is_substituted
        if accumulate_weight_feature is not None:
            self.accumulate_weight_feature = accumulate_weight_feature
        if series is not None:
            self.series = series
        if train_weights_only is not None:
            self.train_weights_only = train_weights_only
        if run_async is not None:
            self.run_async = run_async

    @property
    def cases(self):
        """Get the cases of this TrainRequest.

        One or more cases to train into the model.

        :return: The cases of this TrainRequest.
        :rtype: list[list[object]]
        """
        return self._cases

    @cases.setter
    def cases(self, cases):
        """Set the cases of this TrainRequest.

        One or more cases to train into the model.

        :param cases: The cases of this TrainRequest.
        :type cases: list[list[object]]
        """
        if self.local_vars_configuration.client_side_validation and cases is None:  # noqa: E501
            raise ValueError("Invalid value for `cases`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                cases is not None and len(cases) < 1):
            raise ValueError("Invalid value for `cases`, number of items must be greater than or equal to `1`")  # noqa: E501

        self._cases = cases

    @property
    def features(self):
        """Get the features of this TrainRequest.

        List of feature names. Note, features may not begin with one of the following four characters . ^ ! #

        :return: The features of this TrainRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this TrainRequest.

        List of feature names. Note, features may not begin with one of the following four characters . ^ ! #

        :param features: The features of this TrainRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def derived_features(self):
        """Get the derived_features of this TrainRequest.

        List of feature names for which values should be derived in the specified order. If this list is not provided, features with the \"auto_derive_on_train\" feature attribute set to True will be auto-derived. If provided an empty list, no features are derived. Any derived_features that are already in the \"features\" list will not be derived since their values are being explicitly provided. 

        :return: The derived_features of this TrainRequest.
        :rtype: list[str]
        """
        return self._derived_features

    @derived_features.setter
    def derived_features(self, derived_features):
        """Set the derived_features of this TrainRequest.

        List of feature names for which values should be derived in the specified order. If this list is not provided, features with the \"auto_derive_on_train\" feature attribute set to True will be auto-derived. If provided an empty list, no features are derived. Any derived_features that are already in the \"features\" list will not be derived since their values are being explicitly provided. 

        :param derived_features: The derived_features of this TrainRequest.
        :type derived_features: list[str]
        """

        self._derived_features = derived_features

    @property
    def input_is_substituted(self):
        """Get the input_is_substituted of this TrainRequest.

        If set to true, assumes provided categorical (nominal or ordinal) feature values have already been substituted.

        :return: The input_is_substituted of this TrainRequest.
        :rtype: bool
        """
        return self._input_is_substituted

    @input_is_substituted.setter
    def input_is_substituted(self, input_is_substituted):
        """Set the input_is_substituted of this TrainRequest.

        If set to true, assumes provided categorical (nominal or ordinal) feature values have already been substituted.

        :param input_is_substituted: The input_is_substituted of this TrainRequest.
        :type input_is_substituted: bool
        """

        self._input_is_substituted = input_is_substituted

    @property
    def accumulate_weight_feature(self):
        """Get the accumulate_weight_feature of this TrainRequest.

        The name of a feature into which to accumulate neighbors' influences as weight for ablated cases. If unspecified, will not accumulate weights. 

        :return: The accumulate_weight_feature of this TrainRequest.
        :rtype: str
        """
        return self._accumulate_weight_feature

    @accumulate_weight_feature.setter
    def accumulate_weight_feature(self, accumulate_weight_feature):
        """Set the accumulate_weight_feature of this TrainRequest.

        The name of a feature into which to accumulate neighbors' influences as weight for ablated cases. If unspecified, will not accumulate weights. 

        :param accumulate_weight_feature: The accumulate_weight_feature of this TrainRequest.
        :type accumulate_weight_feature: str
        """

        self._accumulate_weight_feature = accumulate_weight_feature

    @property
    def series(self):
        """Get the series of this TrainRequest.

        The name of the series to pull features and case values from internal series storage. If specified, trains on all cases that are stored in the internal series store for the specified series. The trained feature set is the combined features from storage and the passed in features. If cases is of length one, the value(s) of this case are appended to all cases in the series. If cases is the same length as the series, the value of each case in cases is applied in order to each of the cases in the series. 

        :return: The series of this TrainRequest.
        :rtype: str
        """
        return self._series

    @series.setter
    def series(self, series):
        """Set the series of this TrainRequest.

        The name of the series to pull features and case values from internal series storage. If specified, trains on all cases that are stored in the internal series store for the specified series. The trained feature set is the combined features from storage and the passed in features. If cases is of length one, the value(s) of this case are appended to all cases in the series. If cases is the same length as the series, the value of each case in cases is applied in order to each of the cases in the series. 

        :param series: The series of this TrainRequest.
        :type series: str
        """

        self._series = series

    @property
    def train_weights_only(self):
        """Get the train_weights_only of this TrainRequest.

        When true, and accumulate_weight_feature is provided, will accumulate all of the cases' neighbor weights instead of training the cases into the model. 

        :return: The train_weights_only of this TrainRequest.
        :rtype: bool
        """
        return self._train_weights_only

    @train_weights_only.setter
    def train_weights_only(self, train_weights_only):
        """Set the train_weights_only of this TrainRequest.

        When true, and accumulate_weight_feature is provided, will accumulate all of the cases' neighbor weights instead of training the cases into the model. 

        :param train_weights_only: The train_weights_only of this TrainRequest.
        :type train_weights_only: bool
        """

        self._train_weights_only = train_weights_only

    @property
    def run_async(self):
        """Get the run_async of this TrainRequest.

        Process the request using the asynchronous Request-Reply flow. Otherwise processes request normally. 

        :return: The run_async of this TrainRequest.
        :rtype: bool
        """
        return self._run_async

    @run_async.setter
    def run_async(self, run_async):
        """Set the run_async of this TrainRequest.

        Process the request using the asynchronous Request-Reply flow. Otherwise processes request normally. 

        :param run_async: The run_async of this TrainRequest.
        :type run_async: bool
        """

        self._run_async = run_async

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
        if not isinstance(other, TrainRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TrainRequest):
            return True

        return self.to_dict() != other.to_dict()
