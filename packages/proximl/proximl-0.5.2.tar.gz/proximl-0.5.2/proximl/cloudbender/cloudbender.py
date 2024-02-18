from .providers import Providers
from .regions import Regions
from .nodes import Nodes
from .devices import Devices
from .datastores import Datastores
from .reservations import Reservations
from .device_configs import DeviceConfigs


class Cloudbender(object):
    def __init__(self, proximl):
        self.proximl = proximl
        self.providers = Providers(proximl)
        self.regions = Regions(proximl)
        self.nodes = Nodes(proximl)
        self.devices = Devices(proximl)
        self.datastores = Datastores(proximl)
        self.reservations = Reservations(proximl)
        self.device_configs = DeviceConfigs(proximl)
