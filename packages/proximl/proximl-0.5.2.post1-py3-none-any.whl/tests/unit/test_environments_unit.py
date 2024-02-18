import re
from unittest.mock import AsyncMock
from pytest import mark, fixture

import proximl.environments as specimen

pytestmark = [mark.sdk, mark.unit, mark.environments]


@fixture
def environments(mock_proximl):
    yield specimen.Environments(mock_proximl)


@fixture
def environment(mock_proximl):
    yield specimen.Environment(
        mock_proximl,
        **{
            "id": "PYTORCH_PY38_17",
            "framework": "PyTorch",
            "py_version": "3.8",
            "version": "1.7",
            "cuda_version": "11.1",
            "name": "PyTorch 1.7 - Python 3.8",
        },
    )


class EnvironmentsTests:
    @mark.asyncio
    async def test_list_environments(self, environments, mock_proximl):
        api_response = dict()
        mock_proximl._query = AsyncMock(return_value=api_response)
        await environments.list()
        mock_proximl._query.assert_called_once_with(
            f"/job/environments", "GET"
        )


class EnvironmentTests:
    def test_environment_properties(self, environment):
        assert isinstance(environment.id, str)
        assert isinstance(environment.name, str)
        assert isinstance(environment.py_version, str)
        assert isinstance(environment.framework, str)
        assert isinstance(environment.version, str)
        assert isinstance(environment.cuda_version, str)

    def test_environment_str(self, environment):
        string = str(environment)
        regex = r"^{.*\"id\": \"" + environment.id + r"\".*}$"
        assert isinstance(string, str)
        assert re.match(regex, string)

    def test_environment_repr(self, environment):
        string = repr(environment)
        regex = (
            r"^Environment\( proximl , \*\*{.*'id': '"
            + environment.id
            + r"'.*}\)$"
        )
        assert isinstance(string, str)
        assert re.match(regex, string)
