from lxml import etree

from spei.resources import Respuesta


class RespuestaElement(object):
    def __new__(cls, mensaje_element, respuesta_cls: Respuesta = Respuesta):
        respuesta = mensaje_element.find('respuesta')
        categoria = mensaje_element.attrib['categoria']
        return respuesta_cls.parse_xml(respuesta, categoria)


class MensajeElement(object):
    def __new__(cls, respuesta):
        return etree.fromstring(  # noqa: S320
            bytes(respuesta.text, encoding='cp850'),
        )


class RootElement(object):
    def __new__(cls, body):
        return body.find('{http://www.praxis.com.mx/}respuesta')


class BodyElement(object):
    def __new__(cls, mensaje):
        return mensaje.find(
            '{http://schemas.xmlsoap.org/soap/envelope/}Body',
        )


class RespuestaResponse(object):
    def __new__(cls, respuesta):
        mensaje = etree.fromstring(respuesta)  # noqa: S320
        return RespuestaElement(MensajeElement(RootElement(BodyElement((mensaje)))))
