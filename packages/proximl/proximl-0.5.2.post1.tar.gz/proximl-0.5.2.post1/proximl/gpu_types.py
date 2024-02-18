import json
from proximl.exceptions import ProxiMLException


class GpuTypes(object):
    def __init__(self, proximl):
        self.proximl = proximl

    async def list(self):
        if not self.proximl.project:
            raise ProxiMLException(
                "Active project not configured.  Run 'proximl configure' to select an active project."
            )
        resp = await self.proximl._query(
            f"/project/{self.proximl.project}/gputypes", "GET"
        )
        gpu_types = [GpuType(self.proximl, **gpu_type) for gpu_type in resp]
        return gpu_types

    async def refresh_gpu_types(self):
        await self.proximl._query(
            f"/project/{self.proximl.project}/gputypes", "PATCH"
        )


class GpuType:
    def __init__(self, proximl, **kwargs):
        self.proximl = proximl
        self._gpu_type = kwargs
        self._id = self._gpu_type.get("id", self._gpu_type.get("gpu_type_id"))
        self._name = self._gpu_type.get("name")
        self._abbrv = self._gpu_type.get("abbrv")
        self._credits_per_hour_min = self._gpu_type.get("price").get("min")
        self._credits_per_hour_max = self._gpu_type.get("price").get("max")

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def abbrv(self) -> str:
        return self._abbrv

    @property
    def credits_per_hour_min(self) -> float:
        return self._credits_per_hour_min

    @property
    def credits_per_hour_max(self) -> float:
        return self._credits_per_hour_max

    def __str__(self):
        return json.dumps(
            {
                k: v
                for k, v in self._gpu_type.items()
                if k not in ["createdAt", "updatedAt"]
            }
        )

    def __repr__(self):
        return f"GpuType( proximl , **{self._gpu_type.__repr__()})"
