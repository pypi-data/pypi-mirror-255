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


class ExtremeCasesRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of an extreme cases request. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'num': 'int',
        'sort_feature': 'str',
        'features': 'list[str]'
    }

    attribute_map = {
        'num': 'num',
        'sort_feature': 'sort_feature',
        'features': 'features'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, num=None, sort_feature=None, features=None, local_vars_configuration=None):  # noqa: E501
        """ExtremeCasesRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._num = None
        self._sort_feature = None
        self._features = None

        self.num = num
        self.sort_feature = sort_feature
        if features is not None:
            self.features = features

    @property
    def num(self):
        """Get the num of this ExtremeCasesRequest.

        The number of cases to return. If num is positive, this will return the top (largest value) cases. If num is negative, this will return smallest cases. 

        :return: The num of this ExtremeCasesRequest.
        :rtype: int
        """
        return self._num

    @num.setter
    def num(self, num):
        """Set the num of this ExtremeCasesRequest.

        The number of cases to return. If num is positive, this will return the top (largest value) cases. If num is negative, this will return smallest cases. 

        :param num: The num of this ExtremeCasesRequest.
        :type num: int
        """
        if self.local_vars_configuration.client_side_validation and num is None:  # noqa: E501
            raise ValueError("Invalid value for `num`, must not be `None`")  # noqa: E501

        self._num = num

    @property
    def sort_feature(self):
        """Get the sort_feature of this ExtremeCasesRequest.

        The feature to sort by.

        :return: The sort_feature of this ExtremeCasesRequest.
        :rtype: str
        """
        return self._sort_feature

    @sort_feature.setter
    def sort_feature(self, sort_feature):
        """Set the sort_feature of this ExtremeCasesRequest.

        The feature to sort by.

        :param sort_feature: The sort_feature of this ExtremeCasesRequest.
        :type sort_feature: str
        """
        if self.local_vars_configuration.client_side_validation and sort_feature is None:  # noqa: E501
            raise ValueError("Invalid value for `sort_feature`, must not be `None`")  # noqa: E501

        self._sort_feature = sort_feature

    @property
    def features(self):
        """Get the features of this ExtremeCasesRequest.

        The features to return values for.

        :return: The features of this ExtremeCasesRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this ExtremeCasesRequest.

        The features to return values for.

        :param features: The features of this ExtremeCasesRequest.
        :type features: list[str]
        """

        self._features = features

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
        if not isinstance(other, ExtremeCasesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ExtremeCasesRequest):
            return True

        return self.to_dict() != other.to_dict()
