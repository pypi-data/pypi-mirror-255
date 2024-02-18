"""Takeoff CLI for starting and managing Takeoff servers."""
# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import docker
import typer

from .sdk.takeoff import Takeoff

main = typer.Typer()

# Create a Docker client
client = docker.from_env()


@main.command()
def start(
    model_name: str = typer.Option(..., "--model", "-m", help="The models to optimize."),
    backend: str = typer.Option(..., "--backend", "-b", help="The backend to use."),
    device: str = typer.Option(..., "--device", "-d", help="The device to use."),
):
    try:
        takeoff = Takeoff(model_name=model_name, backend=backend, device=device)
        takeoff.start()
    except Exception as e:
        typer.echo(f"Server start failed: {e}")


@main.command()
def hello(name: str):
    typer.echo(f"Hello {name}")


@main.command()
def list():
    typer.echo("Listing running takeoff servers...")

    # List all running containers
    containers = client.containers.list()

    # Print the list of running containers
    typer.echo("Running containers:")
    for container in containers:
        if "takeoff" in container.name:
            typer.echo(f"ID: {container.short_id}, Name: {container.name}")


@main.command()
def down(
    id: str = typer.Option(None, "--id", "-i", help="The ID of the server to shut down."),
    is_all: bool = typer.Option(False, "--all", "-a", help="Shut down all running servers."),
):
    if id is None and not is_all:
        typer.echo("Please specify the ID of the server to shut down. Or use --all to shut down all running servers.")
        return

    typer.echo("Shutting down server...")
    if id is not None:
        typer.echo(f"Shutting down server with ID {id}...")
        try:
            client.containers.get(id).stop()
            client.containers.get(id).remove()
            typer.echo("Server shut down")
        except Exception as e:
            typer.echo(f"Server shut down failed: {e}")

    if is_all:
        typer.echo("Shutting down all servers...")
        # List all running containers
        containers = client.containers.list()

        # Print the list of running containers
        for container in containers:
            if "takeoff" in container.name:
                typer.echo(f"Shutting down -> ID: {container.short_id}, Name: {container.name}")

                client.containers.get(container.name).stop()
                client.containers.get(container.name).remove()

        typer.echo("Server shut down")


if __name__ == "__main__":
    main()
