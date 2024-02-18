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


class Account(object):
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
        'uuid': 'str',
        'username': 'str',
        'first_name': 'str',
        'last_name': 'str',
        'email': 'str',
        'default_project': 'ProjectIdentity'
    }

    attribute_map = {
        'uuid': 'uuid',
        'username': 'username',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email',
        'default_project': 'default_project'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, uuid=None, username=None, first_name=None, last_name=None, email=None, default_project=None, local_vars_configuration=None):  # noqa: E501
        """Account - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._uuid = None
        self._username = None
        self._first_name = None
        self._last_name = None
        self._email = None
        self._default_project = None

        if uuid is not None:
            self.uuid = uuid
        if username is not None:
            self.username = username
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if email is not None:
            self.email = email
        if default_project is not None:
            self.default_project = default_project

    @property
    def uuid(self):
        """Get the uuid of this Account.

        The user's UUID.

        :return: The uuid of this Account.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        """Set the uuid of this Account.

        The user's UUID.

        :param uuid: The uuid of this Account.
        :type uuid: str
        """

        self._uuid = uuid

    @property
    def username(self):
        """Get the username of this Account.

        The user's username.

        :return: The username of this Account.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """Set the username of this Account.

        The user's username.

        :param username: The username of this Account.
        :type username: str
        """

        self._username = username

    @property
    def first_name(self):
        """Get the first_name of this Account.

        The user's first name.

        :return: The first_name of this Account.
        :rtype: str
        """
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        """Set the first_name of this Account.

        The user's first name.

        :param first_name: The first_name of this Account.
        :type first_name: str
        """

        self._first_name = first_name

    @property
    def last_name(self):
        """Get the last_name of this Account.

        The user's last name.

        :return: The last_name of this Account.
        :rtype: str
        """
        return self._last_name

    @last_name.setter
    def last_name(self, last_name):
        """Set the last_name of this Account.

        The user's last name.

        :param last_name: The last_name of this Account.
        :type last_name: str
        """

        self._last_name = last_name

    @property
    def email(self):
        """Get the email of this Account.

        THe user's email address.

        :return: The email of this Account.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Set the email of this Account.

        THe user's email address.

        :param email: The email of this Account.
        :type email: str
        """

        self._email = email

    @property
    def default_project(self):
        """Get the default_project of this Account.


        :return: The default_project of this Account.
        :rtype: ProjectIdentity
        """
        return self._default_project

    @default_project.setter
    def default_project(self, default_project):
        """Set the default_project of this Account.


        :param default_project: The default_project of this Account.
        :type default_project: ProjectIdentity
        """

        self._default_project = default_project

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
        if not isinstance(other, Account):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Account):
            return True

        return self.to_dict() != other.to_dict()
