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


class ImputeRequest(object):
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
        'batch_size': 'int',
        'features': 'list[str]',
        'features_to_impute': 'list[str]'
    }

    attribute_map = {
        'batch_size': 'batch_size',
        'features': 'features',
        'features_to_impute': 'features_to_impute'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, batch_size=1, features=None, features_to_impute=None, local_vars_configuration=None):  # noqa: E501
        """ImputeRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._batch_size = None
        self._features = None
        self._features_to_impute = None

        if batch_size is not None:
            self.batch_size = batch_size
        if features is not None:
            self.features = features
        if features_to_impute is not None:
            self.features_to_impute = features_to_impute

    @property
    def batch_size(self):
        """Get the batch_size of this ImputeRequest.

        Larger batch size will increase speed but decrease accuracy. Batch size indicates how many rows to fill before recomputing conviction. The default value (which is 1) should return the best accuracy but might be slower. Higher values should improve performance but may decrease accuracy of results. 

        :return: The batch_size of this ImputeRequest.
        :rtype: int
        """
        return self._batch_size

    @batch_size.setter
    def batch_size(self, batch_size):
        """Set the batch_size of this ImputeRequest.

        Larger batch size will increase speed but decrease accuracy. Batch size indicates how many rows to fill before recomputing conviction. The default value (which is 1) should return the best accuracy but might be slower. Higher values should improve performance but may decrease accuracy of results. 

        :param batch_size: The batch_size of this ImputeRequest.
        :type batch_size: int
        """
        if (self.local_vars_configuration.client_side_validation and
                batch_size is not None and batch_size < 1):  # noqa: E501
            raise ValueError("Invalid value for `batch_size`, must be a value greater than or equal to `1`")  # noqa: E501

        self._batch_size = batch_size

    @property
    def features(self):
        """Get the features of this ImputeRequest.


        :return: The features of this ImputeRequest.
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this ImputeRequest.


        :param features: The features of this ImputeRequest.
        :type features: list[str]
        """

        self._features = features

    @property
    def features_to_impute(self):
        """Get the features_to_impute of this ImputeRequest.


        :return: The features_to_impute of this ImputeRequest.
        :rtype: list[str]
        """
        return self._features_to_impute

    @features_to_impute.setter
    def features_to_impute(self, features_to_impute):
        """Set the features_to_impute of this ImputeRequest.


        :param features_to_impute: The features_to_impute of this ImputeRequest.
        :type features_to_impute: list[str]
        """

        self._features_to_impute = features_to_impute

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
        if not isinstance(other, ImputeRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ImputeRequest):
            return True

        return self.to_dict() != other.to_dict()
