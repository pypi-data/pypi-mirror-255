"""CLI cache handler."""

import os
import shutil
import pickle
import zlib
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from redbrick import __version__ as sdk_version
from redbrick.utils.common_utils import hash_sha256
from .conf import CLIConfiguration


class CLICache:
    """CLICache entity."""

    _cache_dir: str
    _conf: CLIConfiguration

    _cache_name: str
    _fixed_cache_name: str = "sdk-cache"

    CACHE_LIFETIME: int = 86400

    def __init__(self, cache_dir: str, conf: CLIConfiguration) -> None:
        """Initialize CLICache."""
        self._cache_dir = cache_dir
        self._conf = conf

        self._cache_name = "cache-" + ".".join(sdk_version.split(".", 2)[:2])

        if self._conf.exists and self._cache_name != self._conf.get_option(
            "cache", "name"
        ):
            self.clear_cache()
            self._conf.set_option("cache", "name", self._cache_name)
            self._conf.save()

    @property
    def exists(self) -> bool:
        """Boolean flag to indicate if cache directory exists."""
        if os.path.exists(self._cache_dir):
            if os.path.isdir(self._cache_dir):
                return True
            raise Exception(f"Not a directory {self._cache_dir}")
        return False

    def cache_path(self, *path: str, fixed_cache: bool = False) -> str:
        """Get cache file path."""
        path_dir = os.path.join(
            self._cache_dir,
            self._fixed_cache_name if fixed_cache else self._cache_name,
            *path[:-1],
        )
        os.makedirs(path_dir, exist_ok=True)
        return os.path.join(path_dir, path[-1])

    def get_object(self, entity: str) -> Any:
        """Get entity object from cache."""
        try:
            prev_timestamp = self._conf.get_option(entity, "refresh", "0")
            timestamp = int(datetime.utcnow().timestamp())
            prev_version = self._conf.get_option(entity, "version")
            if (
                prev_timestamp
                and prev_version
                and prev_version == sdk_version
                and timestamp - int(prev_timestamp) <= self.CACHE_LIFETIME
            ):
                cache_file = self.cache_path(f"{entity}.pickle")

                with open(cache_file, "rb") as cache:
                    return pickle.load(cache)
            return None
        except Exception:  # pylint: disable=broad-except
            return None

    def set_object(self, entity: str, obj: Any, save_conf: bool = True) -> None:
        """Set entity object into cache."""
        self._conf.set_option(
            entity, "refresh", str(int(datetime.utcnow().timestamp()))
        )
        self._conf.set_option(entity, "version", sdk_version)

        cache_file = self.cache_path(f"{entity}.pickle")

        with open(cache_file, "wb") as cache:
            pickle.dump(obj, cache)

        if save_conf:
            self._conf.save()

    def get_data(
        self,
        name: str,
        cache_hash: Optional[str],
        json_data: bool = True,
        fixed_cache: bool = False,
    ) -> Optional[Union[str, Dict, List]]:
        """Get cache data."""
        if cache_hash is None:
            return None
        cache_file = self.cache_path(name, fixed_cache=fixed_cache)
        if os.path.isfile(cache_file):
            with open(cache_file, "rb") as file_:
                data = file_.read()
            if cache_hash == hash_sha256(data):
                data = zlib.decompress(data)
                return json.loads(data) if json_data else data.decode()
        return None

    def set_data(
        self, name: str, entity: Union[str, Dict, List], fixed_cache: bool = False
    ) -> str:
        """Set cache data."""
        cache_file = self.cache_path(name, fixed_cache=fixed_cache)
        data = zlib.compress(
            (
                entity
                if isinstance(entity, str)
                else json.dumps(entity, separators=(",", ":"))
            ).encode()
        )
        cache_hash = hash_sha256(data)
        with open(cache_file, "wb") as file_:
            file_.write(data)
        return cache_hash

    def remove_data(self, name: str, fixed_cache: bool = False) -> None:
        """Remove cache data."""
        cache_file = self.cache_path(name, fixed_cache=fixed_cache)
        if os.path.isfile(cache_file):
            os.remove(cache_file)

    def get_entity(
        self, name: str, fixed_cache: bool = False
    ) -> Optional[Union[str, Dict, List]]:
        """Get cache entity."""
        cache_file = self.cache_path(*self._task_path(name), fixed_cache=fixed_cache)
        with open(cache_file, "r", encoding="utf-8") as file_:
            data = json.load(file_)
        return data

    def set_entity(
        self, name: str, entity: Union[str, Dict, List], fixed_cache: bool = False
    ) -> None:
        """Set cache entity."""
        cache_file = self.cache_path(*self._task_path(name), fixed_cache=fixed_cache)
        with open(cache_file, "w", encoding="utf-8") as file_:
            json.dump(entity, file_, separators=(",", ":"))

    def remove_entity(self, name: str, fixed_cache: bool = False) -> None:
        """Remove cache entity."""
        cache_file = self.cache_path(*self._task_path(name), fixed_cache=fixed_cache)
        if os.path.isfile(cache_file):
            os.remove(cache_file)

    def _task_path(self, task_id: str) -> List[str]:
        """Get task dir from id."""
        return [
            task_id[6:8],
            task_id[11:13],
            task_id[16:18],
            task_id[21:23],
            task_id[34:36],
            task_id,
        ]

    def clear_cache(self, all_caches: bool = False) -> None:
        """Clear project cache."""
        if not self.exists:
            return

        caches = os.listdir(self._cache_dir)
        if not all_caches:
            caches = [
                cache
                for cache in caches
                if cache not in (self._cache_name, self._fixed_cache_name)
            ]

        for cache in caches:
            shutil.rmtree(os.path.join(self._cache_dir, cache), ignore_errors=True)
