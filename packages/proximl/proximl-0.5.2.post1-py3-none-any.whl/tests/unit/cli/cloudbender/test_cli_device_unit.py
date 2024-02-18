import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.cloudbender, mark.devices]

from proximl.cli.cloudbender import device as specimen
from proximl.cloudbender.devices import Device


def test_list(runner, mock_devices):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.cloudbender = AsyncMock()
        mock_proximl.cloudbender.devices = AsyncMock()
        mock_proximl.cloudbender.devices.list = AsyncMock(
            return_value=mock_devices
        )
        result = runner.invoke(
            specimen,
            args=["list", "--provider=prov-id-1", "--region=reg-id-1"],
        )
        assert result.exit_code == 0
        mock_proximl.cloudbender.devices.list.assert_called_once_with(
            provider_uuid="prov-id-1", region_uuid="reg-id-1"
        )


def test_list_no_provider(runner, mock_devices):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.cloudbender = AsyncMock()
        mock_proximl.cloudbender.devices = AsyncMock()
        mock_proximl.cloudbender.devices.list = AsyncMock(
            return_value=mock_devices
        )
        result = runner.invoke(specimen, ["list"])
        assert result.exit_code != 0
