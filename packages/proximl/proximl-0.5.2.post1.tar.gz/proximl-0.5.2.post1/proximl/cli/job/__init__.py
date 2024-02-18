import click
from webbrowser import open as browse
from proximl.cli import cli, pass_config, search_by_id_name


@cli.group()
@pass_config
def job(config):
    """proxiML job commands."""
    pass


@job.command()
@click.argument("job", type=click.STRING)
@pass_config
def attach(config, job):
    """
    Attach to job and show logs.

    JOB may be specified by name or ID, but ID is preferred.
    """
    jobs = config.proximl.run(config.proximl.client.jobs.list())

    found = search_by_id_name(job, jobs)
    if None is found:
        raise click.UsageError("Cannot find specified job.")

    try:
        config.proximl.run(found.attach())
        return config.proximl.run(found.disconnect())
    except:
        try:
            config.proximl.run(found.disconnect())
        except:
            pass
        raise


@job.command()
@click.option(
    "--attach/--no-attach",
    default=True,
    show_default=True,
    help="Auto attach to job.",
)
@click.argument("job", type=click.STRING)
@pass_config
def connect(config, job, attach):
    """
    Connect to job.

    JOB may be specified by name or ID, but ID is preferred.
    """
    jobs = config.proximl.run(config.proximl.client.jobs.list())

    found = search_by_id_name(job, jobs)
    if None is found:
        raise click.UsageError("Cannot find specified job.")

    if found.type != "notebook":
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
    else:
        if found.status in [
            "new",
            "waiting for data/model download",
            "waiting for GPUs",
        ]:
            try:
                if attach:
                    config.proximl.run(found.connect(), found.attach())
                    config.proximl.run(found.disconnect())
                    click.echo("Launching...", file=config.stdout)
                    browse(found.notebook_url)
                else:
                    return config.proximl.run(found.connect())
            except:
                try:
                    config.proximl.run(found.disconnect())
                except:
                    pass
                raise
        elif found.status not in [
            "starting",
            "running",
            "reinitializing",
            "copying",
        ]:
            raise click.UsageError("Notebook job not running.")
        else:
            config.proximl.run(found.wait_for("running"))
            click.echo("Launching...", file=config.stdout)
            browse(found.notebook_url)


@job.command()
@click.argument("job", type=click.STRING)
@pass_config
def disconnect(config, job):
    """
    Disconnect and clean-up job.

    JOB may be specified by name or ID, but ID is preferred.
    """
    jobs = config.proximl.run(config.proximl.client.jobs.list())

    found = search_by_id_name(job, jobs)
    if None is found:
        raise click.UsageError("Cannot find specified job.")

    return config.proximl.run(found.disconnect())


@job.command()
@click.option(
    "--wait/--no-wait",
    default=True,
    show_default=True,
    help="Wait until job is stopped before returning.",
)
@click.argument("job", type=click.STRING)
@pass_config
def stop(config, job, wait):
    """
    Stop a running job.

    JOB may be specified by name or ID, but ID is preferred.
    """
    jobs = config.proximl.run(config.proximl.client.jobs.list())

    found = search_by_id_name(job, jobs)
    if None is found:
        raise click.UsageError("Cannot find specified job.")

    if wait:
        config.proximl.run(found.stop())
        click.echo("Waiting for job to stop...", file=config.stdout)
        return config.proximl.run(found.wait_for("stopped"))
    else:
        return config.proximl.run(found.stop())


@job.command()
@click.option(
    "--connect/--no-connect",
    default=True,
    show_default=True,
    help="Auto connect to job.",
)
@click.argument("job", type=click.STRING)
@pass_config
def start(config, job, connect):
    """
    Start a previously stopped job.

    JOB may be specified by name or ID, but ID is preferred.
    """
    jobs = config.proximl.run(config.proximl.client.jobs.list())

    found = search_by_id_name(job, jobs)
    if None is found:
        raise click.UsageError("Cannot find specified job.")

    if connect:
        config.proximl.run(found.start())
        click.echo("Waiting for job to start...", file=config.stdout)
        config.proximl.run(found.wait_for("running"))
        click.echo("Launching...", file=config.stdout)
        browse(found.notebook_url)
    else:
        return config.proximl.run(found.start())


@job.command()
@click.option(
    "--force/--no-force",
    default=False,
    show_default=True,
    help="Force removal.",
)
@click.argument("job", type=click.STRING)
@pass_config
def remove(config, job, force):
    """
    Remove a job.

    JOB may be specified by name or ID, but ID is preferred.
    """
    jobs = config.proximl.run(config.proximl.client.jobs.list())

    found = search_by_id_name(job, jobs)
    if None is found:
        if force:
            config.proximl.run(config.proximl.client.jobs.remove(job))
        else:
            raise click.UsageError("Cannot find specified job.")

    return config.proximl.run(found.remove(force=force))


@job.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Choose output format.",
)
@pass_config
def list(config, format):
    """List proxiML jobs."""
    jobs = config.proximl.run(config.proximl.client.jobs.list())

    if format == "text":
        data = [
            ["ID", "NAME", "STATUS", "TYPE"],
            ["-" * 80, "-" * 80, "-" * 80, "-" * 80],
        ]

        for job in jobs:
            data.append([job.id, job.name, job.status, job.type])
        for row in data:
            click.echo(
                "{: >38.36} {: >40.38} {: >13.11} {: >14.12}" "".format(*row),
                file=config.stdout,
            )
    elif format == "json":
        output = []
        for job in jobs:
            output.append(job.dict)
        click.echo(output, file=config.stdout)


from proximl.cli.job.create import create
