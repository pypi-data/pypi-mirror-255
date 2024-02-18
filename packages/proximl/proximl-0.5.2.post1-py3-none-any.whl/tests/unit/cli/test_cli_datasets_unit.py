import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.datasets]

from proximl.cli import dataset as specimen
from proximl.datasets import Dataset


def test_list(runner, mock_my_datasets):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.datasets = AsyncMock()
        mock_proximl.datasets.list = AsyncMock(return_value=mock_my_datasets)
        result = runner.invoke(specimen, ["list"])
        print(result)
        assert result.exit_code == 0
        mock_proximl.datasets.list.assert_called_once()
