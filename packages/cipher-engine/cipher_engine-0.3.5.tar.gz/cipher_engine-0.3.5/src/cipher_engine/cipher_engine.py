"""
# CipherEngine

This module provides functions for cryptographic key generation, \
encryption and decryption for text and files using \
the `Fernet` symmetric key cryptography library, `MultiFernet` and `PBKDF2HMAC`.

### Functions:
    - `generate_crypto_key(**kwargs) -> str`: Generates a cryptographic key based on specified parameters.
    - `encrypt_file(**kwargs) -> NamedTuple`: Encrypts a file and returns information about the process.
    - `decrypt_file(**kwargs) -> NamedTuple`: Decrypts a file using encryption details from a previous process.
    - `encrypt_text(**kwargs) -> NamedTuple`: Encrypts text and returns information about the process.
    - `decrypt_text(**kwargs) -> NamedTuple`: Decrypts text using encryption details from a previous process.

### Important Notes:
    - The cryptographic operations use the `Fernet` library for symmetric key cryptography.
    - The `generate_crypto_key` function allows customization of key generation parameters.
    - The `encrypt_file` and `decrypt_file` functions provide file encryption and decryption capabilities.
    - The `encrypt_text` and `decrypt_text` functions handle encryption and decryption of text data.

### Cryptographic Attributes:
    - Various parameters such as `num_of_salts`, `include_all_chars`, `exclude_chars`, and `special_keys` \
        customize the cryptographic operations during key and text generation.

### Exception Handling:
    - The module raises a `CipherException` with specific messages for various error scenarios.

For detailed information on each function and its parameters, refer to the individual docstrings \
or documentations.
"""


import ast
import os
import re
import sys
import math
import json
import psutil
import secrets
import operator
import inspect
import base64
import hashlib
import shutil
import logging
import operator
import configparser
import numpy as np
import tkinter as tk
from copy import deepcopy
from tkinter import simpledialog
from pathlib import Path
from logging import Logger
from datetime import datetime
from functools import partial
from itertools import cycle, islice, tee, chain
from dataclasses import dataclass, field
from collections import OrderedDict, namedtuple
from concurrent.futures import ThreadPoolExecutor
from string import digits, punctuation, ascii_letters, whitespace
from typing import (
    Any,
    AnyStr,
    Iterable,
    NamedTuple,
    TypeVar,
    Optional,
    Union,
    Literal,
    NoReturn,
)
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_logger(
    *,
    name: str = __name__,
    level: int = logging.DEBUG,
    formatter_kwgs: dict = None,
    handler_kwgs: dict = None,
    mode: str = "a",
    write_log: bool = True,
) -> Logger:
    logging.getLogger().setLevel(logging.NOTSET)
    _logger = logging.getLogger(name)

    if logging.getLevelName(level):
        _logger.setLevel(level=level)

    file_name = Path(__file__).with_suffix(".log")
    _formatter_kwgs = {
        **{
            "fmt": "[%(asctime)s][LOG %(levelname)s]:%(message)s",
            "datefmt": "%Y-%m-%d %I:%M:%S %p",
        },
        **(formatter_kwgs or {}),
    }
    _handler_kwgs = {**{"filename": file_name, "mode": mode}, **(handler_kwgs or {})}

    formatter = logging.Formatter(**_formatter_kwgs)

    if write_log:
        file_handler = logging.FileHandler(**_handler_kwgs)
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)

    if level != logging.DEBUG:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        _logger.addHandler(stream_handler)

    return _logger


logger = get_logger(level=logging.INFO, write_log=False)
P = TypeVar("P", Path, str)


class CipherException(BaseException):
    def __init__(self, *args, log_method=logger.critical):
        self.log_method = log_method
        super().__init__(*args)
        self.log_method(*args)


@dataclass(kw_only=True)
class _BaseCryptoEngine:
    """
    Base crypotgraphic class for the CipherEngine hierarchy, providing common attributes and functionality \
    for generating cryptographic keys, salt values, and RSA key pairs.
    """

    num_of_salts: int = field(repr=False, default=None)
    salt_bytes_size: int = field(repr=False, default=None)
    rsa_passphrase: str = field(repr=False, default=None)
    rsa_iterations: int = field(repr=False, default=None)
    rsa_bits_size: Literal[1024, 2048, 3072] = field(repr=False, default=None)
    exclude_chars: str = field(repr=False, default=None)
    include_all_chars: Optional[bool] = field(repr=False, default=False)
    _RSA_BITS = (1024, 2048, 3072)
    _PKCS_VALUE = 8
    _MAX_TOKENS = int(1e5)
    _MAX_KEYLENGTH: int = 32
    _ALL_CHARS: str = digits + ascii_letters + punctuation
    _MAX_CAPACITY = int(1e8)
    _EXECUTOR = ThreadPoolExecutor()

    def _validate_numsalts(cls, __nsalt: int) -> int:
        if __nsalt:
            num_salt = cls._validate_object(__nsalt, type_is=int, arg="Number of Salts")
            if num_salt >= cls._MAX_TOKENS:
                CipherException(
                    f"WARNING: The specified 'num_of_salts' surpasses the recommended limit for {MultiFernet.__name__}. "
                    "Adding a large number of salts for key deriviation can result in computatonal power. "
                    f"It is recommended to keep the number of keys within 2 <= x <= 5 "
                    "for efficient key rotation and optimal performance.\n"
                    f"Specified Amount: {num_salt:_}\n"
                    f"Recommended Amount: 2",
                    log_method=logger.warning,
                )
            return num_salt
        else:
            raise CipherException(
                "Number of keys to be generated must be of value >=1. "
                f"The specified value is considered invalid ({__nsalt})"
            )

    @staticmethod
    def _base64_key(__key: str, base_type="encode") -> Union[bytes, None]:
        base = [base64.urlsafe_b64decode, base64.urlsafe_b64encode][
            base_type == "encode"
        ]
        try:
            return base(__key)
        except AttributeError as attr_error:
            raise CipherException(
                f"Failed to derive encoded bytes from {__key!r}. " f"\n{attr_error}"
            )

    @staticmethod
    def _gen_random(__size: int = 16) -> bytes:
        return secrets.token_bytes(__size)

    @property
    def rsa_keypair(self):
        bits_size = self.rsa_bits_size if self.rsa_bits_size in self._RSA_BITS else 3072
        return RSA.generate(bits_size, randfunc=secrets.token_bytes)

    @property
    def gen_salts(self) -> Union[str, bytes]:
        if self.num_of_salts:
            num_of_salts = self._validate_numsalts(self.num_of_salts)
        else:
            num_of_salts = 2

        if self.salt_bytes_size:
            self.salt_bytes_size = self._validate_object(
                self.salt_bytes_size, type_is=int, arg="Salt Bytes"
            )
        else:
            self.salt_bytes_size = 32
        return (
            self._gen_random(self.salt_bytes_size) for _ in range(1, num_of_salts + 1)
        )

    @classmethod
    def _char_checker(cls, __text: str) -> bool:
        return (
            None
            if not cls._validate_object(__text, type_is=str, arg="Text")
            else all(char in cls._ALL_CHARS for char in __text)
        )

    def _get_fernet(self, __keys=None) -> Any:
        return MultiFernet(tuple(__keys))

    @staticmethod
    def _validate_object(
        __obj: Any, type_is: type = int, arg: str = "Argument"
    ) -> int | str | tuple[str] | Path:
        """
        Validate and coerce the input object to the specified type.

        Parameters:
        - __obj (Any): The input object to be validated and coerced.
        - type_is (Type[Any]): The target type for validation and coercion.
        - arg (str): A descriptive label for the argument being validated.

        Returns:
        - Any: The validated and coerced object.

        Raises:
        - CipherException: If validation or coercion fails.

        """

        possible_instances = (TypeError, ValueError, SyntaxError)

        if type_is is Any:
            type_is = type(__obj)

        if type_is in (int, float):
            try:
                _obj = abs(int(__obj))
            except possible_instances:
                raise CipherException(
                    f"{arg!r} must be of type {int} or integer-like {str}. "
                    f"{__obj!r} is an invalid argument."
                )
        elif type_is is str:
            try:
                _obj = str(__obj)
            except possible_instances:
                raise CipherException(f"{arg!r} must be of type {str}")
        elif type_is is Iterable and isinstance(__obj, (list, tuple, Iterable)):
            try:
                _obj = tuple(map(str, __obj))
            except possible_instances:
                raise CipherException(
                    f"{arg!r} must be of type {list} with {int} or integer-like {str}"
                )
        elif type_is is Path:
            try:
                _obj = Path(__obj)
            except possible_instances:
                raise CipherException(f"{arg!r} must be of type {str} or {Path}")
        else:
            raise CipherException(
                f"{__obj}'s type is not a valid type for this method."
            )

        return _obj

    @classmethod
    def _filter_chars(cls, __string: str, *, exclude: str = "") -> str:
        """
        ### Filter characters in the given string, excluding those specified.

        #### Parameters:
            - `__string` (str): The input string to be filtered.
            - `exclude` (str): Characters to be excluded from the filtering process.

        #### Returns:
            - str: The filtered string with specified characters excluded.

        #### Notes:
            - This method employs the `translate` method to efficiently filter characters.
            - Whitespace ('(space)\t\n\r\v\f') characters are automatically excluded as they can inadvertently impact the configuration file.
            - To exclude additional characters, provide them as a string in the `exclude` parameter.
        """
        check_str = cls._validate_object(__string, type_is=str, arg="Char")
        exclude = cls._validate_object(exclude, type_is=str, arg="Exclude Chars")
        full_string = "".join(check_str)
        filter_out = whitespace + exclude
        string_filtered = full_string.translate(str.maketrans("", "", filter_out))
        return string_filtered

    @staticmethod
    def _exclude_type(
        __key: str = "punct", return_dict: bool = False
    ) -> Union[str, None]:
        """
        ### Exclude specific character sets based on the provided key.

        #### Parameters:
        - __key (str): The key to select the character set to exclude.
        - return_dict (bool): If True, returns the dicitonary containing all possible exluce types.

        #### Returns:
        - str: The selected character set based on the key to be excluded from the generated passkey.

        #### Possible values for __key:
        - 'digits': Excludes digits (0-9).
        - 'punct': Excludes punctuation characters.
        - 'ascii': Excludes ASCII letters (both uppercase and lowercase).
        - 'digits_punct': Excludes both digits and punctuation characters.
        - 'ascii_punct': Excludes both ASCII letters and punctuation characters.
        - 'digits_ascii': Excludes both digits and ASCII letters.
        - 'digits_ascii_lower': Excludes both digits and lowercase ASCII letters.
        - 'digits_ascii_upper': Excludes both digits and uppercase ASCII letters.
        - 'ascii_lower_punct': Excludes both lowercase ASCII letters and punctuation characters.
        - 'ascii_upper_punct': Excludes both uppercase ASCII letters and punctuation characters.
        - 'digits_ascii_lower_punct': Excludes digits, lowercase ASCII letters, and punctuation characters.
        - 'digits_ascii_upper_punct': Excludes digits, uppercase ASCII letters, and punctuation characters.
        """
        all_chars = {
            "digits": digits,
            "punct": punctuation,
            "ascii": ascii_letters,
            "digits_punct": digits + punctuation,
            "ascii_punct": ascii_letters + punctuation,
            "ascii_lower_punct": ascii_letters.lower() + punctuation,
            "ascii_upper_punct": ascii_letters.upper() + punctuation,
            "digits_ascii": digits + ascii_letters,
            "digits_ascii_lower": digits + ascii_letters.lower(),
            "digits_ascii_upper": digits + ascii_letters.upper(),
            "digits_ascii_lower_punct": digits + ascii_letters.lower() + punctuation,
            "digits_ascii_upper_punct": digits + ascii_letters.upper() + punctuation,
        }
        if return_dict:
            return all_chars
        return all_chars.get(__key)

    @classmethod
    def _sig_larger(cls, *args) -> NamedTuple:
        """
        Calculate the significant difference between two numerical values.

        - Special Note:
            - The 'status' field indicates whether the absolute difference between the provided values
            is within the threshold (1e5). If 'status' is False, the 'threshold' field will be the maximum
            of the provided values and the threshold.
        """

        valid_args = all((map(partial(cls._validate_object, arg="Key Length"), args)))

        if len(args) == 2 or valid_args:
            threshold = cls._MAX_TOKENS
            Sig = namedtuple("SigLarger", ("status", "threshold"))
            abs_diff = abs(operator.sub(*args))
            status: bool = operator.le(*map(math.log1p, (abs_diff, threshold)))
            return Sig(status, max(max(args), threshold))
        raise CipherException(
            "Excessive arguments provided; requires precisely two numerical values, such as integers or floats."
        )

    @classmethod
    def _generate_key(
        cls,
        *,
        key_length: int = 32,
        exclude: str = "",
        include_all_chars: bool = False,
        bypass_keylength: bool = False,
        repeat: int = None,
        urlsafe_encoding=False,
    ) -> Union[str, bytes]:
        if all((exclude, include_all_chars)):
            raise CipherException(
                "Cannot specify both 'exclude' and 'include_all_chars' parameters."
            )

        if repeat:
            repeat_val = cls._validate_object(repeat, type_is=int, arg="repeat")
        else:
            repeat_val = cls._MAX_TOKENS

        cls._validate_object(key_length, type_is=int, arg="Key Length")
        if not bypass_keylength and key_length < cls._MAX_KEYLENGTH:
            raise CipherException(
                f"'key_length' must be of value >={cls._MAX_KEYLENGTH}.\n"
                f"Specified Key Length: {key_length}"
            )

        if any((repeat_val >= cls._MAX_CAPACITY, key_length >= cls._MAX_CAPACITY)):
            raise CipherException(
                f"The specified counts surpasses the computational capacity required for {cls.__name__!r}. "
                "It is recommended to use a count of 32 <= x <= 256, considering the specified 'key_length'. \n"
                f"Max Capacity: {cls._MAX_CAPACITY:_}\n"
                f"Character Repeat Count: {repeat_val:_}"
            )

        threshold = cls._sig_larger(key_length, int(repeat_val))
        if not threshold.status:
            cls._MAX_TOKENS = threshold.threshold
            CipherException(
                "The specified values for 'key_length' or 'iterations' (repeat) exceeds the number of characters that can be cycled during repetition."
                f" Higher values for 'max_tokens' count is recommended for better results ('max_tokens' count is now {cls._MAX_TOKENS}).",
                log_method=logger.warning,
            )

        slicer = lambda *args: "".join(islice(*args, cls._MAX_TOKENS))
        all_chars = slicer(cycle(cls._ALL_CHARS))
        filtered_chars = cls._filter_chars(all_chars, exclude=punctuation)

        if include_all_chars:
            filtered_chars = all_chars

        if exclude:
            exclude = cls._validate_object(exclude, type_is=str, arg="exclude_chars")
            filter_char = partial(cls._filter_chars, all_chars)
            exclude_type = cls._exclude_type(exclude)
            filtered_chars = (
                filter_char(exclude=exclude)
                if not exclude_type
                else filter_char(exclude=exclude_type)
            )

        passkey = secrets.SystemRandom().sample(
            population=filtered_chars, k=min(key_length, len(filtered_chars))
        )
        crypto_key = "".join(passkey)
        if urlsafe_encoding:
            crypto_key = cls._base64_key(crypto_key.encode())
        return crypto_key

    @classmethod
    def _fernet_mapper(cls, __keys) -> Iterable[Fernet]:
        return cls._EXECUTOR.map(partial(Fernet, backend=default_backend()), __keys)


class _BasePower:
    """
    ### Base class providing common attributes for power-related configurations in the CipherEngine.

    #### Attributes:
        - `_MHZ`: str: Suffix for MegaHertz.
        - `_GHZ`: str: Suffix for GigaHertz.
        - `_POWER`: None: Placeholder for power-related information.
        - `_SPEED`: None: Placeholder for speed-related information.
        - `_MIN_CORES`: int: Minimum number of CPU cores (default: 2).
        - `_MAX_CORES`: int: Maximum number of CPU cores (default: 64).
        - `_MIN_POWER`: int: Minimum capacity for cryptographic operations (default: 10,000).
        - `_MAX_POWER`: int: Maximum capacity for cryptographic operations (default: 100,000,000).
    """

    _MHZ = "MHz"
    _GHZ = "GHz"
    _POWER = None
    _SPEED = None
    _MIN_CORES = 2
    _MAX_CORES = 64
    _MIN_POWER = int(1e5)
    _MAX_POWER = _BaseCryptoEngine._MAX_CAPACITY

    def __init__(self) -> None:
        pass

    @property
    def clock_speed(self) -> NamedTuple:
        if self._SPEED is None:
            self._SPEED = self._get_clock_speed()
        return self._SPEED

    @property
    def cpu_power(self) -> Union[int, dict[int, int]]:
        if self._POWER is None:
            self._POWER = self._get_cpu_power()
        return self._POWER

    def calculate_cpu(self, **kwargs) -> Union[int, dict[int, int]]:
        return self._get_cpu_power(**kwargs)

    def _get_cpu_chart(self) -> dict[int, int]:
        """CPU _Power Chart"""
        return self._get_cpu_power(return_dict=True)

    @classmethod
    def _get_clock_speed(cls) -> NamedTuple:
        Speed = namedtuple("ClockSpeed", ("speed", "unit"))
        frequencies = psutil.cpu_freq(percpu=False)
        if frequencies:
            mega, giga = cls._MHZ, cls._GHZ
            clock_speed = frequencies.max / 1000
            unit = giga if clock_speed >= 1 else mega
            return Speed(clock_speed, unit)
        raise CipherException(
            "Unable to retrieve CPU frequency information to determine systems clock speed."
        )

    def _get_cpu_power(
        self,
        min_power: bool = False,
        max_power: bool = False,
        return_dict: bool = False,
    ) -> Union[int, dict[int, int]]:
        if all((min_power, max_power)):
            max_power = False

        base_power_range = np.logspace(
            np.log10(self.min_cores),
            np.log10(self._MIN_POWER),
            self._MIN_POWER,
            self._MAX_POWER,
        ).astype("float64")
        base_power = base_power_range[self.max_cores + 1] * self._MIN_POWER
        cpu_counts = np.arange(self.min_cores, self.max_cores // 2)
        cpu_powers = np.multiply(base_power, cpu_counts, order="C", subok=True).astype(
            "int64"
        )
        cpu_chart = OrderedDict(zip(cpu_counts, cpu_powers))

        if return_dict:
            return cpu_chart

        try:
            total_power = cpu_chart[
                self.min_cores + min((self.min_cores % 10, self.max_cores % 10))
            ]
        except KeyError:
            total_power = next(iter(cpu_chart.values()))

        first_or_last = lambda _x: next(iter(_x[slice(-1, None, None)]))

        if any(
            (
                min_power,
                total_power >= self._MAX_POWER,
                self.clock_speed.unit == self._MHZ,
            )
        ):
            total_power = first_or_last(cpu_chart.popitem(last=False))

        if max_power and (
            self.clock_speed.unit == self._GHZ and not total_power >= self._MAX_POWER
        ):
            total_power = first_or_last(cpu_chart.popitem(last=True))
            CipherException(
                "CAUTION: The 'max_power' parameter is designed to determine the maximum number "
                "of iterations used in the algorithm's encryption/decryption process, with consideration "
                "for high-end computational power, specifically GigaHertz (GHz). Please ensure your system "
                "meets the required computational prerequisites before using this option."
                f"\nIterations being used {total_power:_}",
                log_method=logger.warning,
            )

        return total_power

    @classmethod
    def _capacity_error(cls, __strings) -> NoReturn:
        raise CipherException(
            f"The specified counts surpasses the computational capacity required for {cls.__name__!r}. "
            f"It is recommended to use a count of {int(1e3):_} <= x <= {int(1e6):_}, considering the specified 'key_length'. "
            f"{__strings}"
        )

    @property
    def default_cpu_count(self):
        return os.cpu_count() or 1

    @property
    def max_cores(self):
        if self.default_cpu_count > self._MAX_CORES:
            self._MAX_CORES = self.default_cpu_count
        return self._MAX_CORES

    @property
    def min_cores(self):
        if self.default_cpu_count < self._MIN_CORES:
            self._MIN_CORES = self.default_cpu_count
        return self._MIN_CORES


@dataclass(kw_only=True)
class _BaseEngine(_BaseCryptoEngine, _BasePower):
    """
    Base class for the CipherEngine hierarchy, providing common attributes and functionality for encryption.
    """

    # XXX Shared attributes across all engines.
    overwrite_file: Optional[bool] = field(repr=False, default=False)
    identifiers: Optional[Iterable[str]] = field(repr=False, default=None)
    _AES: str = "aes"
    _DEC: str = "dec"
    _INI: str = "ini"
    _ENV: str = "env"
    _JSON: str = "json"
    _PRE_ENC: str = "encrypted"
    _PRE_DEC: str = "decrypted"

    def _get_serializer(self) -> re.Match:
        serializer = self._validate_object(
            self.serializer, type_is=str, arg="Serializer"
        )
        extensions = (self._INI, self._JSON, self._ENV)
        return self._compiler(extensions, serializer, escape_k=False)

    @staticmethod
    def _new_parser() -> configparser.ConfigParser:
        return configparser.ConfigParser()

    @classmethod
    def _failed_hash(cls, org_hash: bytes, second_hash: bytes) -> NoReturn:
        raise CipherException(
            "The discrepancy in hashed values points to a critical integrity issue, suggesting potential data loss. "
            "Immediate data investigation and remedial action are strongly advised. "
            f"\nOriginal Hash: {org_hash}"
            f"\nDecrypted Hash: {second_hash}"
        )

    @staticmethod
    def _template_parameters() -> frozenset:
        """All key sections for configuration file."""
        return frozenset(
            {
                "decipher_keys",
                "encrypted_file",
                "encrypted_text",
                "fernet_encrypted_text",
                "hash_value",
                "id1",
                "id2",
                "iterations",
                "original_file",
                "original_text",
                "passkey",
                "private_key",
                "public_key",
                "rsa_bits_size",
                "rsa_iterations",
                "rsa_passphrase",
                "salt_bytes_size",
                "salt_values",
            }
        )

    @staticmethod
    def _check_headers(
        __data: str, headers, msg="", method=all, include_not=False
    ) -> None:
        """Checks whether specified data contains the correct encryption identifiers."""
        start, end = headers
        try:
            result = method((__data.startswith(start), __data.endswith(end)))
        except TypeError:
            result = method(
                (__data.startswith(start.decode()), __data.endswith(end.decode()))
            )
        if include_not and not result:
            raise CipherException(msg)
        elif not include_not and result:
            raise CipherException(msg)

    @classmethod
    def _base_engines(cls, __engine: str):
        engines = cls._validate_object(__engine, type_is=str, arg="Class Engine")
        splitter = lambda s: str(s).strip("'<>").split(".")[-1]
        return next(c for c in inspect.getmro(cls) if splitter(c) == splitter(engines))

    def _new_template(self, **kwargs) -> dict:
        """
        #### \
        This method creates a dynamic template incorporating encryption parameters and security details \
        suitable for writing encrypted data to a file. \
        The generated template can later be employed in the decryption process.
        """
        
        # XXX CIPHER_INFO Section
        org_str = "original_{}".format("file" if "encrypted_file" in kwargs else "text")
        org_data = kwargs.pop(org_str)
        encr_str = "encrypted_{}".format(
            "file" if "encrypted_file" in kwargs else "text"
        )
        encr_data = kwargs.pop(encr_str)
        decipher_keys = kwargs.pop(decipher_str := ("decipher_keys"))

        # XXX RSA Encryption Data
        private_key = kwargs.pop(private_str := ("private_key"), None)
        public_key = kwargs.pop(public_str := ("public_key"), None)
        rsa_bits_size = kwargs.pop(rsa_bits_str := ("rsa_bits_size"), None)
        rsa_iterations = kwargs.pop(rsa_iter_str := ("rsa_iterations"), None)
        rsa_passphrase = kwargs.pop(rsa_pass_str := ("rsa_passphrase"), None)
        fernet_encr_text = kwargs.pop(f_encr_str := ("fernet_encrypted_text"), None)

        # XXX SECURITY_PARAMS Section
        security_params = (
            {**kwargs,
            decipher_str: decipher_keys}
            if not private_key
            else {
                **kwargs,
                rsa_iter_str: rsa_iterations,
                "rsa_pkcs_value": self._PKCS_VALUE,
                f_encr_str: fernet_encr_text,
                rsa_bits_str: rsa_bits_size,
                rsa_pass_str: rsa_passphrase,
                decipher_str: decipher_keys,
                public_str: public_key,
                private_str: private_key,
            }
        )
        return {
            "CIPHER_INFO": {
                org_str: org_data,
                encr_str: encr_data,
            },
            "SECURITY_PARAMS": security_params,
        }

    @classmethod
    def _key_deriver(cls, *args):
        """Salt, Iterations, Keys"""
        try:
            salt, iterations, key = args
        except ValueError:
            salt, iterations, key = args[0]

        kderiver = cls._create_subclass(
            "KeyDeriver", field_names=("key", "salt", "pbk"), defaults=None
        )
        if isinstance(key, str):
            key = key.encode()
        kdf = cls._get_pbk(salt, iterations=iterations)
        passkey = cls._base64_key(kdf.derive(key))
        if not salt:
            salt = kdf._salt
        return kderiver(passkey, salt.hex(), kdf)

    @staticmethod
    def _format_file(__file: P) -> str:
        time_now = datetime.now()
        formatted_time = time_now.strftime("%Y-%m-%dT%I-%M-%S%p-")
        return (__file.parent / formatted_time).as_posix() + (f"backup-{__file.name}")

    @staticmethod
    def _bytes_read(__file: P) -> bytes:
        with open(__file, mode="rb") as _file:
            _text = _file.read()
        return _text

    @staticmethod
    def none_generator(__data, default=None) -> list:
        return [default] * len(__data)

    @classmethod
    def _create_subclass(
        cls,
        typename: str = "FieldTuple",
        /,
        field_names: Iterable = None,
        *,
        module: str = None,
        defaults: Iterable = None,
        values: Iterable = None,
        field_doc: str = "",
    ) -> NamedTuple:
        default_vals = defaults or cls.none_generator(field_names)

        field_docs = field_doc or "Field documentation not provided."
        module_name = module or typename
        new_tuple = namedtuple(
            typename=typename,
            field_names=field_names,
            defaults=default_vals,
            module=module_name,
        )
        setattr(new_tuple, "__doc__", field_docs)
        if values:
            return new_tuple(*values)
        return new_tuple

    @classmethod
    def _validate_file(cls, __file: P) -> Path:
        try:
            _file = cls._validate_object(
                __file, type_is=Path, arg="Specified File Path"
            )
        except TypeError as t_error:
            raise CipherException(t_error)

        if not _file:
            raise CipherException(f"File arugment must not be empty: {_file!r}")
        elif not _file.exists():
            raise CipherException(
                f"File does not exist: {_file!r}. Please check system files."
            )
        elif all((not _file.is_file(), not _file.is_absolute())):
            raise CipherException(
                f"Invalid path type: {_file!r}. Path must be a file type."
            )
        elif _file.is_dir():
            raise CipherException(
                f"File is a directory: {_file!r}. Argument must be a valid file."
            )
        return _file

    @classmethod
    def convert2strings(cls, __data):
        return {
            k: str(v) if not isinstance(v, dict) else cls.convert2strings(v)
            for k, v in __data.items()
        }

    @staticmethod
    def _terminal_size() -> int:
        return shutil.get_terminal_size().columns

    @classmethod
    def _replace_file(cls, __file, overwrite=False) -> Union[Path, None]:
        new_path = __file.parent
        if overwrite:
            new_file = new_path / __file.stem
            CipherException(f"Overwriting {__file!r}...", log_method=logger.info)
            os.remove(__file)
        else:
            if __file.is_file():
                prefix = cls._PRE_ENC
                _name = __file.stem.removeprefix(prefix)
                if re.search(r"\.", _name):
                    _name = __file.stem.split(".")[0]
                new_file = __file.parent / f"{prefix}_{_name}"
                return new_file

    @classmethod
    def _calc_file_hash(cls, __file: P) -> str:
        """
        Calculate the SHA-256 hash of the content in the specified file.

        Parameters:
        - file_path (str): The path to the file for which the hash is to be calculated.

        Returns:
        - str: The SHA-256 hash value as a hexadecimal string.
        """
        file = cls._validate_file(__file)
        sha256_hash = hashlib.sha256()
        with open(__file, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    @classmethod
    def _calc_str_hash(cls, __text: str = None) -> str:
        """
        Calculate the SHA-256 hash of the provided text.

        Parameters:
        - text (str): The input text for which the hash is to be calculated.

        Returns:
        - str: The SHA-256 hash value as a hexadecimal string.
        """
        hash_ = hashlib.sha256()
        hash_.update(__text.encode())
        return hash_.hexdigest()

    @classmethod
    def _get_pbk(cls, __salt: bytes = None, iterations: int = None) -> PBKDF2HMAC:
        if __salt is None:
            __salt = cls._gen_random()
        return PBKDF2HMAC(
            algorithm=hashes.SHA512(), length=32, salt=__salt, iterations=iterations
        )

    @classmethod
    def _parse_config(
        cls, __config: P, *, section: str = "SECURITY_PARAMS", section_key: str
    ) -> str:
        file_suffix = __config.suffix.lstrip(".")
        try:
            if file_suffix == cls._JSON:
                cparser = json.load(open(__config))
            else:
                cparser = cls._new_parser()
                cparser.read(__config)
            sec_val = cparser[section].get(section_key)
        except configparser.NoSectionError:
            raise CipherException(
                f"Confgiuration file does not contain section {section!r}"
            )
        except configparser.NoOptionError:
            raise CipherException(
                f"{section_key.capitalize()!r} was not found in {section!r} section."
                f"\nIt is imperative that the values stored in the passkey configuration file generated by {cls.__name__.upper()} encryption algorithm tool is saved and not altered in anyway. "
                "Failure to do so may alter the decryption process, potentially corrupting the files data."
            )
        except configparser.Error:
            raise configparser.Error(
                f"An unexpected error occurred while attempting to read the configuration file {__config.name}. "
                f"The decryption algorithm is designed to work with its original values. "
                "Please note that if the passphrase contains special characters, it may result in decryption issues."
            )
        return sec_val

    @classmethod
    def _get_identifiers(cls, __identifiers: Iterable[str]) -> tuple[bytes]:
        if __identifiers:
            identifiers = cls._validate_object(
                __identifiers, type_is=Iterable, arg="Encryption Identifier"
            )
        else:
            base_identifier = "-----{} CIPHERENGINE CRYPTOGRAPHIC ENCRYPTED KEY-----"
            identifiers = (
                base_identifier.format("BEGIN"),
                base_identifier.format("END"),
            )
        return tuple(id_.encode() for id_ in identifiers)

    @property
    def _identifiers(self) -> Iterable[str]:
        headers = "" if not hasattr(self, "identifiers") else self.identifiers
        return self._get_identifiers(headers)

    @classmethod
    def _validate_ciphertuple(cls, __ctuple: NamedTuple) -> NamedTuple:
        all_parameters = cls._template_parameters()
        # ** isinstance(__obj, CipherTuple)?
        if hasattr(__ctuple, "_fields") and all(
            (
                isinstance(__ctuple, tuple),
                isinstance(__ctuple._fields, tuple),
                hasattr(__ctuple, "__module__"),
                __ctuple.__module__ == "CipherTuple",
            )
        ):
            ctuple_set = set(__ctuple._asdict())
            ctuple_paramters = all_parameters & ctuple_set
            try:
                for param in ctuple_paramters:
                    param_attr = getattr(__ctuple, param)
                    str_attr = cls._validate_object(
                        param_attr, type_is=str, arg="CipherTuple"
                    )
                    #! Ensure attribute is not null.
                    if any((not str_attr, not len(str_attr) >= 1)):
                        raise CipherException(
                            f">>{str_attr} is not a valid attribute value. ",
                            ">>Ensure that all predefined configuration CipherTuples have non-null values.",
                        )
            except AttributeError as attr_error:
                raise CipherException(
                    f">>Validation Failed: The following attribute is not predefined. {param}. "
                    f">>Ensure that the specified configuration {NamedTuple.__name__!r} is generated from one of the {CipherEngine.__name__!r} encryption processes. "
                    f">>ERROR: {attr_error}"
                )

        else:
            raise CipherException(
                "Invalid NamedTuple Structure:\n"
                f"{__ctuple!r} must be of type {NamedTuple.__name__!r}"
            )

        return __ctuple

    def _create_backup(self, __file: P) -> None:
        CEinfo = partial(CipherException, log_method=logger.info)
        backup_path = __file.parent / f"backup/{__file.name}"
        formatted_bkp = _BaseEngine._format_file(backup_path)
        if not backup_path.parent.is_dir():
            CEinfo(
                "No backup folder detected. "
                f"Creating a backup folder named {backup_path.parent!r} to store original files securely."
            )
            backup_path.parent.mkdir()

        if not backup_path.is_file():
            CEinfo(
                f"Backing up {backup_path.name} to the newly-created backup folder.",
            )
            shutil.copy2(__file, formatted_bkp)

    @classmethod
    def _write2file(
        cls,
        __file: P,
        *,
        suffix: bool = "ini",
        data: AnyStr = "",
        mode: str = "w",
        parser: configparser = None,
        reason: str = "",
    ) -> None:
        new_file = Path(__file).with_suffix(f".{suffix}")
        with open(new_file, mode=mode) as _file:
            if parser:
                parser.write(_file)
            else:
                _file.write(data)
            p_string = partial(
                "{file!r} has successfully been {reason} to {path!r}".format,
                file=_file.name,
                path=new_file.absolute(),
            )
            CipherException(
                p_string(reason=reason or "written"), log_method=logger.info
            )
        return

    @classmethod
    def _compiler(
        cls, __defaults, __k, escape_default=True, escape_k=True, search=True
    ) -> re.Match:
        valid_instances = (int, str, bool, bytes, Iterable)
        if any(
            (not __k, not isinstance(__k, valid_instances), hasattr(__k, "__str__"))
        ):
            esc_k = str(__k)
        else:
            esc_k = cls._validate_object(__k, type_is=str, arg=__k)

        defaults = map(re.escape, map(str, __defaults))
        flag = "|" if escape_default else ""
        pattern = f"{flag}".join(defaults)
        if escape_k:
            esc_k = "|".join(map(re.escape, __k))

        compiler = re.compile(pattern, re.IGNORECASE)
        if not search:
            compiled = compiler.match(esc_k)
        else:
            compiled = compiler.search(esc_k)
        return compiled


@dataclass(kw_only=True)
class CipherEngine(_BaseEngine):
    """
    `CipherEngine` class for encrypting files and text data using symmetric key `MultiFernet` cryptography.
    """

    __slots__ = (
        "__weakrefs__",
        "_file",
        "_iterations",
        "_passkey",
        "_original_passkey",
        "_serializer",
        "_text",
    )

    file: Optional[P] = field(repr=False, default=None)
    file_name: Optional[str] = field(repr=False, default=None)
    text: Optional[P] = field(repr=False, default=None)
    passkey: Optional[Union[str, int]] = field(repr=False, default=None)
    key_length: Optional[int] = field(repr=True, default=_BaseEngine._MAX_KEYLENGTH)
    iterations: Optional[int] = field(repr=True, default=None)
    export_path: Optional[P] = field(repr=False, default=None)
    min_power: Optional[bool] = field(repr=False, default=False)
    max_power: Optional[bool] = field(repr=False, default=False)
    bypass_keylength: Optional[bool] = field(repr=False, default=False)
    gui_passphrase: bool = field(repr=False, default=False)
    serializer: Literal["ini", "json", "env"] = field(repr=True, default="ini")
    backup_file: Optional[bool] = field(repr=False, default=True)
    export_passkey: Optional[bool] = field(repr=False, default=True)
    special_keys: Optional[bool] = field(repr=False, default=True)
    advanced_encryption: Optional[bool] = field(repr=False, default=False)

    def __post_init__(self):
        self._salt_bytes_size = (
            32
            if not self.salt_bytes_size
            else self._validate_object(
                self.salt_bytes_size, type_is=int, arg="Salt Bytes Size"
            )
        )
        self._file = None if not self.file else self._validate_file(self.file)
        self._iterations = self._calculate_iterations()
        self._passkey = self._validate_passkey(self.passkey)
        self._rsa_passphrase = self._validate_passkey(self.rsa_passphrase, return_as=str)
        self._rsa_iterations = self._get_rsa_iters()
        self._original_passkey = (
            self._base64_key(self._passkey, base_type="decode").decode()
            if not any((self.passkey, self.gui_passphrase))
            else self._passkey
        )
        self._serializer = self._get_serializer()
        self._text = None if not self.text else self._validate_object(self.text, type_is=str, arg="Text")
    
    def _get_rsa_iters(self):
        cpu_chart = self._get_cpu_chart()
        if self.rsa_iterations:
            self.rsa_iterations = self._validate_object(self.rsa_iterations, type_is=int, arg="RSA Iterations")
        
        if not self.rsa_iterations:
            min_max = max if self.clock_speed.unit==self._GHZ else min
            self.rsa_iterations = min_max((
                                    self._MAX_TOKENS,
                                    self._iterations,
                                    cpu_chart.popitem(last=False)[1]
                                    ))
        return self.rsa_iterations

    def _gui_passphrase(self):
        root = tk.Tk()
        root.withdraw()
        gui_pass = simpledialog.askstring(
            "GUI-Passphrase", "Enter a secure passkey:", show="*"
        )
        root.destroy()
        return gui_pass

    def _calculate_iterations(self) -> int:
        if self.iterations:
            iter_count = self._validate_object(
                self.iterations, type_is=int, arg="Iterations"
            )
            if iter_count >= self._MAX_CAPACITY:
                return self._capacity_error(
                    f"\nSpecified value: {iter_count}\n"
                    f"Max Iterations value: {self._MAX_CAPACITY}"
                )
            return iter_count
        args = (self.min_power, self.max_power)
        if any(args):
            power_info = self._create_subclass(
                "PStats",
                ("min", "max"),
                values=args,
                module="PowerInfo",
                field_doc="Minimum and maximum values for number of iterations.",
            )

            return self.calculate_cpu(
                min_power=power_info.min, max_power=power_info.max
            )
        return self.cpu_power

    def _validate_passkey(self, passphrase=None, return_as: str=None) -> str:
        def validator(passkey):
            if not self._char_checker(passkey):
                raise CipherException(
                    "The specified passkey does not meet the required criteria and contains illegal characters which cannot be utilized for security reasons.\n"
                    f"Illegal passphrase: {passkey!r}"
                )

            if self.bypass_keylength and not len(passkey) >= self._MAX_KEYLENGTH:
                return passkey
            elif not self.bypass_keylength and not (
                0 < len(passkey) < self._MAX_KEYLENGTH
            ):
                raise CipherException(
                    "For security reasons, the passkey must have a length of at least 32 characters. "
                    "If a shorter key is desired, provide a 'bypass_keylength' parameter."
                )
            return passkey
        
        if self.gui_passphrase:
            passkey = validator(self._gui_passphrase())
        elif passphrase:
            passkey = validator(passphrase)
        elif self.special_keys:
            passkey = self._generate_key(
                key_length=self.key_length,
                exclude=self.exclude_chars,
                include_all_chars=self.include_all_chars,
                bypass_keylength=self.bypass_keylength,
                urlsafe_encoding=True,
            )
        else:
            #! Change salt bytes size to _BaseKeyEngine property
            # Overrides traditional Fernet.generate_key() for custom (salt) bytes size
            fernet_copycat = self._base64_key(self._gen_random(self._salt_bytes_size))
            passkey = self._base64_key(fernet_copycat)
        if return_as is str:
            passkey = base64.urlsafe_b64decode(passkey.decode())
        return passkey

    def _get_suffix(self):
        if self._serializer:
            map_suffixes = {ext: ext for ext in (self._JSON, self._ENV, self._INI)}
            passkey_suffix = map_suffixes[self._serializer.group()]
        else:
            passkey_suffix = self._INI
        return passkey_suffix

    def _export_passkey(self, *, parser, passkey_file, data) -> None:
        passkey_suffix = self._get_suffix()
        write_func = partial(self._write2file, passkey_file, reason="exported")
        write2file = partial(write_func, suffix=passkey_suffix, parser=parser)

        def json_serializer():
            org_data = self.convert2strings(data)
            new_data = json.dumps(org_data, indent=2, ensure_ascii=False)
            passkey_suffix = self._JSON
            write2file = partial(write_func, suffix=passkey_suffix, data=new_data)
            return write2file

        CipherException("Writing data onto configuration file...")
        if passkey_suffix == "json":
            write2file = json_serializer()
        else:
            try:
                parser.update(**self.convert2strings(data))
            except ValueError:
                CipherException(
                    "Usage of special characters in .INI configurations (ConfigParser module) may not be optimal and could potentially result in errors. "
                    "As a result, the system will proceed to serialize the data in JSON (.json) format to guarantee compatibility with any special characters.",
                    log_method=logger.error
                )
                write2file = json_serializer()

        if self.export_passkey:
            write2file()

    def _base_error(self, __data=None) -> str:
        if not __data:
            __data = "the data"
        return (
            f"{self.__class__.__name__.upper()} encrypter identifications detected signaling that {__data!r} is already encrypted. "
            "\nRe-encrypting it poses a significant risk of resulting in inaccurate decryption, potentially leading to irreversible data corruption. "
            "\nIt is crucial to decrypt the data first before attempting any further encryption."
            "\n\nStrictly limit the encryption process to once per object for each subsequent decryption to safeguard against catastrophic data loss."
        )
    
    @classmethod
    def _ciphertuple(cls, *args, type_file=False, class_only=False) -> NamedTuple:
        """
        ('decipher_key', 'encrypted_text/file',
        'fernet_encrypted_text', 'fernets', 'hash_value',
        'id1', 'id2', 'iterations', 'original_text/file',
        'passkey', 'private_key', 'public_key',
        'rsa_bits_size', 'salt_byte_size', 'salt_values')
        """
        if not class_only:
            parameters = cls._template_parameters()
            specific_params = (
                k
                for k in parameters
                if (type_file and not k.endswith("text"))
                or (not type_file and not k.endswith("file"))
            )
            ordered_params = sorted(specific_params)
            values = cls.none_generator(ordered_params) if not args else args
        else:
            ordered_params, values = args
        return cls._create_subclass(
            "CipherTuple",
            field_names=ordered_params,
            values=values,
            field_doc="Primary NamedTuple \
                                            for storing encryption details.",
        )

    def _rsa_encrypt(self, fencrypted_text):
        key_pair = self.rsa_keypair
        public_key = key_pair.publickey()
        private_key = key_pair.export_key(
            passphrase=self._rsa_passphrase,
            randfunc=secrets.token_bytes,
            pkcs=self._PKCS_VALUE,
            protection="PBKDF2WithHMAC-SHA512AndAES256-CBC",
            prot_params={"iteration_count": self._rsa_iterations}
        )
        cipher = PKCS1_OAEP.new(
            public_key, hashAlgo=SHA512, randfunc=secrets.token_bytes
        )
        ciphertext = cipher.encrypt(fencrypted_text)
        cipherkey = namedtuple(
            "CipherKey", ("keypair", "ciphertext", "private_key", "public_key")
        )
        return cipherkey(key_pair, ciphertext, private_key, public_key.export_key())

    def encrypt_file(self) -> NamedTuple:
        if not self._file:
            raise CipherException(
                f"Specified file cannot be null for encryption. Error on ({self._file!r})"
            )

        org_file = self._file
        hash_val = self._calc_file_hash(org_file)
        plain_btext = self._bytes_read(org_file)
        self._check_headers(
            plain_btext, self._identifiers, msg=self._base_error(org_file), method=any
        )
        
        if not self.backup_file or (self.overwrite_file and not self.backup_file):
            CipherException(
                "Disabling the 'backup_file' parameter poses a significant risk of potential data loss. "
                "It is strongly advised to consistently back up your data before initiating any encryption processes to mitigate potential data loss scenarios.",
                log_method=logger.warning
            )
        
        if self.backup_file or self.overwrite_file:
            self._create_backup(org_file)

        if self.overwrite_file:
            encr_file = org_file.parent / org_file.stem
            CipherException(f"Overwriting {org_file!r}...", log_method=logger.info)
            os.remove(org_file)
        else:
            if org_file.is_file():
                prefix = self._PRE_ENC
                _name = org_file.stem.removeprefix(prefix)
                if re.search(r"\.", _name):
                    _name = org_file.stem.split(".")[0]
                encr_file = org_file.parent / f"{prefix}_{_name}"

        start_key, end_key = self._identifiers
        decipher_keys = tee(
            (
                self._EXECUTOR.map(
                    lambda s: self._key_deriver(s, self._iterations, self._passkey),
                    self.gen_salts,
                )
            ),
            3,
        )
        fernets = self._fernet_mapper((k.key for k in decipher_keys[0]))
        mfernet = self._get_fernet(fernets)
        encr_file = Path(encr_file).with_suffix(f".{self._AES}")
        encryption_data = start_key + mfernet.encrypt(plain_btext) + end_key
        passkey_data = (
            (self._original_passkey, self._passkey)
            if not any((self.passkey, self.gui_passphrase))
            else self._passkey
        )
        self._write2file(
            encr_file,
            suffix=self._AES,
            mode="wb",
            data=encryption_data,
            reason="exported",
        )
        passkey_name = self.file_name or Path(f"{encr_file.stem}_passkey")
        passkey_file = org_file.parent / passkey_name
        ciphertuple = self._ciphertuple(
            tuple(i.key.decode() for i in decipher_keys[1]),
            encr_file.as_posix(),
            mfernet._fernets,
            hash_val,
            start_key.decode(),
            end_key.decode(),
            self._iterations,
            org_file.as_posix(),
            passkey_data,
            tuple(s.salt for s in decipher_keys[2]),
            type_file=True,
        )
        encr_data = self._new_template(**ciphertuple._asdict())
        if self.export_passkey:
            self._export_passkey(
                parser=self._new_parser(), passkey_file=passkey_file, data=encr_data
            )
        return ciphertuple

    def encrypt_text(self) -> NamedTuple:
        CipherException(
            f"{self.__class__.__name__!r} encryption algorithm has begun.",
            log_method=logger.info,
        )

        if not self._text:
            raise CipherException(
                f"Specified text cannot be null for encryption. Error on ({self._text!r})"
            )

        hash_val = self._calc_str_hash(self._text)
        self._check_headers(
            self._text, self._identifiers, msg=self._base_error(), method=any
        )
        passkey = (
            self._passkey
            if not hasattr(self._passkey, "encode")
            else self._passkey.encode()
        )
        start_key, end_key = self._identifiers
        decipher_keys = tee(
            self._EXECUTOR.map(
                lambda s: self._key_deriver(s, self._iterations, passkey),
                self.gen_salts,
            ),
            3,
        )
        fernets = self._fernet_mapper((k.key for k in decipher_keys[0]))
        mfernet = self._get_fernet(fernets)
        mfernet_encryption = mfernet.encrypt(self._text.encode())
        mfernet_copy = deepcopy(mfernet_encryption)
        public_key = private_key = rsa_bits_size = None
        if self.advanced_encryption:
            advanced_encryption = self._rsa_encrypt(mfernet_encryption)
            mfernet_encryption = advanced_encryption.ciphertext
            public_key = advanced_encryption.public_key.decode()
            private_key = advanced_encryption.private_key.decode()
            rsa_bits_size = advanced_encryption.keypair.size_in_bits()
        encrypted_text = start_key + mfernet_encryption + end_key
        passkey_data = (
            (self._original_passkey, self._passkey)
            if not any((self.passkey, self.gui_passphrase))
            else self._passkey
        )
        ciphertuple = self._ciphertuple(
            tuple(k.key.decode() for k in decipher_keys[1]),
            encrypted_text.decode() if not self.advanced_encryption else encrypted_text,
            mfernet_copy.decode() if hasattr(mfernet_copy, 'decode') else mfernet_copy,
            hash_val,
            start_key.decode(),
            end_key.decode(),
            self._iterations,
            self._text,
            passkey_data,
            private_key,
            public_key,
            rsa_bits_size,
            self._rsa_iterations,
            self._rsa_passphrase.decode(),
            self.salt_bytes_size,
            tuple(s.salt for s in decipher_keys[2]),
        )
        if self.export_passkey:
            _file = Path(self.file_name or "ciphertext_passkey")
            cparser = self._new_parser()
            ctuple_data = self._new_template(**ciphertuple._asdict())
            if self.export_path:
                _file = Path(self.export_path) / _file
            self._export_passkey(parser=cparser, passkey_file=_file, data=ctuple_data)
        return self._update_ctuple(ctuple_data)

    def _update_ctuple(self, ctuple_dict: dict):
        """Returns updated CipherTuple based the encryption type used."""
        cipher_info, security_params = (ctuple_dict['CIPHER_INFO'], ctuple_dict['SECURITY_PARAMS'])
        field_names = chain.from_iterable((cipher_info, security_params))
        values = chain.from_iterable((cipher_info.values(), security_params.values()))
        return self._ciphertuple(tuple(field_names), tuple(values), class_only=True)


@dataclass(kw_only=True)
class DecipherEngine(_BaseEngine):
    """
    DecipherEngine is a class designed to decrypt data encrypted through the CipherEngine.
    This class specifically operates with (configuration files | CipherTuples) generated by the CipherEngine during the encryption process.
    """

    __slots__ = (
        "__weakrefs__",
        "_passkey_file",
        "_decipher_keys",
        "_hash_value",
        "_iterations",
        "_org_key" "_start_key",
        "_end_key",
        "_salts" "_encrypted_data",
        "_ciphertuple",
    )
    ciphertuple: Optional[NamedTuple] = field(repr=False, default=None)
    passkey_file: Optional[P] = field(repr=False, default=None)

    def __post_init__(self):
        # ** For configuration files (.INI | .JSON)
        if all((self.passkey_file, self.ciphertuple)):
            raise CipherException(
                "Cannot simultaneously specify 'ciphertuple' and 'passkey_file' arguments."
            )
        elif not any((self.passkey_file, self.ciphertuple)):
            raise CipherException(
                f"One of two optional keyword-only arguments are expected for {DecipherEngine.__name__!r}, "
                "but none were provided."
            )

        if self.passkey_file:
            self._passkey_file = self._validate_file(self.passkey_file)
            cparser_func = partial(self._parse_config, self._passkey_file)
            self._decipher_keys = cparser_func(section_key="decipher_keys")
            self._hash_value = cparser_func(section_key="hash_value")
            self._iterations = cparser_func(section_key="iterations")
            self._org_key = cparser_func(section_key="passkey")
            self._start_key = cparser_func(section_key="id1")
            self._end_key = cparser_func(section_key="id2")
            self._rsa_iters = cparser_func(section_key="rsa_iterations")
            self._salts = cparser_func(section_key="salt_values")
            sec_getter = lambda sec_key: cparser_func(
                section="CIPHER_INFO", section_key=sec_key
            )
            self._encrypted_data = sec_getter(sec_key="encrypted_text") or sec_getter(
                sec_key="encrypted_file"
            )

        # ** For CipherTuple instances.
        if self.ciphertuple:
            self.ciphertuple = self._validate_ciphertuple(self.ciphertuple)
            self._encrypted_data = (
                self.ciphertuple.encrypted_text
                if hasattr(self.ciphertuple, "encrypted_text")
                else self.ciphertuple.encrypted_file
            )
            self._iterations = self.ciphertuple.iterations
            self._decipher_keys = self.ciphertuple.decipher_keys
            self._hash_value = self.ciphertuple.hash_value
            self._start_key = self.ciphertuple.id1
            self._end_key = self.ciphertuple.id2
            self._salts = self.ciphertuple.salt_values
            self._org_key = self.ciphertuple.passkey
            #XXX Attributes for RSA Encryption.
            if hasattr(self.ciphertuple, "rsa_bits_size"):
                self._fernet_encryption = self.ciphertuple.fernet_encrypted_text
                self._rsa_bits = self.ciphertuple.rsa_bits_size
                self._rsa_iters = self.ciphertuple.rsa_iterations
                self._public_key = self.ciphertuple.public_key
                self._private_key = self.ciphertuple.private_key
                self._rsa_passphrase = self.ciphertuple.rsa_passphrase
                self._salt_bytes_size = self.ciphertuple.salt_byte_size

    @classmethod
    def _get_subclass(cls, type_file=False) -> NamedTuple:
        decr_type = "decrypted_{}".format("text" if not type_file else "file")
        return cls._create_subclass(
            "DecipherTuple", field_names=(decr_type, "hash_value")
        )

    @classmethod
    def _validate_token(cls, __mfernet, encrypted_text):
        encrypted_text = (
            encrypted_text
            if not hasattr(encrypted_text, "encode")
            else encrypted_text.encode()
        )
        try:
            decr_text = __mfernet.decrypt(encrypted_text).decode()
        except InvalidToken:
            decr_text = None
        return decr_text

    @classmethod
    def _str2any(cls, __keys=None) -> Iterable[Fernet]:
        if isinstance(__keys, str):
            __keys = ast.literal_eval(__keys)
        return __keys

    def _base_error(self, __data=None) -> str:
        if not __data:
            __data = "provided"
        return (
            f"The data {__data!r} lacks the required identifiers. "
            f"\n{self.__class__.__name__.upper()}'s decryption algorithm only operates with data containing its designated identifiers. "
            f"\nEncryption algorithms identifiers:\n{self._identifiers}"
        )

    def decrypt_file(self) -> NamedTuple:
        if self.passkey_file:
            config_path = self._passkey_file
            hashed_value = self._parse_config(config_path, section_key="hash_value")
        else:
            hashed_value = self._hash_value
        encrypted_file = self._validate_file(self._encrypted_data)
        bytes_data = self._bytes_read(encrypted_file)
        self._check_headers(
            bytes_data,
            self._identifiers,
            msg=self._base_error(encrypted_file),
            method=all,
            include_not=True,
        )
        try:
            passkey = self._str2any(self._org_key)[1]
        except ValueError:
            passkey = self._org_key

        default_suffix = self._DEC
        start_key, end_key = self._identifiers
        salts = (bytes.fromhex(s) for s in self._str2any(self._salts))
        decipher_keys = (
            k.key
            for k in (
                self._key_deriver(s, int(self._iterations), passkey) for s in salts
            )
        )
        fernets = self._fernet_mapper(decipher_keys)
        mfernet = self._get_fernet(fernets)
        encrypted_data = bytes_data[len(start_key) : -len(end_key)]
        decrypted_data = self._validate_token(mfernet, encrypted_data)
        if not decrypted_data:
            CipherException(
                "The decryption process failed due to the specified salt values, indicating that they are invalid tokens. "
                "An attempt will be made to decrypt using the stored decipher keys.",
                log_method=logger.warning,
            )
            fernets = self._fernet_mapper(self._decipher_keys)
            mfernet = self._get_fernet(fernets)
            decrypted_data = self._validate_token(mfernet, encrypted_data)
            if not decrypted_data:
                raise CipherException(
                    "The decryption process has encountered a complete failure with the specified salt and decipher keys. "
                    "Kindly verify that no modifications have been made to the configuration file."
                )

        if self.overwrite_file:
            default_suffix = encrypted_file.name.split(".")[-1]
            decrypted_file = encrypted_file.as_posix()
            os.remove(encrypted_file)
        else:
            if encrypted_file.is_file():
                prefix = self._PRE_DEC
                _name = encrypted_file.stem.removeprefix(prefix)
                if re.search(r"\.", _name):
                    _name = encrypted_file.stem.split(".")[0]
                decrypted_file = (
                    encrypted_file.parent / f"{prefix}_{_name}"
                ).as_posix()

        decrypted_file = Path(decrypted_file)
        self._write2file(
            decrypted_file,
            suffix=default_suffix,
            mode="w",
            data=decrypted_data,
            reason="decrypted",
        )

        decrypted_hash = self._calc_file_hash(
            decrypted_file.with_suffix("." + default_suffix)
        )
        if hashed_value != decrypted_hash:
            self._failed_hash(hashed_value, decrypted_hash)
        decr_tuple = self._get_subclass(type_file=True)
        return decr_tuple(decrypted_file, decrypted_hash)

    def decrypt_text(self) -> NamedTuple:
        obj_validator = partial(self._validate_object, type_is=str)
        encr_text = obj_validator(self._encrypted_data, arg="Encrypted Text")
        org_decipher_keys = self._str2any(self._decipher_keys)
        hash_value = obj_validator(self._hash_value, arg="Hash Value")
        start_key = obj_validator(self._start_key, arg="Beginning Encryption Header")
        end_key = obj_validator(self._end_key, arg="Ending Encryption Header")
        iterations = int(self._iterations)
        try:
            passkey = self._str2any(self._org_key)[1]
        except ValueError:
            passkey = self._org_key

        self._check_headers(
            encr_text,
            (start_key, end_key),
            msg=self._base_error(),
            method=all,
            include_not=True,
        )
        salts = (bytes.fromhex(s) for s in self._str2any(self._salts))
        decipher_keys = (
            k.key for k in (self._key_deriver(s, iterations, passkey) for s in salts)
        )
        fernets = self._fernet_mapper(decipher_keys)
        mfernet = self._get_fernet(fernets)
        encr_text = encr_text[len(start_key.encode()) : -len(end_key.encode())]
        decr_text = self._validate_token(mfernet, encr_text)
        if not decr_text:
            CipherException(
                "The decryption process failed due to the specified salt values, indicating that they are invalid tokens. "
                "An attempt will be made to decrypt using the stored decipher keys.",
                log_method=logger.warning,
            )
            fernets = self._fernet_mapper(org_decipher_keys)
            mfernet = self._get_fernet(fernets)
            decr_text = self._validate_token(mfernet, encr_text)
            if not decr_text:
                raise CipherException(
                    "The decryption process has encountered a complete failure with the specified salt and decipher keys. "
                    "Kindly verify that no modifications have been made to the configuration file."
                )

        decr_hash = self._calc_str_hash(decr_text)
        if hash_value and (decr_hash != hash_value):
            self._failed_hash(hash_value, decr_hash)
        decr_tuple = self._get_subclass()
        return decr_tuple(decr_text, hash_value)


def generate_crypto_key(**kwargs) -> str:
    """
    ### Generate a Cryptographic Key.
    
    #### Parameters:
        - `key_length` (Union[int, str]): The length of the key. Defaults to 32.
        - `exclude` (Union[str, Iterable]): Characters to exclude from the key generation. \
        Can be a string or an iterable of characters. Defaults to an empty string.
        - `include_all_chars` (bool): If True, include all characters from digits, ascii_letters, and punctuation. \
        Defaults to False.
        - `urlsafe_encoding`: Applies URL-safe Base64 encoding to the passkey
        - `repeat` (int): The number of iterations for character cycling. Defaults to 64. \n
            - Note: 
                - `repeat` parameter is used for character cycling from itertools.repeat, \
            and its input is not explicitly needed as its entire purpose is to adjust the key length. \
            If the absolute difference between `repeat` and `key_length` is within a certain threshold (1e5), \
            the `repeat` value will be adjusted as max(max(`repeat`, `key_length`), `threshold`). \n
        >>> if abs(repeat - key_length) <= threshold
        >>> new repeat value -> max(max(repeat, key_length), threshold)
        
    #### Returns:
        - str | bytes: The generated cryptographic key.
        
    #### Raises:
        - CipherException:
            - If conflicting `exclude` and `include_all_chars` arguments are specified
            - If `key_length` is less than default value (32) unless `bypass_keylimit` is passed in.
            - If `key_length` or `repeat` values are greater than the max capacity (1e8).
            
    #### Important Note:
        - The default key includes digits and ascii_letters only.
    """
    return _BaseCryptoEngine._generate_key(**kwargs)


def encrypt_file(**kwargs) -> NamedTuple:
    """
    #### Attributes:
        - `file`: str | Path: The file to be processed and encrypted.
        - `file_name`: str | None: The name of the file containing the encryption details.
        - `export_path`: Path | None: The path where exported files will be stored (default: None).
        - `export_passkey`: bool: Flag indicating whether to export the passphrase to a separate file (default: True).
        - `overwrite_file`: bool | None: Flag indicating whether to overwrite the original file during encryption (default: False).
        - `backup_file`: bool: Flag indicating whether to create a backup of the original file (default: True).
        - `serializer`: str: The type of serialization to be used for exporting the passkey file ('json' or 'ini').
        - `identifiers`: Iterable[str]: Specifiy a custom encryption identifier for the start and end of the encryption key (default: default settings.)
        
    #### Cryptographic Attributes:
        - `num_of_salts`: int: Number of `Fernet` keys to be generated and processed with `MultiFernet`. 
        - `include_all_chars`: bool: Flag indicating whether to include all characters during passphrase generation (default: False).
        - `exclude_chars`: str: Characters to exclude during passphrase generation (default: None).
        - `special_keys`: bool: If True, uses CipherEngines custom cryptographic key generation, \
            otherwise uses default keys generated from `Fernet`.
    
    #### Class Attributes:
        - `_ALL_CHARS`: str: A string containing all possible characters for passphrase generation.
        - `_MAX_KEYLENGTH`: int: The maximum length for cryptographic keys (32).
        - `_MAX_TOKENS`: int: Maximum number of tokens for cryptographic operations (default: 100,000).
        - `_MAX_CAPACITY`: int: = Maximumum number of characters to be generated. (For personal use only when using flexible `_generate_key` method.)
        - `_EXECUTOR`: ThreadPoolExecutor: Base executor for all engine classes.
    
    #### Important Notes:
        - Attributes `include_all_chars` and `exclude_chars` are more customizable features \
            using `secrets.System.Random` when generating Fernet keys compared to:
        
        >>> Fernet.generate_key() # Returns a string of bytes of only containing digits and ascii_letters
        
    #### Returns:
        - NamedTuple: Tuple containing information about the encryption process.
    """
    return CipherEngine(**kwargs).encrypt_file()


def decrypt_file(**kwargs) -> NamedTuple:
    """
    #### Attributes:
        - `ciphertuple` (NamedTuple): The tuple generated from any encryption process to be used for decryption.
        - `passkey_file`: str | Path: The path to the file containing the encryption details.

    #### Returns:
        - NamedTuple: Tuple containing information about the decryption process.
    """
    return DecipherEngine(**kwargs).decrypt_file()


def encrypt_text(**kwargs) -> NamedTuple:
    """
    #### Attributes:
        - `text`: str: The text to be processed and encrypted.
        - `file_name`: str | None: The name of the file containing the encryption details.
        - `export_path`: Path | None: The path where exported files will be stored (default: None).
        - `export_passkey`: bool: Flag indicating whether to export the passphrase to a separate file (default: True).
        - `serializer`: str: The type of serialization to be used for exporting the passkey file ('json' or 'ini').
        - `identifiers`: Iterable[str]: Specifiy a custom encryption identifier for the start and end of the encryption key (default: default settings.)
        
    #### Cryptographic Attributes:
        - `num_of_salts`: int: Number of `Fernet` keys to be generated and processed with `MultiFernet`. 
        - `include_all_chars`: bool: Flag indicating whether to include all characters during passphrase generation (default: False).
        - `exclude_chars`: str: Characters to exclude during passphrase generation (default: None).
        - `special_keys`: bool: If True, uses CipherEngines custom cryptographic key generation, \
            otherwise uses default keys generated from `Fernet` (default: True).
    
    #### Class Attributes:
        - `_ALL_CHARS`: str: A string containing all possible characters for passphrase generation.
        - `_MAX_KEYLENGTH`: int: The maximum length for cryptographic keys (32).
        - `_MAX_TOKENS`: int: Maximum number of tokens for cryptographic operations (default: 100,000).
        - `_MAX_CAPACITY`: int: = Maximumum number of characters to be generated. (For personal use only when using flexible `_generate_key` method.)
        - `_EXECUTOR`: ThreadPoolExecutor: Base executor for all engine classes.
    
    #### Important Notes:
        - Attributes `include_all_chars` and `exclude_chars` are more customizable features \
            using `secrets.SystemRandom` when generating Fernet keys compared to:
        
        >>> Fernet.generate_key() # Returns a string of bytes of only containing digits and ascii_letters
        
        -  `whitespace` ("(space)\\t\\n\\r\\v\\f") are automatically excluded from all available options, \
            as it can interfere with the encryption process when exporting the passkey file.
        
    #### Returns:
        - NamedTuple: Tuple containing information about the encryption process.
    """
    return CipherEngine(**kwargs).encrypt_text()


def decrypt_text(**kwargs) -> NamedTuple:
    return DecipherEngine(**kwargs).decrypt_text()


decrypt_text.__doc__ = decrypt_file.__doc__


def main():
    # a = encrypt_file(file='test.aes', overwrite_file=True)
    # print(a)
    # b = decrypt_file(ciphertuple=a, overwrite_file=True)
    # print(b)
    # a = encrypt_text(text="test", export_passkey=False, bypass_keylength=True)
    # b = decrypt_text(ciphertuple=a)
    # print(a)
    # print(b)
    a = encrypt_text(
        text="test", advanced_encryption=False, iterations=1000, rsa_iterations=1000, export_passkey=True, num_of_salts=2
    )
    b = decrypt_text(passkey_file="ciphertext_passkey.ini")
    b = decrypt_text(ciphertuple=a)
    print(a)
    # print(b)
    # print(_BaseEngine._compiler(('json', 'ini', 'env'), 'ini', escape_k=False))
    # print()
    # b =  [Fernet(Fernet.generate_key()) for _ in range(len(a.decipher_keys))]
    # print(MultiFernet(b).rotate(a.encrypted_text[len(a.id1):-len(a.id2)]))
    return True


# XXX Metadata Information
__version__ = "0.3.5"
__license__ = "Apache License, Version 2.0"
__url__ = "https://github.com/yousefabuz17/CipherEngine"
__author__ = "Yousef Abuzahrieh <yousef.zahrieh17@gmail.com"
__copyright__ = f"Copyright © 2024, {__author__}"
__summary__ = "Comprehensive cryptographic module providing file and text encryption, key generation, and rotation of decipher keys for additional security."

__all__ = (
    "encrypt_file",
    "decrypt_file",
    "encrypt_text",
    "decrypt_text",
    "CipherEngine",
    "DecipherEngine",
    "CipherException",
    "generate_crypto_key",
    "__doc__",
    "__version__",
    "__author__",
    "__license__",
    "__url__",
    "__copyright__",
    "__summary__",
)

if __name__ == "__main__":
    from cli_options import cli_parser

    try:
        main() or cli_parser()
    except NameError:
        # If missing markdown files for 'cli_options'.
        pass
