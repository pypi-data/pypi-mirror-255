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


class Trainee(object):
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
        'name': 'str',
        'features': 'dict[str, FeatureAttributes]',
        'default_context_features': 'list[str]',
        'default_action_features': 'list[str]',
        'persistence': 'str',
        'project_id': 'str',
        'id': 'str',
        'metadata': 'dict[str, object]'
    }

    attribute_map = {
        'name': 'name',
        'features': 'features',
        'default_context_features': 'default_context_features',
        'default_action_features': 'default_action_features',
        'persistence': 'persistence',
        'project_id': 'project_id',
        'id': 'id',
        'metadata': 'metadata'
    }

    nullable_attributes = [
        'name', 
    ]

    discriminator = None

    def __init__(self, name=None, features=None, default_context_features=None, default_action_features=None, persistence='allow', project_id=None, id=None, metadata=None, local_vars_configuration=None):  # noqa: E501
        """Trainee - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._features = None
        self._default_context_features = None
        self._default_action_features = None
        self._persistence = None
        self._project_id = None
        self._id = None
        self._metadata = None

        self.name = name
        if features is not None:
            self.features = features
        if default_context_features is not None:
            self.default_context_features = default_context_features
        if default_action_features is not None:
            self.default_action_features = default_action_features
        if persistence is not None:
            self.persistence = persistence
        if project_id is not None:
            self.project_id = project_id
        if id is not None:
            self.id = id
        if metadata is not None:
            self.metadata = metadata

    @property
    def name(self):
        """Get the name of this Trainee.


        :return: The name of this Trainee.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set the name of this Trainee.


        :param name: The name of this Trainee.
        :type name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 128):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `128`")  # noqa: E501

        self._name = name

    @property
    def features(self):
        """Get the features of this Trainee.


        :return: The features of this Trainee.
        :rtype: dict[str, FeatureAttributes]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Set the features of this Trainee.


        :param features: The features of this Trainee.
        :type features: dict[str, FeatureAttributes]
        """

        self._features = features

    @property
    def default_context_features(self):
        """Get the default_context_features of this Trainee.


        :return: The default_context_features of this Trainee.
        :rtype: list[str]
        """
        return self._default_context_features

    @default_context_features.setter
    def default_context_features(self, default_context_features):
        """Set the default_context_features of this Trainee.


        :param default_context_features: The default_context_features of this Trainee.
        :type default_context_features: list[str]
        """

        self._default_context_features = default_context_features

    @property
    def default_action_features(self):
        """Get the default_action_features of this Trainee.


        :return: The default_action_features of this Trainee.
        :rtype: list[str]
        """
        return self._default_action_features

    @default_action_features.setter
    def default_action_features(self, default_action_features):
        """Set the default_action_features of this Trainee.


        :param default_action_features: The default_action_features of this Trainee.
        :type default_action_features: list[str]
        """

        self._default_action_features = default_action_features

    @property
    def persistence(self):
        """Get the persistence of this Trainee.

        If allow, the trainee may be manually persisted and will be persisted automatically only when unloaded. If always, the trainee will be automatically persisted whenever it is updated. If never, the trainee will never be persisted and any requests to explicitly persist it will fail. 

        :return: The persistence of this Trainee.
        :rtype: str
        """
        return self._persistence

    @persistence.setter
    def persistence(self, persistence):
        """Set the persistence of this Trainee.

        If allow, the trainee may be manually persisted and will be persisted automatically only when unloaded. If always, the trainee will be automatically persisted whenever it is updated. If never, the trainee will never be persisted and any requests to explicitly persist it will fail. 

        :param persistence: The persistence of this Trainee.
        :type persistence: str
        """
        allowed_values = ["allow", "always", "never"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and persistence not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `persistence` ({0}), must be one of {1}"  # noqa: E501
                .format(persistence, allowed_values)
            )

        self._persistence = persistence

    @property
    def project_id(self):
        """Get the project_id of this Trainee.


        :return: The project_id of this Trainee.
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Set the project_id of this Trainee.


        :param project_id: The project_id of this Trainee.
        :type project_id: str
        """

        self._project_id = project_id

    @property
    def id(self):
        """Get the id of this Trainee.


        :return: The id of this Trainee.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Set the id of this Trainee.


        :param id: The id of this Trainee.
        :type id: str
        """

        self._id = id

    @property
    def metadata(self):
        """Get the metadata of this Trainee.

        Metadata for a trainee. User can specify any key-value pair to store custom metadata for a trainee. 

        :return: The metadata of this Trainee.
        :rtype: dict[str, object]
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Set the metadata of this Trainee.

        Metadata for a trainee. User can specify any key-value pair to store custom metadata for a trainee. 

        :param metadata: The metadata of this Trainee.
        :type metadata: dict[str, object]
        """

        self._metadata = metadata

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
        if not isinstance(other, Trainee):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Trainee):
            return True

        return self.to_dict() != other.to_dict()
