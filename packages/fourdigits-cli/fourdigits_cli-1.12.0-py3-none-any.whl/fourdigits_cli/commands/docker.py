import logging
import os
import string
from uuid import uuid4

import click
from packaging.version import InvalidVersion
from packaging.version import parse as version_parser

from fourdigits_cli.settings import DEFAULT_CONFIG
from fourdigits_cli.utils.docker import Docker, DockerException
from fourdigits_cli.utils.git import Git

logger = logging.getLogger(__name__)


@click.group(help="Docker helper command for auto building and pushing")
@click.option(
    "--registry-domain",
    help="Defaults to docker.io, env override DOCKER_REGISTRY_DOMAIN",
)
@click.option("--registry-user", help="env override DOCKER_REGISTRY_USER")
@click.option("--registry-password", help="env override DOCKER_REGISTRY_PASSWORD")
@click.option(
    "--image-user",
    help=f"Defaults to settings ({DEFAULT_CONFIG.docker_image_user}), env override DOCKER_IMAGE_USER",  # noqa: E501
)
@click.pass_context
def group(ctx, **options):
    ctx.obj = Docker(
        registry_user=options["registry_user"]
        or os.environ.get("DOCKER_REGISTRY_USER"),
        registry_password=options["registry_password"]
        or os.environ.get("DOCKER_REGISTRY_PASSWORD"),
        registry=options["registry_domain"]
        or os.environ.get("DOCKER_REGISTRY_DOMAIN", "docker-registry.fourdigits.nl"),
        image_user=options["image_user"]
        or os.environ.get("DOCKER_IMAGE_USER", DEFAULT_CONFIG.docker_image_user),
    )


@group.command(help="Build given environment")
@click.argument("environment")
@click.option(
    "--version",
    help="Version to build. If no version is supplied, it will try to get the current git tag",  # noqa: E501
)
@click.option(
    "--repo",
    default=DEFAULT_CONFIG.docker_repo,
    show_default=True,
    help="Repo to use in the image name. If no repo is supplied, it will use the value from the default config",  # noqa: E501
)
@click.option("--push", is_flag=True, show_default=True, default=False)
@click.option("--target")
@click.option("--file", default="Dockerfile", show_default=True)
@click.option("--context", default=".", show_default=True)
@click.option("--build-arg", multiple=True)
@click.pass_obj
def build(docker: Docker, environment, **options):
    if environment not in DEFAULT_CONFIG.environments:
        raise click.UsageError("Environment doesn't exists in the pyproject.toml")

    version = validate_and_get_version(environment, version=options.get("version"))
    docker_repo = options.get("repo")
    # Download the latest image to increase build process
    latest_image = docker.get_image_name(repo=docker_repo, tag=environment)
    try:
        docker.pull(latest_image)
    except DockerException:
        latest_image = None

    # Docker build, tag and push image
    build_image_name = uuid4().hex
    try:
        docker.build(
            build_image_name,
            file=options.get("file"),
            context=options.get("context"),
            target=options.get("target"),
            release_version=str(version),
            cache_from=latest_image,
            build_args=options.get("build_arg"),
        )
        for tag in [environment, str(version)]:
            docker.image_tag(
                build_image_name,
                docker.get_image_name(
                    repo=docker_repo,
                    tag=tag,
                ),
            )
            if options.get("push"):
                docker.push(
                    docker.get_image_name(
                        repo=docker_repo,
                        tag=tag,
                    )
                )
    except DockerException as e:
        raise click.UsageError(e)


def validate_and_get_version(environment, version=None):
    if version:
        if validate_version(environment, version):
            return version
        elif validate_git_commithash(environment, version):
            return version
        else:
            raise click.UsageError(
                f"Invalid version format ({version}) for {environment}"
            )

    if environment not in ["acc", "prd"]:
        return Git().rev_parse("--short", "HEAD").strip()

    current_commit_tags = Git().tag("--points-at", "HEAD").splitlines()
    for tag_version in current_commit_tags:
        if validate_version(environment, version):
            return tag_version

    if environment == "acc":
        raise click.UsageError(
            f"Could not get valid version tag for ACC on current commit ({current_commit_tags}), valid format is: <major>.<minor>.<patch>rc<number>"  # noqa: E501
        )
    elif environment == "prd":
        raise click.UsageError(
            f"Could not get valid version tag for PRD on current commit ({current_commit_tags}), valid format is: <major>.<minor>.<patch>"  # noqa: E501
        )


def validate_version(environment, version):
    try:
        version = version_parser(version.strip())
    except (IndexError, InvalidVersion):
        return False

    if environment == "acc" and version.pre:
        return True
    elif environment == "prd" and not (
        version.pre or version.post or version.dev or version.local
    ):
        return True
    elif environment in ["acc", "prd"]:
        return False
    return True


def validate_git_commithash(environment, version):
    """
    A commit hash is valid for 'tst' only, and should match a specific format

    Git uses commit hashes in SHA-1 format: 40 chars. The shortened version has no
    defined length other than 'what is needed to make it unique within the repository.'
    git-cli uses 7 chars for `--abbrev-commit`. Github uses 7 chars in it's UI,
    while Gitlab has 8 chars.
    """
    if environment != "tst":
        return False

    version = version.strip()
    return version.strip(string.hexdigits) == "" and 7 <= len(version) <= 40
