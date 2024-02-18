import re
from datetime import datetime
from decimal import Decimal
from typing import Any, AnyStr, Dict, List


def format_data(message: Dict[AnyStr, Any]) -> bytes:
    message_data = [
        _fecha_to_bytearray(message['op_fecha_oper']),
        _clave_to_bytearray(message['op_ins_clave_ord']),
    ]

    if message.get('op_ins_clave_ben'):
        message_data.append(
            _clave_to_bytearray(message['op_ins_clave_ben']),
        )

    message_data.append(
        _to_byte_array(message['op_cve_rastreo'], add_zero_byte=True),
    )

    message_data.append(
        _monto_to_bytearray(message['op_monto']),
    )

    if message.get('op_cuenta_ord'):
        message_data.append(
            _to_byte_array(message['op_cuenta_ord'], add_zero_byte=True),
        )

    if message.get('op_cuenta_ben'):
        message_data.append(
            _to_byte_array(message['op_cuenta_ben'], add_zero_byte=True),
        )

    if message.get('op_cuenta_ben_2'):
        message_data.append(
            _to_byte_array(message['op_cuenta_ben_2'], add_zero_byte=True),
        )

    return _list_to_bytes(message_data)


def split_amount(amount):
    amount_as_cents = int(Decimal(str(amount)) * 100)
    high = 0
    low = amount_as_cents
    tens_of_millons = amount_as_cents // 10**9
    if tens_of_millons:
        high = tens_of_millons
        low = amount_as_cents - (tens_of_millons * 10**9)
    return high, low


def _fecha_to_bytearray(fecha_operacion: int) -> bytearray:
    fecha_operacion = datetime.strptime(str(fecha_operacion), '%Y%m%d')

    day = int.to_bytes(int(fecha_operacion.day), 1, 'big')
    month = int.to_bytes(int(fecha_operacion.month), 1, 'big')
    year = int.to_bytes(int(fecha_operacion.year), 2, 'big')
    return day + month + year


def _clave_to_bytearray(clave: str) -> bytearray:
    return int.to_bytes(int(clave), 4, 'big')


def _monto_to_bytearray(amount: int) -> bytearray:
    high, low = split_amount(amount)
    high = int.to_bytes(int(high), 4, 'big')
    low = int.to_bytes(int(low), 4, 'big')
    return high + low


def _to_byte_array(
    value: str,  # noqa: WPS110
    add_zero_byte: bool = False,
) -> bytearray:
    encoded = value.encode('utf-8')
    bytes_ = bytearray(encoded)
    if add_zero_byte:
        bytes_.append(0)
    return bytes_


def _list_to_bytes(message_data: List[Any]) -> bytes:
    res = bytearray()
    for field in message_data:
        for element in field:
            res.append(element)
    return bytes(res)


def to_upper_camel_case(string):
    temp = string.split('_')
    new_string = [ele.title() for ele in temp]
    return ''.join(new_string)


def to_snake_case(string):
    return re.sub('(.)([A-Z0-9])', r'\1_\2', str(string)).lower()
