import base64
import datetime
from enum import Enum
from os import urandom

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

IV_LIMIT = 16


class SearchCriteria(Enum):
    TRACKING_CODE = 'T'
    REFERENCE_NUMBER = 'R'


class CepGenerator(object):
    def __init__(self, key_base64, rng=urandom):
        self.key_base64 = key_base64
        self.rng = rng

    def generate_cep(
        self,
        date: datetime.datetime,
        search_criteria: SearchCriteria,
        search_value: str,
        origin_bank_code: str,
        receiver_bank_code: str,
        account_number: str,
        amount: float,
    ) -> str:
        formatted_date = self._format_date(date)
        string = '{0}|{1}|{2}|{3}|{4}|{5}|{6}'.format(
            formatted_date,
            search_criteria.value,
            search_value,
            origin_bank_code,
            receiver_bank_code,
            account_number,
            amount,
        )

        return self._encrypt_string(string)

    def decrypt_string(self, encrypted_data_base64: str) -> str:  # noqa: WPS210
        backend = default_backend()
        encrypted_data = base64.b64decode(encrypted_data_base64)
        iv = encrypted_data[:IV_LIMIT]
        cipher = Cipher(
            algorithms.AES(base64.b64decode(self.key_base64)),
            modes.CBC(iv),
            backend=backend,
        )
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(
            encrypted_data[IV_LIMIT:],
        ) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

        return unpadded_data.decode()

    def _format_date(self, date: datetime.datetime) -> str:
        return date.strftime('%Y%m%d')

    def _encrypt_string(self, string: str) -> str:  # noqa: WPS210
        backend = default_backend()
        iv = self.rng(IV_LIMIT)
        cipher = Cipher(
            algorithms.AES(base64.b64decode(self.key_base64)),
            modes.CBC(iv),
            backend=backend,
        )
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(string.encode()) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        encrypted_data_base64 = base64.b64encode(iv + encrypted_data)

        return encrypted_data_base64.decode()
