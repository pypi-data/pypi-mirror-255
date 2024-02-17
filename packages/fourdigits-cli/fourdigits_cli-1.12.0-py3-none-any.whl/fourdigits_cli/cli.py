import logging

import click

from fourdigits_cli.commands.docker import group as docker_group
from fourdigits_cli.commands.exonet import group as exonet_group
from fourdigits_cli.commands.gitlab import group as gitlab_group


@click.group()
@click.option(
    "--debug", is_flag=True, show_default=True, default=False, help="Show debug logging"
)
def main(debug):
    logger = logging.getLogger("fourdigits_cli")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(handler)


main.add_command(docker_group, name="docker")
main.add_command(gitlab_group, name="gitlab")
main.add_command(exonet_group, name="exonet")
