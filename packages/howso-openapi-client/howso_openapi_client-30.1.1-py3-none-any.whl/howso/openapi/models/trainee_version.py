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


class TraineeVersion(object):
    """
    Auto-generated OpenAPI type.

    Trainee version information. 
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'container': 'str',
        'trainee': 'str',
        'core': 'str',
        'amalgam': 'str'
    }

    attribute_map = {
        'container': 'container',
        'trainee': 'trainee',
        'core': 'core',
        'amalgam': 'amalgam'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, container=None, trainee=None, core=None, amalgam=None, local_vars_configuration=None):  # noqa: E501
        """TraineeVersion - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._container = None
        self._trainee = None
        self._core = None
        self._amalgam = None

        if container is not None:
            self.container = container
        if trainee is not None:
            self.trainee = trainee
        if core is not None:
            self.core = core
        if amalgam is not None:
            self.amalgam = amalgam

    @property
    def container(self):
        """Get the container of this TraineeVersion.

        The trainee's platform container version.

        :return: The container of this TraineeVersion.
        :rtype: str
        """
        return self._container

    @container.setter
    def container(self, container):
        """Set the container of this TraineeVersion.

        The trainee's platform container version.

        :param container: The container of this TraineeVersion.
        :type container: str
        """

        self._container = container

    @property
    def trainee(self):
        """Get the trainee of this TraineeVersion.

        The version of core the trainee model is at.

        :return: The trainee of this TraineeVersion.
        :rtype: str
        """
        return self._trainee

    @trainee.setter
    def trainee(self, trainee):
        """Set the trainee of this TraineeVersion.

        The version of core the trainee model is at.

        :param trainee: The trainee of this TraineeVersion.
        :type trainee: str
        """

        self._trainee = trainee

    @property
    def core(self):
        """Get the core of this TraineeVersion.

        The version of the loaded Howso Engine.

        :return: The core of this TraineeVersion.
        :rtype: str
        """
        return self._core

    @core.setter
    def core(self, core):
        """Set the core of this TraineeVersion.

        The version of the loaded Howso Engine.

        :param core: The core of this TraineeVersion.
        :type core: str
        """

        self._core = core

    @property
    def amalgam(self):
        """Get the amalgam of this TraineeVersion.

        The version of the loaded Amalgam library.

        :return: The amalgam of this TraineeVersion.
        :rtype: str
        """
        return self._amalgam

    @amalgam.setter
    def amalgam(self, amalgam):
        """Set the amalgam of this TraineeVersion.

        The version of the loaded Amalgam library.

        :param amalgam: The amalgam of this TraineeVersion.
        :type amalgam: str
        """

        self._amalgam = amalgam

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
        if not isinstance(other, TraineeVersion):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TraineeVersion):
            return True

        return self.to_dict() != other.to_dict()
