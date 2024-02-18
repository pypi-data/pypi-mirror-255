import re
import logging
import json
import os
from unittest.mock import AsyncMock, patch, mock_open
from pytest import mark, fixture, raises
from aiohttp import WSMessage, WSMsgType

import proximl.proximl as specimen

pytestmark = [mark.sdk, mark.unit]


@patch.dict(
    os.environ,
    {
        "PROXIML_USER": "user-id",
        "PROXIML_KEY": "key",
        "PROXIML_REGION": "region",
        "PROXIML_CLIENT_ID": "client_id",
        "PROXIML_POOL_ID": "pool_id",
        "PROXIML_API_URL": "api.example.com",
        "PROXIML_WS_URL": "api-ws.example.com",
    },
)
def test_proximl_from_envs():
    proximl = specimen.ProxiML()
    assert proximl.__dict__.get("api_url") == "api.example.com"
    assert proximl.__dict__.get("ws_url") == "api-ws.example.com"
    assert proximl.auth.__dict__.get("username") == "user-id"
    assert proximl.auth.__dict__.get("password") == "key"
    assert proximl.auth.__dict__.get("region") == "region"
    assert proximl.auth.__dict__.get("client_id") == "client_id"
    assert proximl.auth.__dict__.get("pool_id") == "pool_id"


def test_proximl_env_from_files():
    with patch(
        "proximl.proximl.open",
        mock_open(
            read_data=json.dumps(
                dict(
                    region="region_file",
                    client_id="client_id_file",
                    pool_id="pool_id_file",
                    api_url="api.example.com_file",
                    ws_url="api-ws.example.com_file",
                )
            )
        ),
    ):
        proximl = specimen.ProxiML()
    assert proximl.__dict__.get("api_url") == "api.example.com_file"
    assert proximl.__dict__.get("ws_url") == "api-ws.example.com_file"
