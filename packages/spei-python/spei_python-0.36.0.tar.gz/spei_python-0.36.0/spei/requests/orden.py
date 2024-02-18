from lxml import etree

from spei.resources import Orden

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'


class MensajeElement(object):
    def __new__(cls, orden: Orden):
        mensaje = etree.Element('mensaje', categoria=orden.categoria)
        mensaje.append(orden.build_xml())
        return mensaje


class OrdenPagoElement(object):
    def __new__(cls, mensaje):
        ordenpago = etree.Element(etree.QName(PRAXIS_NS, 'ordenpago'))
        mensaje = etree.tostring(mensaje, xml_declaration=True, encoding='cp850')
        ordenpago.text = etree.CDATA(mensaje)
        return ordenpago


class BodyElement(object):
    def __new__(cls, ordenpago):
        body = etree.Element(etree.QName(SOAP_NS, 'Body'))
        body.append(ordenpago)
        return body


class EnvelopeElement(object):
    def __new__(cls, body):
        namespaces_uris = {
            'soapenv': SOAP_NS,
            'prax': PRAXIS_NS,
        }
        envelope = etree.Element(
            etree.QName(SOAP_NS, 'Envelope'),
            nsmap=namespaces_uris,
        )
        envelope.append(body)
        return envelope


class OrdenRequest(object):
    def __new__(cls, orden: Orden, as_string=True):
        envelope = EnvelopeElement(BodyElement(OrdenPagoElement(MensajeElement(orden))))
        if not as_string:
            return envelope
        return etree.tostring(envelope, xml_declaration=True)
