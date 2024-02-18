import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.environments]

from proximl.cli import environment as specimen
from proximl.environments import Environment


def test_list(runner, mock_environments):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.environments = AsyncMock()
        mock_proximl.environments.list = AsyncMock(
            return_value=mock_environments
        )
        result = runner.invoke(specimen, ["list"])
        assert result.exit_code == 0
        mock_proximl.environments.list.assert_called_once()
