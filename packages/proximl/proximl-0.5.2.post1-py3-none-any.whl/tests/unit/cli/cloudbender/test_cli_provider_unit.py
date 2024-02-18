import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.cloudbender, mark.providers]

from proximl.cli.cloudbender import provider as specimen
from proximl.cloudbender.providers import Provider


def test_list(runner, mock_providers):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.cloudbender = AsyncMock()
        mock_proximl.cloudbender.providers = AsyncMock()
        mock_proximl.cloudbender.providers.list = AsyncMock(
            return_value=mock_providers
        )
        result = runner.invoke(specimen, ["list"])
        assert result.exit_code == 0
        mock_proximl.cloudbender.providers.list.assert_called_once()
