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


class CopyTraineeRequest(object):
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
        'new_trainee_name': 'str',
        'project_id': 'str',
        'library_type': 'str',
        'resources': 'TraineeResources'
    }

    attribute_map = {
        'new_trainee_name': 'new_trainee_name',
        'project_id': 'project_id',
        'library_type': 'library_type',
        'resources': 'resources'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, new_trainee_name=None, project_id=None, library_type=None, resources=None, local_vars_configuration=None):  # noqa: E501
        """CopyTraineeRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._new_trainee_name = None
        self._project_id = None
        self._library_type = None
        self._resources = None

        if new_trainee_name is not None:
            self.new_trainee_name = new_trainee_name
        if project_id is not None:
            self.project_id = project_id
        if library_type is not None:
            self.library_type = library_type
        if resources is not None:
            self.resources = resources

    @property
    def new_trainee_name(self):
        """Get the new_trainee_name of this CopyTraineeRequest.

        The name of the copy to be created. If not defined the original trainee name is used.

        :return: The new_trainee_name of this CopyTraineeRequest.
        :rtype: str
        """
        return self._new_trainee_name

    @new_trainee_name.setter
    def new_trainee_name(self, new_trainee_name):
        """Set the new_trainee_name of this CopyTraineeRequest.

        The name of the copy to be created. If not defined the original trainee name is used.

        :param new_trainee_name: The new_trainee_name of this CopyTraineeRequest.
        :type new_trainee_name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                new_trainee_name is not None and len(new_trainee_name) > 128):
            raise ValueError("Invalid value for `new_trainee_name`, length must be less than or equal to `128`")  # noqa: E501

        self._new_trainee_name = new_trainee_name

    @property
    def project_id(self):
        """Get the project_id of this CopyTraineeRequest.

        The id of the project to create the new trainee in. If not defined, uses user's default project.

        :return: The project_id of this CopyTraineeRequest.
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Set the project_id of this CopyTraineeRequest.

        The id of the project to create the new trainee in. If not defined, uses user's default project.

        :param project_id: The project_id of this CopyTraineeRequest.
        :type project_id: str
        """

        self._project_id = project_id

    @property
    def library_type(self):
        """Get the library_type of this CopyTraineeRequest.

        The library type of the new Trainee. \"st\": use single-threaded library. \"mt\": use multi-threaded library. 

        :return: The library_type of this CopyTraineeRequest.
        :rtype: str
        """
        return self._library_type

    @library_type.setter
    def library_type(self, library_type):
        """Set the library_type of this CopyTraineeRequest.

        The library type of the new Trainee. \"st\": use single-threaded library. \"mt\": use multi-threaded library. 

        :param library_type: The library_type of this CopyTraineeRequest.
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
    def resources(self):
        """Get the resources of this CopyTraineeRequest.


        :return: The resources of this CopyTraineeRequest.
        :rtype: TraineeResources
        """
        return self._resources

    @resources.setter
    def resources(self, resources):
        """Set the resources of this CopyTraineeRequest.


        :param resources: The resources of this CopyTraineeRequest.
        :type resources: TraineeResources
        """

        self._resources = resources

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
        if not isinstance(other, CopyTraineeRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CopyTraineeRequest):
            return True

        return self.to_dict() != other.to_dict()
