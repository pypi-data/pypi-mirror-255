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


class TraineeInformation(object):
    """
    Auto-generated OpenAPI type.

    Information about the trainee configuration. 
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
        'version': 'TraineeVersion'
    }

    attribute_map = {
        'library_type': 'library_type',
        'version': 'version'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, library_type=None, version=None, local_vars_configuration=None):  # noqa: E501
        """TraineeInformation - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._library_type = None
        self._version = None

        if library_type is not None:
            self.library_type = library_type
        if version is not None:
            self.version = version

    @property
    def library_type(self):
        """Get the library_type of this TraineeInformation.

        The library type of the trainee. \"st\": trainee uses the single-threaded amalgam library. \"mt\": trainee uses the multi-threaded amalgam library. \"openmp\": trainee uses the open multiprocessing amalgam library. 

        :return: The library_type of this TraineeInformation.
        :rtype: str
        """
        return self._library_type

    @library_type.setter
    def library_type(self, library_type):
        """Set the library_type of this TraineeInformation.

        The library type of the trainee. \"st\": trainee uses the single-threaded amalgam library. \"mt\": trainee uses the multi-threaded amalgam library. \"openmp\": trainee uses the open multiprocessing amalgam library. 

        :param library_type: The library_type of this TraineeInformation.
        :type library_type: str
        """
        allowed_values = ["st", "mt", "openmp"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and library_type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `library_type` ({0}), must be one of {1}"  # noqa: E501
                .format(library_type, allowed_values)
            )

        self._library_type = library_type

    @property
    def version(self):
        """Get the version of this TraineeInformation.


        :return: The version of this TraineeInformation.
        :rtype: TraineeVersion
        """
        return self._version

    @version.setter
    def version(self, version):
        """Set the version of this TraineeInformation.


        :param version: The version of this TraineeInformation.
        :type version: TraineeVersion
        """

        self._version = version

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
        if not isinstance(other, TraineeInformation):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TraineeInformation):
            return True

        return self.to_dict() != other.to_dict()
