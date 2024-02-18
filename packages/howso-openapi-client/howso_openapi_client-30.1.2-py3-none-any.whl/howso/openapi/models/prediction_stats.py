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


class PredictionStats(object):
    """
    Auto-generated OpenAPI type.

    Prediction feature statistics.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'accuracy': 'float',
        'confusion_matrix': 'dict[str, dict[str, float]]',
        'contribution': 'float',
        'mae': 'float',
        'mda': 'float',
        'mda_permutation': 'float',
        'precision': 'float',
        'r2': 'float',
        'recall': 'float',
        'rmse': 'float',
        'spearman_coeff': 'float'
    }

    attribute_map = {
        'accuracy': 'accuracy',
        'confusion_matrix': 'confusion_matrix',
        'contribution': 'contribution',
        'mae': 'mae',
        'mda': 'mda',
        'mda_permutation': 'mda_permutation',
        'precision': 'precision',
        'r2': 'r2',
        'recall': 'recall',
        'rmse': 'rmse',
        'spearman_coeff': 'spearman_coeff'
    }

    nullable_attributes = [
        'accuracy', 
        'confusion_matrix', 
        'contribution', 
        'mae', 
        'mda', 
        'mda_permutation', 
        'precision', 
        'r2', 
        'recall', 
        'rmse', 
        'spearman_coeff', 
    ]

    discriminator = None

    def __init__(self, accuracy=None, confusion_matrix=None, contribution=None, mae=None, mda=None, mda_permutation=None, precision=None, r2=None, recall=None, rmse=None, spearman_coeff=None, local_vars_configuration=None):  # noqa: E501
        """PredictionStats - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._accuracy = None
        self._confusion_matrix = None
        self._contribution = None
        self._mae = None
        self._mda = None
        self._mda_permutation = None
        self._precision = None
        self._r2 = None
        self._recall = None
        self._rmse = None
        self._spearman_coeff = None

        self.accuracy = accuracy
        self.confusion_matrix = confusion_matrix
        self.contribution = contribution
        self.mae = mae
        self.mda = mda
        self.mda_permutation = mda_permutation
        self.precision = precision
        self.r2 = r2
        self.recall = recall
        self.rmse = rmse
        self.spearman_coeff = spearman_coeff

    @property
    def accuracy(self):
        """Get the accuracy of this PredictionStats.

        The accuracy (1 - mean absolute error) value. Applicable only for nominal features, computed by computing residuals. 

        :return: The accuracy of this PredictionStats.
        :rtype: float
        """
        return self._accuracy

    @accuracy.setter
    def accuracy(self, accuracy):
        """Set the accuracy of this PredictionStats.

        The accuracy (1 - mean absolute error) value. Applicable only for nominal features, computed by computing residuals. 

        :param accuracy: The accuracy of this PredictionStats.
        :type accuracy: float
        """

        self._accuracy = accuracy

    @property
    def confusion_matrix(self):
        """Get the confusion_matrix of this PredictionStats.

        The sparse confusion matrix for the predicted values of an action feature. 

        :return: The confusion_matrix of this PredictionStats.
        :rtype: dict[str, dict[str, float]]
        """
        return self._confusion_matrix

    @confusion_matrix.setter
    def confusion_matrix(self, confusion_matrix):
        """Set the confusion_matrix of this PredictionStats.

        The sparse confusion matrix for the predicted values of an action feature. 

        :param confusion_matrix: The confusion_matrix of this PredictionStats.
        :type confusion_matrix: dict[str, dict[str, float]]
        """

        self._confusion_matrix = confusion_matrix

    @property
    def contribution(self):
        """Get the contribution of this PredictionStats.

        The contribution to the predicted value of an action feature. 

        :return: The contribution of this PredictionStats.
        :rtype: float
        """
        return self._contribution

    @contribution.setter
    def contribution(self, contribution):
        """Set the contribution of this PredictionStats.

        The contribution to the predicted value of an action feature. 

        :param contribution: The contribution of this PredictionStats.
        :type contribution: float
        """

        self._contribution = contribution

    @property
    def mae(self):
        """Get the mae of this PredictionStats.

        The mean absolute error value. 

        :return: The mae of this PredictionStats.
        :rtype: float
        """
        return self._mae

    @mae.setter
    def mae(self, mae):
        """Set the mae of this PredictionStats.

        The mean absolute error value. 

        :param mae: The mae of this PredictionStats.
        :type mae: float
        """

        self._mae = mae

    @property
    def mda(self):
        """Get the mda of this PredictionStats.

        The mean decrease in accuracy value. Computed by dropping each feature and use the full set of remaining context features for each prediction. 

        :return: The mda of this PredictionStats.
        :rtype: float
        """
        return self._mda

    @mda.setter
    def mda(self, mda):
        """Set the mda of this PredictionStats.

        The mean decrease in accuracy value. Computed by dropping each feature and use the full set of remaining context features for each prediction. 

        :param mda: The mda of this PredictionStats.
        :type mda: float
        """

        self._mda = mda

    @property
    def mda_permutation(self):
        """Get the mda_permutation of this PredictionStats.

        The mean decrease in accuracy permutation value. Computed by scrambling each feature and using the full set of remaining context features for each prediction. 

        :return: The mda_permutation of this PredictionStats.
        :rtype: float
        """
        return self._mda_permutation

    @mda_permutation.setter
    def mda_permutation(self, mda_permutation):
        """Set the mda_permutation of this PredictionStats.

        The mean decrease in accuracy permutation value. Computed by scrambling each feature and using the full set of remaining context features for each prediction. 

        :param mda_permutation: The mda_permutation of this PredictionStats.
        :type mda_permutation: float
        """

        self._mda_permutation = mda_permutation

    @property
    def precision(self):
        """Get the precision of this PredictionStats.

        The precision (positive predictive) value. Applicable only for nominal features, computed by computing residuals. 

        :return: The precision of this PredictionStats.
        :rtype: float
        """
        return self._precision

    @precision.setter
    def precision(self, precision):
        """Set the precision of this PredictionStats.

        The precision (positive predictive) value. Applicable only for nominal features, computed by computing residuals. 

        :param precision: The precision of this PredictionStats.
        :type precision: float
        """

        self._precision = precision

    @property
    def r2(self):
        """Get the r2 of this PredictionStats.

        The R-squared (coefficient of determination) value. Applicable only for continuous features, computed by computing residuals. 

        :return: The r2 of this PredictionStats.
        :rtype: float
        """
        return self._r2

    @r2.setter
    def r2(self, r2):
        """Set the r2 of this PredictionStats.

        The R-squared (coefficient of determination) value. Applicable only for continuous features, computed by computing residuals. 

        :param r2: The r2 of this PredictionStats.
        :type r2: float
        """

        self._r2 = r2

    @property
    def recall(self):
        """Get the recall of this PredictionStats.

        The recall (sensitivity) value. Applicable only for nominal features, computed by computing residuals. 

        :return: The recall of this PredictionStats.
        :rtype: float
        """
        return self._recall

    @recall.setter
    def recall(self, recall):
        """Set the recall of this PredictionStats.

        The recall (sensitivity) value. Applicable only for nominal features, computed by computing residuals. 

        :param recall: The recall of this PredictionStats.
        :type recall: float
        """

        self._recall = recall

    @property
    def rmse(self):
        """Get the rmse of this PredictionStats.

        The root-mean-squared-error value. Applicable only for continuous features, computed by computing residuals. 

        :return: The rmse of this PredictionStats.
        :rtype: float
        """
        return self._rmse

    @rmse.setter
    def rmse(self, rmse):
        """Set the rmse of this PredictionStats.

        The root-mean-squared-error value. Applicable only for continuous features, computed by computing residuals. 

        :param rmse: The rmse of this PredictionStats.
        :type rmse: float
        """

        self._rmse = rmse

    @property
    def spearman_coeff(self):
        """Get the spearman_coeff of this PredictionStats.

        The Spearman's rank correlation coefficient value. Applicable only for continuous features, computed by computing residuals. 

        :return: The spearman_coeff of this PredictionStats.
        :rtype: float
        """
        return self._spearman_coeff

    @spearman_coeff.setter
    def spearman_coeff(self, spearman_coeff):
        """Set the spearman_coeff of this PredictionStats.

        The Spearman's rank correlation coefficient value. Applicable only for continuous features, computed by computing residuals. 

        :param spearman_coeff: The spearman_coeff of this PredictionStats.
        :type spearman_coeff: float
        """

        self._spearman_coeff = spearman_coeff

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
        if not isinstance(other, PredictionStats):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PredictionStats):
            return True

        return self.to_dict() != other.to_dict()
