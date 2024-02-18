import click
import logging
from proximl.cli import cli, pass_config, search_by_id_name


def pretty_size(num):
    if not num:
        num = 0.0
    s = ("  B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    n = 0
    while num > 1023:
        num = num / 1024
        n += 1
    return f"{num:.2f} {s[n]}"


@cli.group()
@pass_config
def model(config):
    """proxiML model commands."""
    pass


@model.command()
@click.argument("model", type=click.STRING)
@pass_config
def attach(config, model):
    """
    Attach to model and show creation logs.

    MODEL may be specified by name or ID, but ID is preferred.
    """
    models = config.proximl.run(config.proximl.client.models.list())

    found = search_by_id_name(model, models)
    if None is found:
        raise click.UsageError("Cannot find specified model.")

    try:
        config.proximl.run(found.attach())
        return config.proximl.run(found.disconnect())
    except:
        try:
            config.proximl.run(found.disconnect())
        except:
            pass
        raise


@model.command()
@click.option(
    "--attach/--no-attach",
    default=True,
    show_default=True,
    help="Auto attach to model and show creation logs.",
)
@click.argument("model", type=click.STRING)
@pass_config
def connect(config, model, attach):
    """
    Connect local source to model and begin upload.

    MODEL may be specified by name or ID, but ID is preferred.
    """
    models = config.proximl.run(config.proximl.client.models.list())

    found = search_by_id_name(model, models)
    logging.debug(found)
    if None is found:
        raise click.UsageError("Cannot find specified model.")

    try:
        if attach:
            config.proximl.run(found.connect(), found.attach())
            return config.proximl.run(found.disconnect())
        else:
            return config.proximl.run(found.connect())
    except:
        try:
            config.proximl.run(found.disconnect())
        except:
            pass
        raise


@model.command()
@click.option(
    "--attach/--no-attach",
    default=True,
    show_default=True,
    help="Auto attach to model and show creation logs.",
)
@click.option(
    "--connect/--no-connect",
    default=True,
    show_default=True,
    help="Auto connect source and start model creation.",
)
@click.option(
    "--source",
    "-s",
    type=click.Choice(["local"], case_sensitive=False),
    default="local",
    show_default=True,
    help="Dataset source type.",
)
@click.argument("name", type=click.STRING)
@click.argument(
    "path", type=click.Path(exists=True, file_okay=False, resolve_path=True)
)
@pass_config
def create(config, attach, connect, source, name, path):
    """
    Create a model.

    A model is created with the specified NAME using a local source at the PATH
    specified. PATH should be a local directory containing the source data for
    a local source or a URI for all other source types.
    """

    if source == "local":
        model = config.proximl.run(
            config.proximl.client.models.create(
                name=name, source_type="local", source_uri=path
            )
        )

        try:
            if connect and attach:
                config.proximl.run(model.attach(), model.connect())
                return config.proximl.run(model.disconnect())
            elif connect:
                return config.proximl.run(model.connect())
            else:
                raise click.UsageError(
                    "Abort!\n"
                    "No logs to show for local sourced model without connect."
                )
        except:
            try:
                config.proximl.run(model.disconnect())
            except:
                pass
            raise


@model.command()
@click.argument("model", type=click.STRING)
@pass_config
def disconnect(config, model):
    """
    Disconnect and clean-up model upload.

    MODEL may be specified by name or ID, but ID is preferred.
    """
    models = config.proximl.run(config.proximl.client.models.list())

    found = search_by_id_name(model, models)
    if None is found:
        raise click.UsageError("Cannot find specified model.")

    return config.proximl.run(found.disconnect())


@model.command()
@pass_config
def list(config):
    """List models."""
    data = [
        ["ID", "STATUS", "NAME", "SIZE"],
        ["-" * 80, "-" * 80, "-" * 80, "-" * 80],
    ]

    models = config.proximl.run(config.proximl.client.models.list())

    for model in models:
        data.append(
            [
                model.id,
                model.status,
                model.name,
                pretty_size(model.size),
            ]
        )
    for row in data:
        click.echo(
            "{: >38.36} {: >13.11} {: >40.38} {: >14.12}" "".format(*row),
            file=config.stdout,
        )


@model.command()
@click.option(
    "--force/--no-force",
    default=False,
    show_default=True,
    help="Force removal.",
)
@click.argument("model", type=click.STRING)
@pass_config
def remove(config, model, force):
    """
    Remove a model.

    MODEL may be specified by name or ID, but ID is preferred.
    """
    models = config.proximl.run(config.proximl.client.models.list())

    found = search_by_id_name(model, models)
    if None is found:
        if force:
            config.proximl.run(found.client.models.remove(model))
        else:
            raise click.UsageError("Cannot find specified model.")

    return config.proximl.run(found.remove(force=force))


@model.command()
@click.argument("model", type=click.STRING)
@click.argument("name", type=click.STRING)
@pass_config
def rename(config, model, name):
    """
    Renames a model.

    MODEL may be specified by name or ID, but ID is preferred.
    """
    try:
        model = config.proximl.run(config.proximl.client.models.get(model))
        if model is None:
            raise click.UsageError("Cannot find specified model.")
    except:
        raise click.UsageError("Cannot find specified model.")

    return config.proximl.run(model.rename(name=name))
