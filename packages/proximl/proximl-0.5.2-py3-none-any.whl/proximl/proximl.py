import json
import os
import asyncio
import aiohttp
import logging
import traceback
from importlib.metadata import version

from proximl.auth import Auth
from proximl.datasets import Datasets
from proximl.models import Models
from proximl.checkpoints import Checkpoints
from proximl.jobs import Jobs
from proximl.gpu_types import GpuTypes
from proximl.environments import Environments
from proximl.exceptions import ApiError, ProxiMLException
from proximl.connections import Connections
from proximl.projects import Projects
from proximl.cloudbender import Cloudbender


async def delayed_close(ws):
    await asyncio.sleep(15)
    if not ws.closed:
        await ws.close()


class ProxiML(object):
    def __init__(self, **kwargs):
        self._version = version("proximl")
        CONFIG_DIR = os.path.expanduser(
            os.environ.get("PROXIML_CONFIG_DIR") or "~/.proximl"
        )
        try:
            with open(f"{CONFIG_DIR}/environment.json", "r") as file:
                env_str = file.read().replace("\n", "")
            env = json.loads(env_str)
        except OSError:
            env = dict()
        try:
            with open(f"{CONFIG_DIR}/config.json", "r") as file:
                config_str = file.read().replace("\n", "")
            config = json.loads(config_str)
        except OSError:
            config = dict()
        self.domain_suffix = (
            kwargs.get("domain_suffix")
            or os.environ.get("PROXIML_DOMAIN_SUFFIX")
            or env.get("domain_suffix")
            or "proximl.ai"
        )
        self.auth = Auth(
            domain_suffix=self.domain_suffix,
            user=kwargs.get("user"),
            key=kwargs.get("key"),
            region=kwargs.get("region"),
            client_id=kwargs.get("client_id"),
            pool_id=kwargs.get("pool_id"),
        )
        self.active_project = (
            kwargs.get("project")
            or os.environ.get("PROXIML_PROJECT")
            or config.get("project")
        )
        self.datasets = Datasets(self)
        self.models = Models(self)
        self.checkpoints = Checkpoints(self)
        self.jobs = Jobs(self)
        self.gpu_types = GpuTypes(self)
        self.environments = Environments(self)
        self.connections = Connections(self)
        self.projects = Projects(self)
        self.cloudbender = Cloudbender(self)
        self.api_url = (
            kwargs.get("api_url")
            or os.environ.get("PROXIML_API_URL")
            or env.get("api_url")
            or f"api.{self.domain_suffix}"
        )
        self.ws_url = (
            kwargs.get("ws_url")
            or os.environ.get("PROXIML_WS_URL")
            or env.get("ws_url")
            or f"api-ws.{self.domain_suffix}"
        )

    @property
    def project(self) -> str:
        return self.active_project

    async def _query(self, path, method, params=None, data=None, headers=None):
        try:
            tokens = self.auth.get_tokens()
        except ProxiMLException as e:
            raise e
        except Exception:
            raise ProxiMLException(
                f"Error getting authorization tokens.  Verify configured credentials. Error: {traceback.format_exc()}"
            )
        logging.debug(
            f"Call parameters - Path: {path}, Method: {method}, Params: {params}, Body: {data}, Headers: {headers}"
        )
        headers = (
            {
                **headers,
                **{
                    "Authorization": tokens.get("id_token"),
                    "User-Agent": f"proxiML-sdk/{self._version}",
                },
            }
            if headers
            else {
                "Authorization": tokens.get("id_token"),
                "User-Agent": f"proxiML-sdk/{self._version}",
            }
        )
        if params:
            if not isinstance(params, dict):
                raise ProxiMLException(
                    "Query parameters must be a valid dictionary"
                )
            params = {
                k: (str(v).lower() if isinstance(v, bool) else v)
                for k, v in params.items()
            }  ## aiohttp doesn't support boolean
        if (
            method != "POST"
            and self.active_project
            and (not params or "project_uuid" not in params.keys())
        ):
            params = (
                {**params, **{"project_uuid": self.active_project}}
                if params
                else {"project_uuid": self.active_project}
            )

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        url = f"https://{self.api_url}{path}"

        logging.debug(
            f"Request - Url: {url}, Method: {method}, Params: {params}, Body: {data}, Headers: {headers}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                data=json.dumps(data),
                headers=headers,
                params=params,
            ) as resp:
                if (resp.status // 100) in [4, 5]:
                    what = await resp.read()
                    content_type = resp.headers.get("content-type", "")
                    resp.close()
                    if content_type == "application/json":
                        raise ApiError(
                            resp.status, json.loads(what.decode("utf8"))
                        )
                    else:
                        raise ApiError(
                            resp.status, {"message": what.decode("utf8")}
                        )
                results = await resp.json()
                return results

    async def _ws_subscribe(self, entity, project_uuid, id, msg_handler):
        headers = {
            "User-Agent": f"proxiML-sdk/{self._version}",
            "Content-Type": "application/json",
        }
        try:
            tokens = self.auth.get_tokens()
        except ProxiMLException as e:
            raise e
        except Exception:
            raise ProxiMLException(
                f"Error getting authorization tokens.  Verify configured credentials. Error: {traceback.format_exc()}"
            )
        async with aiohttp.ClientSession() as session:
            done = False
            async with session.ws_connect(
                f"wss://{self.ws_url}?Authorization={tokens.get('id_token')}",
                headers=headers,
                heartbeat=30,
            ) as ws:
                asyncio.create_task(
                    ws.send_json(
                        dict(
                            action="getlogs",
                            data=dict(
                                type="init",
                                entity=entity,
                                id=id,
                                project_uuid=project_uuid,
                            ),
                        )
                    )
                )
                asyncio.create_task(
                    ws.send_json(
                        dict(
                            action="subscribe",
                            data=dict(
                                type="logs",
                                entity=entity,
                                id=id,
                                project_uuid=project_uuid,
                            ),
                        )
                    )
                )
                async for msg in ws:
                    if msg.type in (
                        aiohttp.WSMsgType.CLOSED,
                        aiohttp.WSMsgType.ERROR,
                        aiohttp.WSMsgType.CLOSE,
                    ):
                        logging.debug(
                            f"Websocket Received Closed Message.  Done? {done}"
                        )
                        await ws.close()
                        break
                    data = json.loads(msg.data)
                    if data.get("type") == "end":
                        done = True
                        asyncio.create_task(delayed_close(ws))
                    else:
                        msg_handler(data)
            logging.debug(f"Websocket Disconnected.  Done? {done}")

            connection_tries = 0
            while not done:
                tokens = self.auth.get_tokens()
                try:
                    async with session.ws_connect(
                        f"wss://{self.ws_url}?Authorization={tokens.get('id_token')}",
                        headers=headers,
                        heartbeat=30,
                    ) as ws:
                        asyncio.create_task(
                            ws.send_json(
                                dict(
                                    action="subscribe",
                                    data=dict(
                                        type="logs",
                                        entity=entity,
                                        id=id,
                                        project_uuid=project_uuid,
                                    ),
                                )
                            )
                        )
                        async for msg in ws:
                            if msg.type in (
                                aiohttp.WSMsgType.CLOSED,
                                aiohttp.WSMsgType.ERROR,
                                aiohttp.WSMsgType.CLOSE,
                            ):
                                logging.debug(
                                    f"Websocket Received Closed Message.  Done? {done}"
                                )
                                await ws.close()
                                break
                            data = json.loads(msg.data)
                            if data.get("type") == "end":
                                done = True
                                asyncio.create_task(delayed_close(ws))
                            else:
                                msg_handler(data)
                    connection_tries = 0
                    logging.debug(f"Websocket Disconnected.  Done? {done}")
                except Exception as e:
                    connection_tries += 1
                    logging.debug(
                        f"Connection error: {traceback.format_exc()}"
                    )
                    if connection_tries == 5:
                        raise ApiError(
                            500,
                            {
                                "message": f"Connection error: {traceback.format_exc()}"
                            },
                        )

    def set_active_project(self, project_uuid):
        CONFIG_DIR = os.path.expanduser(
            os.environ.get("PROXIML_CONFIG_DIR") or "~/.proximl"
        )
        with open(f"{CONFIG_DIR}/config.json", "w") as file:
            json.dump(dict(project=project_uuid), file)
