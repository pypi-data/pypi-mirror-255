import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.gpu_types]

from proximl.cli import gpu as specimen
from proximl.gpu_types import GpuType


def test_list(runner, mock_gpu_types):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.gpu_types = AsyncMock()
        mock_proximl.gpu_types.list = AsyncMock(return_value=mock_gpu_types)
        result = runner.invoke(specimen, ["list"])
        print(result)
        assert result.exit_code == 0
        mock_proximl.gpu_types.list.assert_called_once()
