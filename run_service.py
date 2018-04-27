import datetime
import logging
import time
import signal
import sys

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer

from app import app
from common.utils import SERVER_ADDRESS, ping

WAIT_SECONDS_BEFORE_SHUTDOWN = 1

define('port', default=3030, help='Run on the given port', type=int)

http_server = None


def sig_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback(shutdown)


def initialize(use_ssl=False):
    logging.info('Initializing http server on port %d' % options.port)

    server_config = {
        'protocol': 'https' if use_ssl else 'http',
        'address': SERVER_ADDRESS,
        'port': options.port
    }
    url = '%(protocol)s://%(address)s:%(port)s/' % server_config

    ping(url, timeout=6,
         fail_callback=lambda: abort(signal.SIGABRT))


def abort(sig, frame=None):
    logging.error('Fatal error detected, impossible to start recommendation '
                  'system, shutdown application')

    sig_handler(sig, frame)


def shutdown():
    logging.info('Stopping http server')
    http_server.stop()

    logging.info('Will shutdown in %s seconds...', WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = IOLoop.instance()

    deadline = time.time() + WAIT_SECONDS_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logging.info('Shutdown')
    stop_loop()


def main():
    options.parse_command_line()
    global http_server

    webservice = Application([
        # pass off to Flask if we're not using tornado
        (r'.*', FallbackHandler, dict(fallback=WSGIContainer(app))), ],
        debug=True)

    http_server = HTTPServer(webservice, ssl_options=None)
    http_server.listen(options.port, address=SERVER_ADDRESS)

    signal.signal(signal.SIGINT,  sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    IOLoop.instance().add_timeout(datetime.timedelta(seconds=5), initialize)
    IOLoop.instance().start()

    logging.info('Exit...')


if __name__ == '__main__':
    main()
    sys.exit(0)
