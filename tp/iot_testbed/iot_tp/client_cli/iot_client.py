import os
import hashlib
import base64
import time
import datetime
import random
import requests
import yaml
import cbor

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from client_cli.exceptions import IoTException

def _sha512(data):
    return hashlib.sha512(data).hexdigest()

def _get_date():
    current_time = datetime.datetime.utcnow()
    current_time = current_time.strftime("%Y-%m-%d-%H-%M-%S")
    return str(current_time)

def _get_metadata(image_path):
    if os.path.isfile(image_path):
        image = Image.open(image_path)
    else:
        return None

    image_meta = {}
    info = image._getexif()
    if info is not None:
        #hash the whole efix data, this will be use to identify images.
        meta_hash = _sha512(yaml.dump(info).encode('utf-8'))[24:]
        for tag, value in info.items():
            key = TAGS.get(tag, tag)
            if key == 'GPSInfo' \
               or key == 'Make' \
               or key == 'Model' \
               or key == 'Software' \
               or key == 'DateTimeOriginal':
                image_meta[key] = str(value)
            elif key == 'DateTime':
                image_meta['ModifyDate'] = str(value)
        image_meta['Hash'] = meta_hash
    else:
        image_meta['Info'] = 'No Metadata found'
        image_meta['Hash'] = str(random.randint(999,99999)*64)
    return image_meta

class IoTClient:
    def __init__(self, url, keyfile=None):
        self.url = url

        if keyfile is not None:
            try:
                with open(keyfile) as fd:
                    private_key_str = fd.read().strip()
                    fd.close()
            except OSError as err:
                    raise IoTException('Failed to read private key: {}'.format(str(err)))
            try:
                private_key = Secp256k1PrivateKey.from_hex(private_key_str)
            except ParseError as e:
                raise IoTException('Unable to load private key: {}'.format(str(e)))

            self._signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)

    def send(self, path):
        #get user public, we will use as ID
        device_id = self._signer.get_public_key().as_hex()[:4]
        #get image metadata
        metadata = _get_metadata(path)
        #get timestamp
        timestamp = _get_date()
        if metadata is None:
            return "Unable to open Image"
        return self._send_transaction(device_id, metadata, timestamp)

    def list(self):
        result = self._send_request(
            "state?address={}".format(self._get_prefix()))

        try:
            encoded_entries = yaml.safe_load(result)["data"]

            return [
                cbor.loads(base64.b64decode(entry["data"]))
                for entry in encoded_entries
            ]
        except BaseException:
            return None

    def _get_prefix(self):
        return _sha512('iot-tp'.encode('utf-8'))[0:6]

    def _get_address(self, metadata):
        prefix = self._get_prefix()
        txn_address = _sha512(yaml.dump(metadata).encode('utf-8'))[64:]
        return prefix + txn_address

    def _send_request(self, suffix, data=None, content_type=None, name=None):
        if self.url.startswith("http://"):
            url = "{}/{}".format(self.url, suffix)
        else:
            url = "http://{}/{}".format(self.url, suffix)

        headers = {}

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 4004:
                raise IoTClient("No such key: {}".format(name))
            elif not result.ok:
                raise IoTClient("Error {}: {}".format(result.status_code, result.reason))
        except requests.ConnectionError as err:
            raise IoTClient('Failed to connect to REST API: {}'.format(err))
        except BaseException as err:
            raise IoTClient(err)

        return result.text

    def _send_transaction(self, device_id, metadata, timestamp):
        payload = cbor.dumps({
            'device_id' : device_id,
            'metadata'  : metadata,
            'timestamp' :timestamp,
        })

        address = self._get_address(metadata)

        header = TransactionHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            family_name="iot-tp",
            family_version="1.0",
            inputs=[address],
            outputs=[address],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self._signer.get_public_key().as_hex(),
            nonce=hex(random.randint(0, 2**64))
        ).SerializeToString()

        signature = self._signer.sign(header)

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        batch_list = self._create_batch_list([transaction])
        batch_id = batch_list.batches[0].header_signature

        return self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream',
        )

    def _create_batch_list(self, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)

        return BatchList(batches=[batch])
