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


class BaseReactRequest(object):
    """
    Auto-generated OpenAPI type.

    Base parameters that apply to react and react series operations.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'contexts': 'list[list[object]]',
        'actions': 'list[list[object]]',
        'input_is_substituted': 'bool',
        'substitute_output': 'bool',
        'details': 'ReactDetails',
        'context_features': 'list[str]',
        'action_features': 'list[str]',
        'derived_context_features': 'list[str]',
        'derived_action_features': 'list[str]',
        'desired_conviction': 'float',
        'exclude_novel_nominals_from_uniqueness_check': 'bool',
        'use_regional_model_residuals': 'bool',
        'feature_bounds_map': 'dict[str, FeatureBounds]',
        'generate_new_cases': 'str',
        'preserve_feature_values': 'list[str]',
        'new_case_threshold': 'str',
        'case_indices': 'list[list[object]]',
        'leave_case_out': 'bool',
        'ordered_by_specified_features': 'bool',
        'use_case_weights': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'contexts': 'contexts',
        'actions': 'actions',
        'input_is_substituted': 'input_is_substituted',
        'substitute_output': 'substitute_output',
        'details': 'details',
        'context_features': 'context_features',
        'action_features': 'action_features',
        'derived_context_features': 'derived_context_features',
        'derived_action_features': 'derived_action_features',
        'desired_conviction': 'desired_conviction',
        'exclude_novel_nominals_from_uniqueness_check': 'exclude_novel_nominals_from_uniqueness_check',
        'use_regional_model_residuals': 'use_regional_model_residuals',
        'feature_bounds_map': 'feature_bounds_map',
        'generate_new_cases': 'generate_new_cases',
        'preserve_feature_values': 'preserve_feature_values',
        'new_case_threshold': 'new_case_threshold',
        'case_indices': 'case_indices',
        'leave_case_out': 'leave_case_out',
        'ordered_by_specified_features': 'ordered_by_specified_features',
        'use_case_weights': 'use_case_weights',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, contexts=None, actions=None, input_is_substituted=None, substitute_output=None, details=None, context_features=None, action_features=None, derived_context_features=None, derived_action_features=None, desired_conviction=None, exclude_novel_nominals_from_uniqueness_check=None, use_regional_model_residuals=None, feature_bounds_map=None, generate_new_cases=None, preserve_feature_values=None, new_case_threshold=None, case_indices=None, leave_case_out=None, ordered_by_specified_features=None, use_case_weights=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """BaseReactRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._contexts = None
        self._actions = None
        self._input_is_substituted = None
        self._substitute_output = None
        self._details = None
        self._context_features = None
        self._action_features = None
        self._derived_context_features = None
        self._derived_action_features = None
        self._desired_conviction = None
        self._exclude_novel_nominals_from_uniqueness_check = None
        self._use_regional_model_residuals = None
        self._feature_bounds_map = None
        self._generate_new_cases = None
        self._preserve_feature_values = None
        self._new_case_threshold = None
        self._case_indices = None
        self._leave_case_out = None
        self._ordered_by_specified_features = None
        self._use_case_weights = None
        self._weight_feature = None

        if contexts is not None:
            self.contexts = contexts
        if actions is not None:
            self.actions = actions
        if input_is_substituted is not None:
            self.input_is_substituted = input_is_substituted
        if substitute_output is not None:
            self.substitute_output = substitute_output
        if details is not None:
            self.details = details
        if context_features is not None:
            self.context_features = context_features
        if action_features is not None:
            self.action_features = action_features
        if derived_context_features is not None:
            self.derived_context_features = derived_context_features
        if derived_action_features is not None:
            self.derived_action_features = derived_action_features
        if desired_conviction is not None:
            self.desired_conviction = desired_conviction
        if exclude_novel_nominals_from_uniqueness_check is not None:
            self.exclude_novel_nominals_from_uniqueness_check = exclude_novel_nominals_from_uniqueness_check
        if use_regional_model_residuals is not None:
            self.use_regional_model_residuals = use_regional_model_residuals
        if feature_bounds_map is not None:
            self.feature_bounds_map = feature_bounds_map
        if generate_new_cases is not None:
            self.generate_new_cases = generate_new_cases
        if preserve_feature_values is not None:
            self.preserve_feature_values = preserve_feature_values
        if new_case_threshold is not None:
            self.new_case_threshold = new_case_threshold
        if case_indices is not None:
            self.case_indices = case_indices
        if leave_case_out is not None:
            self.leave_case_out = leave_case_out
        if ordered_by_specified_features is not None:
            self.ordered_by_specified_features = ordered_by_specified_features
        if use_case_weights is not None:
            self.use_case_weights = use_case_weights
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def contexts(self):
        """Get the contexts of this BaseReactRequest.

        A 2D array of context values.

        :return: The contexts of this BaseReactRequest.
        :rtype: list[list[object]]
        """
        return self._contexts

    @contexts.setter
    def contexts(self, contexts):
        """Set the contexts of this BaseReactRequest.

        A 2D array of context values.

        :param contexts: The contexts of this BaseReactRequest.
        :type contexts: list[list[object]]
        """

        self._contexts = contexts

    @property
    def actions(self):
        """Get the actions of this BaseReactRequest.

        One or more values for action features, if specified will only return the specified explanation details for the given actions. 

        :return: The actions of this BaseReactRequest.
        :rtype: list[list[object]]
        """
        return self._actions

    @actions.setter
    def actions(self, actions):
        """Set the actions of this BaseReactRequest.

        One or more values for action features, if specified will only return the specified explanation details for the given actions. 

        :param actions: The actions of this BaseReactRequest.
        :type actions: list[list[object]]
        """

        self._actions = actions

    @property
    def input_is_substituted(self):
        """Get the input_is_substituted of this BaseReactRequest.

        If set to true, assumes provided categorical (nominal or ordinal) feature values have already been substituted.

        :return: The input_is_substituted of this BaseReactRequest.
        :rtype: bool
        """
        return self._input_is_substituted

    @input_is_substituted.setter
    def input_is_substituted(self, input_is_substituted):
        """Set the input_is_substituted of this BaseReactRequest.

        If set to true, assumes provided categorical (nominal or ordinal) feature values have already been substituted.

        :param input_is_substituted: The input_is_substituted of this BaseReactRequest.
        :type input_is_substituted: bool
        """

        self._input_is_substituted = input_is_substituted

    @property
    def substitute_output(self):
        """Get the substitute_output of this BaseReactRequest.

        Only applicable if a substitution value map has been set. If set to false, will not substitute categorical feature values.

        :return: The substitute_output of this BaseReactRequest.
        :rtype: bool
        """
        return self._substitute_output

    @substitute_output.setter
    def substitute_output(self, substitute_output):
        """Set the substitute_output of this BaseReactRequest.

        Only applicable if a substitution value map has been set. If set to false, will not substitute categorical feature values.

        :param substitute_output: The substitute_output of this BaseReactRequest.
        :type substitute_output: bool
        """

        self._substitute_output = substitute_output

    @property
    def details(self):
        """Get the details of this BaseReactRequest.


        :return: The details of this BaseReactRequest.
        :rtype: ReactDetails
        """
        return self._details

    @details.setter
    def details(self, details):
        """Set the details of this BaseReactRequest.


        :param details: The details of this BaseReactRequest.
        :type details: ReactDetails
        """

        self._details = details

    @property
    def context_features(self):
        """Get the context_features of this BaseReactRequest.

        The context features to use for this reaction.

        :return: The context_features of this BaseReactRequest.
        :rtype: list[str]
        """
        return self._context_features

    @context_features.setter
    def context_features(self, context_features):
        """Set the context_features of this BaseReactRequest.

        The context features to use for this reaction.

        :param context_features: The context_features of this BaseReactRequest.
        :type context_features: list[str]
        """

        self._context_features = context_features

    @property
    def action_features(self):
        """Get the action_features of this BaseReactRequest.

        The action features to use for this reaction.

        :return: The action_features of this BaseReactRequest.
        :rtype: list[str]
        """
        return self._action_features

    @action_features.setter
    def action_features(self, action_features):
        """Set the action_features of this BaseReactRequest.

        The action features to use for this reaction.

        :param action_features: The action_features of this BaseReactRequest.
        :type action_features: list[str]
        """

        self._action_features = action_features

    @property
    def derived_context_features(self):
        """Get the derived_context_features of this BaseReactRequest.

        A list of feature names whose values should be computed from the provided context in the specified order.  Note: Relies on the features' \"derived_feature_code\" attribute to compute the values. If \"derived_feature_code\" attribute is undefined or references non-0 feature indices, the derived value will be null. 

        :return: The derived_context_features of this BaseReactRequest.
        :rtype: list[str]
        """
        return self._derived_context_features

    @derived_context_features.setter
    def derived_context_features(self, derived_context_features):
        """Set the derived_context_features of this BaseReactRequest.

        A list of feature names whose values should be computed from the provided context in the specified order.  Note: Relies on the features' \"derived_feature_code\" attribute to compute the values. If \"derived_feature_code\" attribute is undefined or references non-0 feature indices, the derived value will be null. 

        :param derived_context_features: The derived_context_features of this BaseReactRequest.
        :type derived_context_features: list[str]
        """

        self._derived_context_features = derived_context_features

    @property
    def derived_action_features(self):
        """Get the derived_action_features of this BaseReactRequest.

        A list of feature names whose values should be computed after reaction from the resulting case prior to output, in the specified order.  Note: Relies on the features' \"derived_feature_code\" attribute to compute the values. If \"derived_feature_code\" attribute is undefined or references non-0 feature indices, the derived value will be null. 

        :return: The derived_action_features of this BaseReactRequest.
        :rtype: list[str]
        """
        return self._derived_action_features

    @derived_action_features.setter
    def derived_action_features(self, derived_action_features):
        """Set the derived_action_features of this BaseReactRequest.

        A list of feature names whose values should be computed after reaction from the resulting case prior to output, in the specified order.  Note: Relies on the features' \"derived_feature_code\" attribute to compute the values. If \"derived_feature_code\" attribute is undefined or references non-0 feature indices, the derived value will be null. 

        :param derived_action_features: The derived_action_features of this BaseReactRequest.
        :type derived_action_features: list[str]
        """

        self._derived_action_features = derived_action_features

    @property
    def desired_conviction(self):
        """Get the desired_conviction of this BaseReactRequest.

        If specified will execute a generative react. If not specified will executed a discriminative react. Conviction is the ratio of expected surprisal to generated surprisal for each feature generated, values are in the range of (0,infinity]. 

        :return: The desired_conviction of this BaseReactRequest.
        :rtype: float
        """
        return self._desired_conviction

    @desired_conviction.setter
    def desired_conviction(self, desired_conviction):
        """Set the desired_conviction of this BaseReactRequest.

        If specified will execute a generative react. If not specified will executed a discriminative react. Conviction is the ratio of expected surprisal to generated surprisal for each feature generated, values are in the range of (0,infinity]. 

        :param desired_conviction: The desired_conviction of this BaseReactRequest.
        :type desired_conviction: float
        """

        self._desired_conviction = desired_conviction

    @property
    def exclude_novel_nominals_from_uniqueness_check(self):
        """Get the exclude_novel_nominals_from_uniqueness_check of this BaseReactRequest.

        For generative reacts only. If true, excludes features which have a subtype in their feature attributes from the uniqueness check performed when generate_new_cases is \"always\". 

        :return: The exclude_novel_nominals_from_uniqueness_check of this BaseReactRequest.
        :rtype: bool
        """
        return self._exclude_novel_nominals_from_uniqueness_check

    @exclude_novel_nominals_from_uniqueness_check.setter
    def exclude_novel_nominals_from_uniqueness_check(self, exclude_novel_nominals_from_uniqueness_check):
        """Set the exclude_novel_nominals_from_uniqueness_check of this BaseReactRequest.

        For generative reacts only. If true, excludes features which have a subtype in their feature attributes from the uniqueness check performed when generate_new_cases is \"always\". 

        :param exclude_novel_nominals_from_uniqueness_check: The exclude_novel_nominals_from_uniqueness_check of this BaseReactRequest.
        :type exclude_novel_nominals_from_uniqueness_check: bool
        """

        self._exclude_novel_nominals_from_uniqueness_check = exclude_novel_nominals_from_uniqueness_check

    @property
    def use_regional_model_residuals(self):
        """Get the use_regional_model_residuals of this BaseReactRequest.

        For generative reacts only. If false uses model feature residuals, if true recalculates regional model residuals.

        :return: The use_regional_model_residuals of this BaseReactRequest.
        :rtype: bool
        """
        return self._use_regional_model_residuals

    @use_regional_model_residuals.setter
    def use_regional_model_residuals(self, use_regional_model_residuals):
        """Set the use_regional_model_residuals of this BaseReactRequest.

        For generative reacts only. If false uses model feature residuals, if true recalculates regional model residuals.

        :param use_regional_model_residuals: The use_regional_model_residuals of this BaseReactRequest.
        :type use_regional_model_residuals: bool
        """

        self._use_regional_model_residuals = use_regional_model_residuals

    @property
    def feature_bounds_map(self):
        """Get the feature_bounds_map of this BaseReactRequest.

        For generative reacts only.

        :return: The feature_bounds_map of this BaseReactRequest.
        :rtype: dict[str, FeatureBounds]
        """
        return self._feature_bounds_map

    @feature_bounds_map.setter
    def feature_bounds_map(self, feature_bounds_map):
        """Set the feature_bounds_map of this BaseReactRequest.

        For generative reacts only.

        :param feature_bounds_map: The feature_bounds_map of this BaseReactRequest.
        :type feature_bounds_map: dict[str, FeatureBounds]
        """

        self._feature_bounds_map = feature_bounds_map

    @property
    def generate_new_cases(self):
        """Get the generate_new_cases of this BaseReactRequest.

        Control whether generated cases can be those that already exist in the model. This parameter takes in a string that could be one of the following:   a. \"attempt\": attempts to generate new cases and if its not possible to generate a new case, it might generate cases in \"no\" mode (see point c.)   b. \"always\": always generates new cases and if its not possible to generate a new case, it returns nulls.   c. \"no\": generates data based on the `desired_conviction` specified and the generated data is not guaranteed to be a new case (that is, a case not found in original dataset.) 

        :return: The generate_new_cases of this BaseReactRequest.
        :rtype: str
        """
        return self._generate_new_cases

    @generate_new_cases.setter
    def generate_new_cases(self, generate_new_cases):
        """Set the generate_new_cases of this BaseReactRequest.

        Control whether generated cases can be those that already exist in the model. This parameter takes in a string that could be one of the following:   a. \"attempt\": attempts to generate new cases and if its not possible to generate a new case, it might generate cases in \"no\" mode (see point c.)   b. \"always\": always generates new cases and if its not possible to generate a new case, it returns nulls.   c. \"no\": generates data based on the `desired_conviction` specified and the generated data is not guaranteed to be a new case (that is, a case not found in original dataset.) 

        :param generate_new_cases: The generate_new_cases of this BaseReactRequest.
        :type generate_new_cases: str
        """
        allowed_values = ["attempt", "always", "no"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and generate_new_cases not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `generate_new_cases` ({0}), must be one of {1}"  # noqa: E501
                .format(generate_new_cases, allowed_values)
            )

        self._generate_new_cases = generate_new_cases

    @property
    def preserve_feature_values(self):
        """Get the preserve_feature_values of this BaseReactRequest.

        List of features that will preserve their values from the case specified by `case_indices`, appending and overwriting the specified contexts as necessary. For generative reacts, if `case_indices` isn't specified will preserve feature values of a random case. 

        :return: The preserve_feature_values of this BaseReactRequest.
        :rtype: list[str]
        """
        return self._preserve_feature_values

    @preserve_feature_values.setter
    def preserve_feature_values(self, preserve_feature_values):
        """Set the preserve_feature_values of this BaseReactRequest.

        List of features that will preserve their values from the case specified by `case_indices`, appending and overwriting the specified contexts as necessary. For generative reacts, if `case_indices` isn't specified will preserve feature values of a random case. 

        :param preserve_feature_values: The preserve_feature_values of this BaseReactRequest.
        :type preserve_feature_values: list[str]
        """

        self._preserve_feature_values = preserve_feature_values

    @property
    def new_case_threshold(self):
        """Get the new_case_threshold of this BaseReactRequest.

        The privacy distance criteria for generated new cases. 

        :return: The new_case_threshold of this BaseReactRequest.
        :rtype: str
        """
        return self._new_case_threshold

    @new_case_threshold.setter
    def new_case_threshold(self, new_case_threshold):
        """Set the new_case_threshold of this BaseReactRequest.

        The privacy distance criteria for generated new cases. 

        :param new_case_threshold: The new_case_threshold of this BaseReactRequest.
        :type new_case_threshold: str
        """
        allowed_values = ["min", "max", "most_similar"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and new_case_threshold not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `new_case_threshold` ({0}), must be one of {1}"  # noqa: E501
                .format(new_case_threshold, allowed_values)
            )

        self._new_case_threshold = new_case_threshold

    @property
    def case_indices(self):
        """Get the case_indices of this BaseReactRequest.

        List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. If this case does not exist, discriminative react outputs null, generative react ignores it. 

        :return: The case_indices of this BaseReactRequest.
        :rtype: list[list[object]]
        """
        return self._case_indices

    @case_indices.setter
    def case_indices(self, case_indices):
        """Set the case_indices of this BaseReactRequest.

        List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. If this case does not exist, discriminative react outputs null, generative react ignores it. 

        :param case_indices: The case_indices of this BaseReactRequest.
        :type case_indices: list[list[object]]
        """
        if (self.local_vars_configuration.client_side_validation and
                case_indices is not None and len(case_indices) < 1):
            raise ValueError("Invalid value for `case_indices`, number of items must be greater than or equal to `1`")  # noqa: E501

        self._case_indices = case_indices

    @property
    def leave_case_out(self):
        """Get the leave_case_out of this BaseReactRequest.

        If set to True and specified along with case_indices, each individual react will respectively ignore the corresponding case specified by case_indices by leaving it out. 

        :return: The leave_case_out of this BaseReactRequest.
        :rtype: bool
        """
        return self._leave_case_out

    @leave_case_out.setter
    def leave_case_out(self, leave_case_out):
        """Set the leave_case_out of this BaseReactRequest.

        If set to True and specified along with case_indices, each individual react will respectively ignore the corresponding case specified by case_indices by leaving it out. 

        :param leave_case_out: The leave_case_out of this BaseReactRequest.
        :type leave_case_out: bool
        """

        self._leave_case_out = leave_case_out

    @property
    def ordered_by_specified_features(self):
        """Get the ordered_by_specified_features of this BaseReactRequest.

        For generative reacts only. Features will be generated in the same order as provided in the 'action_features' parameter.

        :return: The ordered_by_specified_features of this BaseReactRequest.
        :rtype: bool
        """
        return self._ordered_by_specified_features

    @ordered_by_specified_features.setter
    def ordered_by_specified_features(self, ordered_by_specified_features):
        """Set the ordered_by_specified_features of this BaseReactRequest.

        For generative reacts only. Features will be generated in the same order as provided in the 'action_features' parameter.

        :param ordered_by_specified_features: The ordered_by_specified_features of this BaseReactRequest.
        :type ordered_by_specified_features: bool
        """

        self._ordered_by_specified_features = ordered_by_specified_features

    @property
    def use_case_weights(self):
        """Get the use_case_weights of this BaseReactRequest.

        If set to True will scale influence weights by each case's weight_feature weight.

        :return: The use_case_weights of this BaseReactRequest.
        :rtype: bool
        """
        return self._use_case_weights

    @use_case_weights.setter
    def use_case_weights(self, use_case_weights):
        """Set the use_case_weights of this BaseReactRequest.

        If set to True will scale influence weights by each case's weight_feature weight.

        :param use_case_weights: The use_case_weights of this BaseReactRequest.
        :type use_case_weights: bool
        """

        self._use_case_weights = use_case_weights

    @property
    def weight_feature(self):
        """Get the weight_feature of this BaseReactRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :return: The weight_feature of this BaseReactRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this BaseReactRequest.

        The name of the feature whose values to use as case weights. When left unspecified, uses the internally managed case weight. 

        :param weight_feature: The weight_feature of this BaseReactRequest.
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
        if not isinstance(other, BaseReactRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BaseReactRequest):
            return True

        return self.to_dict() != other.to_dict()
