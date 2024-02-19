from datetime import timedelta, datetime
from http import HTTPStatus
from typing import List

import aiohttp
from aiohttp import ClientResponseError

from evdutyapi import Station
from evdutyapi.api_response.charging_session_response import ChargingSessionResponse
from evdutyapi.api_response.station_response import StationResponse
from evdutyapi.api_response.terminal_details_response import TerminalDetailsResponse


class EVDutyApi:
    base_url = 'https://api.evduty.net'

    def __init__(self, username: str, password: str, session: aiohttp.ClientSession):
        self.username = username
        self.password = password
        self.session = session
        self.headers = {'Content-Type': 'application/json'}
        self.expires_at = datetime.now() - timedelta(seconds=1)

    async def async_authenticate(self) -> None:
        if datetime.now() < self.expires_at:
            return

        json = {'device': {'id': '', 'model': '', 'type': 'ANDROID'}, 'email': self.username, 'password': self.password}
        async with self.session.post(f'{self.base_url}/v1/account/login', json=json, headers=self.headers) as response:
            await self.__raise_on_error(response)
            body = await response.json()
            self.headers['Authorization'] = 'Bearer ' + body['accessToken']
            self.expires_at = datetime.now() + timedelta(seconds=body['expiresIn'])

    async def async_get_stations(self) -> List[Station]:
        await self.async_authenticate()
        async with self.session.get(f'{self.base_url}/v1/account/stations', headers=self.headers) as response:
            await self.__raise_on_error(response)
            json_stations = await response.json()
            stations = [StationResponse.from_json(s) for s in json_stations]
            await self.__async_get_terminals(stations)
            await self.__async_get_sessions(stations)
            return stations

    async def __async_get_terminals(self, stations) -> None:
        for station in stations:
            for terminal in station.terminals:
                async with self.session.get(f'{self.base_url}/v1/account/stations/{station.id}/terminals/{terminal.id}', headers=self.headers) as response:
                    await self.__raise_on_error(response)
                    json_terminal_details = await response.json()
                    terminal.network_info = TerminalDetailsResponse.from_json(json_terminal_details)

    async def __async_get_sessions(self, stations) -> None:
        for station in stations:
            for terminal in station.terminals:
                async with self.session.get(f'{self.base_url}/v1/account/stations/{station.id}/terminals/{terminal.id}/session', headers=self.headers) as response:
                    await self.__raise_on_error(response)
                    if await response.text() != '':
                        json_session = await response.json()
                        terminal.session = ChargingSessionResponse.from_json(json_session)

    async def __raise_on_error(self, response):
        try:
            response.raise_for_status()
        except ClientResponseError as error:
            if self.is_auth_failed(error.status):
                self.expires_at = datetime.now() - timedelta(seconds=1)
                del self.headers['Authorization']
            raise error

    @staticmethod
    def is_auth_failed(status: HTTPStatus):
        return status == HTTPStatus.FORBIDDEN or status == HTTPStatus.UNAUTHORIZED
