
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 theloop, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum


__jsonrpc_version = "2.0"


class Code(Enum):
    """Result code enumeration
    Refer to http://www.simple-is-better.org/json-rpc/jsonrpc20.html#examples
    """
    OK = 0

    # -32000 ~ -32099: Server error
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    PARSE_ERROR = -32700

    INVALID_TRANSACTION = -32800
    UNKNOWN_ERROR = -40000

__error_message = {
    Code.OK: "ok",

    Code.INVALID_REQUEST: "invalid request",
    Code.METHOD_NOT_FOUND: "method not found",
    Code.INVALID_PARAMS: "invalid params",
    Code.INTERNAL_ERROR: "internal error",
    Code.PARSE_ERROR: "parse error",

    Code.INVALID_TRANSACTION: "invalid transaction",
    Code.UNKNOWN_ERROR: "unknown error"
}

def get_code_message(code):
    default_message = "unknown code({code}-{str(code)})"
    return __error_message.get(code, default_message)

class IcxError(Exception):

    def __init__(self, code, message=None):
        self.code = code
        if message is None:
            message = get_code_message(code)
        self.message = message



def verify_transaction(transaction):
    """verify transaction using cryptography library
    """
    return True



def str_to_int(s):
    """Convert hexa string to int

    Args:
        hexa (str): ex) '0x1234'

    Returns:
        hexa string's int value
    """
    return int(s, 0)

def int_to_str(value):
    if type(value) != int:
        raise IcxError(Code.INVALID_PARAMS, 'param is not int type')

    return hex(value)



def is_hex(s):
    if not s.startswith('0x'):
        return False

    for i in range(2, len(s)):
        c = s[i]
        if '0' <= c <= '9' or 'a' <= c <= 'f':
            continue
        return False

    return True


def check_address(address):
    """Check icx address format
    Args:
        address (str):
        - lowercase alphabet
        - hexa string consists of 42 chars including '0x' prefix

    Return:
        bool: True or False
    """

    if not isinstance(address, str):
        return False
    if len(address) != 42:
        return False

    return is_hex(address)


def check_db(_db):
    if _db is None:
        raise IcxError(Code.INVALID_PARAMS, 'db is none')
    pass


def get_value(_db, key):
    """get value from leveldb.

    Args:
        _db (leveldb object)
        key (str)

    Returns:
        (str): hexa string
    """
    check_db(_db)
    value = None

    try:
        value = _db.Get(key.encode())
    except:
        return None

    return value.decode()


def set_value(_db, key, value):
    check_db(_db)
    _db.Put(key.encode(), value.encode())


def delete(_db, key):
    check_db(_db)
    _db.Delete(key.encode())


def get_balance_str(_db, address):
    value = get_value(_db, address)
    if value is None:
        value = '0x0'
    return value


def get_balance(_db, address):
    value = 0

    s = get_value(_db, address)
    if s is not None:
        value = str_to_int(s)

    return value


def set_balance_str(_db, address, value):
    """set balance to db.
    Args:
        address (str): icx address
        value (str): balance ex) '0x1234', '0x123'
    """
    set_value(_db, address, value)


def set_balance(_db, address, value):
    """set balance to db.
    Args:
        address (str): icx address
        value (int): balance ex) '0x1234', '0x123'
    """
    set_value(_db, address, int_to_str(value))


def set_balances(_db, params):
    """set balance to db.
    Args:
        _db (leveldb object)
        params: ex {"0xb60e8dd61c5d32be8058bb8eb970870f07233155": 10}
    """
    check_db(_db)
    batch = leveldb.WriteBatch()

    for address in params:
        value = params[address]

        if value > 0:
            set_value(batch, address, int_to_str(value))
        elif value == 0:
            delete(batch, address)
        else:
            raise ValueError

    _db.Write(batch, sync=True)


def create_jsonrpc_error_response(_id, code, message=None, data=None):
    """Create jsonrpc error response json object.
    """
    response = create_jsonrpc_common_response(_id)
    response["error"] = create_jsonrpc_error_object(code, message, data)

    return response


def create_jsonrpc_success_response(_id, result):
    """Create jsonrpc success response json object.
    """
    response = create_jsonrpc_common_response(_id)
    response["result"] = result

    return response


def create_jsonrpc_common_response(_id):
    """Create common response json object
    """
    response = {
        "jsonrpc": __jsonrpc_version,
        "id": _id,
    }

    return response


def create_jsonrpc_error_object(code, message=None, data=None):
    if type(code) != Code:
        raise IcxError(Code.INVALID_PARAMS, "code is not Code type.")

    if message is None:
        message = get_code_message(code)

    error = {
        "code": code.value,
        "message": message
    }

    if data:
        error["data"] = data

    return error


def create_invoke_response(code, message=None, data=None):
    return create_jsonrpc_error_object(code, message, data)
