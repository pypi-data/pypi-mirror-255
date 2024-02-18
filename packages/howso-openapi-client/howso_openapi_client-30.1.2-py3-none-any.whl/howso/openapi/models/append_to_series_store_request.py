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


class AppendToSeriesStoreRequest(object):
    """
    Auto-generated OpenAPI type.

    The body of an append to series store request.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'series': 'str',
        'contexts': 'list[list[object]]',
        'context_features': 'list[str]'
    }

    attribute_map = {
        'series': 'series',
        'contexts': 'contexts',
        'context_features': 'context_features'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, series=None, contexts=None, context_features=None, local_vars_configuration=None):  # noqa: E501
        """AppendToSeriesStoreRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._series = None
        self._contexts = None
        self._context_features = None

        self.series = series
        self.contexts = contexts
        self.context_features = context_features

    @property
    def series(self):
        """Get the series of this AppendToSeriesStoreRequest.

        The name of the series store to append to.

        :return: The series of this AppendToSeriesStoreRequest.
        :rtype: str
        """
        return self._series

    @series.setter
    def series(self, series):
        """Set the series of this AppendToSeriesStoreRequest.

        The name of the series store to append to.

        :param series: The series of this AppendToSeriesStoreRequest.
        :type series: str
        """
        if self.local_vars_configuration.client_side_validation and series is None:  # noqa: E501
            raise ValueError("Invalid value for `series`, must not be `None`")  # noqa: E501

        self._series = series

    @property
    def contexts(self):
        """Get the contexts of this AppendToSeriesStoreRequest.

        A 2D array of context values.

        :return: The contexts of this AppendToSeriesStoreRequest.
        :rtype: list[list[object]]
        """
        return self._contexts

    @contexts.setter
    def contexts(self, contexts):
        """Set the contexts of this AppendToSeriesStoreRequest.

        A 2D array of context values.

        :param contexts: The contexts of this AppendToSeriesStoreRequest.
        :type contexts: list[list[object]]
        """
        if self.local_vars_configuration.client_side_validation and contexts is None:  # noqa: E501
            raise ValueError("Invalid value for `contexts`, must not be `None`")  # noqa: E501

        self._contexts = contexts

    @property
    def context_features(self):
        """Get the context_features of this AppendToSeriesStoreRequest.

        The context feature names.

        :return: The context_features of this AppendToSeriesStoreRequest.
        :rtype: list[str]
        """
        return self._context_features

    @context_features.setter
    def context_features(self, context_features):
        """Set the context_features of this AppendToSeriesStoreRequest.

        The context feature names.

        :param context_features: The context_features of this AppendToSeriesStoreRequest.
        :type context_features: list[str]
        """
        if self.local_vars_configuration.client_side_validation and context_features is None:  # noqa: E501
            raise ValueError("Invalid value for `context_features`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                context_features is not None and len(context_features) < 1):
            raise ValueError("Invalid value for `context_features`, number of items must be greater than or equal to `1`")  # noqa: E501

        self._context_features = context_features

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
        if not isinstance(other, AppendToSeriesStoreRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AppendToSeriesStoreRequest):
            return True

        return self.to_dict() != other.to_dict()
