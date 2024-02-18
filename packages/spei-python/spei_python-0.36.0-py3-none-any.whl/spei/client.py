import base64
import logging

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256

from spei.requests import OrdenRequest
from spei.resources import Orden
from spei.responses import RespuestaResponse
from spei.utils import format_data

logger = logging.getLogger('spei')
logger.setLevel(logging.DEBUG)


class BaseClient(object):
    def __init__(
        self,
        priv_key,
        priv_key_passphrase,
        host,
        username,
        password,
        verify=False,
        http_client=requests,
    ):
        self.priv_key = priv_key
        self.priv_key_passphrase = priv_key_passphrase or None
        self.host = host
        self.session = http_client.Session()
        self.session.headers.update({'Content-Type': 'application/xml'})
        self.session.verify = verify
        self.session.auth = (username, password)

        if priv_key_passphrase:
            self.priv_key_passphrase = priv_key_passphrase.encode('ascii')

        self.pkey = serialization.load_pem_private_key(
            self.priv_key.encode('utf-8'),
            self.priv_key_passphrase,
            default_backend(),
        )

    def generate_checksum(self, message_data):
        message_as_bytes = format_data(message_data)

        signed_message = self.pkey.sign(
            message_as_bytes,
            padding.PKCS1v15(),
            SHA256(),
        )

        return base64.b64encode(signed_message)

    def registra_orden(
        self,
        orden_data,
        orden_cls=Orden,
        respuesta_response_cls=RespuestaResponse,
    ):
        checksum = self.generate_checksum(orden_data)
        orden = orden_cls(op_firma_dig=checksum, **orden_data)
        soap_request = OrdenRequest(orden)
        logger.info(soap_request)
        response = self.session.post(data=soap_request, url=self.host)
        logger.info(response.text)
        response.raise_for_status()
        return respuesta_response_cls(response.text)
