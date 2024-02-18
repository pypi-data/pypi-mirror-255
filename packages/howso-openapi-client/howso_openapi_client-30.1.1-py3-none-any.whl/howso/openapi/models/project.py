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


class Project(object):
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
        'is_private': 'bool',
        'is_default': 'bool',
        'created_by': 'AccountIdentity',
        'created_date': 'datetime',
        'modified_date': 'datetime',
        'permissions': 'list[str]'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'is_private': 'is_private',
        'is_default': 'is_default',
        'created_by': 'created_by',
        'created_date': 'created_date',
        'modified_date': 'modified_date',
        'permissions': 'permissions'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, id=None, name=None, is_private=None, is_default=None, created_by=None, created_date=None, modified_date=None, permissions=None, local_vars_configuration=None):  # noqa: E501
        """Project - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._is_private = None
        self._is_default = None
        self._created_by = None
        self._created_date = None
        self._modified_date = None
        self._permissions = None

        self.id = id
        self.name = name
        if is_private is not None:
            self.is_private = is_private
        if is_default is not None:
            self.is_default = is_default
        if created_by is not None:
            self.created_by = created_by
        if created_date is not None:
            self.created_date = created_date
        if modified_date is not None:
            self.modified_date = modified_date
        if permissions is not None:
            self.permissions = permissions

    @property
    def id(self):
        """Get the id of this Project.

        The project UUID.

        :return: The id of this Project.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Set the id of this Project.

        The project UUID.

        :param id: The id of this Project.
        :type id: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def name(self):
        """Get the name of this Project.

        The project name.

        :return: The name of this Project.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set the name of this Project.

        The project name.

        :param name: The name of this Project.
        :type name: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 128):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `128`")  # noqa: E501

        self._name = name

    @property
    def is_private(self):
        """Get the is_private of this Project.

        Designates if the project is not publicly visible.

        :return: The is_private of this Project.
        :rtype: bool
        """
        return self._is_private

    @is_private.setter
    def is_private(self, is_private):
        """Set the is_private of this Project.

        Designates if the project is not publicly visible.

        :param is_private: The is_private of this Project.
        :type is_private: bool
        """

        self._is_private = is_private

    @property
    def is_default(self):
        """Get the is_default of this Project.

        If project is your default.

        :return: The is_default of this Project.
        :rtype: bool
        """
        return self._is_default

    @is_default.setter
    def is_default(self, is_default):
        """Set the is_default of this Project.

        If project is your default.

        :param is_default: The is_default of this Project.
        :type is_default: bool
        """

        self._is_default = is_default

    @property
    def created_by(self):
        """Get the created_by of this Project.


        :return: The created_by of this Project.
        :rtype: AccountIdentity
        """
        return self._created_by

    @created_by.setter
    def created_by(self, created_by):
        """Set the created_by of this Project.


        :param created_by: The created_by of this Project.
        :type created_by: AccountIdentity
        """

        self._created_by = created_by

    @property
    def created_date(self):
        """Get the created_date of this Project.


        :return: The created_date of this Project.
        :rtype: datetime
        """
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        """Set the created_date of this Project.


        :param created_date: The created_date of this Project.
        :type created_date: datetime
        """

        self._created_date = created_date

    @property
    def modified_date(self):
        """Get the modified_date of this Project.


        :return: The modified_date of this Project.
        :rtype: datetime
        """
        return self._modified_date

    @modified_date.setter
    def modified_date(self, modified_date):
        """Set the modified_date of this Project.


        :param modified_date: The modified_date of this Project.
        :type modified_date: datetime
        """

        self._modified_date = modified_date

    @property
    def permissions(self):
        """Get the permissions of this Project.

        Permissions types the user has in this project.

        :return: The permissions of this Project.
        :rtype: list[str]
        """
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        """Set the permissions of this Project.

        Permissions types the user has in this project.

        :param permissions: The permissions of this Project.
        :type permissions: list[str]
        """

        self._permissions = permissions

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
        if not isinstance(other, Project):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Project):
            return True

        return self.to_dict() != other.to_dict()
