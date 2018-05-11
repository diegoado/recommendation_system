import importlib
import logging

from recommendation_strategy import Item2VecStrategy


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

        self._strategy = Item2VecStrategy()
        RecommendationSystem.__instance = self

    def training(self):
        logging.info('Training selected strategy')
        self._strategy.training()

    def items(self):
        return self._strategy.products()

    def recommendation(self, antecedents):
        return self._strategy.recommendation(antecedents)

    def set_strategy(self, strategy_name):
        module = importlib.import_module('models.recommendation_strategy')

        logging.info('Change the current strategy to ' + strategy_name)
        _class = getattr(module, strategy_name)

        self._strategy = _class()
        self.training()
