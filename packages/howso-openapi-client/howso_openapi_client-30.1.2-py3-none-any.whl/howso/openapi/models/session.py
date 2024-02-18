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


class Session(object):
    """
    Auto-generated OpenAPI type.

    A model session.
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
        'user': 'AccountIdentity',
        'metadata': 'dict[str, object]',
        'created_date': 'datetime',
        'modified_date': 'datetime'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'user': 'user',
        'metadata': 'metadata',
        'created_date': 'created_date',
        'modified_date': 'modified_date'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, id=None, name=None, user=None, metadata=None, created_date=None, modified_date=None, local_vars_configuration=None):  # noqa: E501
        """Session - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._user = None
        self._metadata = None
        self._created_date = None
        self._modified_date = None

        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if user is not None:
            self.user = user
        if metadata is not None:
            self.metadata = metadata
        if created_date is not None:
            self.created_date = created_date
        if modified_date is not None:
            self.modified_date = modified_date

    @property
    def id(self):
        """Get the id of this Session.

        The session's unique identifier.

        :return: The id of this Session.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Set the id of this Session.

        The session's unique identifier.

        :param id: The id of this Session.
        :type id: str
        """

        self._id = id

    @property
    def name(self):
        """Get the name of this Session.

        The name given to the session.

        :return: The name of this Session.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set the name of this Session.

        The name given to the session.

        :param name: The name of this Session.
        :type name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 128):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `128`")  # noqa: E501

        self._name = name

    @property
    def user(self):
        """Get the user of this Session.


        :return: The user of this Session.
        :rtype: AccountIdentity
        """
        return self._user

    @user.setter
    def user(self, user):
        """Set the user of this Session.


        :param user: The user of this Session.
        :type user: AccountIdentity
        """

        self._user = user

    @property
    def metadata(self):
        """Get the metadata of this Session.

        Any key-value pair to store custom metadata for the session.

        :return: The metadata of this Session.
        :rtype: dict[str, object]
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Set the metadata of this Session.

        Any key-value pair to store custom metadata for the session.

        :param metadata: The metadata of this Session.
        :type metadata: dict[str, object]
        """

        self._metadata = metadata

    @property
    def created_date(self):
        """Get the created_date of this Session.

        The timestamp of when the session was issued.

        :return: The created_date of this Session.
        :rtype: datetime
        """
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        """Set the created_date of this Session.

        The timestamp of when the session was issued.

        :param created_date: The created_date of this Session.
        :type created_date: datetime
        """

        self._created_date = created_date

    @property
    def modified_date(self):
        """Get the modified_date of this Session.

        The timestamp of when the session was modified.

        :return: The modified_date of this Session.
        :rtype: datetime
        """
        return self._modified_date

    @modified_date.setter
    def modified_date(self, modified_date):
        """Set the modified_date of this Session.

        The timestamp of when the session was modified.

        :param modified_date: The modified_date of this Session.
        :type modified_date: datetime
        """

        self._modified_date = modified_date

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
        if not isinstance(other, Session):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Session):
            return True

        return self.to_dict() != other.to_dict()
