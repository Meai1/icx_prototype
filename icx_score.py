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

"""ICX SCORE Prototyping code to explain basic SCORE example, NOT OFFICIAL ICX CODE!!!!
NO GUARANTEE FOR ANY RISK OR TROUBLE.
"""

import os
import sys
import leveldb
import json

from loopchain.blockchain import ScoreBase
from loopchain.tools.score_helper import ScoreHelper, ScoreDatabaseType, LogLevel

# Add current path to load other python code.
# SCORE can load module in current path. So you need to add current path into PYTHONPATH.
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path)

# To-Do: Import your own module you wanna to load.
from icx import *


class UserScore(ScoreBase):
    """ICX Coin Score code

    ICX SCORE Prototyping code to explain basic SCORE example, NOT OFFICIAL ICX CODE!!!!
    NO GUARANTEE FOR ANY RISK OR TROUBLE.

    """
    __score_info = None
    __db_id = 'icx.db'
    __db = None
    __score_helper = None
    __initialized = False

    def __init__(self, info=None):
        """Initialize SCORE.
        """

        # Initialize SCORE info and DB module.
        self.logi('__init__() start')
        self.__init_score_info(info)
        self.__init_score_helper()
        self.__init_db()
        self.logd('__init__() end')

    def __init_score_info(self, info):
        """ Read package.json file as SCORE package information.

        ScoreHelper is special module to capsulize SCORE operation.
        """
        if info is None:
            with open(dirname(__file__)+'/'+ScoreBase.PACKAGE_FILE, 'r') as f:
                self.__score_info = json.loads(f.read())
                f.close()
        else:
            self.__score_info = info

    def __init_score_helper(self):
        """ Initialize ScoreHelper().

        ScoreHelper is special module to capsulize SCORE operation.
        """

        if self.__score_helper is None:
            self.__score_helper = ScoreHelper()

    def __init_db(self):
        """ Initialize database for SCORE.

        SCORE have to store all data into its own database.
        """

        self.logd('__init_db() start')
        if self.__db is None:
            db = self.__score_helper.load_database(
                score_id=self.__db_id,
                database_type=ScoreDatabaseType.leveldb)
            self.logd(f'db({db}) is created.')
            self.__db = db

        # TESTING purpose.
        # Create virtual bank account ( 0x00000000000000000000000000000000000000000000 ) into 10^22 ICX.
        address = '0x' + '0' * 40
        value = get_balance(self.__db, address)
        if value == 0:
            value = 10 ** 22
            set_balance(self.__db, address, value)
            self.logd(f'address({address}): {value}')

        self.logd('__init_db() end')


    def invoke(self, transaction, block):
        """ Handler of 'Invoke' requests.

        It's event handler of invoke request. You need to implement this handler like below.
        0. Define the interface of functions in 'invoke' field of package.json.
        1. Parse transaction data and get the name of function by reading 'method' field of transaction.
        2. Call that function.

        :param transaction: transaction data.
        :param block: block data has transaction data.
        :return: response : Invoke result.
        """

        self.logd('invoke() start')

        response = None

        try:
            if not verify_transaction(transaction):
                raise IcxError(Code.INVALID_TRANSACTION)

            # Parse transaction data.
            data = transaction.get_data_string()
            params = json.loads(data)
            self.logi(data)

            methods = {
                'icx_init': self.__invoke_init,
                'icx_sendTransaction': self.__invoke_sendTransaction
            }

            method_name = params['method']
            method = methods.get(method_name, None)
            if method is None:
                raise IcxError(Code.METHOD_NOT_FOUND, method_name)

            # Call pre-defined functions in package.json by the request in transaction.
            method(transaction, block, params['params'])

        # Return response code.
        except IcxError as ie:
            response = create_invoke_response(ie.code, ie.message)
        except Exception as e:
            response = create_invoke_response(Code.UnknownError, str(e))
        else:
            response = create_invoke_response(Code.OK)


        self.logi(f'invoke result: {str(response)}')
        self.logd('invoke() end')

        return response



    def __invoke_init(self, transaction, block, params):
        """ Initialize the value of account.

        :param transaction: Transaction data.
        :param block: Block data.
        :param params: params from transaction data including 'address' and'value'.
        """

        self.logd('__invoke_init() start')
        self.logd(f'{str(params)}')

        if self.__initialized:
            raise IcxError(Code.INVALID_TRANSACTION, 'icx_score has been already initialized.')

        address = params['address']
        value = params['value']
        set_balance_str(self.__db, address, value)
        self.__initialized = True

        self.logd('__invoke_init() end')



    def __invoke_sendTransaction(self, transaction, block, params):
        """ Transfer money to other's bank account.

        :param transaction: Transaction data.
        :param block: Block data.
        :param params: params from transaction data including 'from', 'to', and 'value'
        """
        self.logd('__invoke_sendTransaction() start')

        from_address = params['from']
        to_address = params['to']
        value = str_to_int(params['value'])

        if value <= 0:
            raise IcxError(Code.INVALID_PARAMS, f'value({value}) is invalid.')

        from_balance = get_balance(self.__db, from_address)
        if from_balance < value:
            raise IcxError(Code.INVALID_PARAMS,
                f'from_balance({from_balance}) is less than transaction value({value})')

        to_balance = get_balance(self.__db, to_address)

        from_balance -= value
        to_balance += value

        set_balances(self.__db,
            {from_address: from_balance, to_address: to_balance})

        self.logd('__invoke_sendTransaction() end')



    def query(self, params):
        """ Handler of 'Query' requests.

        It's event handler of query request. You need to implement this handler like below.
        0. Define the interface of functions in 'query' field of package.json.
        1. Parse transaction data and get the name of function by reading 'method' field of transaction.
        2. Call that function.

        :param transaction: transaction data.
        :param block: block data has transaction data.
        :return: response : Query result.
        """
        self.logd('query() start')
        self.logd('params: ' + str(params))

        _id = None
        response = None

        methods = {
            'icx_getBalance': self.__query_getBalance
        }

        try:
            request = json.loads(params)

            _id = request['id']
            method_name = request['method']

            response = methods.get(
                method_name, self.__handle_method_not_found)(_id, request)

        except IcxError as ie:
            response = create_jsonrpc_error_response(_id, ie.code, ie.message)
        except Exception as e:
            response = create_jsonrpc_error_response(_id, Code.UnknownError)

        self.logd('query() end')

        return json.dumps(response)

    def __query_getBalance(self, _id, request):
        """ Get the current value of bank account.

        :param _id: ID of request. Used it to distingush request.
        :param request: Request information
        :return:
        """
        self.logd('__query_getBalance() start')
        self.logd(f'{str(request)}')

        params = request['params']
        self.logd(params)
        address = params[0]
        self.logd(address)

        if not check_address(address):
            return create_jsonrpc_error_response(
                _id, Code.INVALID_PARAMS, f'invalid address({address})')

        value = get_balance_str(self.__db, address)
        response = create_jsonrpc_success_response(_id, value)

        self.logd('__query_get_balance() end')

        return response

    def __handle_method_not_found(self, _id, request):
        self.logd('__handle_method_not_found() start')

        method_name = request['method']
        response = create_jsonrpc_error_response(
            _id, Code.METHOD_NOT_FOUND, method_name)

        self.logd('__handle_method_not_found() end')

        return response

    def info(self):
        return self.__score_info

    def log(self, level, message):
        if self.__score_helper:
            self.__score_helper.log("ICX", message, level)

    def logd(self, message):
        self.log(LogLevel.DEBUG, message)

    def logi(self, message):
        self.log(LogLevel.INFO, message)

