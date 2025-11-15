from __future__ import annotations

from typing import Any, Dict

from .settings import AppSettings, settings as runtime_settings


class Config:
    """
    Backwards compatible facade around the new AppSettings object.
    """

    def __init__(self, app_settings: AppSettings | None = None):
        self._settings = app_settings or runtime_settings

    def get_env_config(self) -> Dict[str, Any]:
        return self._settings.model_dump(by_alias=True)

    def get_config(self) -> Dict[str, Any]:
        return self._settings.model_dump(by_alias=True)

    def get_mysql_config(self) -> Dict[str, Any]:
        return self._settings.database.model_dump()

    def get_log_config(self) -> Dict[str, Any]:
        return self._settings.logging.model_dump()

    def get_module_config(self) -> Dict[str, Any]:
        return self._settings.module.model_dump()

    def get_load_modules(self) -> Dict[str, Any]:
        return self.get_module_config()

    def get_scheduler_config(self) -> Dict[str, Any]:
        return self._settings.scheduler.model_dump()

    def get_tasks_config(self) -> Dict[str, Any]:
        return self._settings.tasks

    def get_cache_config(self) -> Dict[str, Any]:
        return self._settings.cache.model_dump()

    def get_monitoring_config(self) -> Dict[str, Any]:
        return self._settings.monitoring.model_dump()

    def get_api_config(self) -> Dict[str, Any]:
        return self._settings.api.model_dump()

    def get_time_zone(self) -> str:
        return self._settings.common.time_zone

    def get_common_config(self) -> Dict[str, Any]:
        return self._settings.common.model_dump()

    def get_api_version(self) -> str:
        return self._settings.common.api_version


config = Config()
