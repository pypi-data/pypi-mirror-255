import inspect
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from ds_capability.components.discovery import DataDiscovery
from scipy.stats import stats

from ds_capability.components.commons import Commons
from ds_capability.intent.common_intent import CommonsIntentModel
from ds_capability.intent.abstract_feature_transform_intent import AbstractFeatureTransformIntentModel


class FeatureTransformIntent(AbstractFeatureTransformIntentModel, CommonsIntentModel):
    """This class represents feature transformation intent actions whereby features are converted
    from one format or structure to another. This includes, scaling and activation trigger
    algorithms.
    """

    def activate_sigmoid(self, canonical: pa.Table, header: str, precision: int=None, seed: int=None,
                         save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                         replace_intent: bool=None, remove_duplicates: bool=None):
        """Activation functions play a crucial role in the backpropagation algorithm, which is the primary
        algorithm used for training neural networks. During backpropagation, the error of the output is
        propagated backwards through the network, and the weights of the network are updated based on this
        error. The activation function is used to introduce non-linearity into the output of a neural network
        layer.

        Logistic Sigmoid a.k.a logit, tmaps any input value to a value between 0 and 1, making it useful for
        binary classification problems and is defined as f(x) = 1/(1+exp(-x))

        The sigmoid function has an S-shaped curve, and it asymptotically approaches 0 as z approaches
        negative infinity and approaches 1 as z approaches positive infinity. This property makes it
        useful for binary classification problems, where the goal is to classify inputs into one of
        two categories.

        :param canonical: a pa.Table as the reference dataframe
        :param header: the header in the Table to correlate
        :param precision: (optional) how many decimal places. default to 3
        :param seed: (optional) the random seed. defaults to current datetime
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        if not isinstance(header, str) or header not in canonical.column_names:
            raise ValueError(f"The header '{header}' can't be found in the canonical table")
        if canonical.column(header).null_count > 0:
            raise ValueError(f"The values in '{header}' can not contain nulls")
        _seed = seed if isinstance(seed, int) else self._seed()
        precision = precision if isinstance(precision, int) else 5
        npv = canonical.column(header).to_numpy()
        arr = pa.array(np.round(1 / (1 + np.exp(-npv)), precision))
        return Commons.table_append(canonical, pa.table([arr], names=[header]))

    def activate_tanh(self, canonical: pa.Table, header: str, precision: int=None, seed: int=None,
                      save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                      replace_intent: bool=None, remove_duplicates: bool=None):
        """Activation functions play a crucial role in the backpropagation algorithm, which is the primary
        algorithm used for training neural networks. During backpropagation, the error of the output is
        propagated backwards through the network, and the weights of the network are updated based on this
        error. The activation function is used to introduce non-linearity into the output of a neural network
        layer.

        Tangent Hyperbolic (tanh) function is a shifted and stretched version of the Sigmoid function but maps
        the input values to a range between -1 and 1. and is defined as f(x) = (exp(x)-exp(-x))/(exp(x)+exp(-x))

        Similar to the logistic sigmoid function, the hyperbolic tangent function has an S-shaped curve,
        but it maps its input to values between -1 and 1. This function is advantageous because it has
        desirable properties, such as being zero-centered (meaning that the average of its output is
        close to zero), which can help with the convergence of optimization algorithms during training.

        :param canonical: a pa.Table as the reference dataframe
        :param header: the header in the Table to correlate
        :param precision: (optional) how many decimal places. default to 3
        :param seed: (optional) the random seed. defaults to current datetime
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        if not isinstance(header, str) or header not in canonical.column_names:
            raise ValueError(f"The header '{header}' can't be found in the canonical table")
        if canonical.column(header).null_count > 0:
            raise ValueError(f"The values in '{header}' can not contain nulls")
        _seed = seed if isinstance(seed, int) else self._seed()
        precision = precision if isinstance(precision, int) else 5
        npv = canonical.column(header).to_numpy()
        arr = pa.array(np.round((np.exp(npv) - np.exp(-npv)) / (np.exp(npv) + np.exp(-npv)), precision))
        return Commons.table_append(canonical, pa.table([arr], names=[header]))

    def activate_relu(self, canonical: pa.Table, header: str, precision: int=None, seed: int=None,
                      save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                      replace_intent: bool=None, remove_duplicates: bool=None):
        """Activation functions play a crucial role in the backpropagation algorithm, which is the primary
        algorithm used for training neural networks. During backpropagation, the error of the output is
        propagated backwards through the network, and the weights of the network are updated based on this
        error. The activation function is used to introduce non-linearity into the output of a neural network
        layer.

        Rectified Linear Unit (ReLU) function. is the most popular activation function, which replaces negative
        values with zero and keeps the positive values unchanged. and is defined as f(x) = x * (x > 0)

        :param canonical: a pa.Table as the reference dataframe
        :param header: the header in the Table to correlate
        :param precision: (optional) how many decimal places. default to 3
        :param seed: (optional) the random seed. defaults to current datetime
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        if not isinstance(header, str) or header not in canonical.column_names:
            raise ValueError(f"The header '{header}' can't be found in the canonical table")
        if canonical.column(header).null_count > 0:
            raise ValueError(f"The values in '{header}' can not contain nulls")
        _seed = seed if isinstance(seed, int) else self._seed()
        precision = precision if isinstance(precision, int) else 5
        npv = canonical.column(header).to_numpy()
        arr = pa.array(np.round(npv * (npv > 0), precision))
        return Commons.table_append(canonical, pa.table([arr], names=[header]))

    def encode_date_integer(self, canonical: pa.Table, headers: [str, list]=None, prefix=None, day_first: bool=None,
                            year_first: bool=None, seed: int=None, save_intent: bool=None,
                            intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                            remove_duplicates: bool=None):
        """ date encoding to integer replaces dates for integer values.

        :param canonical: pyarrow Table
        :param headers: the header(s) to apply encoding too
        :param prefix: (optional) a str to prefix the column
        :param day_first: (optional) if the dates given are day first format. Default to True
        :param year_first: (optional) if the dates given are year first. Default to False
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        prefix = prefix if isinstance(prefix, str) else ''
        headers = Commons.list_formatter(headers) if isinstance(headers,(str, list)) else canonical.column_names
        _ = self._seed() if seed is None else seed
        tbl = None
        for n in headers:
            c = canonical.column(n).combine_chunks()
            if not (pa.types.is_timestamp(c.type) or pa.types.is_time(c.type)):
                continue
            column = pa.array(Commons.date2value(c.to_pylist()), pa.int64())
            new_header = f"{prefix}{n}"
            tbl = Commons.table_append(tbl, pa.table([column], names=[new_header]))
        if not tbl:
            return canonical
        return Commons.table_append(canonical, tbl)

    def encode_category_integer(self, canonical: pa.Table, headers: [str, list]=None, ordinal: bool=None,
                                label_count: int=None, prefix=None, seed: int=None, save_intent: bool=None,
                                intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                                remove_duplicates: bool=None):
        """ Integer encoding replaces the categories by digits from 1 to n, where n is the number of distinct
        categories of the variable. Integer encoding can be either nominal or ordinal.

        Nominal data is categorical variables without any particular order between categories. This means that
        the categories cannot be sorted and there is no natural order between them.

        Ordinal data represents categories with a natural, ordered relationship between each category. This means
        that the categories can be sorted in either ascending or descending order. In order to encode integers as
        ordinal, a ranking must be provided.

        If ranking is given, the return will be ordinal values based on the ranking order of the list. If a
        categorical value is not found in the list it is grouped with other missing values and given the last
        ranking. This is known as rare-label encoding.

        :param canonical: pyarrow Table
        :param headers: the header(s) to apply encoding too
        :param ordinal: (optional) if the integer encoder is ordinal
        :param label_count: (optional) if the ordinal is rare-label, the number of categories to rank
        :param prefix: (optional) a str to prefix the column
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        prefix = prefix if isinstance(prefix, str) else ''
        headers = Commons.list_formatter(headers) if isinstance(headers, (str, list)) else canonical.column_names
        _ = self._seed() if seed is None else seed
        tbl = None
        for header in headers:
            column = canonical.column(header).combine_chunks()
            if isinstance(label_count, int): # rare-label
                if not pa.types.is_dictionary(column.type):
                    column = column.dictionary_encode()
                full_rank = column.dictionary.sort().to_pylist()
                rank = full_rank[:label_count]
                missing = full_rank[label_count:]
                values = list(range(len(rank)))
                values = values + ([len(rank)] * (len(full_rank) - len(rank)))
                mapper = dict(zip(full_rank, values))
                s_column = column.to_pandas()
                column =  pa.Array.from_pandas(s_column.replace(mapper))
            elif isinstance(ordinal, bool) and ordinal: # ordinal
                if not pa.types.is_dictionary(column.type):
                    column = column.dictionary_encode()
                rank = column.dictionary.sort().to_pylist()
                values = list(range(len(rank)))
                mapper = dict(zip(rank, values))
                s_column = column.to_pandas()
                column = pa.Array.from_pandas(s_column.replace(mapper))
            else: # nominal
                if not pa.types.is_dictionary(column.type):
                    column = column.dictionary_encode()
                column = pa.array(column.indices, pa.int64())
            if pa.types.is_dictionary(column.type):
                column = column.dictionary_decode()
            new_header = f"{prefix}{header}"
            tbl = Commons.table_append(tbl, pa.table([column], names=[new_header]))
        if not tbl:
            return canonical
        return Commons.table_append(canonical, tbl)

    def encode_category_one_hot(self, canonical: pa.Table, headers: [str, list]=None, prefix=None, data_type: pa.Table=None,
                                prefix_sep: str=None, dummy_na: bool = False, drop_first: bool = False, seed: int=None,
                                save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                                replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ encodes categorical data types, One hot encoding, consists in encoding each categorical variable with
        different boolean variables (also called dummy variables) which take values 0 or 1, indicating if a category
        is present in an observation.

        :param canonical: pyarrow Table
        :param headers: the header(s) to apply encoding too
        :param prefix: str, list of str, or dict of str, String to append Table intent levels, with equal length.
        :param prefix_sep: str separator, default '_'
        :param dummy_na: Add a column to indicate null values, if False nullss are ignored.
        :param drop_first:  Whether to get k-1 dummies out of k categorical levels by removing the first level.
        :param data_type: Data type for new columns. Only a single dtype is allowed.
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        headers = Commons.list_formatter(headers) if isinstance(headers, (str, list)) else canonical.column_names
        _ = self._seed() if seed is None else seed
        prefix_sep = prefix_sep if isinstance(prefix_sep, str) else "_"
        dummy_na = dummy_na if isinstance(dummy_na, bool) else False
        drop_first = drop_first if isinstance(drop_first, bool) else False
        d_type = data_type if data_type else pa.int64()
        dummies = pd.get_dummies(canonical.to_pandas(), columns=headers, prefix=prefix, prefix_sep=prefix_sep,
                              dummy_na=dummy_na, drop_first=drop_first, dtype=data_type)
        return pa.Table.from_pandas(dummies)

    def scale_normalize(self, canonical: pa.Table, headers: [str, list]=None, scalar: [tuple, str]=None,
                        prefix: str=None, precision: int=None, seed: int=None, save_intent: bool=None,
                        intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                        remove_duplicates: bool=None):
        """ Normalization of continuous data using either Min-Max Scaling or Robust Scaling, dependent on the
        scalar passed.

        Min-Max Scaling: scales the data such that it falls within a specified range, typically (0,1) as default if
        no value is passed, or (min, max) tuple. This method is suitable when your data should be uniformly
        distributed across the specified range.

        Robust Scaling: Robust scaling is similar to min-max scaling but is less sensitive to outliers. It uses
        the interquartile range (0.25, 0.75) to scale the data. This is used if the scalar equals 'robust'.
        Robust scaling is particularly useful when your dataset contains outliers or when the underlying data
        distribution is not necessarily Gaussian.

        :param canonical: pyarrow Table
        :param headers: the header(s) to apply scaling too
        :param scalar: (optional) a tuple scalar representing min and max values or 'robust' for interquartile scaling
        :param prefix: (optional) a str prefix for generated headers
        :param precision: (optional) how many decimal places. default to 3
        :param seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        headers = Commons.list_formatter(headers) if isinstance(headers, (str, list)) else canonical.column_names
        _seed = seed if isinstance(seed, int) else self._seed()
        scalar = scalar if isinstance(scalar, (tuple, str)) else (0, 1)
        tbl = None
        for n in headers:
            c = canonical.column(n).combine_chunks()
            if not (pa.types.is_floating(c.type) or pa.types.is_integer(c.type)):
                continue
            precision = precision if isinstance(precision, int) else Commons.column_precision(c)+2
            s_values = c.to_pandas()
            null_idx = s_values[s_values.isna()].index
            s_values = s_values.fillna(0)
            if isinstance(scalar, str) and scalar == 'robust':
                if s_values.max() == s_values.min():
                    s_values = pd.Series([0.5] * canonical.num_rows)
                else:
                    s_values = pd.Series(Commons.list_normalize_robust(s_values.to_list(), precision))
            elif s_values.max() == s_values.min():
                s_values = pd.Series([np.mean([scalar[0], scalar[1]])] * canonical.num_rows)
            else:
                if scalar[0] >= scalar[1] or len(scalar) != 2:
                    scalar = (0,1)
                s_values = pd.Series(Commons.list_normalize(s_values.to_list(), scalar[0], scalar[1]))
            s_values = s_values.round(precision)
            if null_idx.size > 0:
                s_values.iloc[null_idx] = np.nan
            new_header = f"{prefix}{n}"
            tbl = Commons.table_append(tbl, pa.table([s_values], names=[n]))
        if not tbl:
            return canonical
        return Commons.table_append(canonical, tbl)

    def scale_standardize(self, canonical: pa.Table, headers: [str, list]=None, prefix: str=None, precision: int=None,
                          seed: int=None, save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                          replace_intent: bool=None, remove_duplicates: bool=None):
        """ Z-Score Standardization (Standard Scaling). This method transforms the data to have a mean of 0
        and a standard deviation of 1. It's particularly useful when your data follows a Gaussian (normal)
        distribution. This transformation makes it easier to compare and work with features that may have
        different scales and ensures that they contribute equally to model training.

        :param canonical: pyarrow Table
        :param headers: the header(s) to apply scaling too
        :param prefix: (optional) a str prefix for generated headers
        :param precision: (optional) how many decimal places. default to 3
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        headers = Commons.list_formatter(headers) if isinstance(headers, (str, list)) else canonical.column_names
        _seed = seed if isinstance(seed, int) else self._seed()
        tbl = None
        for n in headers:
            c = canonical.column(n).combine_chunks()
            if not (pa.types.is_floating(c.type) or pa.types.is_integer(c.type)):
                continue
            precision = precision if isinstance(precision, int) else Commons.column_precision(c)+2
            s_values = c.to_pandas()
            null_idx = s_values[s_values.isna()].index
            s_values = s_values.fillna(0)
            s_values = pd.Series(Commons.list_standardize(s_values.to_list()))
            s_values = s_values.round(precision)
            if null_idx.size > 0:
                s_values.iloc[null_idx] = np.nan
            new_header = f"{prefix}{n}"
            tbl = Commons.table_append(tbl, pa.table([s_values], names=[n]))
        if not tbl:
            return canonical
        return Commons.table_append(canonical, tbl)

    def scale_transform(self, canonical: pa.Table, transform: str, headers: [str, list]=None, prefix: str=None,
                        precision: int=None, seed: int=None, save_intent: bool=None, intent_level: [int, str]=None,
                        intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None):
        """ Log, sqrt (square root), cbrt (cube root), Box-Cox, and Yeo-Johnson transformations. These are techniques
        used to modify the distribution or scale of continuous data to make the data conform more closely to a
        normal distribution or to stabilize the variance.

        Log Transformation (log): The log transformation involves taking the natural logarithm of each data point.
        It is particularly useful when dealing with data that follows an exponential distribution or has a
        right-skewed distribution. The log transformation can help make the data more symmetric and stabilize
        the variance.

        Square Root Transformation (sqrt): The square root transformation involves taking the square root of
        each data point. It is often used when dealing with count data or data with a right-skewed distribution.
        Like the log transformation, the square root transformation can make the data more symmetric and stabilize
        the variance.

        Cube Root Transformation (cbrt): The cube root transformation involves taking the cube root of each
        data point. It is another option for stabilizing variance and making data less skewed, especially when
        dealing with positive data with right-skewed distributions.

        Box-Cox Transformation: The Box-Cox transformation is a family of power transformations that includes
        both the log and square root transformations as special cases. Can only work with positive values

        Yeo-Johnson Transformation: The Yeo-Johnson transformation is an extension of the Box-Cox transformation
        that allows for the transformation of data with both positive and negative values.

        These transformations are often applied to address issues like non-normality, heteroscedasticity (unequal variance),
        and skewed distributions in the data.

        :param canonical: pyarrow Table
        :param headers: the header(s) to apply scaling to
        :param transform: transform function, 'log', 'sqrt', 'cbrt', 'boxcox' or 'yeojohnson'
        :param prefix: (optional) a str prefix for generated headers
        :param precision: (optional) how many decimal places. default to 3
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        headers = Commons.list_formatter(headers) if isinstance(headers, (str, list)) else canonical.column_names
        _seed = seed if isinstance(seed, int) else self._seed()
        tbl = None
        for n in headers:
            c = canonical.column(n).combine_chunks()
            if not (pa.types.is_floating(c.type) or pa.types.is_integer(c.type)):
                continue
            precision = precision if isinstance(precision, int) else Commons.column_precision(c)+2
            s_values = c.to_pandas()
            null_idx = s_values[s_values.isna()].index
            s_values = s_values.fillna(0)
            if transform == 'log':
                s_values = np.log(s_values)
            elif transform == 'sqrt':
                s_values = np.sqrt(s_values)
            elif transform == 'cbrt':
                s_values = np.cbrt(s_values)
            elif transform == 'boxcox' or transform.startswith('box'):
                bc, _ = stats.boxcox(s_values.to_numpy())
                s_values = pd.Series(bc)
            elif transform == 'yeojohnson' or transform.startswith("yeo"):
                yj, _ = stats.yeojohnson(s_values.to_numpy())
                s_values = pd.Series(yj)
            else:
                raise ValueError(f"The transformer {transform} is not recognized. See contacts notes for reference")
            s_values = s_values.round(precision)
            if null_idx.size > 0:
                s_values.iloc[null_idx] = np.nan
            new_header = f"{prefix}{n}"
            tbl = Commons.table_append(tbl, pa.table([s_values], names=[n]))
        if not tbl:
            return canonical
        return Commons.table_append(canonical, tbl)

    def scale_mapping(self, canonical: pa.Table, numerator: str, denominator: str, prefix: str=None,
                      precision: int=None, to_header: str=None, seed: int=None, save_intent: bool=None,
                      intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                      remove_duplicates: bool=None):
        """ Scales a numeric column against another numeric column providing mapped standardisation.
        An example might be a churn problem for a bank with the hypothesis that older customers are
        more like to stay. Therefore, scaling 'Tenure' against 'age' gives us a mapped scalar of
        the hypothesis.

        :param canonical: pyarrow Table
        :param numerator: the column name of the numerator
        :param denominator:  the column name of the denominator
        :param prefix: (optional) a str prefix for generated headers
        :param precision: (optional) how many decimal places. default to 3
        :param to_header: (optional) an optional name to call the column
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        _seed = seed if isinstance(seed, int) else self._seed()
        a = canonical.column(numerator).cast(pa.float64())
        b = canonical.column(denominator)
        precision = precision if isinstance(precision, int) else Commons.column_precision(a) + 3
        arr = pc.round(pc.divide(a, b), precision)
        arr = pc.if_else(pc.equal(arr, np.inf), 0, arr)
        to_header = to_header if isinstance(to_header, str) else numerator
        if to_header == numerator:
            canonical = canonical.drop_columns([numerator, denominator])
        return Commons.table_append(canonical, pa.table([arr], names=[to_header]))

    def discrete_intervals(self, canonical: pa.Table, header: str, interval: [int, list]=None, categories: list=None,
                           to_header: str=None, precision: int=None, duplicates: str=None, seed: int=None,
                           save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                           replace_intent: bool=None, remove_duplicates: bool=None):
        """ Converts continuous values into discrete values through interval categorisation based on
        quantile discretization. Intervals can be either a single value representing the number of
        quantiles or an ordered list of quantiles between 0 and 1, e.g. [0, .25, .5, .75, 1.]

        If intervals are not unique duplicates provide a strategy to 'raise' a ValueError, 'drop'
        duplicate bins or 'rank' values from 1 to n before binning. Ranking might be used for sparse
        date with predominant zeros as an example.

        :param canonical: a pa.Table as the reference table
        :param header: the header in the Table to correlate
        :param interval: (optional) the granularity of the analysis across the range. Default is 3
                int passed - represents the number of periods
                list[int] - specific interval periods e.g []

        :param to_header: (optional) an optional name to call the column
        :param precision: (optional) The precision of the range and boundary values. by default set to 5.
        :param categories: (optional) a set of labels the same length as the intervals to name the categories
        :param duplicates: (optional) If intervals are not unique, 'raise' ValueError, 'drop' intervals or 'rank' values
        :param seed: (optional) the random seed. defaults to current datetime
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: an equal length list of correlated values
        """
        self._set_intend_signature( self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                    intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                    remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        header = self._extract_value(header)
        to_header = self._extract_value(to_header)
        if not isinstance(header, str) or header not in canonical.column_names:
            raise ValueError(f"The header '{header}' can't be found in the canonical headers")
        interval = interval if isinstance(interval, (int, list)) else 5
        n = interval if isinstance(interval, int) else len(interval)
        categories = categories if isinstance(categories, list) else range(1, n+1) if isinstance(interval, int) else range(1, n)
        precision = precision if isinstance(precision, int) else 3
        duplicates = duplicates if isinstance(duplicates, str) and duplicates in ['drop', 'rank'] else 'raise'
        seed = seed if isinstance(seed, int) else self._seed()
        c = canonical.column(header).combine_chunks()
        if not (pa.types.is_floating(c.type) or pa.types.is_integer(c.type)):
            raise ValueError(f"The header '{header}' value type must be numerical, '{c.type}' was passed")
        s = c.to_pandas()
        if duplicates == 'rank':
            s = s.rank(method="first")
            duplicates = 'raise'
        s = pd.cut(s, interval, labels=categories, precision=precision, duplicates=duplicates)
        c = pa.Array.from_pandas(s)
        if pa.types.is_dictionary(c.type):
            c = c.dictionary_decode()
        to_header = to_header if isinstance(to_header, str) else header
        return Commons.table_append(canonical, pa.table([c], names=[to_header]))

    def discrete_quantiles(self, canonical: pa.Table, header: str, interval: [int, list]=None, categories: list=None,
                           to_header: str=None, precision: int=None, duplicates: str=None, seed: int=None,
                           save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                           replace_intent: bool=None, remove_duplicates: bool=None):
        """ Converts continuous values into discrete values through interval categorisation based on
        interval bins. Intervals can be either a single value number of bins or a list of bin edges
        allowing for non-uniform width.

        If intervals are not unique duplicates provide a strategy to 'raise' a ValueError, 'drop'
        duplicate bins or 'rank' values from 1 to n before binning. Ranking might be used for sparse
        date with predominant zeros as an example.

        :param canonical: a pa.Table as the reference table
        :param header: the header in the Table to correlate
        :param interval: (optional) the granularity of the analysis across the range. Default is 3
                int passed - represents the number of periods
                list[float] - the percentile or quantities, All should fall between 0 and 1

        :param to_header: (optional) an optional name to call the column
        :param precision: (optional) The precision of the range and boundary values. by default set to 5.
        :param categories: (optional)  a set of labels the same length as the intervals to name the categories
        :param duplicates: (optional) If intervals are not unique, 'raise' ValueError, 'drop' intervals or 'rank' values
        :param seed: (optional) the random seed. defaults to current datetime
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: an equal length list of correlated values
        """
        self._set_intend_signature( self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                    intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                    remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        header = self._extract_value(header)
        to_header = self._extract_value(to_header)
        if not isinstance(header, str) or header not in canonical.column_names:
            raise ValueError(f"The header '{header}' can't be found in the canonical headers")
        interval = interval if isinstance(interval, (int, list)) else 4
        n = interval if isinstance(interval, int) else len(interval)
        categories = categories if isinstance(categories, list) else False
        precision = precision if isinstance(precision, int) else 3
        duplicates = duplicates if isinstance(duplicates, str) and duplicates in ['drop', 'rank'] else 'raise'
        seed = seed if isinstance(seed, int) else self._seed()
        c = canonical.column(header).combine_chunks()
        if not (pa.types.is_floating(c.type) or pa.types.is_integer(c.type)):
            raise ValueError(f"The header '{header}' value type must be numerical, '{c.type}' was passed")
        s = c.to_pandas()
        if duplicates == 'rank':
            s = s.rank(method="first")
            duplicates = 'raise'
        s = pd.qcut(s, interval, labels=categories, precision=precision, duplicates=duplicates)
        if categories is False:
            s += 1
        c = pa.Array.from_pandas(s)
        if pa.types.is_dictionary(c.type):
            c = c.dictionary_decode()
        to_header = to_header if isinstance(to_header, str) else header
        return Commons.table_append(canonical, pa.table([c], names=[to_header]))

    def discrete_custom(self, canonical: pa.Table, header: str, interval: [int, float, list]=None,
                        lower: [int, float]=None, upper: [int, float]=None, categories: list=None,
                        to_header: str=None, precision: int=None, seed: int=None, save_intent: bool=None,
                        intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                        remove_duplicates: bool=None) -> pa.Table:
        """ converts continuous representation into discrete representation through interval
        categorisation based on custom intervals

        :param canonical: a pa.Table as the reference table
        :param header: the header in the Table to correlate
        :param interval: (optional) the granularity of the analysis across the range. Default is 3
                float passed - the length of each interval
                list[tuple] - specific interval periods e.g []

        :param lower: (optional) the lower limit of the number value. Default min()
        :param upper: (optional) the upper limit of the number value. Default max()
        :param to_header: (optional) an optional name to call the column
        :param precision: (optional) The precision of the range and boundary values. by default set to 5.
        :param categories: (optional)  a set of labels the same length as the intervals to name the categories
        :param seed: (optional) the random seed. defaults to current datetime
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: an equal length list of correlated values
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        header = self._extract_value(header)
        to_header  = self._extract_value(to_header)
        if not isinstance(header, str) or header not in canonical.column_names:
            raise ValueError(f"The header '{header}' can't be found in the canonical headers")
        seed = seed if isinstance(seed, int) else self._seed()
        rtn_arr = DataDiscovery.to_discrete_intervals(column=canonical.column(header), granularity=interval,
                                                      lower=lower, upper=upper, categories=categories,
                                                      precision=precision)
        to_header = to_header if isinstance(to_header, str) else header
        return Commons.table_append(canonical, pa.table([rtn_arr.dictionary_encode()], names=[to_header]))

