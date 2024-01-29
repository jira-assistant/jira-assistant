# -*- coding: utf-8 -*-
from subprocess import CalledProcessError, run

import pytest

from . import ASSETS_FILES, ASSETS_ENV_FILES


def test_process_excel_file(tmpdir):
    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "happy_path.xlsx",
            "--output_folder",
            tmpdir,
            "--excel_definition_file",
            ASSETS_FILES / "excel_definition_avoid_jira_operations.json",
            "--sprint_schedule_file",
            ASSETS_FILES / "sprint_schedule.json",
        ],
        capture_output=True,
        check=True,
    )

    assert "xlsx has been saved" in result.stdout.decode("utf-8")
    assert (tmpdir / "happy_path_sorted.xlsx").exists()


def test_process_excel_file_apply_env_file(tmpdir):
    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "happy_path.xlsx",
            "--output_folder",
            tmpdir,
            "--excel_definition_file",
            ASSETS_FILES / "excel_definition_avoid_jira_operations.json",
            "--sprint_schedule_file",
            ASSETS_FILES / "sprint_schedule.json",
            "--env_file",
            ASSETS_ENV_FILES / "default.env",
        ],
        capture_output=True,
        check=True,
    )

    assert "xlsx has been saved" in result.stdout.decode("utf-8")
    assert (tmpdir / "happy_path_sorted.xlsx").exists()


def test_process_excel_file_run_twice(tmpdir):
    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "happy_path.xlsx",
            "--excel_definition_file",
            ASSETS_FILES / "excel_definition_avoid_jira_operations.json",
            "--sprint_schedule_file",
            ASSETS_FILES / "sprint_schedule.json",
            "-o",
            tmpdir,
        ],
        capture_output=True,
        check=True,
    )

    assert "xlsx has been saved" in result.stdout.decode("utf-8")
    assert (tmpdir / "happy_path_sorted.xlsx").exists()

    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "happy_path.xlsx",
            "--excel_definition_file",
            ASSETS_FILES / "excel_definition_avoid_jira_operations.json",
            "--sprint_schedule_file",
            ASSETS_FILES / "sprint_schedule.json",
            "--output_folder",
            tmpdir,
        ],
        capture_output=True,
        check=True,
    )

    assert "xlsx has been saved" in result.stdout.decode("utf-8")
    assert (tmpdir / "happy_path_sorted_1.xlsx").exists()


def test_process_excel_file_using_invalid_definition_file():
    with pytest.raises(CalledProcessError) as e:
        run(
            [
                "process-excel-file",
                ASSETS_FILES / "happy_path.xlsx",
                "--excel_definition_file",
                ASSETS_FILES / "excel_definition_invalid_structure.txt",
                "--sprint_schedule_file",
                ASSETS_FILES / "sprint_schedule.json",
            ],
            capture_output=True,
            check=True,
        )

    assert "The structure of excel definition file is wrong" in str(e.value.output)


def test_process_excel_file_using_wrong_input_file():
    with pytest.raises(CalledProcessError) as e:
        run(
            [
                "process-excel-file",
                ASSETS_FILES / "excel_definition_invalid_index.json",
                "--excel_definition_file",
                ASSETS_FILES / "excel_definition_invalid_structure.txt",
            ],
            capture_output=True,
            check=True,
        )

    assert "Please provide an Excel file" in str(e.value.output)


def test_process_excel_file_input_file_not_found():
    with pytest.raises(CalledProcessError) as e:
        run(
            [
                "process-excel-file",
                ASSETS_FILES / "not_found.xlsx",
                "--excel_definition_file",
                ASSETS_FILES / "excel_definition_invalid_structure.txt",
            ],
            capture_output=True,
            check=True,
        )

    assert "Input file is not exist" in str(e.value.output)


def test_process_excel_file_output_folder_not_exist(tmpdir):
    tmpdir.remove(ignore_errors=True)

    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "happy_path.xlsx",
            "--output_folder",
            tmpdir,
            "--excel_definition_file",
            ASSETS_FILES / "excel_definition_avoid_jira_operations.json",
            "--sprint_schedule_file",
            ASSETS_FILES / "sprint_schedule.json",
        ],
        capture_output=True,
        check=True,
    )

    assert "xlsx has been saved" in result.stdout.decode("utf-8")


def test_generate_template_excel_definition(tmpdir):
    result = run(
        ["generate-template", "--output_folder", tmpdir, "excel-definition"],
        capture_output=True,
        check=True,
    )

    assert "Generate success" in result.stdout.decode("utf-8")
    assert "excel-definition" in result.stdout.decode("utf-8")


def test_generate_template_excel(tmpdir):
    result = run(
        ["generate-template", "--output_folder", tmpdir, "excel"],
        capture_output=True,
        check=True,
    )

    assert "Generate success" in result.stdout.decode("utf-8")
    assert "excel" in result.stdout.decode("utf-8")


def test_generate_template_sprint_schedule(tmpdir):
    result = run(
        ["generate-template", "sprint-schedule", "--output_folder", tmpdir],
        capture_output=True,
        check=True,
    )

    assert "Generate success" in result.stdout.decode("utf-8")
    assert "schedule" in result.stdout.decode("utf-8")


def test_generate_template_jira_field_mapping_failed(tmpdir):
    with pytest.raises(CalledProcessError) as e:
        run(
            [
                "generate-template",
                "--output_folder",
                tmpdir,
                "jira-field-mapping",
                "--env_file",
                ASSETS_ENV_FILES / "default.env",
            ],
            capture_output=True,
            check=True,
        )

    assert "Generate failed! Template type: jira-field-mapping." in str(e.value.stdout)


def test_generate_template_failed():
    with pytest.raises(CalledProcessError) as e:
        run(["generate-template", "abc"], capture_output=True, check=True)

    assert "argument template_type: invalid choice" in str(e.value.stderr)


def test_update_jira_info():
    result = run(
        [
            "update-jira-info",
            "--access_token",
            "123",
            "--url",
            "http://localhost",
            "--env_file",
            ASSETS_ENV_FILES / "default.env",
        ],
        capture_output=True,
        check=True,
    )

    assert "Add/Update jira url success" in result.stdout.decode("utf-8")
    assert "Add/Update jira access token success" in result.stdout.decode("utf-8")


def test_update_jira_info_failed():
    with pytest.raises(CalledProcessError) as e:
        run(
            ["update-jira-info", "--access_token", " "],
            capture_output=True,
            check=True,
        )

    assert "Please check the access token" in str(e.value.output)
