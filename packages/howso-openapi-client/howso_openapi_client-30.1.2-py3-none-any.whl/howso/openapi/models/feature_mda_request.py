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


class FeatureMdaRequest(object):
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
        'action_feature': 'str',
        'permutation': 'bool',
        'robust': 'bool',
        'weight_feature': 'str'
    }

    attribute_map = {
        'action_feature': 'action_feature',
        'permutation': 'permutation',
        'robust': 'robust',
        'weight_feature': 'weight_feature'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, action_feature=None, permutation=None, robust=None, weight_feature=None, local_vars_configuration=None):  # noqa: E501
        """FeatureMdaRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_feature = None
        self._permutation = None
        self._robust = None
        self._weight_feature = None

        self.action_feature = action_feature
        if permutation is not None:
            self.permutation = permutation
        if robust is not None:
            self.robust = robust
        if weight_feature is not None:
            self.weight_feature = weight_feature

    @property
    def action_feature(self):
        """Get the action_feature of this FeatureMdaRequest.

        Will attempt to return MDA that was computed for this specified action feature. 

        :return: The action_feature of this FeatureMdaRequest.
        :rtype: str
        """
        return self._action_feature

    @action_feature.setter
    def action_feature(self, action_feature):
        """Set the action_feature of this FeatureMdaRequest.

        Will attempt to return MDA that was computed for this specified action feature. 

        :param action_feature: The action_feature of this FeatureMdaRequest.
        :type action_feature: str
        """
        if self.local_vars_configuration.client_side_validation and action_feature is None:  # noqa: E501
            raise ValueError("Invalid value for `action_feature`, must not be `None`")  # noqa: E501

        self._action_feature = action_feature

    @property
    def permutation(self):
        """Get the permutation of this FeatureMdaRequest.

        When False, will attempt to return MDA that was computed by dropping each feature. When True, will attempt to return MDA that was computed with permutations by scrambling each feature. 

        :return: The permutation of this FeatureMdaRequest.
        :rtype: bool
        """
        return self._permutation

    @permutation.setter
    def permutation(self, permutation):
        """Set the permutation of this FeatureMdaRequest.

        When False, will attempt to return MDA that was computed by dropping each feature. When True, will attempt to return MDA that was computed with permutations by scrambling each feature. 

        :param permutation: The permutation of this FeatureMdaRequest.
        :type permutation: bool
        """

        self._permutation = permutation

    @property
    def robust(self):
        """Get the robust of this FeatureMdaRequest.

        When specified, will attempt to return MDA that was computed with the specified robust or non-robust type. 

        :return: The robust of this FeatureMdaRequest.
        :rtype: bool
        """
        return self._robust

    @robust.setter
    def robust(self, robust):
        """Set the robust of this FeatureMdaRequest.

        When specified, will attempt to return MDA that was computed with the specified robust or non-robust type. 

        :param robust: The robust of this FeatureMdaRequest.
        :type robust: bool
        """

        self._robust = robust

    @property
    def weight_feature(self):
        """Get the weight_feature of this FeatureMdaRequest.

        When specified, will attempt to return MDA that was computed using this weight_feature. 

        :return: The weight_feature of this FeatureMdaRequest.
        :rtype: str
        """
        return self._weight_feature

    @weight_feature.setter
    def weight_feature(self, weight_feature):
        """Set the weight_feature of this FeatureMdaRequest.

        When specified, will attempt to return MDA that was computed using this weight_feature. 

        :param weight_feature: The weight_feature of this FeatureMdaRequest.
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
        if not isinstance(other, FeatureMdaRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureMdaRequest):
            return True

        return self.to_dict() != other.to_dict()
