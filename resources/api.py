from flask_restful import Resource
from flask_restful import reqparse

from models.recommendation_system import RecommendationSystem


class AssociationRulesAPI(Resource):

    def __init__(self):
        self._parser = reqparse.RequestParser(bundle_errors=True)

        self._parser.add_argument('cart', action='append',
                                  required=True,
                                  help='Cart\'s items cannot be blank!')

        self._adviser = RecommendationSystem.instance()

    def post(self):
        args = self._parser.parse_args()
        recommendation = self._adviser.recommendation(args.cart)

        return {'recommendation': recommendation}, 200
