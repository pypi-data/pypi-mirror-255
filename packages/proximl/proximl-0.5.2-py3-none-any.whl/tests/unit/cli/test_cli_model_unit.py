import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.models]

from proximl.cli import model as specimen
from proximl.models import Model


def test_list(runner, mock_models):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.models = AsyncMock()
        mock_proximl.models.list = AsyncMock(return_value=mock_models)
        result = runner.invoke(specimen, ["list"])
        print(result)
        assert result.exit_code == 0
        mock_proximl.models.list.assert_called_once()
