from flask_restful import Resource
from flask_restful import reqparse

from models.recommendation_system import RecommendationSystem


class RecommendationSystemAPI(Resource):

    strategies = ('Item2VecStrategy', 'AssociationRulesStrategy')

    def __init__(self):
        self._recommendation_parser = reqparse.RequestParser(bundle_errors=True)
        self._strategy_parser = self._recommendation_parser.copy()

        self._recommendation_parser.\
            add_argument('cart', action='append',
                         required=True, help='Cart\'s items cannot be blank!')

        self._strategy_parser.\
            add_argument('strategy',
                         required=True,
                         choices=RecommendationSystemAPI.strategies,
                         help='Unknown strategy: {error_msg}!')

        self._adviser = RecommendationSystem.instance()

    def post(self):
        args = self._recommendation_parser.parse_args()
        recommendation = self._adviser.recommendation(args.cart)

        return {'recommendation': recommendation}, 200

    def patch(self):
        args = self._strategy_parser.parse_args()
        self._adviser.set_strategy(args.strategy)

        return 200
