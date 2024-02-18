import re
import json
import logging
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises
from aiohttp import WSMessage, WSMsgType

import proximl.cloudbender.reservations as specimen
from proximl.exceptions import (
    ApiError,
    SpecificationError,
    ProxiMLException,
)

pytestmark = [mark.sdk, mark.unit, mark.cloudbender, mark.reservations]


@fixture
def reservations(mock_proximl):
    yield specimen.Reservations(mock_proximl)


@fixture
def reservation(mock_proximl):
    yield specimen.Reservation(
        mock_proximl,
        provider_uuid="1",
        region_uuid="a",
        reservation_id="x",
        name="On-Prem Reservation",
        type="port",
        resource="8001",
        hostname="service.local",
    )


class RegionsTests:
    @mark.asyncio
    async def test_get_reservation(
        self,
        reservations,
        mock_proximl,
    ):
        api_response = dict()
        mock_proximl._query = AsyncMock(return_value=api_response)
        await reservations.get("1234", "5687", "91011")
        mock_proximl._query.assert_called_once_with(
            "/provider/1234/region/5687/reservation/91011", "GET", {}
        )

    @mark.asyncio
    async def test_list_reservations(
        self,
        reservations,
        mock_proximl,
    ):
        api_response = dict()
        mock_proximl._query = AsyncMock(return_value=api_response)
        await reservations.list("1234", "5687")
        mock_proximl._query.assert_called_once_with(
            "/provider/1234/region/5687/reservation", "GET", {}
        )

    @mark.asyncio
    async def test_remove_reservation(
        self,
        reservations,
        mock_proximl,
    ):
        api_response = dict()
        mock_proximl._query = AsyncMock(return_value=api_response)
        await reservations.remove("1234", "4567", "8910")
        mock_proximl._query.assert_called_once_with(
            "/provider/1234/region/4567/reservation/8910", "DELETE", {}
        )

    @mark.asyncio
    async def test_create_reservation(self, reservations, mock_proximl):
        requested_config = dict(
            provider_uuid="provider-id-1",
            region_uuid="region-id-1",
            name="On-Prem Reservation",
            type="port",
            resource="8001",
            hostname="service.local",
        )
        expected_payload = dict(
            name="On-Prem Reservation",
            type="port",
            resource="8001",
            hostname="service.local",
        )
        api_response = {
            "provider_uuid": "provider-id-1",
            "region_uuid": "region-id-1",
            "reservation_id": "reservation-id-1",
            "name": "On-Prem Reservation",
            "type": "port",
            "resource": "8001",
            "hostname": "service.local",
            "createdAt": "2020-12-31T23:59:59.000Z",
        }

        mock_proximl._query = AsyncMock(return_value=api_response)
        response = await reservations.create(**requested_config)
        mock_proximl._query.assert_called_once_with(
            "/provider/provider-id-1/region/region-id-1/reservation",
            "POST",
            None,
            expected_payload,
        )
        assert response.id == "reservation-id-1"


class reservationTests:
    def test_reservation_properties(self, reservation):
        assert isinstance(reservation.id, str)
        assert isinstance(reservation.provider_uuid, str)
        assert isinstance(reservation.region_uuid, str)
        assert isinstance(reservation.type, str)
        assert isinstance(reservation.name, str)
        assert isinstance(reservation.resource, str)
        assert isinstance(reservation.hostname, str)

    def test_reservation_str(self, reservation):
        string = str(reservation)
        regex = r"^{.*\"reservation_id\": \"" + reservation.id + r"\".*}$"
        assert isinstance(string, str)
        assert re.match(regex, string)

    def test_reservation_repr(self, reservation):
        string = repr(reservation)
        regex = (
            r"^Reservation\( proximl , \*\*{.*'reservation_id': '"
            + reservation.id
            + r"'.*}\)$"
        )
        assert isinstance(string, str)
        assert re.match(regex, string)

    def test_reservation_bool(self, reservation, mock_proximl):
        empty_reservation = specimen.Reservation(mock_proximl)
        assert bool(reservation)
        assert not bool(empty_reservation)

    @mark.asyncio
    async def test_reservation_remove(self, reservation, mock_proximl):
        api_response = dict()
        mock_proximl._query = AsyncMock(return_value=api_response)
        await reservation.remove()
        mock_proximl._query.assert_called_once_with(
            "/provider/1/region/a/reservation/x", "DELETE"
        )

    @mark.asyncio
    async def test_reservation_refresh(self, reservation, mock_proximl):
        api_response = {
            "provider_uuid": "provider-id-1",
            "region_uuid": "region-id-1",
            "reservation_id": "reservation-id-1",
            "name": "On-Prem Reservation",
            "type": "port",
            "resource": "8001",
            "hostname": "service.local",
            "createdAt": "2020-12-31T23:59:59.000Z",
        }
        mock_proximl._query = AsyncMock(return_value=api_response)
        response = await reservation.refresh()
        mock_proximl._query.assert_called_once_with(
            f"/provider/1/region/a/reservation/x", "GET"
        )
        assert reservation.id == "reservation-id-1"
        assert response.id == "reservation-id-1"
