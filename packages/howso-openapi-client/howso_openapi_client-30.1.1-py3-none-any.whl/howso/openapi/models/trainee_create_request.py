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


class TraineeCreateRequest(object):
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
        'library_type': 'str',
        'timeout': 'float',
        'resources': 'TraineeResources',
        'trainee': 'TraineeRequest'
    }

    attribute_map = {
        'library_type': 'library_type',
        'timeout': 'timeout',
        'resources': 'resources',
        'trainee': 'trainee'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, library_type=None, timeout=0, resources=None, trainee=None, local_vars_configuration=None):  # noqa: E501
        """TraineeCreateRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._library_type = None
        self._timeout = None
        self._resources = None
        self._trainee = None

        if library_type is not None:
            self.library_type = library_type
        if timeout is not None:
            self.timeout = timeout
        if resources is not None:
            self.resources = resources
        self.trainee = trainee

    @property
    def library_type(self):
        """Get the library_type of this TraineeCreateRequest.

        The library type of the Trainee. \"st\": use single-threaded library. \"mt\": use multi-threaded library. 

        :return: The library_type of this TraineeCreateRequest.
        :rtype: str
        """
        return self._library_type

    @library_type.setter
    def library_type(self, library_type):
        """Set the library_type of this TraineeCreateRequest.

        The library type of the Trainee. \"st\": use single-threaded library. \"mt\": use multi-threaded library. 

        :param library_type: The library_type of this TraineeCreateRequest.
        :type library_type: str
        """
        allowed_values = ["st", "mt"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and library_type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `library_type` ({0}), must be one of {1}"  # noqa: E501
                .format(library_type, allowed_values)
            )

        self._library_type = library_type

    @property
    def timeout(self):
        """Get the timeout of this TraineeCreateRequest.

        The maximum seconds to wait for a trainee to be created.

        :return: The timeout of this TraineeCreateRequest.
        :rtype: float
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Set the timeout of this TraineeCreateRequest.

        The maximum seconds to wait for a trainee to be created.

        :param timeout: The timeout of this TraineeCreateRequest.
        :type timeout: float
        """
        if (self.local_vars_configuration.client_side_validation and
                timeout is not None and timeout < 0):  # noqa: E501
            raise ValueError("Invalid value for `timeout`, must be a value greater than or equal to `0`")  # noqa: E501

        self._timeout = timeout

    @property
    def resources(self):
        """Get the resources of this TraineeCreateRequest.


        :return: The resources of this TraineeCreateRequest.
        :rtype: TraineeResources
        """
        return self._resources

    @resources.setter
    def resources(self, resources):
        """Set the resources of this TraineeCreateRequest.


        :param resources: The resources of this TraineeCreateRequest.
        :type resources: TraineeResources
        """

        self._resources = resources

    @property
    def trainee(self):
        """Get the trainee of this TraineeCreateRequest.


        :return: The trainee of this TraineeCreateRequest.
        :rtype: TraineeRequest
        """
        return self._trainee

    @trainee.setter
    def trainee(self, trainee):
        """Set the trainee of this TraineeCreateRequest.


        :param trainee: The trainee of this TraineeCreateRequest.
        :type trainee: TraineeRequest
        """
        if self.local_vars_configuration.client_side_validation and trainee is None:  # noqa: E501
            raise ValueError("Invalid value for `trainee`, must not be `None`")  # noqa: E501

        self._trainee = trainee

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
        if not isinstance(other, TraineeCreateRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TraineeCreateRequest):
            return True

        return self.to_dict() != other.to_dict()
