# -*- coding: utf-8 -*-
from subprocess import CalledProcessError, run

import pytest

from . import ASSETS_FILES, ASSETS_ENV_FILES


def test_process_excel_file(tmpdir):
    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "excel.xlsx",
            "--output-folder",
            tmpdir,
            "--excel-definition-file",
            ASSETS_FILES / "excel_definition_avoid_jira_operations.json",
            "--sprint-schedule-file",
            ASSETS_FILES / "sprint_schedule.json",
        ],
        capture_output=True,
        check=True,
    )

    assert "xlsx has been saved" in result.stdout.decode("utf-8")
    assert (tmpdir / "excel_sorted.xlsx").exists()


def test_process_excel_file_output_version():
    result = run(
        ["process-excel-file", "--version"],
        capture_output=True,
        check=True,
    )

    assert "process-excel-file" in result.stdout.decode("utf-8")


def test_process_excel_file_apply_env_file(tmpdir):
    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "excel.xlsx",
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
    assert (tmpdir / "excel_sorted.xlsx").exists()


def test_process_excel_file_run_twice(tmpdir):
    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "excel.xlsx",
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
    assert (tmpdir / "excel_sorted.xlsx").exists()

    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "excel.xlsx",
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
    assert (tmpdir / "excel_sorted_1.xlsx").exists()


def test_process_excel_file_using_invalid_definition_file():
    with pytest.raises(CalledProcessError) as e:
        run(
            [
                "process-excel-file",
                ASSETS_FILES / "excel.xlsx",
                "--excel_definition_file",
                ASSETS_FILES / "excel_definition_invalid_json.txt",
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
                ASSETS_FILES / "excel_definition_invalid_json.txt",
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
                ASSETS_FILES / "excel_definition_invalid_json.txt",
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
            ASSETS_FILES / "excel.xlsx",
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


def test_generate_template_output_version():
    result = run(
        ["generate-template", "--version"],
        capture_output=True,
        check=True,
    )

    assert "generate-template" in result.stdout.decode("utf-8")


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


def test_update_jira_info_output_version():
    result = run(
        ["update-jira-info", "--v"],
        capture_output=True,
        check=True,
    )

    assert "update-jira-info" in result.stdout.decode("utf-8")


def test_update_jira_info_failed():
    with pytest.raises(CalledProcessError) as e:
        run(
            ["update-jira-info", "--access_token", " "],
            capture_output=True,
            check=True,
        )

    assert "Please check the access token" in str(e.value.output)


def test_dry_run_steps_and_sort_excel_file(tmpdir):
    result = run(
        [
            "process-excel-file",
            ASSETS_FILES / "excel.xlsx",
            "--output-folder",
            tmpdir,
            "--excel-definition-file",
            ASSETS_FILES / "excel_definition_avoid_jira_operations.json",
            "--sprint-schedule-file",
            ASSETS_FILES / "sprint_schedule.json",
            "--dry-run",
        ],
        capture_output=True,
        check=True,
    )

    output = result.stdout.decode("utf-8")
    assert not (tmpdir / "excel_sorted.xlsx").exists()
    assert "Using custom sprint schedule..." in output
    assert "Using custom excel definition..." in output
    assert "Validating excel definition success." in output
    assert "There are 29 columns in the excel." in output
    assert "There are 25 columns in the definition file." in output
    assert "There are 8 stories can be sorted." in output
    assert "Pre-process steps:" in output
    assert "FilterOutStoryWithoutId" in output
    assert "Sort strategies:" in output
    assert "InlineWeights" in output
    assert "SortOrder" in output
    assert "RaiseRanking" in output
