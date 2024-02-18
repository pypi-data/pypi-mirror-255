import re
import json
import click
from unittest.mock import AsyncMock, patch
from pytest import mark, fixture, raises

pytestmark = [mark.cli, mark.unit, mark.jobs]

from proximl.cli import job as specimen
from proximl.jobs import Job


def test_list(runner, mock_jobs):
    with patch("proximl.cli.ProxiML", new=AsyncMock) as mock_proximl:
        mock_proximl.jobs = AsyncMock()
        mock_proximl.jobs.list = AsyncMock(return_value=mock_jobs)
        result = runner.invoke(specimen, ["list"])
        print(result)
        assert result.exit_code == 0
        mock_proximl.jobs.list.assert_called_once()
