from lxml import etree

from spei.resources import CDA

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/EnvioCda/'


class CDAElement(object):
    def __new__(cls, element):
        cda = etree.Element(
            etree.QName(PRAXIS_NS, 'generaCda'),
        )
        cda.append(element)
        return cda


class BodyElement(object):
    def __new__(cls, respuesta):
        body = etree.Element(etree.QName(SOAP_NS, 'Body'))
        body.append(respuesta)
        return body


class EnvelopeElement(object):
    def __new__(cls, body):
        namespaces_uris = {
            'soapenv': SOAP_NS,
            'env': PRAXIS_NS,
        }
        envelope = etree.Element(
            etree.QName(SOAP_NS, 'Envelope'),
            nsmap=namespaces_uris,
        )
        envelope.append(body)
        return envelope


class CDARequest(object):
    def __new__(cls, mensaje: CDA, as_string=True):
        envelope = EnvelopeElement(BodyElement(CDAElement(mensaje.build_xml())))  # noqa: E501
        if not as_string:
            return envelope
        return etree.tostring(envelope, xml_declaration=True)
