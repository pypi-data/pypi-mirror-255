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


class DetailsResponseDistanceRatioPartsInner(object):
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
        'local_distance_contribution': 'float',
        'nearest_distance': 'float'
    }

    attribute_map = {
        'local_distance_contribution': 'local_distance_contribution',
        'nearest_distance': 'nearest_distance'
    }

    nullable_attributes = [
        'local_distance_contribution', 
        'nearest_distance', 
    ]

    discriminator = None

    def __init__(self, local_distance_contribution=None, nearest_distance=None, local_vars_configuration=None):  # noqa: E501
        """DetailsResponseDistanceRatioPartsInner - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._local_distance_contribution = None
        self._nearest_distance = None

        self.local_distance_contribution = local_distance_contribution
        self.nearest_distance = nearest_distance

    @property
    def local_distance_contribution(self):
        """Get the local_distance_contribution of this DetailsResponseDistanceRatioPartsInner.


        :return: The local_distance_contribution of this DetailsResponseDistanceRatioPartsInner.
        :rtype: float
        """
        return self._local_distance_contribution

    @local_distance_contribution.setter
    def local_distance_contribution(self, local_distance_contribution):
        """Set the local_distance_contribution of this DetailsResponseDistanceRatioPartsInner.


        :param local_distance_contribution: The local_distance_contribution of this DetailsResponseDistanceRatioPartsInner.
        :type local_distance_contribution: float
        """

        self._local_distance_contribution = local_distance_contribution

    @property
    def nearest_distance(self):
        """Get the nearest_distance of this DetailsResponseDistanceRatioPartsInner.


        :return: The nearest_distance of this DetailsResponseDistanceRatioPartsInner.
        :rtype: float
        """
        return self._nearest_distance

    @nearest_distance.setter
    def nearest_distance(self, nearest_distance):
        """Set the nearest_distance of this DetailsResponseDistanceRatioPartsInner.


        :param nearest_distance: The nearest_distance of this DetailsResponseDistanceRatioPartsInner.
        :type nearest_distance: float
        """

        self._nearest_distance = nearest_distance

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
        if not isinstance(other, DetailsResponseDistanceRatioPartsInner):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DetailsResponseDistanceRatioPartsInner):
            return True

        return self.to_dict() != other.to_dict()
