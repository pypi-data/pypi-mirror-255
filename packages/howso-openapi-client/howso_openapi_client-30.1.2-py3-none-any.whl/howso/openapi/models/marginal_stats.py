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


class MarginalStats(object):
    """
    Auto-generated OpenAPI type.

    Marginal feature statistics.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'count': 'float',
        'kurtosis': 'float',
        'mean': 'float',
        'mean_absdev': 'float',
        'median': 'float',
        'mode': 'object',
        'min': 'float',
        'max': 'float',
        'percentile_25': 'float',
        'percentile_75': 'float',
        'skew': 'float',
        'stddev': 'float',
        'uniques': 'float',
        'variance': 'float',
        'entropy': 'float'
    }

    attribute_map = {
        'count': 'count',
        'kurtosis': 'kurtosis',
        'mean': 'mean',
        'mean_absdev': 'mean_absdev',
        'median': 'median',
        'mode': 'mode',
        'min': 'min',
        'max': 'max',
        'percentile_25': 'percentile_25',
        'percentile_75': 'percentile_75',
        'skew': 'skew',
        'stddev': 'stddev',
        'uniques': 'uniques',
        'variance': 'variance',
        'entropy': 'entropy'
    }

    nullable_attributes = [
        'count', 
        'kurtosis', 
        'mean', 
        'mean_absdev', 
        'median', 
        'mode', 
        'min', 
        'max', 
        'percentile_25', 
        'percentile_75', 
        'skew', 
        'stddev', 
        'uniques', 
        'variance', 
        'entropy', 
    ]

    discriminator = None

    def __init__(self, count=None, kurtosis=None, mean=None, mean_absdev=None, median=None, mode=None, min=None, max=None, percentile_25=None, percentile_75=None, skew=None, stddev=None, uniques=None, variance=None, entropy=None, local_vars_configuration=None):  # noqa: E501
        """MarginalStats - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._count = None
        self._kurtosis = None
        self._mean = None
        self._mean_absdev = None
        self._median = None
        self._mode = None
        self._min = None
        self._max = None
        self._percentile_25 = None
        self._percentile_75 = None
        self._skew = None
        self._stddev = None
        self._uniques = None
        self._variance = None
        self._entropy = None

        self.count = count
        self.kurtosis = kurtosis
        self.mean = mean
        self.mean_absdev = mean_absdev
        self.median = median
        self.mode = mode
        self.min = min
        self.max = max
        self.percentile_25 = percentile_25
        self.percentile_75 = percentile_75
        self.skew = skew
        self.stddev = stddev
        self.uniques = uniques
        self.variance = variance
        self.entropy = entropy

    @property
    def count(self):
        """Get the count of this MarginalStats.


        :return: The count of this MarginalStats.
        :rtype: float
        """
        return self._count

    @count.setter
    def count(self, count):
        """Set the count of this MarginalStats.


        :param count: The count of this MarginalStats.
        :type count: float
        """

        self._count = count

    @property
    def kurtosis(self):
        """Get the kurtosis of this MarginalStats.


        :return: The kurtosis of this MarginalStats.
        :rtype: float
        """
        return self._kurtosis

    @kurtosis.setter
    def kurtosis(self, kurtosis):
        """Set the kurtosis of this MarginalStats.


        :param kurtosis: The kurtosis of this MarginalStats.
        :type kurtosis: float
        """

        self._kurtosis = kurtosis

    @property
    def mean(self):
        """Get the mean of this MarginalStats.


        :return: The mean of this MarginalStats.
        :rtype: float
        """
        return self._mean

    @mean.setter
    def mean(self, mean):
        """Set the mean of this MarginalStats.


        :param mean: The mean of this MarginalStats.
        :type mean: float
        """

        self._mean = mean

    @property
    def mean_absdev(self):
        """Get the mean_absdev of this MarginalStats.


        :return: The mean_absdev of this MarginalStats.
        :rtype: float
        """
        return self._mean_absdev

    @mean_absdev.setter
    def mean_absdev(self, mean_absdev):
        """Set the mean_absdev of this MarginalStats.


        :param mean_absdev: The mean_absdev of this MarginalStats.
        :type mean_absdev: float
        """

        self._mean_absdev = mean_absdev

    @property
    def median(self):
        """Get the median of this MarginalStats.


        :return: The median of this MarginalStats.
        :rtype: float
        """
        return self._median

    @median.setter
    def median(self, median):
        """Set the median of this MarginalStats.


        :param median: The median of this MarginalStats.
        :type median: float
        """

        self._median = median

    @property
    def mode(self):
        """Get the mode of this MarginalStats.


        :return: The mode of this MarginalStats.
        :rtype: object
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Set the mode of this MarginalStats.


        :param mode: The mode of this MarginalStats.
        :type mode: object
        """

        self._mode = mode

    @property
    def min(self):
        """Get the min of this MarginalStats.


        :return: The min of this MarginalStats.
        :rtype: float
        """
        return self._min

    @min.setter
    def min(self, min):
        """Set the min of this MarginalStats.


        :param min: The min of this MarginalStats.
        :type min: float
        """

        self._min = min

    @property
    def max(self):
        """Get the max of this MarginalStats.


        :return: The max of this MarginalStats.
        :rtype: float
        """
        return self._max

    @max.setter
    def max(self, max):
        """Set the max of this MarginalStats.


        :param max: The max of this MarginalStats.
        :type max: float
        """

        self._max = max

    @property
    def percentile_25(self):
        """Get the percentile_25 of this MarginalStats.


        :return: The percentile_25 of this MarginalStats.
        :rtype: float
        """
        return self._percentile_25

    @percentile_25.setter
    def percentile_25(self, percentile_25):
        """Set the percentile_25 of this MarginalStats.


        :param percentile_25: The percentile_25 of this MarginalStats.
        :type percentile_25: float
        """

        self._percentile_25 = percentile_25

    @property
    def percentile_75(self):
        """Get the percentile_75 of this MarginalStats.


        :return: The percentile_75 of this MarginalStats.
        :rtype: float
        """
        return self._percentile_75

    @percentile_75.setter
    def percentile_75(self, percentile_75):
        """Set the percentile_75 of this MarginalStats.


        :param percentile_75: The percentile_75 of this MarginalStats.
        :type percentile_75: float
        """

        self._percentile_75 = percentile_75

    @property
    def skew(self):
        """Get the skew of this MarginalStats.


        :return: The skew of this MarginalStats.
        :rtype: float
        """
        return self._skew

    @skew.setter
    def skew(self, skew):
        """Set the skew of this MarginalStats.


        :param skew: The skew of this MarginalStats.
        :type skew: float
        """

        self._skew = skew

    @property
    def stddev(self):
        """Get the stddev of this MarginalStats.


        :return: The stddev of this MarginalStats.
        :rtype: float
        """
        return self._stddev

    @stddev.setter
    def stddev(self, stddev):
        """Set the stddev of this MarginalStats.


        :param stddev: The stddev of this MarginalStats.
        :type stddev: float
        """

        self._stddev = stddev

    @property
    def uniques(self):
        """Get the uniques of this MarginalStats.


        :return: The uniques of this MarginalStats.
        :rtype: float
        """
        return self._uniques

    @uniques.setter
    def uniques(self, uniques):
        """Set the uniques of this MarginalStats.


        :param uniques: The uniques of this MarginalStats.
        :type uniques: float
        """

        self._uniques = uniques

    @property
    def variance(self):
        """Get the variance of this MarginalStats.


        :return: The variance of this MarginalStats.
        :rtype: float
        """
        return self._variance

    @variance.setter
    def variance(self, variance):
        """Set the variance of this MarginalStats.


        :param variance: The variance of this MarginalStats.
        :type variance: float
        """

        self._variance = variance

    @property
    def entropy(self):
        """Get the entropy of this MarginalStats.


        :return: The entropy of this MarginalStats.
        :rtype: float
        """
        return self._entropy

    @entropy.setter
    def entropy(self, entropy):
        """Set the entropy of this MarginalStats.


        :param entropy: The entropy of this MarginalStats.
        :type entropy: float
        """

        self._entropy = entropy

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
        if not isinstance(other, MarginalStats):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MarginalStats):
            return True

        return self.to_dict() != other.to_dict()
