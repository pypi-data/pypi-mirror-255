import logging
import os
from dataclasses import dataclass, field

import tomli

logger = logging.getLogger(__name__)

PROJECT_NAME_DEFAULTS = [
    "exonet_project_name",
    "docker_repo",
    "slack_channel",
]


@dataclass(frozen=True)
class EnvironmentConfig:
    """
    Configuration for an environment: test, acceptation, production, etc.
    For Exonet projects, this is tst, acc, prd.

    In pyproject.toml, this is defined as:

    ```toml
    [tool.fourdigits.envs.tst]

    [tool.fourdigits.envs.acc]

    [tool.fourdigits.envs.prd]
    ```

    TODO: Add overrides for some settings, like exonet_project_name,
        docker_repo and docker_image_user.
        This way we can have a django and nextjs project in the same repository:

        ```toml
        [tool.fourdigits.envs.tst]

        [tool.fourdigits.envs.acc]

        [tool.fourdigits.envs.prd]

        [tool.fourdigits.envs.nextjs_tst]
        exonet_project_name = "nextjs"
        docker_repo = "nextjs"

        [tool.fourdigits.envs.nextjs_acc]
        exonet_project_name = "nextjs"
        docker_repo = "nextjs"

        [tool.fourdigits.envs.nextjs_prd]
        exonet_project_name = "nextjs"
        docker_repo = "nextjs"
        ```
    """

    name: str = ""


@dataclass(frozen=True)
class Config:
    name: str = ""
    exonet_project_name: str = ""
    docker_repo: str = ""
    slack_channel: str = ""
    docker_image_user: str = "fourdigits"
    environments: dict[str, EnvironmentConfig] = field(default_factory=dict)


def load_config(py_project_paths: list):
    config = {}
    for path in py_project_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    config = tomli.load(f)
            except tomli.TOMLDecodeError as e:
                logger.warning(f"Could not load pyproject.toml file: {e}")
                config = {}

    cli_config = config.get("tool", {}).get("fourdigits", {})

    kwargs = {
        key: value for key, value in cli_config.items() if key in Config.__annotations__
    }

    kwargs["name"] = config.get("project", {}).get("name", "")

    # Set defaults
    project_name = config.get("project", {}).get("name", "")
    for key in PROJECT_NAME_DEFAULTS:
        if not kwargs.get(key):
            kwargs[key] = project_name

    # Get environments
    kwargs["environments"] = {}
    for group, group_config in cli_config.get("envs", {}).items():
        kwargs["environments"][group] = EnvironmentConfig(
            **{
                key: value
                for key, value in group_config.items()
                if key in EnvironmentConfig.__annotations__
            }
        )

    return Config(**kwargs)


DEFAULT_CONFIG = load_config(
    [
        os.path.join(os.getcwd(), "pyproject.toml"),
        os.path.join(os.getcwd(), "src", "pyproject.toml"),
    ]
)
