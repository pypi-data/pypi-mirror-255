import glob
import importlib
import os
from pathlib import Path
from typing import List, Optional

import yaml
from diffsync.store.redis import RedisStore

from infrahub_sync import SyncAdapter, SyncConfig, SyncInstance
from potenda import Potenda


def import_adapter(adapter: SyncAdapter, directory: str):
    here = os.path.abspath(os.path.dirname(__file__))
    relative_directory = directory.replace(here, "")[1:]
    module = importlib.import_module(f"infrahub_sync.{relative_directory.replace('/', '.')}.{adapter.name}.adapter")
    return getattr(module, f"{adapter.name.title()}Sync")


def get_all_sync() -> List[SyncInstance]:
    results = []
    here = os.path.abspath(os.path.dirname(__file__))

    for config_file in glob.glob(f"{here}/sync/**/config.yml", recursive=True):
        directory_name = os.path.dirname(config_file)
        config_data = yaml.safe_load(Path(config_file).read_text(encoding="utf-8"))
        SyncConfig(**config_data)
        results.append(SyncInstance(**config_data, directory=directory_name))

    return results


def get_instance(name: str) -> Optional[SyncInstance]:
    for item in get_all_sync():
        if item.name == name:
            return item

    return None


def get_potenda_from_instance(
    sync_instance: SyncInstance, branch: Optional[str] = None, show_progress: Optional[bool] = True
) -> Potenda:
    source = import_adapter(adapter=sync_instance.source, directory=sync_instance.directory)
    destination = import_adapter(adapter=sync_instance.destination, directory=sync_instance.directory)

    internal_storage_engine = None

    if sync_instance.store:
        if sync_instance.store.type == "redis":
            if sync_instance.store.settings and isinstance(sync_instance.store.settings, dict):
                redis_settings = sync_instance.store.settings
                internal_storage_engine = RedisStore(**redis_settings)
            else:
                internal_storage_engine = RedisStore()

    if sync_instance.source.name == "infrahub" and branch:
        src = source(
            config=sync_instance,
            target="source",
            adapter=sync_instance.source,
            branch=branch,
            internal_storage_engine=internal_storage_engine
            )
    else:
        src = source(
            config=sync_instance,
            target="source",
            adapter=sync_instance.source,
            internal_storage_engine=internal_storage_engine
            )
    if sync_instance.destination.name == "infrahub" and branch:
        dst = destination(
            config=sync_instance,
            target="destination",
            adapter=sync_instance.destination,
            branch=branch,
            internal_storage_engine=internal_storage_engine
            )
    else:
        dst = destination(
            config=sync_instance,
            target="destination",
            adapter=sync_instance.destination,
            internal_storage_engine=internal_storage_engine
            )

    ptd = Potenda(
        destination=dst,
        source=src,
        config=sync_instance,
        top_level=sync_instance.order,
        show_progress=show_progress,
    )

    return ptd
