import logging
import re
import traceback
import threading
import time

import requests

SERVER_ADDRESS = 'localhost'
SRC_REGEX = re.compile(r'\\association_rules\\')


def ping(url, timeout=60, fail_callback=None):

    def start_loop():
        is_ok = False
        limit = time.time() + timeout

        while not is_ok and time.time() <= limit:
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    is_ok = True
            except:
                logging.debug(traceback.print_exc())

            time.sleep(timeout * .1)

        if fail_callback is not None and not is_ok:
            fail_callback()

    logging.info('Testing http server, sending a request to URL %s' % url)

    thread = threading.Thread(target=start_loop)
    thread.daemon = True
    thread.start()
