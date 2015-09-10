__author__ = "Jeremy Nelson"

import argparse
import hashlib
import subprocess
import os
try:
    import ingester
except ImportError:
    pass
from wsgiref import simple_server
from werkzeug.serving import run_simple

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CURRENT_DIR = os.path.dirname(PROJECT_ROOT)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "instance", "config.py")

def run(args):
    api =  subprocess.Popen(    
        ['python', 'api.py'])
    ingester.app.run(host='0.0.0.0', port=8000, debug=True)

def setup(args):
    if os.path.exists(CONFIG_PATH):
        print("Configuration already exists")
        return
    os.mkdir(os.path.join(PROJECT_ROOT, "instance"))
    with open(CONFIG_PATH, "w+") as config:
        config.write("""SECRET_KEY="{}"\n""".format(args.secret_key))
        tomcat_port = args.tomcat_port 
        config.write(
            """DEFAULT = {{"DEFAULT": {{"host": "{}"}} }}\n""".format(
            args.host))
        config.write(
            """TOMCAT={{"TOMCAT": {{"host": "{}",
                                    "port": {} }} }}\n""".format(
                args.tomcat_host, args.tomcat_port))
        config.write(
            """BLAZEGRAPH={{ "BLAZEGRAPH": {{"host": "{}",
                                             "path": "{}" }} }}\n""".format(
                args.blazegraph_host,
                args.blazegraph_path))
    


def main(args):
    action = args.action.lower()
    if action.startswith("run"):
        run(args)
    if action.startswith("setup"):
        setup(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['run', 'setup'],
        help = "Action for Music Library Reserves")
    parser.add_argument(
        '--secret_key',
        default = hashlib.sha1(os.urandom(30)).hexdigest())
    parser.add_argument(
        '--host',
        default = "semantic_server")
    parser.add_argument(
        '--tomcat_host',
        default =  "semantic_server")
    parser.add_argument(
        '--tomcat_port',
        default = 8080)
    parser.add_argument(
        '--blazegraph_host',
        default = "semantic_server")
    parser.add_argument(
        '--blazegraph_path',
        default = 'bigdata')
    parser.add_argument(
        '--debug',
        default=False)
    args = parser.parse_args()
    main(args)
