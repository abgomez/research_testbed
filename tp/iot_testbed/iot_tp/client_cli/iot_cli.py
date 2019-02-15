import argparse
import getpass
import logging
import os
import sys
import traceback
import cbor
import yaml

from pprint import pprint
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from colorlog import ColoredFormatter

from client_cli.exceptions import IoTException
from client_cli.iot_client import IoTClient

DISTRIBUTION_NAME = 'iot-tp'
DEFAULT_URL = 'http://127.0.0.1:8008'

def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog

def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    return parent_parser

def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    add_send_image_parser(subparsers, parent_parser)
    add_list_image_parser(subparsers, parent_parser)

    return parser

def add_send_image_parser(subparsers, parent_parser):
    message = 'Submit an image to the network. <name> <path>'

    parser = subparsers.add_parser(
        'send',
        parents=[parent_parser],
        description=message,
        help='Submit Image')

    parser.add_argument(
        'name',
        type=str,
        help='image name')

    parser.add_argument(
        '--path',
        type=str,
        help='image path')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

def send_image(args):
    name = args.name
    if args.path is None:
        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        image_path = path + "/iot_tp/images/" + name
    else:
        path = args.path
        image_path = path + name

    print (image_path)

    client = _get_client(args)
    response = client.send(image_path)
    print(response)

def add_list_image_parser(subparsers, parent_parser):
    message = 'Shows the values of all transactions in state.'

    parser = subparsers.add_parser(
        'list',
        parents=[parent_parser],
        description=message,
        help='Displays all iot transactions')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

def list_image(args):
    client = _get_client(args, False)
    results = client.list()
    #pprint (results)
    for txns in results:
        for txn_id, txn_info in txns.items():
            content = cbor.loads(txn_info)
            pprint (content)

def _get_client(args, read_key_file=True):
    return IoTClient(
        url=DEFAULT_URL if args.url is None else args.url,
        keyfile=_get_keyfile(args) if read_key_file else None)

def _get_keyfile(args):
    try:
        if args.keyfile is not None:
            return args.keyfile
    except AttributeError:
        return None

    real_user = getpass.getuser()
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, real_user)

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose
    setup_loggers(verbose_level=verbose_level)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'send':
        send_image(args)
    elif args.command == 'list':
        list_image(args)
    else:
        raise IoTException("Invalid command: {}".format(args.command))

def main_wrapper():
    try:
        main()
    except (IoTException) as err:
        print ("Error: :".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as e:
        raise e
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
