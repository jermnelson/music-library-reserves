__author__ = "Jeremy Nelsn"

import argparse
import os
import ingester 
import api

from wsgiref import simple_server
from werkzeug.serving import run_simple

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CURRENT_DIR = os.path.dirname(PROJECT_ROOT)

def run():
    ingester.app.run(host='0.0.0.0', port=8000, debug=True)
    run_simple(
        '0.0.0.0', 
        8756,
        api.app,
        use_reloader=False)
#    run_simple(
#        '0.0.0.0',
#        8000,
#        ingester.app,
#        use_reloader=False)

def main(args):
    action = args.action.lower()
    if action.startswith('run'):
        run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['run'],
        help = "Action for Music Library Reserves")
    args = parser.parse_args()
    main(args)
