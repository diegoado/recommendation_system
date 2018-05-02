import logging

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules


pd.options.mode.chained_assignment = None

COL_TYPES = {
    'InvoiceNo': np.str,
    'StockCode': np.str,
    'Description': np.str,
    'Quantity': np.int8,
    'InvoiceDate': np.str,
    'UnitPrice': np.float32,
    'CustomerID': np.str,
    'Country': np.str
}


class RecommendationSystem(object):
    __instance = None

    @staticmethod
    def instance():
        if RecommendationSystem.__instance is None:
            RecommendationSystem()

        return RecommendationSystem.__instance

    def __init__(self):
        if RecommendationSystem.__instance is not None:
            raise UserWarning(
                'This class is a singleton, use static method to access it.')

        self._rules = None
        self._data_manager = RetailDataManager('data/online_retail.csv')

        RecommendationSystem.__instance = self

    def training(self):
        logging.info('Generating association rules')
        self._rules = self._data_manager.training()

    def items(self):
        return self._data_manager.products()

    def recommendation(self, antecedents, metric='lift'):
        current_cart = set(antecedents)

        def find(row):
            subset = current_cart - row.antecedants
            items_limit_outside_cart = int(round(0.3 * len(antecedents)))

            return (len(subset) <= max(3, items_limit_outside_cart) and
                    len(current_cart) > len(subset))

        response_df = self._rules[self._rules.apply(find, axis=1)]

        if not response_df.empty:
            consequents = \
                response_df.loc[response_df[metric].idxmax()].consequents

            return list(consequents - current_cart)

        return []


class RetailDataManager(object):
    def __init__(self, data_path):
        df = \
            pd.read_csv(data_path, dtype=COL_TYPES)

        df.dropna(axis=0, subset=['InvoiceNo'], inplace=True)

        self._retail_data = \
            df[df['Country'] == 'France']

        self._retail_data['Description'] = \
            df.loc[:, 'Description'].str.strip(' ')

    def training(self, metric='lift', min_threshold=2):
        df = \
            self._retail_data[~self._retail_data['InvoiceNo'].str.contains('C')]

        basket = df \
            .groupby(['InvoiceNo', 'Description'])['Quantity'] \
            .sum() \
            .unstack() \
            .reset_index() \
            .fillna(0) \
            .set_index('InvoiceNo')

        basket_sets = basket.applymap(self._encode_units)
        basket_sets.drop('POSTAGE', inplace=True, axis=1)

        frequent_items = \
            apriori(basket_sets, min_support=0.05, use_colnames=True)

        return association_rules(frequent_items,
                                 metric=metric, min_threshold=min_threshold)

    def products(self):
        return sorted(self._retail_data['Description'].unique().tolist())

    @staticmethod
    def _encode_units(x):
        if x <= 0:
            return 0
        if x >= 1:
            return 1
