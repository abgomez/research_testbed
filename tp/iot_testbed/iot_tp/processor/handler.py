import logging
import hashlib
import cbor
import yaml

from pprint import pprint
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'iot-tp'

IOT_ADDRESS_PREFIX = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[0:6]

def make_iot_address(metadata):
    return IOT_ADDRESS_PREFIX + hashlib.sha512(yaml.dump(metadata).encode('utf-8')).hexdigest()[-64:]

class IotTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [IOT_ADDRESS_PREFIX]

    def apply(self, transaction, context):
        device_id, metadata, timestamp = _unpack_transaction(transaction)

        state = _get_state_data(metadata, context)

        updated_state = _do_iot(device_id, metadata, timestamp, state)

        _set_state_data(metadata, updated_state, context)

def _unpack_transaction(transaction):
    try:
        content = cbor.loads(transaction.payload)
    except:
        raise InvalidTransaction('Invalid payload serialization')

    try:
        device_id = content['device_id']
    except AttributeError:
        raise InvalidTransaction('device_id is required')

    try:
        metadata = content['metadata']
    except AttributeError:
        raise InvalidTransaction('metadata is required')

    try:
        timestamp = content['timestamp']
    except AttributeError:
        raise InvalidTransaction('timestamp is required')

    return device_id, metadata, timestamp

def _get_state_data(metadata, context):
    address = make_iot_address(metadata)

    state_entries = context.get_state([address])

    try:
        return cbor.loads(state_entries[0].data)
    except IndexError:
        return {}
    except:
        raise InternalError('Failed to load state data')

def _set_state_data(metadata, state, context):
    address = make_iot_address(metadata)

    encoded = cbor.dumps(state)

    addresses = context.set_state({address: encoded})

    if not address:
        raise InternalError('State error')

def _do_iot(device_id, metadata, timestamp, state):
    print ("Setting {d}, {m}, {t}".format(d=device_id, m=metadata, t=timestamp))
    msg = 'Setting "{d}", "{m}", "{t}"'.format(d=device_id, m=metadata, t=timestamp)
    LOGGER.debug(msg)

    address = make_iot_address(metadata)
    #if address in state:
    #    raise InvalidTransaction('Image already exists: {i}'. format(i=state[address]))

    updated = {k: v for k, v in state.items()}

    updated[address] = cbor.dumps({
        'device_id' : device_id,
        'metadata'  : metadata,
        'timestamp' :timestamp,
    })

    #updated[address] = str(device_id) + str(metadata) + str(timestamp)

    return updated
