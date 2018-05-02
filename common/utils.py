import logging
import re
import traceback
import threading
import time

import requests

SERVER_ADDRESS = 'localhost'
SRC_REGEX = re.compile(r'\\association_rules\\')


ASSAILABLE = [
    'ALARM CLOCK BAKELIKE GREEN',
    'ALARM CLOCK BAKELIKE PINK',
    'ALARM CLOCK BAKELIKE RED',
    'CHILDRENS CUTLERY DOLLY GIRL',
    'CHILDRENS CUTLERY SPACEBOY',
    'DOLLY GIRL LUNCH BOX',
    'LUNCH BAG APPLE DESIGN',
    'LUNCH BAG DOLLY GIRL DESIGN',
    'LUNCH BAG RED RETROSPOT',
    'LUNCH BAG SPACEBOY DESIGN',
    'LUNCH BAG WOODLAND',
    'LUNCH BOX WITH CUTLERY RETROSPOT',
    'PACK OF 6 SKULL PAPER CUPS',
    'PACK OF 6 SKULL PAPER PLATES',
    'PLASTERS IN TIN CIRCUS PARADE',
    'PLASTERS IN TIN SPACEBOY',
    'PLASTERS IN TIN STRONGMAN',
    'RED RETROSPOT MINI CASES',
    'ROUND SNACK BOXES SET OF 4 FRUITS',
    'ROUND SNACK BOXES SET OF 4 WOODLAND',
    'SET/6 RED SPOTTY PAPER CUPS',
    'SET/6 RED SPOTTY PAPER PLATES',
    'SET/20 RED RETROSPOT PAPER NAPKINS',
    'SPACEBOY LUNCH BOX',
    'STRAWBERRY LUNCH BOX WITH CUTLERY'
]


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
