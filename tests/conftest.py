# -*- coding: utf-8 -*-
from dotenv import load_dotenv

from . import ASSETS_ENV_FILES


def pytest_configure():
    load_dotenv(ASSETS_ENV_FILES / "default.env")
