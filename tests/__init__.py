# -*- coding: utf-8 -*-
import pathlib

TESTS_ROOT = pathlib.Path(__file__).resolve().parent
ASSETS_FILES: pathlib.Path = TESTS_ROOT / "assets/files"
ASSETS_ENV_FILES: pathlib.Path = TESTS_ROOT / "assets/env_files"
PROJECT_ROOT = TESTS_ROOT.parent
SRC_ASSETS: pathlib.Path = PROJECT_ROOT / "src/jira_assistant/assets"
