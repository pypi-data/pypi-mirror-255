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


class TraineeIdentity(object):
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
        'id': 'str',
        'name': 'str',
        'project': 'ProjectIdentity',
        'created_by': 'AccountIdentity'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'project': 'project',
        'created_by': 'created_by'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, id=None, name=None, project=None, created_by=None, local_vars_configuration=None):  # noqa: E501
        """TraineeIdentity - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._project = None
        self._created_by = None

        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if project is not None:
            self.project = project
        if created_by is not None:
            self.created_by = created_by

    @property
    def id(self):
        """Get the id of this TraineeIdentity.

        The trainee UUID.

        :return: The id of this TraineeIdentity.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Set the id of this TraineeIdentity.

        The trainee UUID.

        :param id: The id of this TraineeIdentity.
        :type id: str
        """

        self._id = id

    @property
    def name(self):
        """Get the name of this TraineeIdentity.

        The trainee name.

        :return: The name of this TraineeIdentity.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set the name of this TraineeIdentity.

        The trainee name.

        :param name: The name of this TraineeIdentity.
        :type name: str
        """

        self._name = name

    @property
    def project(self):
        """Get the project of this TraineeIdentity.


        :return: The project of this TraineeIdentity.
        :rtype: ProjectIdentity
        """
        return self._project

    @project.setter
    def project(self, project):
        """Set the project of this TraineeIdentity.


        :param project: The project of this TraineeIdentity.
        :type project: ProjectIdentity
        """

        self._project = project

    @property
    def created_by(self):
        """Get the created_by of this TraineeIdentity.


        :return: The created_by of this TraineeIdentity.
        :rtype: AccountIdentity
        """
        return self._created_by

    @created_by.setter
    def created_by(self, created_by):
        """Set the created_by of this TraineeIdentity.


        :param created_by: The created_by of this TraineeIdentity.
        :type created_by: AccountIdentity
        """

        self._created_by = created_by

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
        if not isinstance(other, TraineeIdentity):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TraineeIdentity):
            return True

        return self.to_dict() != other.to_dict()
