from fourdigits_cli.settings import load_config
from tests import DATA_DIR


def test_load_config_valid():
    config = load_config([DATA_DIR / "valid.toml"])

    assert config.docker_repo == "test-repo"
    assert config.docker_image_user == "test-image-user"
    assert not hasattr(config, "extra_option")

    # test environments
    for env, name in {
        "tst": "testing",
        "acc": "acceptance",
        "prd": "production",
    }.items():
        assert config.environments[env].name == name


def test_load_config_invalid():
    config = load_config([DATA_DIR / "invalid.toml"])

    # Still default value
    assert config.docker_repo == ""
    assert config.docker_image_user == "fourdigits"


def test_load_config_defaults():
    config = load_config([DATA_DIR / "defaults.toml"])

    assert config.exonet_project_name == "default-project"
    assert config.docker_repo == "default-project"
    assert config.slack_channel == "default-project"
