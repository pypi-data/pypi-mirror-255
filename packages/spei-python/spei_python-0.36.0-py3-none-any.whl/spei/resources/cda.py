from lxml import etree
from pydantic import BaseModel

from spei import types
from spei.utils import to_snake_case, to_upper_camel_case  # noqa: WPS347

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'
ENVIO_PRAXIS_NS = 'http://www.praxis.com.mx/EnvioCda/'


class CDA(BaseModel):
    id: int
    mensaje_id: int
    op_fecha_oper: str
    op_fecha_abono: str
    op_hora_abono: str

    op_cve_rastreo: str

    op_folio_orig_odp: int
    op_folio_orig_paq: int

    op_clave_emisor: str
    op_nombre_emisor: str

    op_tipo_pag: types.TipoPagoOrdenPago

    op_monto: str

    op_nombre_receptor: str

    op_concepto_pag: str = None
    op_concepto_pag_2: str = None

    op_nom_ord: str = None
    op_tp_cta_ord: types.TipoCuentaOrdenPago = None
    op_cuenta_ord: str = None
    op_rfc_curp_ord: str = None

    op_nom_ben: str = None
    op_tp_cta_ben: types.TipoCuentaOrdenPago = None
    op_cuenta_ben: str = None
    op_rfc_curp_ben: str = None

    op_iva: str = None
    op_hora_00: str = None

    class Config:  # noqa: WPS306, WPS431
        use_enum_values = True

    def build_xml(self):
        mensaje = etree.Element(
            etree.QName(ENVIO_PRAXIS_NS, 'datosCda'),
            idCda=str(self.id),
            idMensaje=str(self.mensaje_id),
            nsmap={'env': ENVIO_PRAXIS_NS},
        )

        elements = self.dict(exclude_none=True, exclude={'id', 'mensaje_id'})

        for element, value in elements.items():  # noqa: WPS110
            if element in self.__fields__:
                upper_camel_case_element = to_upper_camel_case(element)
                subelement = etree.SubElement(mensaje, etree.QName(ENVIO_PRAXIS_NS, upper_camel_case_element))  # noqa: E501
                subelement.text = str(value)

        return mensaje

    @classmethod
    def parse_xml(cls, mensaje_element):
        genera_cda = mensaje_element.find('generaCda')
        datos_cta = genera_cda.find('datosCda')

        cda_data = {
            'id': datos_cta.attrib['idCda'],
            'mensaje_id': datos_cta.attrib['idMensaje'],
        }

        for element in datos_cta.getchildren():
            tag = to_snake_case(element.tag)
            if tag in cls.__fields__:
                cda_data[tag] = element.text

        return cls(**cda_data)
