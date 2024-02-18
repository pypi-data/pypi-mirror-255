import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.cloudbender, mark.datastores]

from proximl.cli.cloudbender import datastore as specimen
from proximl.cloudbender.datastores import Datastore


def test_list(runner, mock_datastores):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.cloudbender = AsyncMock()
        mock_proximl.cloudbender.datastores = AsyncMock()
        mock_proximl.cloudbender.datastores.list = AsyncMock(
            return_value=mock_datastores
        )
        result = runner.invoke(
            specimen,
            args=["list", "--provider=prov-id-1", "--region=reg-id-1"],
        )
        assert result.exit_code == 0
        mock_proximl.cloudbender.datastores.list.assert_called_once_with(
            provider_uuid="prov-id-1", region_uuid="reg-id-1"
        )


def test_list_no_provider(runner, mock_datastores):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.cloudbender = AsyncMock()
        mock_proximl.cloudbender.datastores = AsyncMock()
        mock_proximl.cloudbender.datastores.list = AsyncMock(
            return_value=mock_datastores
        )
        result = runner.invoke(specimen, ["list"])
        assert result.exit_code != 0
