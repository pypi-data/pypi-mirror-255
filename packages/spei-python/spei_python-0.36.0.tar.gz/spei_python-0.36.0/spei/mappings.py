from types import MappingProxyType

from spei.resources import orden
from spei.types import CategoriaOrdenPago, TipoPagoOrdenPago

ORDEN_RESPONSES = MappingProxyType({
    CategoriaOrdenPago.odps_liquidadas_abonos: CategoriaOrdenPago.odps_liquidadas_abonos_respuesta,  # noqa: E501
    CategoriaOrdenPago.odps_liquidadas_cargos: CategoriaOrdenPago.odps_liquidadas_cargos_respuesta,  # noqa: E501
    CategoriaOrdenPago.odps_canceladas_local: CategoriaOrdenPago.odps_canceladas_local_respuesta,  # noqa: E501
    CategoriaOrdenPago.odps_canceladas_x_banxico: CategoriaOrdenPago.odps_canceladas_x_banxico_respuesta,  # noqa: E501
})

ORDEN_PAYMENT_TYPES = MappingProxyType({
    TipoPagoOrdenPago.devolucion_no_acreditada: orden.DevolucionNoAcreditada,
    TipoPagoOrdenPago.tercero_a_tercero: orden.TerceroATercero,
    TipoPagoOrdenPago.tercero_a_ventanilla: orden.TerceroAVentilla,
    TipoPagoOrdenPago.tercero_a_tercero_vostro: orden.TerceroATerceroVostro,
    TipoPagoOrdenPago.tercero_a_participante: orden.TerceroAParticipante,
    TipoPagoOrdenPago.participante_a_tercero: orden.ParticipanteATercero,
    TipoPagoOrdenPago.participante_a_tercero_vostro: orden.ParticipanteATerceroVostro,
    TipoPagoOrdenPago.participante_a_participante: orden.ParticipanteAParticipante,
    TipoPagoOrdenPago.tercero_a_tercero_fsw: orden.TerceroATerceroFSW,
    TipoPagoOrdenPago.tercero_a_tercero_vostro_fsw: orden.TerceroATerceroVostroFSW,
    TipoPagoOrdenPago.participante_a_tercero_fsw: orden.ParticipanteATerceroFSW,
    TipoPagoOrdenPago.participante_a_tercero_vostro_fsw: orden.TerceroATerceroFSW,
    TipoPagoOrdenPago.nomina: orden.Nomina,
    TipoPagoOrdenPago.pago_factura: orden.PagoFactura,
    TipoPagoOrdenPago.devolucion_extemporanea_no_acreditada: orden.DevolucionExtemporaneaNoAcreditada,
    TipoPagoOrdenPago.devolucion_acreditada: orden.DevolucionAcreditada,
    TipoPagoOrdenPago.devolucion_extemporanea_acreditada: orden.DevolucionExtemporaneaAcreditada,
    TipoPagoOrdenPago.cobros_presenciales_de_una_ocasion: orden.CobrosPresencialesUnaOcasion,
    TipoPagoOrdenPago.cobros_no_presenciales_de_una_ocasion: orden.CobrosNoPresencialesUnaOcasion,
    TipoPagoOrdenPago.cobros_no_presenciales_recurrentes: orden.CobrosNoPresencialesRecurrentes,
    TipoPagoOrdenPago.cobros_no_presenciales_a_nombre_de_tercero: orden.CobrosNoPresencialesNoRecurrentesTercero,
    TipoPagoOrdenPago.devolucion_especial_acreditada: orden.DevolucionEspecialAcreditada,
    TipoPagoOrdenPago.devolucion_extemporanea_especial_acreditada: orden.DevolucionEspecialAcreditada,
})
