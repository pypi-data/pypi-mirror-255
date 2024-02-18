import re
import logging
import json
import os
from unittest.mock import AsyncMock, patch, mock_open, MagicMock
from pytest import mark, fixture, raises
from aiohttp import WSMessage, WSMsgType

import proximl.auth as specimen

pytestmark = [mark.sdk, mark.unit]


@patch.dict(
    os.environ,
    {
        "PROXIML_USER": "user-id",
        "PROXIML_KEY": "key",
        "PROXIML_REGION": "ap-east-1",
        "PROXIML_CLIENT_ID": "client_id",
        "PROXIML_POOL_ID": "pool_id",
    },
)
def test_auth_from_envs():
    auth = specimen.Auth(config_dir=os.path.expanduser("~/.proximl"))
    assert auth.__dict__.get("username") == "user-id"
    assert auth.__dict__.get("password") == "key"
    assert auth.__dict__.get("region") == "ap-east-1"
    assert auth.__dict__.get("client_id") == "client_id"
    assert auth.__dict__.get("pool_id") == "pool_id"
