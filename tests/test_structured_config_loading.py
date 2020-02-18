# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
from dataclasses import dataclass
from typing import Any, List

import pkg_resources
import pytest
from omegaconf import MISSING, ListConfig, OmegaConf, ValidationError

from hydra._internal.config_loader_impl import ConfigLoaderImpl
from hydra._internal.utils import create_config_search_path
from hydra.core.config_store import ConfigStore, ConfigStoreWithProvider
from hydra.errors import MissingConfigException
from hydra.test_utils.test_utils import (  # noqa: F401
    chdir_hydra_root,
    restore_singletons,
)
from typing import Any, Optional

chdir_hydra_root()


@dataclass
class MySQLConfig:
    driver: str = MISSING
    host: str = MISSING
    port: int = MISSING
    user: str = MISSING
    password: str = MISSING


hydra_load_list = [
    ("hydra_config", "structured://", "hydra"),
    ("hydra/hydra_logging/default", "pkg://hydra.conf", "hydra"),
    ("hydra/job_logging/default", "pkg://hydra.conf", "hydra"),
    ("hydra/launcher/basic", "pkg://hydra.conf", "hydra"),
    ("hydra/sweeper/basic", "pkg://hydra.conf", "hydra"),
    ("hydra/output/default", "pkg://hydra.conf", "hydra"),
    ("hydra/help/default", "pkg://hydra.conf", "hydra"),
    ("hydra/hydra_help/default", "pkg://hydra.conf", "hydra"),
]


def test_load_as_configuration(restore_singletons) -> None:
    """
    Load structured config as a configuration
    """
    with ConfigStoreWithProvider("test_provider") as config_store:
        config_store.store(group="db", name="mysql", node=MySQLConfig, path="db")

    config_loader = ConfigLoaderImpl(config_search_path=create_config_search_path(None))
    cfg = config_loader.load_configuration(config_name="db/mysql", overrides=[])
    del cfg["hydra"]
    assert cfg == {
        "db": {
            "driver": MISSING,
            "host": MISSING,
            "port": MISSING,
            "user": MISSING,
            "password": MISSING,
        }
    }

    expected = hydra_load_list.copy()
    expected.extend([("db/mysql", "structured://", "test_provider")])
    assert config_loader.get_load_history() == expected


@pytest.mark.parametrize(
    "path", ["file://hydra/test_utils/configs", "pkg://hydra.test_utils.configs"]
)
class TestConfigLoader:
    pass
