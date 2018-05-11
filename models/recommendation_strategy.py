from abc import ABCMeta, abstractmethod
import logging
from os import path

import gensim as gs
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

from common import utils

pd.options.mode.chained_assignment = None


class RecommendationStrategy(object):
    __metaclass__ = ABCMeta

    DATA_TYPES = {
        'invoice.no': np.int32,
        'product': np.str
    }

    def __init__(self, filepath, modelpath):
        self.modelpath = modelpath
        self.data = pd.read_csv(filepath,
                                dtype=RecommendationStrategy.DATA_TYPES)

    def products(self):
        return sorted(self.data['product'].unique().tolist())

    @abstractmethod
    def training(self):
        raise NotImplementedError

    @abstractmethod
    def recommendation(self, antecedents, metric, top_n):
        raise NotImplementedError


class AssociationRulesStrategy(RecommendationStrategy):
    COL_CONVERTERS = {
        'antecedants': utils.frozenset_eval,
        'consequents': utils.frozenset_eval
    }

    def __init__(self,
                 filepath='./data/sales.csv', modelpath='./data/model.csv'):
        super(AssociationRulesStrategy, self).__init__(filepath, modelpath)

        self.rules = None

    def training(self, metric='lift', threshold=2):

        if not path.exists(self.modelpath):
            basket = self.data.\
                pivot_table(index='invoice.no', columns=['product'],
                            values=['product'],
                            aggfunc=lambda val: len(val), fill_value=0)

            frequent_items = \
                apriori(basket, min_support=0.01, use_colnames=True)

            self.rules = association_rules(frequent_items, metric=metric,
                                           min_threshold=threshold)

            logging.info('New AssociationRules model created, saving it')
            self.rules.to_csv(self.modelpath, index=False)
        else:
            logging.info('AssociationRules model found, using it.')
            self.rules = \
                pd.read_csv(self.modelpath,
                            converters=AssociationRulesStrategy.COL_CONVERTERS)

    def recommendation(self, antecedents, metric='lift', top_n=None):
        current_cart = set(antecedents)

        def find(row):
            subset = current_cart - row.antecedants
            items_limit_outside_cart = int(round(0.3 * len(antecedents)))

            return (len(subset) <= max(3, items_limit_outside_cart) and
                    len(current_cart) > len(subset))

        result = self.rules[self.rules.apply(find, axis=1)]

        if not result.empty:
            consequents = \
                result.loc[result[metric].idxmax()].consequents

            return list(consequents - current_cart)

        return []


class Item2VecStrategy(RecommendationStrategy):
    MIN_CART_LEN_TO_FIND_OUTLIER = 5

    def __init__(self,
                 filepath='./data/sales.csv', modelpath='./data/model.txt'):
        super(Item2VecStrategy, self).__init__(filepath, modelpath)

        self.model = None

    def training(self):

        if not path.exists(self.modelpath):
            logging.info('Word2Vec model not found, creating another model')
            basket = self.data.groupby(['invoice.no'])['product'] \
                .apply(list).tolist()

            gs_model = \
                gs.models.Word2Vec(basket,
                                   # Disregard words that appear less than that
                                   min_count=10,
                                   # The maximum distance between the current
                                   # and predicted word within a sentence.
                                   window=5,
                                   # Activating the CBOW
                                   sg=0,
                                   # Degrees of freedom (the larger the size,
                                   # the more training data is needed,
                                   # but can lead to more accurate models)
                                   size=200,
                                   # Number of CPU cores
                                   workers=2,
                                   # CBOW method
                                   cbow_mean=0)

            logging.info('New Word2Vec model created, saving it')
            gs_model.save(self.modelpath)

            self.model = gs_model.wv
            del gs_model
        else:
            logging.info('Word2Vec model found, using it.')
            gs_model = gs.models.Word2Vec.load(self.modelpath)

            self.model = gs_model.wv
            del gs_model

    def recommendation(self, antecedents, metric=None, top_n=3):
        current_cart = set(antecedents)

        if len(current_cart) >= Item2VecStrategy.MIN_CART_LEN_TO_FIND_OUTLIER:
            outlier_items = self.model.doesnt_match(antecedents)
        else:
            outlier_items = []

        result = self.model.most_similar(positive=antecedents,
                                         negative=outlier_items, topn=top_n)

        return list({item for item, similarity in result} - current_cart)
