import tempfile
from pathlib import Path

import typer
from natsort import natsorted

import edge_containers_cli.globals as globals
from edge_containers_cli.autocomplete import (
    all_svc,
    avail_IOCs,
    avail_versions,
    force_plain_completion,
    running_svc,
)
from edge_containers_cli.cmds.k8s_commands import IocK8sCommands
from edge_containers_cli.cmds.local_commands import IocLocalCommands
from edge_containers_cli.git import create_svc_graph
from edge_containers_cli.logging import log
from edge_containers_cli.utils import cleanup_temp, drop_path

cli = typer.Typer(pretty_exceptions_show_locals=False)


@cli.command()
def ps(
    ctx: typer.Context,
    all: bool = typer.Option(
        False, "-a", "--all", help="list stopped IOCs as well as running IOCs"
    ),
    wide: bool = typer.Option(
        False, "--wide", "-w", help="use a wide format with additional fields"
    ),
):
    """List the IOCs running in the current namespace"""
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj).ps(all, wide)
    else:
        IocK8sCommands(ctx.obj).ps(all, wide)


@cli.command()
def env(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "-v", "--verbose", help="show all relevant environment variables"
    ),
):
    """List all relevant environment variables"""
    IocLocalCommands(ctx.obj).environment(verbose == verbose)


@cli.command()
def attach(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC to attach to", autocompletion=running_svc
    ),
):
    """
    Attach to the IOC shell of a live IOC
    """
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj, service_name).attach()
    else:
        IocK8sCommands(ctx.obj, service_name).attach()


@cli.command()
def delete(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC to delete", autocompletion=all_svc
    ),
):
    """
    Remove an IOC helm deployment from the cluster
    """
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj, service_name).delete()
    else:
        IocK8sCommands(ctx.obj, service_name).delete()


@cli.command()
def template(
    ctx: typer.Context,
    svc_instance: Path = typer.Argument(
        ...,
        help="folder of local service definition",
        exists=True,
        file_okay=False,
        resolve_path=True,
        autocompletion=force_plain_completion,
    ),  # noqa: B008
    args: str = typer.Option("", help="Additional args for helm, 'must be quoted'"),
):
    """
    print out the helm template generated from a local service instance
    """
    args = f"{args} --debug"
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        typer.echo("Not applicable to local deployments")
    else:
        IocK8sCommands(ctx.obj).template(svc_instance, args)


@cli.command()
def deploy_local(
    ctx: typer.Context,
    svc_instance: Path = typer.Argument(
        ...,
        help="folder of local service definition",
        exists=True,
        file_okay=False,
        resolve_path=True,
        autocompletion=force_plain_completion,
    ),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation prompt"),
    args: str = typer.Option("", help="Additional args for helm, 'must be quoted'"),
):
    """
    Deploy a local IOC helm chart directly to the cluster with dated beta version
    """
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj).deploy_local(svc_instance, yes, args)
    else:
        IocK8sCommands(ctx.obj).deploy_local(svc_instance, yes, args)


@cli.command()
def deploy(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC to deploy", autocompletion=avail_IOCs
    ),
    version: str = typer.Argument(
        ..., help="Version tag of the IOC to deploy", autocompletion=avail_versions
    ),
    args: str = typer.Option(
        "", help="Additional args for helm or docker, 'must be quoted'"
    ),
):
    """
    Pull an IOC helm chart version from the domain repo and deploy it to the cluster
    """
    service_name = drop_path(service_name)
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj, service_name).deploy(service_name, version, args)
    else:
        IocK8sCommands(ctx.obj, service_name, check=False).deploy(
            service_name, version, args
        )


@cli.command()
def list(
    ctx: typer.Context,
):
    """List all IOCs available in the helm registry"""
    typer.echo(typer.style(f"{'Available IOCs:':35}Latest instance:", bold=True))
    tmp_dir = Path(tempfile.mkdtemp())
    svc_graph = create_svc_graph(ctx.obj.beamline_repo, tmp_dir)
    svc_list = natsorted(svc_graph.keys())
    log.debug(f"svc_graph = {svc_graph}")

    for svc in svc_list:
        if len(svc_graph[svc]) == 0:
            latest_instance = "None found."
        else:
            latest_instance = natsorted(svc_graph[svc])[-1]
        typer.echo(f"{svc:35}{latest_instance}")

    cleanup_temp(tmp_dir)


@cli.command()
def instances(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC to inspect", autocompletion=avail_IOCs
    ),
):
    """List all versions of the IOC available in the helm registry"""
    typer.echo(f"Available instance versions for {service_name}:")
    tmp_dir = Path(tempfile.mkdtemp())
    svc_graph = create_svc_graph(ctx.obj.beamline_repo, tmp_dir)
    try:
        svc_list = svc_graph[service_name]
    except KeyError:
        svc_list = []

    sorted_list = natsorted(svc_list)[::-1]
    typer.echo("  ".join(sorted_list))

    cleanup_temp(tmp_dir)


@cli.command()
def exec(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC container to run in", autocompletion=running_svc
    ),
):
    """Execute a bash prompt in a live IOC's container"""
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj, service_name).exec()
    else:
        IocK8sCommands(ctx.obj, service_name).exec()


@cli.command()
def log_history(
    service_name: str = typer.Argument(
        ...,
        help="Name of the IOC to inspect",
        autocompletion=all_svc,
    ),
):
    """Open historical logs for an IOC"""
    IocK8sCommands(None, service_name).log_history()


@cli.command()
def logs(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC to inspect", autocompletion=running_svc
    ),
    prev: bool = typer.Option(
        False, "--previous", "-p", help="Show log from the previous instance of the IOC"
    ),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow the log stream"),
):
    """Show logs for current and previous instances of an IOC"""
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj, service_name).logs(prev, follow)
    else:
        IocK8sCommands(ctx.obj, service_name).logs(prev, follow)


@cli.command()
def restart(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC container to restart", autocompletion=running_svc
    ),
):
    """Restart an IOC"""
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj, service_name).restart()
    else:
        IocK8sCommands(ctx.obj, service_name).restart()


@cli.command()
def start(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC container to start", autocompletion=all_svc
    ),
):
    """Start an IOC"""
    log.debug("Starting IOC with LOCAL={ctx.obj.namespace == " "}")
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj, service_name).start()
    else:
        IocK8sCommands(ctx.obj, service_name).start()


@cli.command()
def stop(
    ctx: typer.Context,
    service_name: str = typer.Argument(
        ..., help="Name of the IOC container to stop", autocompletion=running_svc
    ),
):
    """Stop an IOC"""
    if ctx.obj.namespace == globals.LOCAL_NAMESPACE:
        IocLocalCommands(ctx.obj, service_name).stop()
    else:
        IocK8sCommands(ctx.obj, service_name).stop()


@cli.command()
def validate(
    ctx: typer.Context,
    svc_instance: Path = typer.Argument(
        ...,
        help="folder of local IOC definition",
        exists=True,
        file_okay=False,
        resolve_path=True,
        autocompletion=force_plain_completion,
    ),
):
    """
    Verify a local IOC definition folder is valid

    Checks that values.yaml points at a valid image
    Checks that ioc.yaml has the matching schema header and that it passes
      scheme validation
    """
    IocLocalCommands(ctx.obj).validate_instance(svc_instance)
