from __future__ import annotations

from fastapi import FastAPI

from pythonprojecttemplate.log.logHelper import get_logger
from pythonprojecttemplate.modules.base import BaseModule

logger = get_logger()


class TestModule:
    async def on_startup(self, app: FastAPI) -> None:
        logger.info("Test module startup complete")

    async def on_shutdown(self, app: FastAPI) -> None:
        logger.info("Test module shutdown complete")


def get_module() -> BaseModule:
    return TestModule()
