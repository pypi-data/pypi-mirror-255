from subprocess import run
from typing import Dict, List, Literal

import click
from click import Group
from dotenv import dotenv_values

cli = Group()


@cli.command()
@click.argument("file", type=str)
@click.argument("env-type", type=click.Choice(["conda", "mamba"]), default="mamba")
def load(file, env_type):
    """Add environment variables from a file to the active environment. (This will be persisted across conda/mamba sessions)"""
    env = dotenv_values(file)
    click.echo(
        f"Setting {len(env)} environment variables: {', '.join(list(env.keys()))}"
    )
    set_vars(env_type, env)


@cli.command()
@click.argument("file", type=str)
@click.argument("env-type", type=click.Choice(["conda", "mamba"]), default="mamba")
def unload(file, env_type):
    """Remove environment variables listed in file from the active environment. (This will be persisted across conda/mamba sessions)"""
    env = dotenv_values(file)
    click.echo(f"Unsetting file {file} environment variables.")
    unset_vars(env_type, env.keys())


@cli.command()
@click.argument("name", type=str)
@click.argument("value", type=str)
@click.argument("env-type", type=click.Choice(["conda", "mamba"]), default="mamba")
def set(name, value, env_type):
    """Set an environment variable in the active environment. (This will be persisted across conda/mamba sessions)"""
    click.echo(f"Setting environment variables: {name}")
    set_vars(env_type, {name: value})


@cli.command()
@click.argument("var_name", type=str)
@click.argument("env-type", type=click.Choice(["conda", "mamba"]), default="mamba")
def unset(var_name, env_type):
    """Remove an environment variable from the active environment. (This will be persisted across conda/mamba sessions)"""
    click.echo(f"Unsetting {var_name}.")
    unset_vars(env_type, [var_name])


@cli.command()
@click.argument("env-type", type=click.Choice(["conda", "mamba"]), default="mamba")
def clear(env_type):
    """Clear all environment variables from the active environment."""
    vars_list = run(
        f"{env_type} env config vars list".split(),
        capture_output=True,
    )
    unset_vars(env_type, vars_list.stdout.decode().split("\n"))


@cli.command()
@click.argument("env-type", type=click.Choice(["conda", "mamba"]), default="mamba")
def show(env_type):
    """Show environment variables in the active environment."""
    run(f"{env_type} env config vars list".split())


def unset_vars(env_type: Literal["conda", "mamba"], env_vars: List[str]):
    var_names = " ".join([var.split("=")[0].strip() for var in env_vars])
    click.echo(f"Unsetting environment variables: {var_names}")
    run(f"{env_type} env config vars unset {var_names}".split())


def set_vars(env_type: Literal["conda", "mamba"], env_vars: Dict[str, str]):
    env_vars = " ".join([f"{k}={v}" for k, v in env_vars.items()])
    run(f"{env_type} env config vars set {env_vars}".split())
