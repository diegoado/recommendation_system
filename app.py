import logging
from logging.config import dictConfig
import os
import sys
import traceback

from flask import Flask
from flask import got_request_exception
from flask import render_template
from flask_restful import Api

from common import utils
from resources.api import AssociationRulesAPI
from models.recommendation_system import RecommendationSystem

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def log_exception(sender, exception):
    """ Log an exception to our logging framework """
    regex = utils.SRC_REGEX

    files_path = [path[0] for path in traceback.extract_tb(sys.exc_info()[-1])]
    files_path = filter(regex.search, files_path)

    logger = sender.logger

    if app.debug:
        logger.debug(traceback.print_exc())

    if len(files_path) > 0:
        filename = files_path[0][:-3].split(os.path.sep)[-1]
        logger.error('Got exception during processing request on file %s: %s',
                     filename, exception)
    else:
        logger.error('Got exception during processing request: %s', exception)


app = Flask(__name__)
got_request_exception.connect(log_exception, app)


@app.before_first_request
def restore_service_state():
    logging.info('Server started, getting online retail data.')
    RecommendationSystem.instance().training()


@app.route('/', methods=['GET'])
def index():
    items = RecommendationSystem.instance().items()
    return render_template('index.html',
                           products=items, assailable=utils.ASSAILABLE)


api = Api(app, catch_all_404s=True)
api.add_resource(AssociationRulesAPI, '/recommendation_system')

