<div align="center">
  <a href="https://www.proximl.ai/"><img src="https://www.proximl.ai/static/img/proxiML-logo-purple.png"></a><br>
</div>

# proxiML Python SDK and Command Line Tools

Provides programmatic access to [proxiML platform](https://app.proximl.ai).

## Installation

Python 3.8 or above is required.

```
pip install proximl
```

## Authentication

### Prerequisites

You must have a valid [proxiML account](https://app.proximl.ai). On the [account settings page](https://app.proximl.ai/account/settings) click the `Create` button in the `API Keys` section. This will automatically download a `credentials.json` file. This file can only be generated once per API key. Treat this file as a password, as anyone with access to your API key will have the ability to create and control resources in your proxiML account. You can deactivate any API key by clicking the `Remove` button.

> Creating resources on the proxiML platform requires a non-zero credit balance. To purchase credits or sign-up for automatic credit top-ups, visit the [billing page](https://app.proximl.ai/account/billing).

### Methods

#### Credentials File

The easiest way to authenticate is to place the credentials file downloaded into the `.proximl` folder of your home directory and ensure only you have access to it. From the directory that the `credentials.json` file was downloaded, run the following command:

```
mkdir -p ~/.proximl
mv credentials.json ~/.proximl/credentials.json
chmod 600 ~/.proximl/credentials.json
```

#### Environment Variables

You can also use environment variables `PROXIML_USER` and `PROXIML_KEY` and set them to their respective values from the `credentials.json` file.

```
export PROXIML_USER=<'user' field from credentials.json>
export PROXIML_KEY=<'key' field from credentials.json>
python create_job.py
```

Environment variables will override any credentials stored in `~/.proximl/credentials.json`

#### Runtime Variables

API credentials can also be passed directly to the ProxiML object constructor at runtime.

```
import proximl
proximl = proximl.ProxiML(user="user field from credentials.json",key="key field from credentials.json>")
await proximl.jobs.create(...)
```

Passing credentials to the ProxiML constructor will override all other methods for setting credentials.

## Configuration

By default, all operations using the proxiML SDK/CLI will use the Personal [project](https://docs.proximl.ai/reference/projects) for proxiML account the API keys were generated from. To change the active project, run the configure command:

```
proximl configure
```

This command will output the currently configured active project (`UNSET` defaults to `Personal`) and allows you to specify any project you have access to as the new active project.

```
Current Active Project: Personal
Select Active Project: (My Other Project, Personal, Project Shared With Me) [Personal]:
```

Once you select a project, it will store the results of your selection in the `config.json` file in the `PROXIML_CONFIG_DIR` folder (`~/.proximl` by default). Once the active project is set, all subsequent operations will use the selected project.

This setting can also be overridden at runtime using the environment variable `PROXIML_PROJECT`:

```
PROXIML_PROJECT=<PROJECT ID> python create_job.py
```

or by instantiating the proximl client with the `project` keyword argument:

```
import proximl
proximl = proximl.ProxiML(project="PROJECT ID")
await proximl.jobs.create(...)
```

> You must specify the project ID (not name) when using the runtime options. The project ID can be found by running `proximl project list`.

## Usage

### Python SDK

The proxiML SDK utilizes the [asyncio library](https://docs.python.org/3/library/asyncio.html) to ease the concurrent execution of long running tasks. An example of how to create a dataset from an S3 bucket and immediately run a training job on that dataset is the following:

```
from proximl.proximl import ProxiML
import asyncio


proximl_client = ProxiML()

# Create the dataset
dataset = asyncio.run(
    proximl_client.datasets.create(
        name="Example Dataset",
        source_type="aws",
        source_uri="s3://proximl-examples/data/cifar10",
    )
)

print(dataset)

# Watch the log output, attach will return when data transfer is complete
asyncio.run(dataset.attach())

# Create the job
job = asyncio.run(
    proximl_client.jobs.create(
        name="Example Training Job",
        type="training",
        gpu_type="GTX 1060",
        gpu_count=1,
        disk_size=10,
        workers=[
            "PYTHONPATH=$PYTHONPATH:$PROXIML_MODEL_PATH python -m official.vision.image_classification.resnet_cifar_main --num_gpus=1 --data_dir=$PROXIML_DATA_PATH --model_dir=$PROXIML_OUTPUT_PATH --enable_checkpoint_and_export=True --train_epochs=10 --batch_size=1024",
        ],
        data=dict(
            datasets=[dict(id=dataset.id, type="existing")],
            output_uri="s3://proximl-examples/output/resnet_cifar10",
            output_type="aws",
        ),
        model=dict(git_uri="git@github.com:proxiML/test-private.git"),
    )
)
print(job)

# Watch the log output, attach will return when the training job stops
asyncio.run(job.attach())

# Cleanup job and dataset
asyncio.run(job.remove())
asyncio.run(dataset.remove())
```

See more examples in the [examples folder](examples)

### Command Line Interface

The command line interface is rooted in the `proximl` command. To see the available options, run:

```
proximl --help
```

To list all jobs:

```
proximl job list
```

To list all datasets:

```
proximl dataset list
```

To connect to a job that requires the [connection capability](https://docs.proximl.ai/reference/connection-capability):

```
proximl job connect <job ID or name>
```

To watch the realtime job logs:

```
proximl job attach <job ID or name>
```

To create and open a notebook job:

```
proximl job create notebook "My Notebook Job"
```

To create a multi-GPU notebook job on a specific GPU type with larger scratch directory space:

```
proximl job create notebook --gpu-type "RTX 3090" --gpu-count 4 --disk-size 50 "My Notebook Job"
```

To run the model training code in the `train.py` file in your local `~/model-code` directory on the training data in your local `~/data` directory:

```
proximl job create training --model-dir ~/model-code --data-dir ~/data "My Training Job" "python train.py"
```

Stop a job by job ID:

```
proximl job stop fe52527c-1f4b-468f-b57d-86db864cc089
```

Stop a job by name:

```
proximl job stop "My Notebook Job"
```

Restart a notebook job:

```
proximl job start "My Notebook Job"
```

Remove a job by job ID:

```
proximl job remove fe52527c-1f4b-468f-b57d-86db864cc089
```
