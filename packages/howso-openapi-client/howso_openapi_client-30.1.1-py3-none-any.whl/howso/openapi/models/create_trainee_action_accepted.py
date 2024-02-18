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


class CreateTraineeActionAccepted(object):
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
        'tracking': 'AsyncActionAcceptedTracking',
        'estimated_completion': 'datetime',
        'rejected_after': 'datetime',
        'trainee_id': 'str'
    }

    attribute_map = {
        'action_id': 'action_id',
        'operation_type': 'operation_type',
        'tracking': 'tracking',
        'estimated_completion': 'estimated_completion',
        'rejected_after': 'rejected_after',
        'trainee_id': 'trainee_id'
    }

    nullable_attributes = [
        'estimated_completion', 
        'rejected_after', 
    ]

    discriminator = None

    def __init__(self, action_id=None, operation_type=None, tracking=None, estimated_completion=None, rejected_after=None, trainee_id=None, local_vars_configuration=None):  # noqa: E501
        """CreateTraineeActionAccepted - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_id = None
        self._operation_type = None
        self._tracking = None
        self._estimated_completion = None
        self._rejected_after = None
        self._trainee_id = None

        if action_id is not None:
            self.action_id = action_id
        if operation_type is not None:
            self.operation_type = operation_type
        if tracking is not None:
            self.tracking = tracking
        self.estimated_completion = estimated_completion
        self.rejected_after = rejected_after
        if trainee_id is not None:
            self.trainee_id = trainee_id

    @property
    def action_id(self):
        """Get the action_id of this CreateTraineeActionAccepted.

        The async action's unique identifier.

        :return: The action_id of this CreateTraineeActionAccepted.
        :rtype: str
        """
        return self._action_id

    @action_id.setter
    def action_id(self, action_id):
        """Set the action_id of this CreateTraineeActionAccepted.

        The async action's unique identifier.

        :param action_id: The action_id of this CreateTraineeActionAccepted.
        :type action_id: str
        """

        self._action_id = action_id

    @property
    def operation_type(self):
        """Get the operation_type of this CreateTraineeActionAccepted.

        The type of operation that is running.

        :return: The operation_type of this CreateTraineeActionAccepted.
        :rtype: str
        """
        return self._operation_type

    @operation_type.setter
    def operation_type(self, operation_type):
        """Set the operation_type of this CreateTraineeActionAccepted.

        The type of operation that is running.

        :param operation_type: The operation_type of this CreateTraineeActionAccepted.
        :type operation_type: str
        """

        self._operation_type = operation_type

    @property
    def tracking(self):
        """Get the tracking of this CreateTraineeActionAccepted.


        :return: The tracking of this CreateTraineeActionAccepted.
        :rtype: AsyncActionAcceptedTracking
        """
        return self._tracking

    @tracking.setter
    def tracking(self, tracking):
        """Set the tracking of this CreateTraineeActionAccepted.


        :param tracking: The tracking of this CreateTraineeActionAccepted.
        :type tracking: AsyncActionAcceptedTracking
        """

        self._tracking = tracking

    @property
    def estimated_completion(self):
        """Get the estimated_completion of this CreateTraineeActionAccepted.

        An estimated time of when the action may be complete and any output ready to retrieve.

        :return: The estimated_completion of this CreateTraineeActionAccepted.
        :rtype: datetime
        """
        return self._estimated_completion

    @estimated_completion.setter
    def estimated_completion(self, estimated_completion):
        """Set the estimated_completion of this CreateTraineeActionAccepted.

        An estimated time of when the action may be complete and any output ready to retrieve.

        :param estimated_completion: The estimated_completion of this CreateTraineeActionAccepted.
        :type estimated_completion: datetime
        """

        self._estimated_completion = estimated_completion

    @property
    def rejected_after(self):
        """Get the rejected_after of this CreateTraineeActionAccepted.

        A timestamp of when the action will be rejected if it has not yet been acted upon.

        :return: The rejected_after of this CreateTraineeActionAccepted.
        :rtype: datetime
        """
        return self._rejected_after

    @rejected_after.setter
    def rejected_after(self, rejected_after):
        """Set the rejected_after of this CreateTraineeActionAccepted.

        A timestamp of when the action will be rejected if it has not yet been acted upon.

        :param rejected_after: The rejected_after of this CreateTraineeActionAccepted.
        :type rejected_after: datetime
        """

        self._rejected_after = rejected_after

    @property
    def trainee_id(self):
        """Get the trainee_id of this CreateTraineeActionAccepted.


        :return: The trainee_id of this CreateTraineeActionAccepted.
        :rtype: str
        """
        return self._trainee_id

    @trainee_id.setter
    def trainee_id(self, trainee_id):
        """Set the trainee_id of this CreateTraineeActionAccepted.


        :param trainee_id: The trainee_id of this CreateTraineeActionAccepted.
        :type trainee_id: str
        """

        self._trainee_id = trainee_id

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
        if not isinstance(other, CreateTraineeActionAccepted):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateTraineeActionAccepted):
            return True

        return self.to_dict() != other.to_dict()
