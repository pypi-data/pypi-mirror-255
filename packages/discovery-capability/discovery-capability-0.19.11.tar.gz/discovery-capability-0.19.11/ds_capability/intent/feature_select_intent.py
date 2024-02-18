import inspect
import random
import re
import pyarrow as pa
import pyarrow.compute as pc
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from ds_capability.components.commons import Commons
from ds_capability.intent.common_intent import CommonsIntentModel
from ds_capability.intent.abstract_feature_select_intent import AbstractFeatureSelectIntentModel


class FeatureSelectIntent(AbstractFeatureSelectIntentModel, CommonsIntentModel):

    """This class represents feature selection intent actions focusing on dimensionality and
    specifically columnar reduction. Its purpose is to disregard irrelevant features to remove,
    amongst other things, constants, duplicates and statistically uninteresting columns.

    As an early stage data pipeline process, FeatureSelect focuses on data preprocessing, and as
    such is a filter step for extracting features of interest.
    """

    def auto_clean_header(self, canonical: pa.Table, case: str=None, rename_map: [dict, list, str]=None,
                          replace_spaces: str=None, save_intent: bool=None, intent_level: [int, str]=None,
                          intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ clean the headers of a Table replacing space with underscore. This also allows remapping and case selection

        :param canonical: the pa.Table
        :param rename_map: (optional) a dict of name value pairs, a fixed length list of column names or connector name
        :param case: (optional) changes the headers to lower, upper, title. if none of these then no change
        :param replace_spaces: (optional) character to replace spaces with. Default is '_' (underscore)
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pa.Table.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        # auto mapping
        if isinstance(rename_map, str):
            if self._pm.has_connector(rename_map):
                handler = self._pm.get_connector_handler(rename_map)
                mapper = handler.load_canonical()
                if mapper.shape[1] == 1:
                    rename_map = mapper.iloc[:, 0].values.tolist()
                else:
                    rename_map = dict(zip(mapper.iloc[:, 0].values, mapper.iloc[:, 1].values))
            else:
                mapper=None
        # map the headers
        if isinstance(rename_map, dict):
            names = [rename_map.get(item,item)  for item in canonical.column_names]
            canonical = canonical.rename_columns(names)
        if isinstance(rename_map, list) and len(rename_map) == canonical.num_columns:
            tbl = canonical.rename_columns(rename_map)
        # tidy
        headers = []
        for s in canonical.column_names:
            s = re.sub(r"[^\w\s]", '', s)
            s = re.sub(r"\s+", '_', s)
            headers.append(s)
        # convert case
        if isinstance(case, str):
            headers = pa.array(headers)
            if case.lower() == 'lower':
                headers = pc.ascii_lower(headers)
            elif case.lower() == 'upper':
                headers = pc.ascii_upper(headers)
            elif case.lower() == 'title':
                headers = pc.ascii_title(headers)
            headers = headers.to_pylist()
        # return table with new headers
        return canonical.rename_columns(headers)

    def auto_cast_types(self, canonical: pa.Table, include_category: bool=None, category_max: int=None, include_bool: bool=None,
                        include_timestamp: bool=None, tm_format: str=None, tm_units: str=None, tm_tz: str=None, save_intent: bool=None,
                        intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                        remove_duplicates: bool=None) -> pa.Table:
        """ attempts to cast the columns of a table to its appropriate type. Categories boolean and timestamps
        are toggled on and off with the include parameters being true or false.

        :param canonical: the pa.Table
        :param include_category: (optional) if categories should be cast.  Default True
        :param category_max: (optional) the max number of unique values to consider categorical
        :param include_bool: (optional) if booleans should be cast. Default True
        :param include_timestamp: (optional) if categories should be cast.  Default True
        :param tm_format: (optional) if not standard, the format of the dates, example '%m-%d-%Y %H:%M:%S'
        :param tm_units: (optional) units to cast timestamp. Options are 's', 'ms', 'us', 'ns'
        :param tm_tz: (optional) timezone to cast timestamp
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pa.Table.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        return Commons.table_cast(canonical, inc_cat=include_category, cat_max=category_max, inc_bool=include_bool,
                                  inc_time=include_timestamp, dt_format=tm_format, units=tm_units, tz=tm_tz)

    def auto_reinstate_nulls(self, canonical: pa.Table, nulls_list=None, headers: [str, list]=None, drop: bool=None,
                             data_type: [str, list]=None, regex: [str, list]=None, save_intent: bool=None,
                             intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                             remove_duplicates: bool=None) -> pa.Table:
        """ automatically reinstates nulls in a string that have been masked with alternate values such as space
        or question-mark. By default, the nulls list is ['',' ','NaN','nan','None','null','Null','NULL']

        :param canonical: the pa.Table
        :param nulls_list: (optional) potential null values to replace with a null.
        :param headers: a list of headers to drop or filter on type
        :param drop: to drop or not drop the headers
        :param data_type: the column types to include or exclude. Default None else int, float, bool, object, 'number'
        :param regex: a regular expression to search the headers
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pa.Table.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        nulls_list = nulls_list if isinstance(nulls_list, list) else ['', ' ', 'NaN', 'nan', 'None', 'null', 'Null',
                                                                      'NULL']

        selected_headers = Commons.filter_headers(canonical, headers=headers, d_types=data_type, regex=regex, drop=drop)
        rtn_tbl = None
        for n in selected_headers:
            c = canonical.column(n).combine_chunks()
            if pa.types.is_string(c.type):
                mask = pc.is_in(c, pa.array(nulls_list))
                c = pc.if_else(mask, None, c)
                canonical = Commons.table_append(canonical, pa.table([c], names=[n]))
        return canonical

    def auto_drop_noise(self, canonical: pa.Table, nulls_threshold: float=None, nulls_list: [bool, list]=None,
                        drop_predominant: bool=None, drop_empty_row: bool=None, drop_unknown: bool=None,
                        save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                        replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ auto removes columns that are at least 0.998 percent np.NaN, a single value, std equal zero or have a
        predominant value greater than the default 0.998 percent.

        :param canonical: the pa.Table
        :param nulls_threshold:  (optional) The threshold limit of a nulls value. Default 0.95
        :param nulls_list:  (optional) can be boolean or a list:
                    if boolean and True then null_list equals ['NaN', 'nan', 'null', '', 'None', ' ']
                    if list then this is considered potential null values.
        :param drop_predominant:  (optional) drop columns that have a predominant value of the given predominant max
        :param drop_empty_row:  (optional) also drop any rows where all the values are empty
        :param drop_unknown:  (optional) drop objects that are not string types such as binary
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pa.Table.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        nulls_threshold = nulls_threshold if isinstance(nulls_threshold, float) and 0 <= nulls_threshold <= 1 else 0.95
        drop_unknown = drop_unknown if isinstance(drop_unknown, bool) else False
        # drop knowns
        to_drop = []
        for n in canonical.column_names:
            c = canonical.column(n).combine_chunks()
            if pa.types.is_dictionary(c.type):
                c = c.dictionary_decode()
            if pa.types.is_nested(c.type) or pa.types.is_list(c.type) or pa.types.is_struct(c.type):
                to_drop.append(n)
            elif c.null_count / canonical.num_rows > nulls_threshold:
                to_drop.append(n)
            elif pc.count(pc.unique(c)).as_py() <= 1:
                to_drop.append(n)
        return canonical.drop_columns(to_drop)

    def auto_sample_rows(self, canonical: pa.Table, size: int, save_intent: bool=None, intent_level: [int, str]=None,
                         intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ auto samples rows of a canonical returning a randomly selected subset of the canonical based on size.

        :param canonical: the pa.Table
        :param size: the randomly selected subset size of the canonical
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pa.Table.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        if canonical.num_rows > size > 0:
            sample = random.sample(range(canonical.num_rows), k=int(size))
            canonical = canonical.take(sample)
        return canonical

    def auto_drop_columns(self, canonical: pa.Table, headers: [str, list]=None, d_types: [str, list]=None,
                          regex: [str, list]=None, drop: bool=None, save_intent: bool=None,
                          intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                          remove_duplicates: bool=None) -> pa.Table:
        """ auto removes columns that are selected.

        :param canonical: the pa.Table
        :param headers: (optional) a filter of headers from the 'other' dataset
        :param drop: (optional) to drop or not drop the headers if specified
        :param d_types: (optional) a filter on data type for the 'other' dataset. int, float, bool, object
        :param regex: (optional) a regular expression to search the headers. example '^((?!_amt).)*$)' excludes '_amt'
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pa.Table.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        to_drop = Commons.filter_headers(canonical, headers=headers, regex=regex, d_types=d_types, drop=drop)
        return canonical.drop_columns(to_drop)

    def auto_drop_duplicates(self, canonical: pa.Table, save_intent: bool=None, intent_level: [int, str]=None,
                             intent_order: int=None, replace_intent: bool=None,
                             remove_duplicates: bool=None) -> pa.Table:
        """ Removes columns that are duplicates of each other

        :param canonical: the pa.Table
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: Canonical,.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        to_drop = []
        for i in range(0, len(canonical.column_names)):
            col_1 = canonical.column_names[i]
            for col_2 in canonical.column_names[i + 1:]:
                if canonical.column(col_1).equals(canonical.column(col_2)):
                    to_drop.append(col_2)
        return canonical.drop_columns(to_drop)

    def auto_drop_correlated(self, canonical: pa.Table, threshold: float=None, save_intent: bool=None,
                             intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                             remove_duplicates: bool=None) -> pa.Table:
        """ uses 'brute force' techniques to remove highly correlated numeric columns based on the threshold,
        set by default to 0.95.

        :param canonical: the pa.Table
        :param threshold: (optional) threshold correlation between columns. default 0.95
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: Canonical,.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        threshold = threshold if isinstance(threshold, float) and 0 < threshold < 1 else 0.95
        # extract numeric columns
        tbl_filter = Commons.filter_columns(canonical, d_types=[pa.int64(), pa.int32(), pa.float64(), pa.float32()])
        df_filter = tbl_filter.to_pandas()
        to_drop = set()
        corr_matrix = df_filter.corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if abs(corr_matrix.iloc[i, j]) > threshold:  # we are interested in absolute coeff value
                    col_name = corr_matrix.columns[i]  # getting the name of column
                    to_drop.add(col_name)
        return canonical.drop_columns(to_drop)

    def auto_aggregate(self, canonical: pa.Table, action: str, headers: [str, list]=None, d_types: [str, list]=None,
                       regex: [str, list]=None, drop: bool=None, to_header: str=None, drop_aggregated: bool=None,
                       precision: int=None, save_intent: bool=None, intent_level: [int, str]=None,
                       intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ given a set of columns, aggregates those columns based upon the aggregation action given.
        The actions are 'sum', 'prod', 'count', 'min', 'max', 'mean', 'list', 'list_first', 'list_last'.
        'list_first' and 'list_last' return the first or last value in a list.

        :param canonical: the pa.Table
        :param action: an aggregation action such as count or list_first.
        :param headers: (optional) a filter of headers from the 'other' dataset
        :param drop: (optional) to drop or not drop the headers if specified
        :param d_types: (optional) a filter on data type for the 'other' dataset. int, float, bool, object
        :param regex: (optional) a regular expression to search the headers. example '^((?!_amt).)*$)' excludes '_amt'
        :param to_header: (optional) an optional name to call the column
        :param drop_aggregated: (optional) drop the aggregation headers
        :param precision: the value precision of the return values
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: Canonical,.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        drop_aggregated = drop_aggregated if isinstance(drop_aggregated, bool) else False
        tbl = Commons.filter_columns(canonical, headers=headers, d_types=d_types, regex=regex, drop=drop)
        headers = tbl.column_names
        df = tbl.to_pandas()
        if action not in ['sum', 'prod', 'count', 'min', 'max', 'mean', 'list', 'list_first', 'list_last']:
            raise ValueError("The only values are 'sum','prod','count','min','max','mean','list','list_first','list_last'")
        # Code block for intent
        precision = precision if isinstance(precision, int) else 3
        if action.startswith('list'):
            rtn_values = df.loc[:, headers].values.tolist()
            rtn_values = [[x for x in y if x is not None] for y in rtn_values]
            if action.endswith('_first'):
                rtn_values = [x[0] if len(x) > 0 else None for x in rtn_values]
            if action.endswith('_last'):
                rtn_values = [x[-1] if len(x) > 0 else None for x in rtn_values]
        else:
            rtn_values = eval(f"df.loc[:, headers].{action}(axis=1)", globals(), locals()).round(precision).to_list()
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        if drop_aggregated:
            canonical = canonical.drop_columns(headers)
        return Commons.table_append(canonical, pa.table([pa.array(rtn_values)], names=[to_header]))

    def auto_projection(self, canonical: pa.Table, headers: list=None, drop: bool=None, n_components: [int, float]=None,
                        seed: int=None, save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                        replace_intent: bool=None, remove_duplicates: bool=None, **kwargs) -> pa.Table:
        """Principal component analysis (PCA) is a linear dimensionality reduction using Singular Value Decomposition
        of the data to project it to a lower dimensional space.

        :param canonical: the pa.Table
        :param headers: (optional) a list of headers to select (default) or drop from the dataset
        :param drop: (optional) if True then srop the headers. False by default
        :param n_components: (optional) Number of components to keep.
        :param seed: (optional) placeholder
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :param kwargs: additional parameters to pass the PCA model
        :return: a pd.DataFrame
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        headers = Commons.list_formatter(headers)
        sample = Commons.filter_columns(canonical, headers=headers, drop=drop, d_types=[pa.float64(), pa.int64()])
        sample = self.auto_drop_noise(sample, nulls_threshold=0.3)
        sample = Commons.table_fill_null(sample)
        if not sample or len(sample) == 0:
            return canonical
        n_components = n_components if isinstance(n_components, (int, float)) \
                                       and 0 < n_components < sample.shape[1]  else sample.shape[1]
        sample = sample.to_pandas(split_blocks=True)
        # standardise
        scaler = StandardScaler()
        train = scaler.fit_transform(sample)
        # pca
        pca = PCA(n_components=n_components, **kwargs)
        train = pca.fit_transform(train)
        gen = Commons.label_gen(prefix='pca_')
        names = []
        for n in range(train.shape[1]):
            names.append(next(gen))
        tbl = pa.Table.from_arrays(train.T, names=names)
        canonical = canonical.drop_columns(sample.columns)
        return Commons.table_append(canonical, tbl)

    def auto_append_tables(self, canonical: pa.Table, other: pa.Table=None, headers: [str, list]=None,
                           data_types: [str, list]=None, regex: [str, list]=None, drop: bool=None,
                           other_headers: [str, list]=None, other_data_type: [str, list]=None,
                           other_regex: [str, list]=None, other_drop: bool=None, seed: int=None,
                           save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                           replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ Appends the canonical table with other

        :param canonical: a pa.Table
        :param other: (optional) the pa.Table or connector to join. This is the dominant table and will replace like named columns
        :param headers: (optional) headers to select
        :param data_types: (optional) data types to select. use PyArrow data types eg 'pa.string()'
        :param regex: (optional) a regular expression
        :param drop: (optional) if True then drop the headers. False by default
        :param other_headers: other headers to select
        :param other_data_type: other data types to select. use PyArrow data types eg 'pa.string()'
        :param other_regex: other regular expression
        :param other_drop: if True then drop the other headers
        :param seed: (optional) placeholder
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
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
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        canonical = self._get_canonical(canonical)
        other = self._get_canonical(other)
        canonical = Commons.filter_columns(canonical, headers=headers, d_types=data_types, regex=regex, drop=drop)
        if other is None:
            return canonical
        other = Commons.filter_columns(other, headers=other_headers, d_types=other_data_type, regex=other_regex,
                                       drop=other_drop)
        if canonical.num_rows > other.num_rows:
            df = other.to_pandas()
            df = df.sample(n=canonical.num_rows, random_state=seed, ignore_index=True, replace=True)
            other = pa.Table.from_pandas(df)
        else:
            other = other.slice(0, canonical.num_rows)
        # append
        return Commons.table_append(canonical, other)
