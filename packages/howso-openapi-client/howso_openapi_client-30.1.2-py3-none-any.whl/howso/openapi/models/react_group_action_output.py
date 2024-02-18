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


class ReactGroupActionOutput(object):
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
        'status': 'str',
        'operation_type': 'str',
        'output': 'ReactGroupResponse'
    }

    attribute_map = {
        'action_id': 'action_id',
        'status': 'status',
        'operation_type': 'operation_type',
        'output': 'output'
    }

    nullable_attributes = [
        'output', 
    ]

    discriminator = None

    def __init__(self, action_id=None, status=None, operation_type=None, output=None, local_vars_configuration=None):  # noqa: E501
        """ReactGroupActionOutput - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_id = None
        self._status = None
        self._operation_type = None
        self._output = None

        if action_id is not None:
            self.action_id = action_id
        self.status = status
        self.operation_type = operation_type
        self.output = output

    @property
    def action_id(self):
        """Get the action_id of this ReactGroupActionOutput.

        The async action's unique identifier.

        :return: The action_id of this ReactGroupActionOutput.
        :rtype: str
        """
        return self._action_id

    @action_id.setter
    def action_id(self, action_id):
        """Set the action_id of this ReactGroupActionOutput.

        The async action's unique identifier.

        :param action_id: The action_id of this ReactGroupActionOutput.
        :type action_id: str
        """

        self._action_id = action_id

    @property
    def status(self):
        """Get the status of this ReactGroupActionOutput.

        The status of the action.

        :return: The status of this ReactGroupActionOutput.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Set the status of this ReactGroupActionOutput.

        The status of the action.

        :param status: The status of this ReactGroupActionOutput.
        :type status: str
        """
        if self.local_vars_configuration.client_side_validation and status is None:  # noqa: E501
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501

        self._status = status

    @property
    def operation_type(self):
        """Get the operation_type of this ReactGroupActionOutput.

        The type of operation that is running.

        :return: The operation_type of this ReactGroupActionOutput.
        :rtype: str
        """
        return self._operation_type

    @operation_type.setter
    def operation_type(self, operation_type):
        """Set the operation_type of this ReactGroupActionOutput.

        The type of operation that is running.

        :param operation_type: The operation_type of this ReactGroupActionOutput.
        :type operation_type: str
        """
        if self.local_vars_configuration.client_side_validation and operation_type is None:  # noqa: E501
            raise ValueError("Invalid value for `operation_type`, must not be `None`")  # noqa: E501

        self._operation_type = operation_type

    @property
    def output(self):
        """Get the output of this ReactGroupActionOutput.


        :return: The output of this ReactGroupActionOutput.
        :rtype: ReactGroupResponse
        """
        return self._output

    @output.setter
    def output(self, output):
        """Set the output of this ReactGroupActionOutput.


        :param output: The output of this ReactGroupActionOutput.
        :type output: ReactGroupResponse
        """

        self._output = output

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
        if not isinstance(other, ReactGroupActionOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactGroupActionOutput):
            return True

        return self.to_dict() != other.to_dict()
