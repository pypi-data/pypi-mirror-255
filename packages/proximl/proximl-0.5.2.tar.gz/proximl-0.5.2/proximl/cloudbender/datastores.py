import json
import logging


class Datastores(object):
    def __init__(self, proximl):
        self.proximl = proximl

    async def get(self, provider_uuid, region_uuid, id, **kwargs):
        resp = await self.proximl._query(
            f"/provider/{provider_uuid}/region/{region_uuid}/datastore/{id}",
            "GET",
            kwargs,
        )
        return Datastore(self.proximl, **resp)

    async def list(self, provider_uuid, region_uuid, **kwargs):
        resp = await self.proximl._query(
            f"/provider/{provider_uuid}/region/{region_uuid}/datastore",
            "GET",
            kwargs,
        )
        datastores = [
            Datastore(self.proximl, **datastore) for datastore in resp
        ]
        return datastores

    async def create(
        self,
        provider_uuid,
        region_uuid,
        name,
        type,
        uri,
        root,
        options=None,
        **kwargs,
    ):
        logging.info(f"Creating Datastore {name}")
        data = dict(
            name=name,
            type=type,
            uri=uri,
            root=root,
            options=options,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        resp = await self.proximl._query(
            f"/provider/{provider_uuid}/region/{region_uuid}/datastore",
            "POST",
            None,
            payload,
        )
        datastore = Datastore(self.proximl, **resp)
        logging.info(f"Created Datastore {name} with id {datastore.id}")
        return datastore

    async def remove(self, provider_uuid, region_uuid, id, **kwargs):
        await self.proximl._query(
            f"/provider/{provider_uuid}/region/{region_uuid}/datastore/{id}",
            "DELETE",
            kwargs,
        )


class Datastore:
    def __init__(self, proximl, **kwargs):
        self.proximl = proximl
        self._datastore = kwargs
        self._id = self._datastore.get("store_id")
        self._provider_uuid = self._datastore.get("provider_uuid")
        self._region_uuid = self._datastore.get("region_uuid")
        self._type = self._datastore.get("type")
        self._name = self._datastore.get("name")
        self._uri = self._datastore.get("uri")
        self._root = self._datastore.get("root")

    @property
    def id(self) -> str:
        return self._id

    @property
    def provider_uuid(self) -> str:
        return self._provider_uuid

    @property
    def region_uuid(self) -> str:
        return self._region_uuid

    @property
    def type(self) -> str:
        return self._type

    @property
    def name(self) -> str:
        return self._name

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def root(self) -> str:
        return self._root

    def __str__(self):
        return json.dumps({k: v for k, v in self._datastore.items()})

    def __repr__(self):
        return f"Datastore( proximl , **{self._datastore.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):
        await self.proximl._query(
            f"/provider/{self._provider_uuid}/region/{self._region_uuid}/datastore/{self._id}",
            "DELETE",
        )

    async def refresh(self):
        resp = await self.proximl._query(
            f"/provider/{self._provider_uuid}/region/{self._region_uuid}/datastore/{self._id}",
            "GET",
        )
        self.__init__(self.proximl, **resp)
        return self
