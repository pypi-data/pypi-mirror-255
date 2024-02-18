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


class TrainResponse(object):
    """
    Auto-generated OpenAPI type.

    The result of the train request.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'ablated_indices': 'list[int]',
        'num_trained': 'int',
        'status': 'str'
    }

    attribute_map = {
        'ablated_indices': 'ablated_indices',
        'num_trained': 'num_trained',
        'status': 'status'
    }

    nullable_attributes = [
        'status', 
    ]

    discriminator = None

    def __init__(self, ablated_indices=None, num_trained=None, status=None, local_vars_configuration=None):  # noqa: E501
        """TrainResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._ablated_indices = None
        self._num_trained = None
        self._status = None

        if ablated_indices is not None:
            self.ablated_indices = ablated_indices
        if num_trained is not None:
            self.num_trained = num_trained
        self.status = status

    @property
    def ablated_indices(self):
        """Get the ablated_indices of this TrainResponse.

        The indices of ablated cases.

        :return: The ablated_indices of this TrainResponse.
        :rtype: list[int]
        """
        return self._ablated_indices

    @ablated_indices.setter
    def ablated_indices(self, ablated_indices):
        """Set the ablated_indices of this TrainResponse.

        The indices of ablated cases.

        :param ablated_indices: The ablated_indices of this TrainResponse.
        :type ablated_indices: list[int]
        """

        self._ablated_indices = ablated_indices

    @property
    def num_trained(self):
        """Get the num_trained of this TrainResponse.

        The number of cases that were trained.

        :return: The num_trained of this TrainResponse.
        :rtype: int
        """
        return self._num_trained

    @num_trained.setter
    def num_trained(self, num_trained):
        """Set the num_trained of this TrainResponse.

        The number of cases that were trained.

        :param num_trained: The num_trained of this TrainResponse.
        :type num_trained: int
        """

        self._num_trained = num_trained

    @property
    def status(self):
        """Get the status of this TrainResponse.

        Status message output. Valid status values are:   null - default output, no status   \"analyze\" - if auto analysis is enabled and the model has grown large enough to be analyzed again 

        :return: The status of this TrainResponse.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Set the status of this TrainResponse.

        Status message output. Valid status values are:   null - default output, no status   \"analyze\" - if auto analysis is enabled and the model has grown large enough to be analyzed again 

        :param status: The status of this TrainResponse.
        :type status: str
        """

        self._status = status

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
        if not isinstance(other, TrainResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TrainResponse):
            return True

        return self.to_dict() != other.to_dict()
