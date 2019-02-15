import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'iot_tp'))

from client_cli.iot_cli import main_wrapper

if __name__ == '__main__':
    main_wrapper()
