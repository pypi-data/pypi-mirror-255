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


class Error(object):
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
        'status': 'int',
        'title': 'str',
        'detail': 'str',
        'code': 'str',
        'type': 'str'
    }

    attribute_map = {
        'status': 'status',
        'title': 'title',
        'detail': 'detail',
        'code': 'code',
        'type': 'type'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, status=None, title=None, detail=None, code=None, type=None, local_vars_configuration=None):  # noqa: E501
        """Error - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._status = None
        self._title = None
        self._detail = None
        self._code = None
        self._type = None

        if status is not None:
            self.status = status
        if title is not None:
            self.title = title
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code
        if type is not None:
            self.type = type

    @property
    def status(self):
        """Get the status of this Error.


        :return: The status of this Error.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Set the status of this Error.


        :param status: The status of this Error.
        :type status: int
        """

        self._status = status

    @property
    def title(self):
        """Get the title of this Error.


        :return: The title of this Error.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Set the title of this Error.


        :param title: The title of this Error.
        :type title: str
        """

        self._title = title

    @property
    def detail(self):
        """Get the detail of this Error.


        :return: The detail of this Error.
        :rtype: str
        """
        return self._detail

    @detail.setter
    def detail(self, detail):
        """Set the detail of this Error.


        :param detail: The detail of this Error.
        :type detail: str
        """

        self._detail = detail

    @property
    def code(self):
        """Get the code of this Error.


        :return: The code of this Error.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Set the code of this Error.


        :param code: The code of this Error.
        :type code: str
        """

        self._code = code

    @property
    def type(self):
        """Get the type of this Error.


        :return: The type of this Error.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Set the type of this Error.


        :param type: The type of this Error.
        :type type: str
        """

        self._type = type

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
        if not isinstance(other, Error):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Error):
            return True

        return self.to_dict() != other.to_dict()
