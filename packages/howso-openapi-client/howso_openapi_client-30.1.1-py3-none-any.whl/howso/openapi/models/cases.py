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


class Cases(object):
    """
    Auto-generated OpenAPI type.

    A matrix of data.
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
        'cases': 'list[list[object]]'
    }

    attribute_map = {
        'features': 'features',
        'cases': 'cases'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, features=None, cases=None, local_vars_configuration=None):  # noqa: E501
        """Cases - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._features = None
        self._cases = None

        if features is not None:
            self.features = features
        if cases is not None:
            self.cases = cases

    @property
    def features(self):
        """Get the features of this Cases.

        The feature names that correspond to the case columns.

        :return: The features of this Cases.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this Cases.

        The feature names that correspond to the case columns.

        :param features: The features of this Cases.
        :type features: list[str]
        """

        self._features = features

    @property
    def cases(self):
        """Get the cases of this Cases.

        A 2D array of case values.

        :return: The cases of this Cases.
        :rtype: list[list[object]]
        """
        return self._cases

    @cases.setter
    def cases(self, cases):
        """Set the cases of this Cases.

        A 2D array of case values.

        :param cases: The cases of this Cases.
        :type cases: list[list[object]]
        """

        self._cases = cases

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
        if not isinstance(other, Cases):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Cases):
            return True

        return self.to_dict() != other.to_dict()
