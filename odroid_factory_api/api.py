import asyncio
from re import A
import aiohttp

try:
    from .constants import *
except ImportError:
    from constants import *

class API_MANAGER:

    #def __init__(self, board, server_host=API_SERVER_HOST):
    def __init__(self, board, server_host=API_TEST_SERVER_HOST):
        # Version
        # All of the python files place on the same diectory follows this version
        self.version = '1.3'

        # Properties
        self.server_host = server_host
        self.board = board.lower()
        self.mac_addr = None
        self.uuid_mac = None
        self.api_auth_expires_in = 0
        self.api_auth_token = ''
        self.msg_en = 0

    def info_print(self):
        self.log(f'================================')
        self.log(f'API version: {self.version}')
        self.log(f'Server URL for test: {self.server_host}')
        self.log(f'Given board: {self.board}')
        self.log(f'================================')

    async def _login_to_api_server(self):
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    url=self.server_host + API_POST_URL['login'],
                    headers={
                        'content-type': 'application/json'
                    },
                    ssl=False,
                    json=API_USER_INFO
                )
                response_json = await response.json()
        except Exception as error:
            return { 'error': str(error) }

        if 'error' not in response_json:
            self.log(f'API: Success: {response_json}')
            self.api_auth_expires_in = response_json['expires_in']
            self.api_auth_token = response_json['token']
        else:
            error_msg = response_json['error']
            self.log(f'API: Error: {error_msg}')
            response_json['error'] = error_msg

        return response_json

    async def _check_token_expired(self):
        response = await self._login_to_api_server()

        if 'error' in response:
            return False
        else:
            self.log('API: Info: Renewing the token success')

        return True

    async def update_record(self, data):
        if (type(data) is not dict):
            error_msg = 'Given fields/data type must be Dictionary'
            self.log(f'API: Error: {error_msg}')
            return { 'error' : error_msg }

        # Filters invalid fields
        for entry in data:
            # Check if the given field is valid
            if entry not in TABLE_FIELDS_BY_BOARD[self.board]:
                error_msg = 'Invalid field found: ' + entry
                self.log(f'API: Error: {error_msg}')
                return { 'error': error_msg }

            # Check if the type of the given value is boolean that is not supported on the server
            if type(data[entry]) is bool:
                data[entry] = 1 if data[entry] else 0

            # Check if the type of the given value is float that is not supported on the server
            if type(data[entry]) is float:
                data[entry] = str(data[entry])

            # Check if there's any white space exists in the value string
            if type(data[entry]) is str:
                data[entry] = data[entry].replace(' ', '')

        data['mac_addr'] = self.mac_addr
        data['board'] = self.board

        if not await self._check_token_expired():
            error_msg = 'Failed to renew the token'
            self.log(f'API: Error: {error_msg}')
            return { 'error': error_msg }

        try:
            self.log(f'API: Try to send data: {data}')

            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    url=self.server_host + API_POST_URL['update'],
                    headers={
                        'content-type': 'application/json',
                        'Authorization': 'Token ' + self.api_auth_token
                    },
                    ssl=False,
                    json=data
                )
                response_json = await response.json()
        except Exception as error:
            self.log(f'API: Exception: {str(error)}')
            return { 'error': str(error) }

        if response.status == 401:
            self.log(f'API: Unauthorized: {response_json}')
        else:
            self.api_auth_expires_in = response_json['auth']['expires_in']
            if response.status == 200 and 'error' not in response_json:
                self.log(f'API: Success: {response_json}')
                self.last_update_return = response_json
            else:
                self.log(f'API: Error: {response_json}')

        return response_json

    async def request_mac_addr(self):
        if self.board is None:
            return

        if not await self._check_token_expired():
            error_msg = 'Failed to renew the token'
            self.log(f'API: Error: {error_msg}')
            return { 'error': error_msg }

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.server_host + API_POST_URL['request'],
                headers={
                    'content-type': 'application/json',
                    'Authorization': 'Token ' + self.api_auth_token
                },
                ssl=False,
                json={
                    'board': self.board
                })
            response_json = await response.json()
        self.log('4')

        if response.status == 401:
            self.log(f'API: Unauthorized: {response_json}')
        else:
            self.api_auth_expires_in = response_json['auth']['expires_in']
            if response.status == 200 and 'error' not in response_json:
                self.log(f'API: Success: {response_json}')
                self.mac_addr = response_json['mac_addr']

                # For N2, ...
                if 'uuid_mac' in response_json:
                    self.uuid_mac = response_json['uuid_mac']

                # The return value will be
                # only mac address (001e06300001) or
                # including uuid (00000000-...-001e06420001) string
                return self.uuid_mac or self.mac_addr
            else:
                self.log(f'API: Error: {response_json}')
                return response_json

    async def delete_assigned_sign(self):
        # If it obtains MAC address from the API server but it couldn't write
        # that, delete assigned sign that is written temporary from the record has
        # obtained MAC address on the database.
        if self.board is None or self.mac_addr is None:
            self.log(f'{self.board} / {self.mac_addr}')
            return

        if not await self._check_token_expired():
            error_msg = 'Failed to renew the token'
            self.log(f'API: Error: {error_msg}')
            return { 'error': error_msg }

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.server_host + API_POST_URL['delete'],
                headers={
                    'content-type': 'application/json',
                    'Authorization': 'Token ' + self.api_auth_token
                },
                ssl=False,
                json={
                    'mac_addr': self.mac_addr,
                    'board': self.board
                })
            response_json = await response.json()

        if response.status == 401:
            self.log(f'API: Unauthorized: {response_json}')
        else:
            self.api_auth_expires_in = response_json['auth']['expires_in']
            if response.status == 200 and 'error' not in response_json:
                self.log(f'API: Success: {response_json}')
            else:
                self.log(f'API: Error: {response_json}')
        return response_json

    async def get_criteria_for_board(self):
        if not await self._check_token_expired():
            error_msg = 'Failed to renew the token'
            self.log(f'API: Error: {error_msg}')
            return { 'error': error_msg }

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.server_host + API_POST_URL['criteria'],
                headers={
                    'content-type': 'application/json',
                    'Authorization': 'Token ' + self.api_auth_token
                },
                ssl=False,
                json={
                    'board': self.board
                })
            response_json = await response.json()

        if response.status == 401:
            self.log(f'API: Unauthorized: {response_json}')
        else:
            self.api_auth_expires_in = response_json['auth']['expires_in']
            if response.status == 200 and 'error' not in response_json:
                self.log(f'API: Success: {response_json}')
            else:
                self.log(f'API: Error: {response_json}')

        return response

    async def get_counts(self, filter, filter_only_all_pass=True, update_date_from=None, update_date_to=None):
        if not await self._check_token_expired():
            error_msg = 'Failed to renew the token'
            self.log(f'API: Error: {error_msg}')
            return { 'error': error_msg }

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.server_host + API_POST_URL['counts'],
                headers={
                    'content-type': 'application/json',
                    'Authorization': 'Token ' + self.api_auth_token
                },
                ssl=False,
                json={
                    'board': self.board,
                    'filter': filter,
                    'filter_only_all_pass': filter_only_all_pass,
                    'update_date_from': update_date_from,
                    'update_date_to': update_date_to
                })
            response_json = await response.json()

        if response.status == 401:
            self.log(f'API: Unauthorized: {response_json}')
        else:
            self.api_auth_expires_in = response_json['auth']['expires_in']
            if response.status == 200 and 'error' not in response_json:
                self.log(f'API: Success: {response_json}')
            else:
                self.log(f'API: Error: {response_json}')

        return response_json['counts']

    def log_en(self, en):
        self.msg_en = en

    def log(self, msg):
        if self.msg_en == 1 :
            print(msg)

    def clear(self, board):
        self.mac_addr = None
        self.uuid_mac = None
        self.api_auth_expires_in = 0
        self.api_auth_token = ''
        self.board = board
    
    def set_mac_addr (self, m):
        self.mac_addr = m
        self.log (self.mac_addr)

if __name__ == "__main__":
    api_manager = API_MANAGER(board='m1')
    api_manager.log_en(1)
    uuid = asyncio.run(api_manager.request_mac_addr())
    asyncio.run(api_manager.update_record({'uuid': uuid}))
    asyncio.run(api_manager.delete_assigned_sign())
    uuid_msg = 'mac,' + uuid
    asyncio.run(api_manager.log (uuid))
    api_manager.log(uuid_msg)
    
    # await api_manager.update_record({'uuid': uuid})
    
