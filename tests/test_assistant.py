# -*- coding: utf-8 -*-
import pathlib
from os import environ
import pytest

from requests_mock import Mocker

from jira_assistant.assistant import (
    generate_jira_field_mapping_file,
    run_steps_and_sort_excel_file,
    dry_run_steps_and_sort_excel_file,
)
from jira_assistant.excel_definition import ExcelDefinition
from jira_assistant.excel_operation import read_excel_file
from jira_assistant.jira_client import JiraClient
from jira_assistant.sprint_schedule import SprintScheduleStore
from jira_assistant.story import compare_story_based_on_inline_weights
from tests.mock_server import (
    mock_jira_requests,
    mock_jira_requests_with_failed_status_code,
)
from tests.utils import read_stories_from_excel

from . import ASSETS_ENV_FILES, ASSETS_FILES, SRC_ASSETS


def test_run_steps_and_sort_excel_file(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel.xlsx",
            tmpdir / "excel_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )

        excel_definition = ExcelDefinition()
        excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
        sprint_schedule = SprintScheduleStore()
        sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

        _, stories = read_excel_file(
            tmpdir / "excel_sorted.xlsx",
            excel_definition,
            sprint_schedule,
        )

        assert len(stories) == 8

        jira_client = JiraClient(environ["JIRA_URL"], environ["JIRA_ACCESS_TOKEN"])

        noneed_sort_statuses = [
            "SPRINT COMPLETE",
            "PENDING RELEASE",
            "PRODUCTION TESTING",
            "CLOSED",
        ]

        jira_fields = [
            {
                "name": "domain",
                "jira_name": "customfield_15601",
                "jira_path": "customfield_15601.value",
            },
            {"name": "status", "jira_name": "status", "jira_path": "status.name"},
        ]

        for i in range(len(stories) - 1):
            story_id_0 = stories[i]["storyid"].lower().strip()
            story_id_1 = stories[i + 1]["storyid"].lower().strip()
            query_result = jira_client.get_stories_detail(
                [story_id_0, story_id_1], jira_fields
            )
            if (
                query_result[story_id_0]["status.name"].upper()
                not in noneed_sort_statuses
                and query_result[story_id_1]["status.name"].upper()
                not in noneed_sort_statuses
            ):
                assert (
                    compare_story_based_on_inline_weights(stories[i], stories[i + 1])
                    >= 0
                )


def test_run_steps_and_sort_excel_file_addition_columns(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel_addition_columns.xlsx",
            tmpdir / "excel_addition_columns_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )

        excel_definition = ExcelDefinition()
        excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
        sprint_schedule = SprintScheduleStore()
        sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

        columns, stories = read_excel_file(
            tmpdir / "excel_addition_columns_sorted.xlsx",
            excel_definition,
            sprint_schedule,
        )
        assert "abc" in columns
        assert "123" in columns

        assert len(stories) == 8

        jira_client = JiraClient(environ["JIRA_URL"], environ["JIRA_ACCESS_TOKEN"])

        noneed_sort_statuses = [
            "SPRINT COMPLETE",
            "PENDING RELEASE",
            "PRODUCTION TESTING",
            "CLOSED",
        ]

        jira_fields = [
            {
                "name": "domain",
                "jira_name": "customfield_15601",
                "jira_path": "customfield_15601.value",
            },
            {"name": "status", "jira_name": "status", "jira_path": "status.name"},
        ]

        for i in range(len(stories) - 1):
            story_id_0 = stories[i]["storyid"].lower().strip()
            story_id_1 = stories[i + 1]["storyid"].lower().strip()
            query_result = jira_client.get_stories_detail(
                [story_id_0, story_id_1], jira_fields
            )
            if (
                query_result[story_id_0]["status.name"].upper()
                not in noneed_sort_statuses
                and query_result[story_id_1]["status.name"].upper()
                not in noneed_sort_statuses
            ):
                assert (
                    compare_story_based_on_inline_weights(stories[i], stories[i + 1])
                    >= 0
                )


def test_run_steps_and_sort_excel_file_use_default_files(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel.xlsx",
            tmpdir / "excel_sorted.xlsx",
            env_file=ASSETS_ENV_FILES / "default.env",
        )

        excel_definition = ExcelDefinition()
        excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
        sprint_schedule = SprintScheduleStore()
        sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

        _, stories = read_excel_file(
            tmpdir / "excel_sorted.xlsx",
            excel_definition,
            sprint_schedule,
        )

        assert len(stories) == 8


def test_run_steps_and_sort_excel_file_use_wrong_excel_definition_file(capsys, tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel.xlsx",
            tmpdir / "excel_sorted.xlsx",
            excel_definition_file=ASSETS_FILES
            / "excel_definition_duplicate_index.json",
            env_file=ASSETS_ENV_FILES / "default.env",
        )
        output = capsys.readouterr()
        assert "Validating excel definition failed." in output.out


def test_run_steps_and_sort_excel_file_with_empty_excel_file(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "empty_excel.xlsx",
            tmpdir / "empty_excel_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
        )


def test_run_steps_and_sort_excel_file_with_raise_ranking_file(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel.xlsx",
            tmpdir / "excel_sorted.xlsx",
            excel_definition_file=str(
                ASSETS_FILES / "excel_definition_with_raise_ranking.json"
            ),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )

        _, stories = read_stories_from_excel(
            tmpdir / "excel_sorted.xlsx",
            SRC_ASSETS / "excel_definition.json",
            SRC_ASSETS / "sprint_schedule.json",
        )

        false_value_begin = False
        for story in stories:
            if story["isthisaharddate"] is True:
                continue
            if story["isthisaharddate"] is False and false_value_begin is False:
                false_value_begin = True
                continue
            if story["isthisaharddate"] is True and false_value_begin is True:
                raise AssertionError


def test_run_steps_and_sort_excel_file_missing_jira_url(capsys, tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel.xlsx",
            tmpdir / "excel_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "missing_jira_url.env",
        )
        output = capsys.readouterr()
        assert "The jira url is invalid." in output.out


def test_run_steps_and_sort_excel_file_missing_access_token(capsys, tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel.xlsx",
            tmpdir / "excel_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "missing_jira_access_token.env",
        )
        output = capsys.readouterr()
        assert "The jira access token is invalid." in output.out


def test_run_steps_and_sort_excel_file_jira_health_check_failed(capsys, tmpdir):
    with Mocker(
        real_http=False,
        case_sensitive=False,
        adapter=mock_jira_requests_with_failed_status_code(),
    ):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel.xlsx",
            tmpdir / "excel_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )
        output = capsys.readouterr()
        assert "The jira access token is revoked." in output.out


def test_generate_jira_field_mapping_file(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        output_file: pathlib.Path = tmpdir / "jira_field_mapping.json"

        assert (
            generate_jira_field_mapping_file(
                file=output_file, env_file=ASSETS_ENV_FILES / "default.env"
            )
            is True
        )
        assert output_file.exists() is True


def test_generate_jira_field_mapping_file_over_write_is_true(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        output_file: pathlib.Path = pathlib.Path(tmpdir) / "jira_field_mapping.json"
        output_file.touch(exist_ok=True)

        assert (
            generate_jira_field_mapping_file(
                file=output_file,
                over_write=True,
                env_file=ASSETS_ENV_FILES / "default.env",
            )
            is True
        )
        assert output_file.exists() is True


def test_generate_jira_field_mapping_file_over_write_is_false(tmpdir):
    with pytest.raises(expected_exception=FileExistsError) as e:
        with Mocker(
            real_http=False, case_sensitive=False, adapter=mock_jira_requests()
        ):
            output_file: pathlib.Path = pathlib.Path(tmpdir) / "jira_field_mapping.json"
            output_file.touch(exist_ok=True)

            generate_jira_field_mapping_file(
                output_file,
                over_write=False,
                env_file=ASSETS_ENV_FILES / "default.env",
            )
    assert "already exist" in str(e.value.args[0])


def test_run_steps_and_sort_excel_file_with_no_need_sort_stories(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel_with_no_need_sort_stories.xlsx",
            tmpdir / "excel_with_no_need_sort_stories_sorted.xlsx",
            excel_definition_file=str(ASSETS_FILES / "excel_definition.json"),
            sprint_schedule_file=str(ASSETS_FILES / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )

        excel_definition = ExcelDefinition()
        excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
        sprint_schedule = SprintScheduleStore()
        sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

        _, stories = read_excel_file(
            tmpdir / "excel_with_no_need_sort_stories_sorted.xlsx",
            excel_definition,
            sprint_schedule,
        )

        assert len(stories) == 8

        jira_client = JiraClient(environ["JIRA_URL"], environ["JIRA_ACCESS_TOKEN"])

        noneed_sort_statuses = [
            "SPRINT COMPLETE",
            "PENDING RELEASE",
            "PRODUCTION TESTING",
            "CLOSED",
        ]

        jira_fields = [
            {
                "name": "domain",
                "jira_name": "customfield_15601",
                "jira_path": "customfield_15601.value",
            },
            {"name": "status", "jira_name": "status", "jira_path": "status.name"},
        ]

        for i in range(len(stories) - 1):
            if stories[i]["storyid"] is None or stories[i + 1]["storyid"] is None:
                continue
            story_id_0 = stories[i]["storyid"].lower().strip()
            story_id_1 = stories[i + 1]["storyid"].lower().strip()
            query_result = jira_client.get_stories_detail(
                [story_id_0, story_id_1], jira_fields
            )
            if (
                query_result[story_id_0]["status.name"].upper()
                not in noneed_sort_statuses
                and query_result[story_id_1]["status.name"].upper()
                not in noneed_sort_statuses
            ):
                assert (
                    compare_story_based_on_inline_weights(stories[i], stories[i + 1])
                    >= 0
                )


def test_create_jira_stories_and_sort_excel_file(tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel_create_story.xlsx",
            tmpdir / "excel_create_story_sorted.xlsx",
            excel_definition_file=str(
                ASSETS_FILES / "excel_definition_create_story.json"
            ),
            sprint_schedule_file=str(ASSETS_FILES / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )

        excel_definition = ExcelDefinition()
        excel_definition.load_file(ASSETS_FILES / "excel_definition_create_story.json")
        sprint_schedule = SprintScheduleStore()
        sprint_schedule.load_file(ASSETS_FILES / "sprint_schedule.json")

        _, stories = read_excel_file(
            tmpdir / "excel_create_story_sorted.xlsx",
            excel_definition,
            sprint_schedule,
        )

        assert len(stories) == 1
        assert stories[0]["storyid"] is not None


def test_create_jira_stories_invalid_value(capsys, tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel_create_story_invalid_value.xlsx",
            tmpdir / "excel_create_story_invalid_value_sorted.xlsx",
            excel_definition_file=str(
                ASSETS_FILES / "excel_definition_create_story.json"
            ),
            sprint_schedule_file=str(ASSETS_FILES / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )

        output = capsys.readouterr()
        assert (
            "MyValue has not allowed value: 3. ProjectType: SD and IssueType: Story."
            in output.out
        )
        assert "Allowed values:" in output.out
        assert "1. 1" in output.out
        assert "2. 2" in output.out


def test_create_jira_stories_invalid_project_type(capsys, tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel_create_story_invalid_project_type.xlsx",
            tmpdir / "excel_create_story_invalid_project_type_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )
        output = capsys.readouterr()
        assert "ProjectType: ABC is not supported." in output.out


def test_create_jira_stories_invalid_issue_type(capsys, tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel_create_story_invalid_issue_type.xlsx",
            tmpdir / "excel_create_story_invalid_issue_type_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )
        output = capsys.readouterr()
        assert "IssueType: WHH is not supported." in output.out


def test_create_jira_stories_no_project_type(capsys, tmpdir):
    with Mocker(real_http=False, case_sensitive=False, adapter=mock_jira_requests()):
        run_steps_and_sort_excel_file(
            ASSETS_FILES / "excel_create_story_no_project_type.xlsx",
            tmpdir / "excel_create_story_no_project_type_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
            env_file=ASSETS_ENV_FILES / "default.env",
        )
        output = capsys.readouterr()
        assert "Please fulfill ProjectType/IssueType field." in output.out


def test_dry_run_steps_and_sort_excel_file(capsys):
    dry_run_steps_and_sort_excel_file(
        ASSETS_FILES / "excel_with_no_need_sort_stories.xlsx",
        excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
        sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
    )

    output = capsys.readouterr()
    assert "Using custom sprint schedule..." in output.out
    assert "Using custom excel definition..." in output.out
    assert "Validating excel definition success." in output.out
    assert "There are 29 columns in the excel." in output.out
    assert "There are 29 columns in the definition file." in output.out
    assert "There are 8 stories can be sorted." in output.out
    assert "Pre-process steps:" in output.out
    assert "CreateJiraStory" in output.out
    assert "FilterOutStoryWithoutId" in output.out
    assert "RetrieveJiraInformation" in output.out
    assert "FilterOutStoryBasedOnJiraStatus" in output.out
    assert "Sort strategies:" in output.out
    assert "InlineWeights" in output.out
    assert "SortOrder" in output.out
    assert "SortOrder" in output.out
    assert "RaiseRanking" in output.out
