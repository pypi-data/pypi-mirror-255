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


class AsyncActionCancel(object):
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
        'action_id': 'str',
        'operation_type': 'str',
        'scheduled': 'bool',
        'message': 'str'
    }

    attribute_map = {
        'action_id': 'action_id',
        'operation_type': 'operation_type',
        'scheduled': 'scheduled',
        'message': 'message'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, action_id=None, operation_type=None, scheduled=None, message=None, local_vars_configuration=None):  # noqa: E501
        """AsyncActionCancel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_id = None
        self._operation_type = None
        self._scheduled = None
        self._message = None

        if action_id is not None:
            self.action_id = action_id
        if operation_type is not None:
            self.operation_type = operation_type
        if scheduled is not None:
            self.scheduled = scheduled
        if message is not None:
            self.message = message

    @property
    def action_id(self):
        """Get the action_id of this AsyncActionCancel.

        The async action's unique identifier.

        :return: The action_id of this AsyncActionCancel.
        :rtype: str
        """
        return self._action_id

    @action_id.setter
    def action_id(self, action_id):
        """Set the action_id of this AsyncActionCancel.

        The async action's unique identifier.

        :param action_id: The action_id of this AsyncActionCancel.
        :type action_id: str
        """

        self._action_id = action_id

    @property
    def operation_type(self):
        """Get the operation_type of this AsyncActionCancel.

        The type of operation that is running.

        :return: The operation_type of this AsyncActionCancel.
        :rtype: str
        """
        return self._operation_type

    @operation_type.setter
    def operation_type(self, operation_type):
        """Set the operation_type of this AsyncActionCancel.

        The type of operation that is running.

        :param operation_type: The operation_type of this AsyncActionCancel.
        :type operation_type: str
        """

        self._operation_type = operation_type

    @property
    def scheduled(self):
        """Get the scheduled of this AsyncActionCancel.

        If action cancellation has been scheduled.

        :return: The scheduled of this AsyncActionCancel.
        :rtype: bool
        """
        return self._scheduled

    @scheduled.setter
    def scheduled(self, scheduled):
        """Set the scheduled of this AsyncActionCancel.

        If action cancellation has been scheduled.

        :param scheduled: The scheduled of this AsyncActionCancel.
        :type scheduled: bool
        """

        self._scheduled = scheduled

    @property
    def message(self):
        """Get the message of this AsyncActionCancel.

        Cancellation result message.

        :return: The message of this AsyncActionCancel.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Set the message of this AsyncActionCancel.

        Cancellation result message.

        :param message: The message of this AsyncActionCancel.
        :type message: str
        """

        self._message = message

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
        if not isinstance(other, AsyncActionCancel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AsyncActionCancel):
            return True

        return self.to_dict() != other.to_dict()
