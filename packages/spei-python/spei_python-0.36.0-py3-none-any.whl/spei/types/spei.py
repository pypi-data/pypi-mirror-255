from enum import Enum

from spei.errors import generate_error_codes


class TipoPagoOrdenPago(str, Enum):
    devolucion_no_acreditada = '0'
    tercero_a_tercero = '1'
    tercero_a_ventanilla = '2'
    tercero_a_tercero_vostro = '3'
    tercero_a_participante = '4'
    participante_a_tercero = '5'
    participante_a_tercero_vostro = '6'
    participante_a_participante = '7'
    tercero_a_tercero_fsw = '8'
    tercero_a_tercero_vostro_fsw = '9'
    participante_a_tercero_fsw = '10'
    participante_a_tercero_vostro_fsw = '11'
    nomina = '12'
    pago_por_celular = '14'
    pago_factura = '15'
    devolucion_extemporanea_no_acreditada = '16'
    devolucion_acreditada = '17'
    devolucion_extemporanea_acreditada = '18'
    cobros_presenciales_de_una_ocasion = '19'
    cobros_no_presenciales_de_una_ocasion = '20'
    cobros_no_presenciales_recurrentes = '21'
    cobros_no_presenciales_a_nombre_de_tercero = '22'
    devolucion_especial_acreditada = '23'
    devolucion_extemporanea_especial_acreditada = '24'


class TipoOrdenPago(str, Enum):
    envio = 'E'
    recepcion = 'R'


class TipoCuentaOrdenPago(str, Enum):
    inexsitente = '-1'
    desconocida = '0'
    desconocida_1 = '1'
    desconocida_2 = '2'
    tarjeta_debito = '3'
    cuenta_vostro = '4'
    custodia_de_valores = '5'
    cuenta_vostro_1 = '6'
    cuenta_vostro_2 = '7'
    cuenta_vostro_3 = '8'
    cuenta_vostro_4 = '9'
    telefono = '10'
    descripcion_11 = '11'
    clabe = '40'
    cuenta_subvostro_1 = '41'
    cuenta_subvostro_2 = '42'
    horario = '43'


class PrioridadOrdenPago(str, Enum):
    normal = 0
    alta = 1


class CategoriaOrdenPago(str, Enum):
    respuesta = 'RESPUESTA'
    cargar_odp = 'CARGAR_ODP'
    cargar_odp_respuesta = 'CARGAR_ODP_RESPUESTA'
    odps_liquidadas_cargos = 'ODPS_LIQUIDADAS_CARGOS'
    odps_liquidadas_cargos_respuesta = 'ODPS_LIQUIDADAS_CARGOS_RESPUESTA'
    odps_liquidadas_abonos = 'ODPS_LIQUIDADAS_ABONOS'
    odps_liquidadas_abonos_respuesta = 'ODPS_LIQUIDADAS_ABONOS_RESPUESTA'
    odps_canceladas_local = 'ODPS_CANCELADAS_LOCAL'
    odps_canceladas_local_respuesta = 'ODPS_CANCELADAS_LOCAL_RESPUESTA'
    odps_canceladas_x_banxico = 'ODPS_CANCELADAS_X_BANXICO'
    odps_canceladas_x_banxico_respuesta = 'ODPS_CANCELADAS_X_BANXICO_RESPUESTA'


class EstadoOrdenPago(str, Enum):
    liquidada = 'LQ'
    liberada = 'L'
    capturada = 'C'
    autorizada = 'A'


class ClaveOrdenanteOrdenPago(int, Enum):
    AMU = 90699
    GEMELA = 699


class FolioOrdenPago(str, Enum):
    cargar_odp = '-1'


class MedioEntregaOrdenPago(str, Enum):
    local = '1'
    spei = '2'
    archivos = '3'
    devoluciones = '4'
    devoluciones_abono = '5'
    ce = '6'
    cei = '7'
    hsbc = '8'
    htvf = '9'
    dtp = '10'
    ifai = '13'
    swift = '17'
    nomina = '18'


class TopologiaOrdenPago(str, Enum):
    notify_on_payment_settlement = 'V'
    notify_on_payment_instruction = 'T'


class TipoDevolucionOrdenPago(str, Enum):
    account_not_found = 1
    account_blocked = 2
    account_canceled = 3
    account_number_is_not_fondea = 4
    missing_required_data = 14
    invalid_payment_type = 15
    invalid_operation_type = 16
    invalid_account_type = 17
    invalid_character = 19
    autorized_limit_exceeded = 20
    deposit_limit_exceeded = 21
    invalid_optional_payment_type = 27
    duplicated_tracking_code = 30


CodigoError = generate_error_codes()
