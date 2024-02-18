import asyncio
from pytest import fixture, mark
from unittest.mock import Mock, patch, create_autospec

from proximl.proximl import ProxiML

pytestmark = mark.integration

ENVS = {
    "dev": dict(
        region="us-east-2",
        client_id="6hiktq1842ko01jmtbafd0ki87",
        pool_id="us-east-2_OhcBqdjVS",
        domain_suffix="proximl.dev",
        api_url="api.proximl.dev",
        ws_url="api-ws.proximl.dev",
    ),
    "staging": dict(
        region="us-east-2",
        client_id="6hiktq1842ko01jmtbafd0ki87",
        pool_id="us-east-2_OhcBqdjVS",
        domain_suffix="proximl.page",
        api_url="api.proximl.page",
        ws_url="api-ws.proximl.page",
    ),
    "prod": dict(
        region="us-east-2",
        client_id="32mc1obk9nq97iv015fnmc5eq5",
        pool_id="us-east-2_68kbvTL5p",
        domain_suffix="proximl.ai",
        api_url="api.proximl.ai",
        ws_url="api-ws.proximl.ai",
    ),
}


@fixture(scope="session")
def env(request):
    env = request.config.getoption("--env")
    yield ENVS[env]


@fixture(scope="module")
def proximl(env):
    proximl = ProxiML(**env)
    yield proximl
