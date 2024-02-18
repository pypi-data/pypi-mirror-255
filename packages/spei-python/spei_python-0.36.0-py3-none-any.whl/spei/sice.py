import logging
from urllib.parse import urljoin

import requests

from spei.requests import CDARequest
from spei.resources import CDA
from spei.responses import AcuseResponse

logger = logging.getLogger('sice')
logger.setLevel(logging.DEBUG)


class BaseClient(object):
    def __init__(
        self,
        host,
        verify=False,
        http_client=requests,
    ):
        self.host = host
        self.session = http_client.Session()
        self.session.headers.update({'Content-Type': 'application/xml'})
        self.session.verify = verify

    def registra_cda(
        self,
        cda_data,
        cda_cls=CDA,
        acuse_response_cls=AcuseResponse,
        endpoint='/enlace-cep/EnvioCdaPortTypeImpl?wsdl',
    ):
        orden = cda_cls(**cda_data)
        soap_request = CDARequest(orden)
        logger.info(soap_request)
        cda_url = urljoin(self.host, endpoint)
        response = self.session.post(data=soap_request, url=cda_url)
        logger.info(response.text)
        response.raise_for_status()
        return acuse_response_cls(response.text)
