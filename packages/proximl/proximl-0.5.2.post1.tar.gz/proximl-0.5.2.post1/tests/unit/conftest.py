import asyncio
from proximl.projects import Projects
from pytest import fixture, mark
from unittest.mock import Mock, AsyncMock, patch, create_autospec

from proximl.proximl import ProxiML
from proximl.auth import Auth
from proximl.datasets import Dataset, Datasets
from proximl.checkpoints import Checkpoint, Checkpoints
from proximl.models import Model, Models
from proximl.gpu_types import GpuType, GpuTypes
from proximl.environments import Environment, Environments
from proximl.jobs import Job, Jobs
from proximl.connections import Connections
from proximl.projects import (
    Projects,
    Project,
    ProjectDatastore,
    ProjectReservation,
)
from proximl.cloudbender import Cloudbender
from proximl.cloudbender.providers import Provider, Providers
from proximl.cloudbender.regions import Region, Regions
from proximl.cloudbender.nodes import Node, Nodes
from proximl.cloudbender.devices import Device, Devices
from proximl.cloudbender.datastores import Datastore, Datastores
from proximl.cloudbender.reservations import Reservation, Reservations
from proximl.cloudbender.device_configs import DeviceConfig, DeviceConfigs


pytestmark = mark.unit


@fixture(scope="session")
def mock_my_datasets():
    proximl = Mock()
    yield [
        Dataset(
            proximl,
            dataset_uuid="1",
            project_uuid="proj-id-1",
            name="first one",
            status="ready",
            size=100000000,
            createdAt="2020-12-31T23:59:59.000Z",
        ),
        Dataset(
            proximl,
            dataset_uuid="2",
            project_uuid="proj-id-1",
            name="second one",
            status="ready",
            size=100000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
        Dataset(
            proximl,
            dataset_uuid="3",
            project_uuid="proj-id-1",
            name="first one",
            status="ready",
            size=100000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
        Dataset(
            proximl,
            dataset_uuid="4",
            project_uuid="proj-id-1",
            name="other one",
            status="ready",
            size=100000000,
            createdAt="2020-12-31T23:59:59.000Z",
        ),
        Dataset(
            proximl,
            dataset_uuid="5",
            project_uuid="proj-id-1",
            name="not ready",
            status="new",
            size=100000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
        Dataset(
            proximl,
            dataset_uuid="6",
            project_uuid="proj-id-1",
            name="failed",
            status="failed",
            size=100000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
    ]


@fixture(scope="session")
def mock_public_datasets():
    proximl = Mock()
    yield [
        Dataset(
            proximl,
            dataset_uuid="11",
            name="first one",
            status="ready",
        ),
        Dataset(
            proximl,
            dataset_uuid="12",
            name="second one",
            status="ready",
        ),
        Dataset(
            proximl,
            dataset_uuid="15",
            name="not ready",
            status="new",
        ),
        Dataset(
            proximl,
            dataset_uuid="16",
            name="failed",
            status="failed",
        ),
    ]


@fixture(scope="session")
def mock_my_checkpoints():
    proximl = Mock()
    yield [
        Checkpoint(
            proximl,
            checkpoint_uuid="1",
            project_uuid="proj-id-1",
            name="first one",
            status="ready",
            size=100000000,
            createdAt="2020-12-31T23:59:59.000Z",
        ),
        Checkpoint(
            proximl,
            checkpoint_uuid="2",
            project_uuid="proj-id-1",
            name="second one",
            status="ready",
            size=100000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
        Checkpoint(
            proximl,
            checkpoint_uuid="3",
            project_uuid="proj-id-1",
            name="first one",
            status="ready",
            size=100000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
        Checkpoint(
            proximl,
            checkpoint_uuid="4",
            project_uuid="proj-id-1",
            name="other one",
            status="ready",
            size=100000000,
            createdAt="2020-12-31T23:59:59.000Z",
        ),
        Checkpoint(
            proximl,
            checkpoint_uuid="5",
            project_uuid="proj-id-1",
            name="not ready",
            status="new",
            size=100000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
        Checkpoint(
            proximl,
            checkpoint_uuid="6",
            project_uuid="proj-id-1",
            name="failed",
            status="failed",
            size=100000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
    ]


@fixture(scope="session")
def mock_public_checkpoints():
    proximl = Mock()
    yield [
        Checkpoint(
            proximl,
            checkpoint_uuid="11",
            name="first one",
            status="ready",
        ),
        Checkpoint(
            proximl,
            checkpoint_uuid="12",
            name="second one",
            status="ready",
        ),
        Checkpoint(
            proximl,
            checkpoint_uuid="15",
            name="not ready",
            status="new",
        ),
        Checkpoint(
            proximl,
            checkpoint_uuid="16",
            name="failed",
            status="failed",
        ),
    ]


@fixture(scope="session")
def mock_models():
    proximl = Mock()
    yield [
        Model(
            proximl,
            model_uuid="1",
            project_uuid="proj-id-1",
            name="first one",
            status="ready",
            size=10000000,
            createdAt="2020-12-31T23:59:59.000Z",
        ),
        Model(
            proximl,
            model_uuid="2",
            project_uuid="proj-id-1",
            name="second one",
            status="ready",
            size=10000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
        Model(
            proximl,
            model_uuid="5",
            project_uuid="proj-id-1",
            name="not ready",
            status="new",
            size=10000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
        Model(
            proximl,
            model_uuid="6",
            project_uuid="proj-id-1",
            name="failed",
            status="failed",
            size=10000000,
            createdAt="2021-01-01T00:00:01.000Z",
        ),
    ]


@fixture(scope="session")
def mock_gpu_types():
    proximl = Mock()
    yield [
        GpuType(
            proximl,
            **{
                "name": "A100",
                "price": {"min": 2.78, "max": 4.9},
                "id": "a100-id",
                "abbrv": "a100",
            },
        ),
        GpuType(
            proximl,
            **{
                "price": {"min": 1, "max": 3.94},
                "name": "V100",
                "id": "v100-id",
                "abbrv": "v100",
            },
        ),
        GpuType(
            proximl,
            **{
                "price": {"min": 0.35, "max": 0.35},
                "name": "RTX 2080 Ti",
                "id": "2080ti-id",
                "abbrv": "rtx2080ti",
            },
        ),
        GpuType(
            proximl,
            **{
                "price": {"min": 0.1, "max": 0.1},
                "name": "GTX 1060",
                "id": "1060-id",
                "abbrv": "gtx1060",
            },
        ),
    ]


@fixture(scope="function")
def mock_environments():
    proximl = Mock()
    yield [
        Environment(
            proximl,
            **{
                "id": "DEEPLEARNING_PY39",
                "framework": "Deep Learning",
                "py_version": "3.9",
                "cuda_version": "11.7",
                "name": "Deep Learning - Python 3.9",
            },
        ),
        Environment(
            proximl,
            **{
                "id": "DEEPLEARNING_PY310",
                "framework": "Deep Learning",
                "py_version": "3.10",
                "cuda_version": "12.1",
                "name": "Deep Learning - Python 3.10",
            },
        ),
        Environment(
            proximl,
            **{
                "id": "PYTORCH_PY38_17",
                "framework": "PyTorch",
                "py_version": "3.8",
                "version": "1.7",
                "cuda_version": "11.1",
                "name": "PyTorch 1.7 - Python 3.8",
            },
        ),
        Environment(
            proximl,
            **{
                "id": "PYTORCH_PY37_17",
                "framework": "PyTorch",
                "py_version": "3.7",
                "version": "1.7",
                "cuda_version": "10.2",
                "name": "PyTorch 1.7 - Python 3.7",
            },
        ),
        Environment(
            proximl,
            **{
                "id": "PYTORCH_PY37_16",
                "framework": "PyTorch",
                "py_version": "3.7",
                "version": "1.6",
                "cuda_version": "10.2",
                "name": "PyTorch 1.6 - Python 3.7",
            },
        ),
        Environment(
            proximl,
            **{
                "id": "PYTORCH_PY37_15",
                "framework": "PyTorch",
                "py_version": "3.7",
                "version": "1.5",
                "cuda_version": "10.1",
                "name": "PyTorch 1.5 - Python 3.7",
            },
        ),
        Environment(
            proximl,
            **{
                "id": "TENSORFLOW_PY38_24",
                "framework": "Tensorflow",
                "py_version": "3.8",
                "version": "2.4",
                "cuda_version": "11.1",
                "name": "Tensorflow 2.4 - Python 3.8",
            },
        ),
        Environment(
            proximl,
            **{
                "id": "TENSORFLOW_PY37_114",
                "framework": "Tensorflow",
                "py_version": "3.7",
                "version": "1.14",
                "cuda_version": "10.1",
                "name": "Tensorflow 1.14 - Python 3.7",
            },
        ),
    ]


@fixture(scope="session")
def mock_jobs():
    proximl = Mock()
    yield [
        Job(
            proximl,
            **{
                "project_uuid": "proj-id-1",
                "job_uuid": "job-id-1",
                "name": "test notebook",
                "start": "2021-02-11T15:46:22.455Z",
                "type": "notebook",
                "status": "new",
                "credits_per_hour": 0.1,
                "credits": 0.1007,
                "workers": [
                    {
                        "rig_uuid": "rig-id-1",
                        "job_worker_uuid": "worker-id-1",
                        "command": "jupyter lab",
                        "status": "new",
                    }
                ],
                "worker_status": "new",
                "resources": {
                    "gpu_count": 1,
                    "gpu_type_id": "1060-id",
                    "disk_size": 10,
                },
                "model": {
                    "size": 7176192,
                    "source_type": "git",
                    "source_uri": "git@github.com:proxiML/test-private.git",
                    "status": "new",
                },
                "data": {
                    "datasets": [
                        {
                            "dataset_uuid": "data-id-1",
                            "name": "first one",
                            "type": "public",
                            "size": 184549376,
                        },
                        {
                            "dataset_uuid": "data-id-2",
                            "name": "second one",
                            "type": "public",
                            "size": 5068061409,
                        },
                    ],
                    "status": "ready",
                },
                "environment": {
                    "type": "DEEPLEARNING_PY310",
                    "image_size": 44966989795,
                    "env": [
                        {"value": "env1val", "key": "env1"},
                        {"value": "env2val", "key": "env2"},
                    ],
                    "worker_key_types": ["aws", "gcp"],
                    "status": "new",
                },
                "vpn": {
                    "status": "new",
                    "cidr": "10.106.171.0/24",
                    "client": {
                        "port": "36017",
                        "id": "cus-id-1",
                        "address": "10.106.171.253",
                    },
                    "net_prefix_type_id": 1,
                },
                "nb_token": "token",
            },
        ),
        Job(
            proximl,
            **{
                "project_uuid": "proj-id-1",
                "job_uuid": "job-id-2",
                "name": "test training",
                "start": "2021-02-11T15:48:39.476Z",
                "stop": "2021-02-11T15:50:16.554Z",
                "type": "training",
                "status": "finished",
                "credits_per_hour": 0.3,
                "credits": 0.0054,
                "workers": [
                    {
                        "rig_uuid": "rig-id-1",
                        "job_worker_uuid": "worker-id-11",
                        "command": "PYTHONPATH=$PYTHONPATH:$ML_MODEL_PATH python -m official.vision.image_classification.resnet_cifar_main --num_gpus=1 --data_dir=$ML_DATA_PATH --model_dir=$ML_OUTPUT_PATH --enable_checkpoint_and_export=True --train_epochs=1 --batch_size=1024",
                        "status": "stopped",
                    },
                    {
                        "rig_uuid": "rig-id-2",
                        "job_worker_uuid": "worker-id-12",
                        "command": "PYTHONPATH=$PYTHONPATH:$ML_MODEL_PATH python -m official.vision.image_classification.resnet_cifar_main --num_gpus=1 --data_dir=$ML_DATA_PATH --model_dir=$ML_OUTPUT_PATH --enable_checkpoint_and_export=True --train_epochs=1 --batch_size=1024",
                        "status": "stopped",
                    },
                    {
                        "rig_uuid": "rig-id-2",
                        "job_worker_uuid": "worker-id-13",
                        "command": "PYTHONPATH=$PYTHONPATH:$ML_MODEL_PATH python -m official.vision.image_classification.resnet_cifar_main --num_gpus=1 --data_dir=$ML_DATA_PATH --model_dir=$ML_OUTPUT_PATH --enable_checkpoint_and_export=True --train_epochs=1 --batch_size=1024",
                        "status": "stopped",
                    },
                ],
                "worker_status": "stopped",
                "resources": {
                    "gpu_count": 1,
                    "gpu_type_id": "1060-id",
                    "disk_size": 10,
                },
                "model": {
                    "size": 7086080,
                    "source_type": "git",
                    "source_uri": "git@github.com:proxiML/test-private.git",
                    "status": "ready",
                },
                "data": {
                    "datasets": [
                        {
                            "dataset_uuid": "data-id-1",
                            "name": "first one",
                            "type": "public",
                            "size": 184549376,
                        }
                    ],
                    "status": "ready",
                    "output_type": "aws",
                    "output_uri": "s3://proximl-examples/output/resnet_cifar10",
                },
                "environment": {
                    "type": "DEEPLEARNING_PY37",
                    "image_size": 39656398629,
                    "env": [],
                    "worker_key_types": [],
                    "status": "ready",
                },
                "vpn": {
                    "status": "stopped",
                    "cidr": "10.222.241.0/24",
                    "client": {
                        "port": "36978",
                        "id": "cus-id-1",
                        "address": "10.222.241.253",
                    },
                    "net_prefix_type_id": 1,
                },
            },
        ),
    ]


@fixture(scope="session")
def mock_projects():
    proximl = Mock()
    yield [
        Project(
            proximl,
            **{
                "id": "proj-id-1",
                "name": "Personal",
                "owner": True,
                "owner_name": "Me",
                "created_name": "Me",
                "job_all": True,
                "dataset_all": True,
                "model_all": True,
                "createdAt": "2020-12-31T23:59:59.000Z",
            },
        ),
        Project(
            proximl,
            **{
                "id": "project-id-2",
                "name": "My Other Project",
                "owner": True,
                "owner_name": "Me",
                "created_name": "Me",
                "job_all": True,
                "dataset_all": True,
                "model_all": True,
                "createdAt": "2020-12-31T23:59:59.000Z",
            },
        ),
        Project(
            proximl,
            **{
                "id": "project-id-3",
                "name": "Someone Elses Project",
                "owner": False,
                "owner_name": "Someone Else",
                "created_name": "Someone Else",
                "job_all": False,
                "dataset_all": False,
                "model_all": False,
                "createdAt": "2020-12-31T23:59:59.000Z",
            },
        ),
    ]


@fixture(scope="session")
def mock_providers():
    proximl = Mock()
    yield [
        Provider(
            proximl,
            **{
                "customer_uuid": "cust-id-1",
                "provider_uuid": "prov-id-1",
                "type": "physical",
                "credits": 10.0,
                "payment_mode": "stripe",
            },
        ),
        Provider(
            proximl,
            **{
                "customer_uuid": "cust-id-1",
                "provider_uuid": "prov-id-2",
                "type": "gcp",
                "credits": 0.0,
                "payment_mode": "credits",
                "credentials": {
                    "project": "proj-1",
                    "id": "gcp@serviceaccount.com",
                },
            },
        ),
    ]


@fixture(scope="session")
def mock_regions():
    proximl = Mock()
    yield [
        Region(
            proximl,
            **{
                "provider_uuid": "prov-id-1",
                "region_uuid": "reg-id-1",
                "provider_type": "physical",
                "name": "Physical Region 1",
                "status": "healthy",
            },
        ),
        Region(
            proximl,
            **{
                "provider_uuid": "prov-id-2",
                "region_uuid": "reg-id-2",
                "provider_type": "gcp",
                "name": "Cloud Region 1",
                "status": "healthy",
            },
        ),
    ]


@fixture(scope="session")
def mock_nodes():
    proximl = Mock()
    yield [
        Node(
            proximl,
            **{
                "provider_uuid": "prov-id-1",
                "region_uuid": "reg-id-1",
                "rig_uuid": "rig-id-1",
                "type": "permanent",
                "service": "compute",
                "friendly_name": "hq-a100-01",
                "hostname": "hq-a100-01",
                "status": "active",
                "online": True,
                "maintenance_mode": False,
            },
        ),
        Node(
            proximl,
            **{
                "provider_uuid": "prov-id-2",
                "region_uuid": "reg-id-2",
                "rig_uuid": "rig-id-2",
                "type": "ephemeral",
                "service": "compute",
                "friendly_name": "gcp-a100-01",
                "hostname": "gcp-a100-01",
                "status": "active",
                "online": True,
                "maintenance_mode": False,
            },
        ),
        Node(
            proximl,
            **{
                "provider_uuid": "prov-id-2",
                "region_uuid": "reg-id-2",
                "rig_uuid": "rig-id-3",
                "type": "permanent",
                "service": "storage",
                "friendly_name": "gcp-storage-01",
                "hostname": "gcp-storage-01",
                "status": "active",
                "online": True,
                "maintenance_mode": False,
            },
        ),
    ]


@fixture(scope="session")
def mock_devices():
    proximl = Mock()
    yield [
        Device(
            proximl,
            **{
                "provider_uuid": "prov-id-1",
                "region_uuid": "reg-id-1",
                "device_id": "dev-id-1",
                "type": "device",
                "service": "compute",
                "friendly_name": "hq-orin-01",
                "hostname": "hq-orin-01",
                "status": "active",
                "online": True,
                "maintenance_mode": False,
                "job_status": "running",
                "job_last_deployed": "2023-06-02T21:22:40.084Z",
                "job_config_id": "job-id-1",
                "job_config_revision": "1685740490096",
                "device_config_id": "conf-id-1",
            },
        ),
        Device(
            proximl,
            **{
                "provider_uuid": "prov-id-1",
                "region_uuid": "reg-id-1",
                "device_id": "dev-id-2",
                "type": "device",
                "service": "compute",
                "friendly_name": "hq-orin-02",
                "hostname": "hq-orin-02",
                "status": "active",
                "online": True,
                "maintenance_mode": False,
                "job_status": "running",
                "job_last_deployed": "2023-06-02T21:22:40.084Z",
                "job_config_id": "job-id-2",
                "job_config_revision": "1685740490096",
                "device_config_id": "conf-id-1",
            },
        ),
    ]


@fixture(scope="session")
def mock_datastores():
    proximl = Mock()
    yield [
        Datastore(
            proximl,
            **{
                "provider_uuid": "prov-id-1",
                "region_uuid": "reg-id-1",
                "store_id": "store-id-1",
                "type": "nfs",
                "name": "On-prem NFS",
                "uri": "192.168.0.50",
                "root": "/exports",
            },
        ),
        Datastore(
            proximl,
            **{
                "provider_uuid": "prov-id-2",
                "region_uuid": "reg-id-2",
                "store_id": "store-id-2",
                "type": "smb",
                "name": "GCP Samba",
                "uri": "192.168.1.50",
                "root": "/DATA",
            },
        ),
    ]


@fixture(scope="session")
def mock_project_datastores():
    proximl = Mock()
    yield [
        ProjectDatastore(
            proximl,
            **{
                "project_uuid": "proj-id-1",
                "region_uuid": "reg-id-1",
                "id": "store-id-1",
                "type": "nfs",
                "name": "On-prem NFS",
            },
        ),
        ProjectDatastore(
            proximl,
            **{
                "project_uuid": "proj-id-1",
                "region_uuid": "reg-id-2",
                "id": "store-id-2",
                "type": "smb",
                "name": "GCP Samba",
            },
        ),
    ]


@fixture(scope="session")
def mock_reservations():
    proximl = Mock()
    yield [
        Reservation(
            proximl,
            **{
                "provider_uuid": "prov-id-1",
                "region_uuid": "reg-id-1",
                "reservation_id": "res-id-1",
                "type": "port",
                "name": "On-Prem Service A",
                "resource": "8001",
                "hostname": "service-a.local",
            },
        ),
        Reservation(
            proximl,
            **{
                "provider_uuid": "prov-id-2",
                "region_uuid": "reg-id-2",
                "reservation_id": "res-id-2",
                "type": "port",
                "name": "Cloud Service B",
                "resource": "8001",
                "hostname": "service-b.local",
            },
        ),
    ]


@fixture(scope="session")
def mock_project_reservations():
    proximl = Mock()
    yield [
        ProjectReservation(
            proximl,
            **{
                "project_uuid": "proj-id-1",
                "region_uuid": "reg-id-1",
                "id": "res-id-1",
                "type": "port",
                "name": "On-Prem Service A",
                "resource": "8001",
                "hostname": "service-a.local",
            },
        ),
        ProjectReservation(
            proximl,
            **{
                "project_uuid": "proj-id-1",
                "region_uuid": "reg-id-2",
                "id": "res-id-2",
                "type": "port",
                "name": "Cloud Service B",
                "resource": "8001",
                "hostname": "service-b.local",
            },
        ),
    ]


@fixture(scope="session")
def mock_device_configs():
    proximl = Mock()
    yield [
        DeviceConfig(
            proximl,
            **{
                "provider_uuid": "prov-id-1",
                "region_uuid": "reg-id-1",
                "config_id": "conf-id-1",
                "name": "IoT 1",
            },
        ),
        DeviceConfig(
            proximl,
            **{
                "provider_uuid": "prov-id-1",
                "region_uuid": "reg-id-1",
                "config_id": "conf-id-2",
                "name": "IoT 2",
            },
        ),
    ]


@fixture(scope="function")
def mock_proximl(
    mock_my_datasets,
    mock_public_datasets,
    mock_models,
    mock_gpu_types,
    mock_environments,
    mock_jobs,
    mock_projects,
    mock_providers,
    mock_regions,
    mock_nodes,
    mock_devices,
    mock_datastores,
    mock_reservations,
    mock_device_configs,
):
    proximl = create_autospec(ProxiML)
    proximl.active_project = "proj-id-1"
    proximl.project = "proj-id-1"
    proximl.datasets = create_autospec(Datasets)
    proximl.checkpoints = create_autospec(Checkpoints)
    proximl.models = create_autospec(Models)
    proximl.gpu_types = create_autospec(GpuTypes)
    proximl.environments = create_autospec(Environments)
    proximl.jobs = create_autospec(Jobs)
    proximl.connections = create_autospec(Connections)
    proximl.projects = create_autospec(Projects)
    proximl.datasets.list = AsyncMock(return_value=mock_my_datasets)
    proximl.datasets.list_public = AsyncMock(return_value=mock_public_datasets)
    proximl.checkpoints.list = AsyncMock(return_value=mock_my_checkpoints)
    proximl.checkpoints.list_public = AsyncMock(
        return_value=mock_public_checkpoints
    )
    proximl.models.list = AsyncMock(return_value=mock_models)
    proximl.gpu_types.list = AsyncMock(return_value=mock_gpu_types)
    proximl.environments.list = AsyncMock(return_value=mock_environments)
    proximl.jobs.list = AsyncMock(return_value=mock_jobs)
    proximl.projects.list = AsyncMock(return_value=mock_projects)

    proximl.cloudbender = create_autospec(Cloudbender)

    proximl.cloudbender.providers = create_autospec(Providers)
    proximl.cloudbender.providers.list = AsyncMock(return_value=mock_providers)
    proximl.cloudbender.regions = create_autospec(Regions)
    proximl.cloudbender.regions.list = AsyncMock(return_value=mock_regions)
    proximl.cloudbender.nodes = create_autospec(Nodes)
    proximl.cloudbender.nodes.list = AsyncMock(return_value=mock_nodes)
    proximl.cloudbender.devices = create_autospec(Nodes)
    proximl.cloudbender.devices.list = AsyncMock(return_value=mock_devices)
    proximl.cloudbender.datastores = create_autospec(Datastores)
    proximl.cloudbender.datastores.list = AsyncMock(
        return_value=mock_datastores
    )
    proximl.cloudbender.reservations = create_autospec(Reservations)
    proximl.cloudbender.reservations.list = AsyncMock(
        return_value=mock_reservations
    )
    proximl.cloudbender.device_configs = create_autospec(DeviceConfigs)
    proximl.cloudbender.device_configs.list = AsyncMock(
        return_value=mock_device_configs
    )
    yield proximl
