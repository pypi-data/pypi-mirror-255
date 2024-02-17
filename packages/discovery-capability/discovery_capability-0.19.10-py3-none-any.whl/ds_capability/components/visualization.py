import math
import random
import pyarrow as pa
import pyarrow.compute as pc
import pandas as pd
import numpy as np
from matplotlib.colors import LogNorm

from ds_capability.components.commons import Commons
from scipy import stats
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
import seaborn as sns


class Visualisation(object):
    """ a set of data components methods to Visualise pandas.Dataframe"""

    @staticmethod
    def show_chi_square(canonical: pa.Table, target: str, capped_at: int=None, seed: int=None, width: float=None, height: float=None):
        """ Chi-square is one of the most widely used supervised feature selection methods. It selects each feature
         independently in accordance with their scores against a target or label then ranks them by their importance.
         This score should be used to evaluate categorical variables in a classification task.

        :param canonical: The canonical to apply
        :param target: the str header that constitute a binary target.
        :param capped_at: (optional) a cap on the size of elements (columns x rows) to process. default at 5,000,000
        :param seed: (optional) a seed value for the test train dataset
        :param width: (optional) the figure size width
        :param height: (optional) the figure size height
        """
        if target not in canonical.column_names:
            raise ValueError(f"The target '{target}' can't be found in the canonical")
        if pc.count(pc.unique(canonical.column(target))).as_py() != 2:
            raise ValueError(f"The target '{target}' must only be two unique values")
        width = width if isinstance(width, float) else 6
        height = height if isinstance(height, float) else 4
        cap = capped_at if isinstance(capped_at, int) else 1_000_000
        if canonical.num_rows*canonical.num_columns > cap > 0:
            sample = random.sample(range(canonical.num_rows), k=int(cap/canonical.num_columns))
            canonical = canonical.take(sample)
        control = canonical.to_pandas()
        # separate train and test sets
        X_train, X_test, y_train, y_test = train_test_split(control.drop(target, axis=1), control[target],
                                                            test_size=0.3, random_state=seed)
        chi_ls = []
        for feature in X_train.columns:
            # create contingency table
            c = pd.crosstab(y_train, X_train[feature])
            # chi_test
            p_value = stats.chi2_contingency(c)[1]
            chi_ls.append(p_value)
        plt.figure(figsize=(width, height))
        pd.Series(chi_ls, index=X_train.columns).sort_values(ascending=True).plot.bar(rot=45)
        plt.ylabel('p value')
        plt.title('Feature importance based on chi-square test', fontdict={'size': 20})
        plt.tight_layout()
        plt.show()
        plt.clf()

    @staticmethod
    def show_missing(canonical: pa.Table, headers: [str, list]=None, d_types: [str, list]=None,
                     regex: [str, list]=None, drop: bool=None, capped_at: int=None, width: float=None, height: float=None):
        """ A heatmap of missing data. Each column shows missing values and where in the column the missing data is.

        :param canonical: a canonical to apply
        :param headers: (optional) a filter on headers from the canonical
        :param d_types: (optional) a filter on data type for the canonical. example [pa.int64(), pa.string()]
        :param regex: (optional) a regular expression to search the headers.
        :param drop: (optional) to drop or not drop the resulting headers.
        :param capped_at: (optional) a cap on the size of elements (columns x rows) to process. default at 5,000,000
        :param width: (optional) the figure size width
        :param height: (optional) the figure size height
        """
        width = width if isinstance(width, float) else 6
        height = height if isinstance(height, float) else 5
        cap = capped_at if isinstance(capped_at, int) else 1_000_000
        if canonical.num_rows*canonical.num_columns > cap > 0:
            sample = random.sample(range(canonical.num_rows), k=int(cap/canonical.num_columns))
            canonical = canonical.take(sample)
        canonical = Commons.filter_columns(canonical, headers=headers, d_types=d_types, regex=regex, drop=drop)
        control = canonical.to_pandas()
        sns.set(rc={'figure.figsize': (width, height)})
        sns.heatmap(control.isnull(), yticklabels=False, cbar=False, cmap='viridis')
        plt.title('missing data', fontdict={'size': 20})
        plt.tight_layout()
        plt.show()
        plt.clf()

    @staticmethod
    def show_correlated(canonical: pa.Table, headers: [str, list]=None, d_types: [str, list]=None,
                        regex: [str, list]=None, drop: bool=None, capped_at: int=None, width: float=None, height: float=None):
        """ shows correlation as a grid of values for each column pair where correlation is represented by a value
        moving towards 100. This only applies to int and float.

        :param canonical: a canonical to apply
        :param headers: (optional) a filter on headers from the canonical
        :param d_types: (optional) a filter on data type for the canonical. example [pa.int64(), pa.string()]
        :param regex: (optional) a regular expression to search the headers.
        :param drop: (optional) to drop or not drop the resulting headers.
        :param capped_at: (optional) a cap on the size of elements (columns x rows) to process. default at 5,000,000
        :param width: (optional) the figure size width
        :param height: (optional) the figure size height
        :return: pa.Table
        """
        width = width if isinstance(width, float) else 6
        height = height if isinstance(height, float) else 5
        cap = capped_at if isinstance(capped_at, int) else 1_000_000
        if canonical.num_rows*canonical.num_columns > cap > 0:
            sample = random.sample(range(canonical.num_rows), k=int(cap/canonical.num_columns))
            canonical = canonical.take(sample)
        canonical = Commons.filter_columns(canonical, headers=headers, d_types=d_types, regex=regex, drop=drop)
        canonical = Commons.filter_columns(canonical, d_types=[pa.int64(),pa.int32(),pa.int16(),pa.int8(),
                                                               pa.float64(),pa.float32(),pa.float16()])
        control = canonical.to_pandas()
        sns.set(rc={'figure.figsize': (width, height)})
        sns.heatmap(control.corr(), annot=True, cmap='BuGn', robust=True)
        plt.title('correlated data', fontdict={'size': 20})
        plt.tight_layout()
        plt.show()
        plt.clf()

    @staticmethod
    def show_distributions(canonical: pa.Table, headers: [str, list]=None, d_types: [str, list]=None,
                        regex: [str, list]=None, drop: bool=None, capped_at: int=None, width: float=None, height: float=None):
        """ Shows three key distributions for a target sample array."""
        width = width if isinstance(width, float) else 16
        height = height if isinstance(height, float) else 4
        cap = capped_at if isinstance(capped_at, int) else 1_000_000
        if canonical.num_rows*canonical.num_columns > cap > 0:
            sample = random.sample(range(canonical.num_rows), k=int(cap/canonical.num_columns))
            canonical = canonical.take(sample)
        canonical = Commons.filter_columns(canonical, headers=headers, d_types=d_types, regex=regex, drop=drop)
        canonical = Commons.filter_columns(canonical, d_types=[pa.int64(),pa.int32(),pa.int16(),pa.int8(),
                                                               pa.float64(),pa.float32(),pa.float16()])
        control = canonical.to_pandas()
        for target in canonical.column_names:
        # Define figure size.
            _ = plt.figure(figsize=(width, height))
            _ = plt.suptitle('Show Distribution', fontdict={'size': 20})
            # histogram
            plt.subplot(1, 3, 1)
            sns.histplot(control[target], bins=30)
            plt.title('Histogram')
            # Q-Q plot
            plt.subplot(1, 3, 2)
            stats.probplot(control[target], dist="norm", plot=plt)
            plt.ylabel('RM quantiles')
            # boxplot
            plt.subplot(1, 3, 3)
            sns.boxplot(y=control[target])
            plt.title('Boxplot')
        plt.tight_layout()
        plt.show()
        plt.clf()

    @staticmethod
    def show_category_frequency(canonical: pa.Table, target_dt, headers: [str, list]=None, d_types: [str, list]=None,
                                regex: [str, list]=None, drop: bool=None, category_limit: int=None, capped_at: int=None, log_scale=False,
                                subplot_h=2, subplot_w=15, param_scale=8, rotation=360, hspace=0.35):
        """ creates the frequencies (colors of heatmap) of the elements (y axis) of the categorical columns
        over time (x axis)

        :param canonical:
        :param target_dt: the target date
        :param headers: (optional) a filter on headers from the canonical
        :param d_types: (optional) a filter on data type for the canonical. example [pa.int64(), pa.string()]
        :param regex: (optional) a regular expression to search the headers.
        :param drop: (optional) to drop or not drop the resulting headers.
        :param category_limit: (optional) the number of unique values that make up a category. Default 10
        :param capped_at: (optional) a cap on the size of elements (columns x rows) to process. default at 5,000,000
        :param log_scale: (optional)
        :param subplot_h: (optional)
        :param subplot_w: (optional)
        :param param_scale: (optional)
        :param rotation: (optional)
        :param hspace: (optional)
        """
        cap = capped_at if isinstance(capped_at, int) else 1_000_000
        category_limit = category_limit if isinstance(category_limit, str) else 10
        log_scale = log_scale if isinstance(log_scale, bool) else False
        subplot_h = subplot_h if isinstance(subplot_h, int) else 2
        subplot_w = subplot_w if isinstance(subplot_w, int) else 15
        param_scale = param_scale if isinstance(param_scale, int) else 0
        rotation = rotation if isinstance(rotation, int) else 360
        hspace = hspace if isinstance(hspace, float) else 0.35
        if canonical.num_rows*canonical.num_columns > cap > 0:
            sample = random.sample(range(canonical.num_rows), k=int(cap/canonical.num_columns))
            canonical = canonical.take(sample)
        canonical = Commons.filter_columns(canonical, headers=headers, d_types=d_types, regex=regex, drop=drop)
        col_names = Commons.filter_headers(canonical, d_types=[pa.string()])
        for n in tuple(col_names):
            c = canonical.column(n).combine_chunks()
            if pc.count(pc.unique(c)).as_py() > category_limit:
                col_names.remove(n)
        if target_dt in col_names:
            col_names.remove(target_dt)
        df = canonical.to_pandas()
        df[target_dt] = pd.to_datetime(df[target_dt])
        dates = pd.date_range(start=df[target_dt].min(), end=df[target_dt].max())
        n_categories = len(col_names)
        cbar_kws = {'orientation': 'horizontal', 'shrink': 0.5}
        n_subplot_rows = np.ceil(df[col_names].nunique(dropna=True).divide(param_scale))
        n_subplot_rows.iloc[-1] += 1
        n_rows = int(n_subplot_rows.sum())
        grid_weights = {'height_ratios': n_subplot_rows.values}
        cmap = 'rocket_r'
        # cmap = sns.cm.rocket_r
        fig, axes = plt.subplots(n_categories, 1, gridspec_kw=grid_weights, sharex='col',
                                 figsize=(subplot_w, n_rows * subplot_h))
        if n_categories == 1:
            axes = [axes]
        for ii in range(n_categories):
            cc = col_names[ii]
            df_single_cat = df[[target_dt, cc]]
            df_single_cat = df_single_cat.loc[df_single_cat[target_dt].notnull(),]
            df_single_cat['Index'] = df_single_cat[target_dt].dt.date
            df_pivot = df_single_cat.pivot_table(index='Index', columns=cc, aggfunc=len, dropna=True)
            df_pivot.index = pd.to_datetime(df_pivot.index)
            toplot = df_pivot.reindex(dates.date).T

            v_min = toplot.min().min()
            v_max = toplot.max().max()
            toplot.reset_index(level=0, drop=True, inplace=True)
            if log_scale:
                cbar_ticks = [math.pow(10, i) for i in range(int(math.floor(math.log10(v_min))),
                                                             int(1 + math.ceil(math.log10(v_max))))]
                log_norm = LogNorm(vmin=v_min, vmax=v_max)
            else:
                cbar_ticks = list(range(int(v_min), int(v_max + 1)))
                if len(cbar_ticks) > 5:
                    v_step = int(math.ceil((v_max - v_min) / 4))
                    cbar_ticks = list(range(int(v_min), int(v_max + 1), v_step))
                log_norm = None
            cbar_kws['ticks'] = cbar_ticks
            if ii < (n_categories - 1):
                cbar_kws['pad'] = 0.05
            else:
                cbar_kws['pad'] = 0.25
            sns.heatmap(toplot, cmap=cmap, ax=axes[ii], norm=log_norm, cbar_kws=cbar_kws, yticklabels=True)
            axes[ii].set_ylabel('')
            axes[ii].set_xlabel('')
            axes[ii].set_title(cc)
            axes[ii].set_yticklabels(axes[ii].get_yticklabels(), rotation=rotation)
            for _, spine in axes[ii].spines.items():
                spine.set_visible(True)
        axes[-1].set_xlabel(target_dt)
        plt.subplots_adjust(bottom=0.05, hspace=hspace)
        plt.tight_layout()
        plt.show()
        plt.clf()

    @staticmethod
    def show_category_appearance(canonical: pa.Table, target_dt: str, headers: [str, list]=None,
                                 d_types: [str, list]=None, regex: [str, list]=None, drop: bool=None,
                                 category_limit: int=None, capped_at: int=None, subplot_h: int=None,
                                 subplot_w: int=None, rotation: int=None):
        """ creates the proportion (as percentages) (colors of heatmap) of the appearing elements (y axis)
        of the categorical columns over time (x axis)

        :param canonical:
        :param target_dt:
        :param headers: (optional) a filter on headers from the canonical
        :param d_types: (optional) a filter on data type for the canonical. example [pa.int64(), pa.string()]
        :param regex: (optional) a regular expression to search the headers.
        :param drop: (optional) to drop or not drop the resulting headers.
        :param category_limit: (optional) the number of unique values that make up a category. Default 10
        :param capped_at: (optional) a cap on the size of elements (columns x rows) to process. default at 5,000,000
        :param subplot_h: (optional)
        :param subplot_w: (optional)
        :param rotation: (optional)
        """
        category_limit = category_limit if isinstance(category_limit, str) else 10
        cap = capped_at if isinstance(capped_at, int) else 1_000_000
        subplot_h = subplot_h if isinstance(subplot_h, int) else 6
        subplot_w = subplot_w if isinstance(subplot_w, int) else 10
        rotation = rotation if isinstance(rotation, int) else 360
        if canonical.num_rows*canonical.num_columns > cap > 0:
            sample = random.sample(range(canonical.num_rows), k=int(cap/canonical.num_columns))
            canonical = canonical.take(sample)
        canonical = Commons.filter_columns(canonical, headers=headers, d_types=d_types, regex=regex, drop=drop)
        col_names = Commons.filter_headers(canonical, d_types=[pa.string()])
        for n in tuple(col_names):
            c = canonical.column(n).combine_chunks()
            if pc.count(pc.unique(c)).as_py() > category_limit:
                col_names.remove(n)
        if target_dt in col_names:
            col_names.remove(target_dt)
        df = canonical.to_pandas()
        df[target_dt] = pd.to_datetime(df[target_dt])
        dates = pd.date_range(start=df[target_dt].min(), end=df[target_dt].max())
        cmap = 'rocket_r'
        # cmap = sns.cm.rocket_r
        df0 = df[col_names + [target_dt]]
        df0['Index'] = df0.loc[:,target_dt].dt.date
        df_unique = df0[col_names].nunique(dropna=True)
        df_agg = df0.groupby('Index').nunique(dropna=True)
        # df_agg = df_agg.drop('Index', axis='columns')
        df_frac = df_agg[col_names].divide(df_unique, axis=1)
        df_frac.index = pd.to_datetime(df_frac.index)
        toplot = df_frac.reindex(dates.date).T
        new_labels = df_unique.index.values + '\n(' + pd.Series(df_unique.values).apply(str) + ')'
        fig = plt.figure(figsize=(subplot_w, subplot_h))
        ax = sns.heatmap(toplot, cmap=cmap, vmin=0, vmax=1, cbar_kws={'shrink': 0.75})
        ax.set_yticklabels(new_labels, rotation=rotation)
        ax.set_ylabel('')
        ax.set_xlabel(target_dt)
        cbar = ax.collections[0].colorbar
        cbar.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])
        cbar.set_ticklabels(['0%', '25%', '50%', '75%', '100%'])
        plt.tight_layout()
        plt.show()
        plt.clf()

    @staticmethod
    def show_numeric_density(canonical: pa.Table, headers: [str, list]=None, d_types: [str, list]=None,
                             regex: [str, list]=None, drop: bool=None, capped_at: int=None, width: float=None, height: float=None):
        """"""
        width = width if isinstance(width, float) else 16
        height = height if isinstance(height, float) else 4
        cap = capped_at if isinstance(capped_at, int) else 1_000_000
        if canonical.num_rows*canonical.num_columns > cap > 0:
            sample = random.sample(range(canonical.num_rows), k=int(cap/canonical.num_columns))
            canonical = canonical.take(sample)
        canonical = Commons.filter_columns(canonical, headers=headers, d_types=d_types, regex=regex, drop=drop)
        num_cols = Commons.filter_headers(canonical, d_types=[pa.int64(),pa.int32(),pa.int16(),pa.int8(),
                                                               pa.float64(),pa.float32(),pa.float16()])
        control = canonical.to_pandas()
        depth = int(round(len(num_cols) / 2, 0) + len(num_cols) % 2)
        _figsize = (width, height * depth)
        fig = plt.figure(figsize=_figsize)
        right = False
        line = 0
        for c in num_cols:
            col = control[c]
            #     print("{}, {}, {}, {}".format(c, depth, line, right))
            ax = plt.subplot2grid((depth, 2), (line, int(right)))
            g = col.dropna().plot.kde(ax=ax, title=str.title(c))
            g.get_xaxis().tick_bottom()
            g.get_yaxis().tick_left()
            if right:
                line += 1
            right = not right
        plt.tight_layout()
        plt.show()
        plt.clf()

    @staticmethod
    def show_categories(canonical: pa.Table, headers: [str, list]=None, d_types: [str, list]=None,
                         regex: [str, list]=None, drop: bool=None, capped_at: int=None, top=None):
        """"""
        cap = capped_at if isinstance(capped_at, int) else 1_000_000
        if canonical.num_rows*canonical.num_columns > cap > 0:
            sample = random.sample(range(canonical.num_rows), k=int(cap/canonical.num_columns))
            canonical = canonical.take(sample)
        canonical = Commons.filter_columns(canonical, headers=headers, d_types=d_types, regex=regex, drop=drop)
        cat_cols = Commons.filter_headers(canonical, d_types=[pa.string()])
        control = canonical.to_pandas()
        sns.set(style='darkgrid', color_codes=True)
        if len(cat_cols) == 1:
            c = cat_cols[0]
            width = control[c].nunique() + 1
            if width > 16:
                width = 16
            _ = plt.subplots(1, 1, figsize=(width, 4))
            _ = sns.countplot(c)
            _ = sns.countplot(x=c, data=control, palette="summer")
            _ = plt.xticks(rotation=-90)
            _ = plt.xlabel(str.title(c))
            _ = plt.ylabel('Count')
            title = "{} Categories".format(str.title(c))
            _ = plt.title(title, fontsize=16)
        else:
            wide_col, thin_col = [], []
            for c in cat_cols:
                if control[c].nunique() > 10:
                    wide_col += [c]
                else:
                    thin_col += [c]
            depth = len(wide_col) + int(round(len(thin_col) / 2, 0))
            _ = plt.figure(figsize=(20, 5 * depth))
            sns.set(style='darkgrid', color_codes=True)
            for c, i in zip(wide_col, range(len(wide_col))):
                ax = plt.subplot2grid((depth, 2), (i, 0), colspan=2)
                order = list(control[c].value_counts().index.values)
                if isinstance(top, int):
                    order = order[:top]
                _ = sns.countplot(x=c, data=control, ax=ax, order=order)
                _ = plt.xticks(rotation=-90)
                _ = plt.xlabel(str.title(c))
                _ = plt.ylabel('Count')
                title = "{} Categories".format(str.title(c))
                _ = plt.title(title, fontsize=16)
            right = False
            line = len(wide_col)
            for c in thin_col:
                ax = plt.subplot2grid((depth, 2), (line, int(right)))
                order = list(control[c].value_counts().index.values)
                _ = sns.countplot(x=c, data=control, ax=ax, order=order)
                _ = plt.xticks(rotation=-90)
                _ = plt.xlabel(str.title(c))
                _ = plt.ylabel('Count')
                title = "{} Categories".format(str.title(c))
                _ = plt.title(title, fontsize=16)
                if right:
                    line += 1
                right = not right

        _ = plt.tight_layout()
        _ = plt.show()
        _ = plt.clf()
