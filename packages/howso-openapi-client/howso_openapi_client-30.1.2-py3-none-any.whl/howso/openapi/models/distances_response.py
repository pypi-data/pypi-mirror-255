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


class DistancesResponse(object):
    """
    Auto-generated OpenAPI type.

    The body of the distances metric response.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'row_case_indices': 'list[list[object]]',
        'column_case_indices': 'list[list[object]]',
        'distances': 'list[list[float]]'
    }

    attribute_map = {
        'row_case_indices': 'row_case_indices',
        'column_case_indices': 'column_case_indices',
        'distances': 'distances'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, row_case_indices=[], column_case_indices=[], distances=[], local_vars_configuration=None):  # noqa: E501
        """DistancesResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._row_case_indices = None
        self._column_case_indices = None
        self._distances = None

        if row_case_indices is not None:
            self.row_case_indices = row_case_indices
        if column_case_indices is not None:
            self.column_case_indices = column_case_indices
        if distances is not None:
            self.distances = distances

    @property
    def row_case_indices(self):
        """Get the row_case_indices of this DistancesResponse.

        The list of case identifiers corresponding to the distances matrix rows. List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. 

        :return: The row_case_indices of this DistancesResponse.
        :rtype: list[list[object]]
        """
        return self._row_case_indices

    @row_case_indices.setter
    def row_case_indices(self, row_case_indices):
        """Set the row_case_indices of this DistancesResponse.

        The list of case identifiers corresponding to the distances matrix rows. List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. 

        :param row_case_indices: The row_case_indices of this DistancesResponse.
        :type row_case_indices: list[list[object]]
        """

        self._row_case_indices = row_case_indices

    @property
    def column_case_indices(self):
        """Get the column_case_indices of this DistancesResponse.

        The list of case identifiers corresponding to the distances matrix columns. List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. 

        :return: The column_case_indices of this DistancesResponse.
        :rtype: list[list[object]]
        """
        return self._column_case_indices

    @column_case_indices.setter
    def column_case_indices(self, column_case_indices):
        """Set the column_case_indices of this DistancesResponse.

        The list of case identifiers corresponding to the distances matrix columns. List of tuples, of session id and index, where index is the original 0-based index of the case as it was trained into the session. 

        :param column_case_indices: The column_case_indices of this DistancesResponse.
        :type column_case_indices: list[list[object]]
        """

        self._column_case_indices = column_case_indices

    @property
    def distances(self):
        """Get the distances of this DistancesResponse.

        The distance values matrix.

        :return: The distances of this DistancesResponse.
        :rtype: list[list[float]]
        """
        return self._distances

    @distances.setter
    def distances(self, distances):
        """Set the distances of this DistancesResponse.

        The distance values matrix.

        :param distances: The distances of this DistancesResponse.
        :type distances: list[list[float]]
        """

        self._distances = distances

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
        if not isinstance(other, DistancesResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DistancesResponse):
            return True

        return self.to_dict() != other.to_dict()
