from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {**base}
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ModuleSettings(BaseModel):
    base_path: str = "pythonprojecttemplate.modules"
    modules: List[str] = Field(default_factory=list)


class LoggingSettings(BaseModel):
    project_name: str = "python_project_template"
    base_log_directory: str = "../log"
    log_level: str = "INFO"


class SchedulerExecutorsSettings(BaseModel):
    default_threads: int = 20
    process_pool: int = 5


class SchedulerJobDefaultsSettings(BaseModel):
    coalesce: bool = False
    max_instances: int = 3


class SchedulerSettings(BaseModel):
    executors: SchedulerExecutorsSettings = SchedulerExecutorsSettings()
    job_defaults: SchedulerJobDefaultsSettings = SchedulerJobDefaultsSettings()


class CommonPortsSettings(BaseModel):
    redis_default: int = 6379
    mysql_default: int = 3306


class CommonSettings(BaseModel):
    time_zone: str = "Asia/Shanghai"
    api_version: str = "v1"
    ports: CommonPortsSettings = CommonPortsSettings()


class ApiSettings(BaseModel):
    title: str = "Python Project Template API"
    description: str = "A production ready FastAPI service"
    version: str = "3.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    loop: str = "asyncio"
    open_api_on_startup: bool = True
    docs_url: str | None = "/docs"
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    max_concurrency: int = 100
    request_timeout: int = 30
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 180
    refresh_token_expire_days: int = 7


class DatabaseSettings(BaseModel):
    driver: str = "mysql+pymysql"
    username: str = "root"
    password: str = "password"
    host: str = "localhost"
    port: int = 3306
    database: str = "pythonprojecttemplate"
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600
    echo: bool = False

    @property
    def url(self) -> str:
        return (
            f"{self.driver}://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class CacheRedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class CacheSettings(BaseModel):
    type: str = "memory"
    ttl: int = 3600
    max_size: int = 1000
    redis: CacheRedisSettings = CacheRedisSettings()


class MonitoringSettings(BaseModel):
    prometheus_port: int = 9966
    cpu_threshold: int = 80
    memory_threshold: int = 80


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PPT_",
        env_file=".env",
        extra="allow",
        populate_by_name=True,
    )

    env: str = "dev"
    module: ModuleSettings = Field(default_factory=ModuleSettings, alias="module_config")
    logging: LoggingSettings = LoggingSettings()
    scheduler: SchedulerSettings = SchedulerSettings()
    common: CommonSettings = CommonSettings()
    api: ApiSettings = ApiSettings()
    database: DatabaseSettings = DatabaseSettings()
    cache: CacheSettings = CacheSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    tasks: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def settings_customise_sources(
        cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            cls.yaml_config_settings_source,
            file_secret_settings,
        )

    @classmethod
    def yaml_config_settings_source(cls, _: BaseSettings) -> Dict[str, Any]:
        base_dir = Path(__file__).resolve().parent
        env_yaml = base_dir / "env.yaml"
        env_data = cls._load_yaml(env_yaml)
        env_name = os.getenv("PPT_ENV", env_data.get("env", "dev"))
        config_yaml = base_dir / f"{env_name}.yaml"
        config_data = cls._load_yaml(config_yaml)
        merged = _deep_merge(env_data, config_data)
        merged["env"] = env_name
        return merged

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
            if not isinstance(data, dict):
                raise ValueError(f"{path} must define a mapping")
            return data


settings = AppSettings()
