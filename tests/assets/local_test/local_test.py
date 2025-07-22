# -*- coding: utf-8 -*-

import pathlib

import pytest

from jira_assistant.assistant import run_steps_and_sort_excel_file

LOCAL_TEST = pathlib.Path(__file__).resolve().parent


@pytest.mark.skip(reason="For local testing only")
def test_run_steps_and_sort_excel_file(tmpdir):
    run_steps_and_sort_excel_file(
        LOCAL_TEST / "confident.xlsx",
        tmpdir / "excel_sorted.xlsx",
        excel_definition_file=str(LOCAL_TEST / "excel_definition_for_creation.json"),
        env_file=LOCAL_TEST / "confident.env",
    )
