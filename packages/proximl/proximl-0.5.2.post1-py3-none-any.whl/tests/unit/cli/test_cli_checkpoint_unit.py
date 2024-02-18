import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.checkpoints]

from proximl.cli import checkpoint as specimen
from proximl.checkpoints import Checkpoint


def test_list(runner, mock_my_checkpoints):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.checkpoints = AsyncMock()
        mock_proximl.checkpoints.list = AsyncMock(
            return_value=mock_my_checkpoints
        )
        result = runner.invoke(specimen, ["list"])
        print(result)
        assert result.exit_code == 0
        mock_proximl.checkpoints.list.assert_called_once()
