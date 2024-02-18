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


class ReactGroupResponseContent(object):
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
        'familiarity_conviction_addition': 'list[float]',
        'familiarity_conviction_removal': 'list[float]',
        'kl_divergence_addition': 'list[float]',
        'kl_divergence_removal': 'list[float]',
        'p_value_of_addition': 'list[float]',
        'p_value_of_removal': 'list[float]',
        'distance_contribution': 'list[float]',
        'base_model_average_distance_contribution': 'list[float]',
        'combined_model_average_distance_contribution': 'list[float]'
    }

    attribute_map = {
        'familiarity_conviction_addition': 'familiarity_conviction_addition',
        'familiarity_conviction_removal': 'familiarity_conviction_removal',
        'kl_divergence_addition': 'kl_divergence_addition',
        'kl_divergence_removal': 'kl_divergence_removal',
        'p_value_of_addition': 'p_value_of_addition',
        'p_value_of_removal': 'p_value_of_removal',
        'distance_contribution': 'distance_contribution',
        'base_model_average_distance_contribution': 'base_model_average_distance_contribution',
        'combined_model_average_distance_contribution': 'combined_model_average_distance_contribution'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, familiarity_conviction_addition=None, familiarity_conviction_removal=None, kl_divergence_addition=None, kl_divergence_removal=None, p_value_of_addition=None, p_value_of_removal=None, distance_contribution=None, base_model_average_distance_contribution=None, combined_model_average_distance_contribution=None, local_vars_configuration=None):  # noqa: E501
        """ReactGroupResponseContent - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._familiarity_conviction_addition = None
        self._familiarity_conviction_removal = None
        self._kl_divergence_addition = None
        self._kl_divergence_removal = None
        self._p_value_of_addition = None
        self._p_value_of_removal = None
        self._distance_contribution = None
        self._base_model_average_distance_contribution = None
        self._combined_model_average_distance_contribution = None

        if familiarity_conviction_addition is not None:
            self.familiarity_conviction_addition = familiarity_conviction_addition
        if familiarity_conviction_removal is not None:
            self.familiarity_conviction_removal = familiarity_conviction_removal
        if kl_divergence_addition is not None:
            self.kl_divergence_addition = kl_divergence_addition
        if kl_divergence_removal is not None:
            self.kl_divergence_removal = kl_divergence_removal
        if p_value_of_addition is not None:
            self.p_value_of_addition = p_value_of_addition
        if p_value_of_removal is not None:
            self.p_value_of_removal = p_value_of_removal
        if distance_contribution is not None:
            self.distance_contribution = distance_contribution
        if base_model_average_distance_contribution is not None:
            self.base_model_average_distance_contribution = base_model_average_distance_contribution
        if combined_model_average_distance_contribution is not None:
            self.combined_model_average_distance_contribution = combined_model_average_distance_contribution

    @property
    def familiarity_conviction_addition(self):
        """Get the familiarity_conviction_addition of this ReactGroupResponseContent.

        The familiarity conviction of adding the cases to the Model.

        :return: The familiarity_conviction_addition of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._familiarity_conviction_addition

    @familiarity_conviction_addition.setter
    def familiarity_conviction_addition(self, familiarity_conviction_addition):
        """Set the familiarity_conviction_addition of this ReactGroupResponseContent.

        The familiarity conviction of adding the cases to the Model.

        :param familiarity_conviction_addition: The familiarity_conviction_addition of this ReactGroupResponseContent.
        :type familiarity_conviction_addition: list[float]
        """

        self._familiarity_conviction_addition = familiarity_conviction_addition

    @property
    def familiarity_conviction_removal(self):
        """Get the familiarity_conviction_removal of this ReactGroupResponseContent.

        The familiarity conviction of removing the cases from the Model.

        :return: The familiarity_conviction_removal of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._familiarity_conviction_removal

    @familiarity_conviction_removal.setter
    def familiarity_conviction_removal(self, familiarity_conviction_removal):
        """Set the familiarity_conviction_removal of this ReactGroupResponseContent.

        The familiarity conviction of removing the cases from the Model.

        :param familiarity_conviction_removal: The familiarity_conviction_removal of this ReactGroupResponseContent.
        :type familiarity_conviction_removal: list[float]
        """

        self._familiarity_conviction_removal = familiarity_conviction_removal

    @property
    def kl_divergence_addition(self):
        """Get the kl_divergence_addition of this ReactGroupResponseContent.

        The KL divergence of adding the cases to the Model.

        :return: The kl_divergence_addition of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._kl_divergence_addition

    @kl_divergence_addition.setter
    def kl_divergence_addition(self, kl_divergence_addition):
        """Set the kl_divergence_addition of this ReactGroupResponseContent.

        The KL divergence of adding the cases to the Model.

        :param kl_divergence_addition: The kl_divergence_addition of this ReactGroupResponseContent.
        :type kl_divergence_addition: list[float]
        """

        self._kl_divergence_addition = kl_divergence_addition

    @property
    def kl_divergence_removal(self):
        """Get the kl_divergence_removal of this ReactGroupResponseContent.

        The KL divergence of removing the cases from the Model.

        :return: The kl_divergence_removal of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._kl_divergence_removal

    @kl_divergence_removal.setter
    def kl_divergence_removal(self, kl_divergence_removal):
        """Set the kl_divergence_removal of this ReactGroupResponseContent.

        The KL divergence of removing the cases from the Model.

        :param kl_divergence_removal: The kl_divergence_removal of this ReactGroupResponseContent.
        :type kl_divergence_removal: list[float]
        """

        self._kl_divergence_removal = kl_divergence_removal

    @property
    def p_value_of_addition(self):
        """Get the p_value_of_addition of this ReactGroupResponseContent.

        The p value of adding the cases to the Model.

        :return: The p_value_of_addition of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._p_value_of_addition

    @p_value_of_addition.setter
    def p_value_of_addition(self, p_value_of_addition):
        """Set the p_value_of_addition of this ReactGroupResponseContent.

        The p value of adding the cases to the Model.

        :param p_value_of_addition: The p_value_of_addition of this ReactGroupResponseContent.
        :type p_value_of_addition: list[float]
        """

        self._p_value_of_addition = p_value_of_addition

    @property
    def p_value_of_removal(self):
        """Get the p_value_of_removal of this ReactGroupResponseContent.

        The p value of removing the cases from the Model.

        :return: The p_value_of_removal of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._p_value_of_removal

    @p_value_of_removal.setter
    def p_value_of_removal(self, p_value_of_removal):
        """Set the p_value_of_removal of this ReactGroupResponseContent.

        The p value of removing the cases from the Model.

        :param p_value_of_removal: The p_value_of_removal of this ReactGroupResponseContent.
        :type p_value_of_removal: list[float]
        """

        self._p_value_of_removal = p_value_of_removal

    @property
    def distance_contribution(self):
        """Get the distance_contribution of this ReactGroupResponseContent.

        Distance contribution ratios.

        :return: The distance_contribution of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._distance_contribution

    @distance_contribution.setter
    def distance_contribution(self, distance_contribution):
        """Set the distance_contribution of this ReactGroupResponseContent.

        Distance contribution ratios.

        :param distance_contribution: The distance_contribution of this ReactGroupResponseContent.
        :type distance_contribution: list[float]
        """

        self._distance_contribution = distance_contribution

    @property
    def base_model_average_distance_contribution(self):
        """Get the base_model_average_distance_contribution of this ReactGroupResponseContent.

        The base Model average distance contribution.

        :return: The base_model_average_distance_contribution of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._base_model_average_distance_contribution

    @base_model_average_distance_contribution.setter
    def base_model_average_distance_contribution(self, base_model_average_distance_contribution):
        """Set the base_model_average_distance_contribution of this ReactGroupResponseContent.

        The base Model average distance contribution.

        :param base_model_average_distance_contribution: The base_model_average_distance_contribution of this ReactGroupResponseContent.
        :type base_model_average_distance_contribution: list[float]
        """

        self._base_model_average_distance_contribution = base_model_average_distance_contribution

    @property
    def combined_model_average_distance_contribution(self):
        """Get the combined_model_average_distance_contribution of this ReactGroupResponseContent.

        The combined Model average distance contribution.

        :return: The combined_model_average_distance_contribution of this ReactGroupResponseContent.
        :rtype: list[float]
        """
        return self._combined_model_average_distance_contribution

    @combined_model_average_distance_contribution.setter
    def combined_model_average_distance_contribution(self, combined_model_average_distance_contribution):
        """Set the combined_model_average_distance_contribution of this ReactGroupResponseContent.

        The combined Model average distance contribution.

        :param combined_model_average_distance_contribution: The combined_model_average_distance_contribution of this ReactGroupResponseContent.
        :type combined_model_average_distance_contribution: list[float]
        """

        self._combined_model_average_distance_contribution = combined_model_average_distance_contribution

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
        if not isinstance(other, ReactGroupResponseContent):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactGroupResponseContent):
            return True

        return self.to_dict() != other.to_dict()
