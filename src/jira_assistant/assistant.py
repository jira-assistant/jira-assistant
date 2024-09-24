# -*- coding: utf-8 -*-
"""This module will provide console command signatures."""
import pathlib
import warnings

from json import dump
from os import environ, remove
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from termcolor import cprint

from dotenv import load_dotenv
from urllib3 import disable_warnings

from .excel_definition import ExcelDefinition, ExcelDefinitionColumn
from .excel_operation import output_to_excel_file, read_excel_file
from .jira_client import JiraClient, JiraIssueType, JiraField
from .sprint_schedule import SprintScheduleStore
from .story import (
    Story,
    sort_stories_by_inline_weights,
    sort_stories_by_property_and_order,
    sort_stories_by_raise_ranking,
)
from .utils import standardize_column_name, strip_lower

__all__ = [
    "run_steps_and_sort_excel_file",
    "generate_jira_field_mapping_file",
    "dry_run_steps_and_sort_excel_file",
]

# Currently, the openpyxl package will report an obsolete warning.
warnings.simplefilter(action="ignore", category=UserWarning)
# Disable the HTTPS certificate verification warning.
disable_warnings()

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE / "assets"
DEFAULT_JSON_IDENT = 4
DEFAULT_SPRINT_SCHEDULE_FILE = ASSETS / "sprint_schedule.json"
DEFAULT_EXCEL_DEFINITION_FILE = ASSETS / "excel_definition.json"


def __clear_env_variables():
    if "JIRA_URL" in environ:
        del environ["JIRA_URL"]
    if "JIRA_ACCESS_TOKEN" in environ:
        del environ["JIRA_ACCESS_TOKEN"]


def __get_jira_client(env_file: Optional[Path] = None) -> Optional[JiraClient]:
    if env_file is None:
        if not load_dotenv(ASSETS / ".env"):
            cprint(
                """The default env file is missing.
Please use the update-jira-info command to 
run any command for creating the file.""",
                color="light_yellow",
            )
            return None
    else:
        __clear_env_variables()
        if not load_dotenv(env_file):
            cprint(
                "The env file is invalid. Please double check the env file.",
                color="light_red",
            )
            return None

    jira_url: Optional[str] = environ.get("JIRA_URL", default=None)
    if jira_url is None or jira_url.isspace() or len(jira_url) == 0:
        cprint(
            """The jira url is invalid.
Please use the update-jira-info command to add/update url.""",
            color="light_red",
        )
        return None

    jira_access_token = environ.get("JIRA_ACCESS_TOKEN", default=None)
    if (
        jira_access_token is None
        or jira_access_token.isspace()
        or len(jira_access_token) == 0
    ):
        cprint(
            """The jira access token is invalid.
Please use the update-jira-info command to add/update token.""",
            color="light_red",
        )
        return None

    jira_timeout: Optional[float] = None
    tmp = environ.get("JIRA_TIMEOUT", default=None)
    if tmp is not None:
        jira_timeout = float(tmp)

    jira_client = JiraClient(jira_url, jira_access_token, jira_timeout)

    if not jira_client.health_check():
        cprint(
            """The jira access token is revoked.
Please use the update-jira-info command to add/update token.""",
            color="light_red",
        )
        return None

    cprint(f"Jira link: {jira_url}", color="light_cyan")

    return jira_client


def __query_jira_information(
    stories: List[Story],
    excel_definition: ExcelDefinition,
    env_file: Optional[Path] = None,
) -> bool:
    jira_client = __get_jira_client(env_file)

    if jira_client is None:
        return False

    jira_fields = []

    for definition_column in excel_definition.get_columns():
        if (
            not definition_column["query_jira_info"]
            or definition_column["jira_field_mapping"] is None
        ):
            continue
        jira_fields.append(
            {
                "name": definition_column["name"],
                # Jira API not support specific property level.
                "jira_name": definition_column["jira_field_mapping"]["name"],
                "jira_path": definition_column["jira_field_mapping"]["path"],
            }
        )

    jira_query_result = jira_client.get_stories_detail(
        [story["storyid"].strip() for story in stories], jira_fields
    )

    for story in stories:
        story_id: str = strip_lower(story["storyid"])
        if story_id in jira_query_result:
            for jira_field in jira_fields:
                story[jira_field["name"]] = jira_query_result[story_id].get(
                    jira_field["jira_path"], None
                )
        else:
            # Story ID has been changed because of convertion.
            tmp_res = jira_client.get_stories_detail([story_id], jira_fields)
            if len(tmp_res) > 0:
                story["storyid"] = list(tmp_res.keys())[0].upper()
                for jira_field in jira_fields:
                    story[jira_field["name"]] = (
                        list(tmp_res.values())[0]
                        .get(jira_field["jira_path"], "")
                        .upper()
                    )
                cprint(
                    f"Story id has been changed. \
Previous: {story_id.upper()}, \
Current: {story['storyid'].upper()}",
                    color="light_blue",
                )
            else:
                cprint(
                    f"Cannot find related information for story: {story_id}",
                    color="light_yellow",
                )
                story.need_sort = False
                continue

    return True


def __check_allowed_value(
    current_value: Any,
    jira_field: JiraField,
    excel_column: ExcelDefinitionColumn,
    project_type_name: str,
    issue_type_name: str,
) -> "bool":
    if excel_column["jira_field_mapping"] is not None:
        jira_field_path = excel_column["jira_field_mapping"]["path"]
        if not jira_field.is_value_allowed(str(current_value), jira_field_path):
            cprint(
                f"{excel_column['name']} has not allowed value: {current_value}. ProjectType: {project_type_name} and IssueType: {issue_type_name}.",  # pylint: disable=line-too-long
                color="light_yellow",
            )
            cprint("Allowed values:", color="light_yellow")
            for index, value in enumerate(jira_field.allowed_values[jira_field_path]):
                cprint(f"{index + 1}. {value}", color="light_yellow")
            return False
    return True


def __assign_new_story_field(
    is_array: bool,
    new_story_fields: Dict[str, Any],
    excel_column: ExcelDefinitionColumn,
    value: Any,
):
    if excel_column is None or excel_column["jira_field_mapping"] is None:
        return
    jira_field_path = excel_column["jira_field_mapping"]["path"]
    if is_array:
        new_story_fields[jira_field_path] = str(value).split(excel_column["delimiter"])
    else:
        new_story_fields[jira_field_path] = value


def __create_jira_stories(
    stories: List[Story],
    excel_definition: ExcelDefinition,
    env_file: Optional[Path] = None,
) -> bool:
    jira_client = __get_jira_client(env_file)

    if jira_client is None:
        return False

    for story in stories:
        input_project_type: Optional[str] = story["projecttype"]
        input_issue_type: Optional[str] = story["issuetype"]
        # Validation
        if input_project_type is None or input_issue_type is None:
            cprint(
                f"Please fulfill ProjectType/IssueType field. \
Excel row number: {story.excel_row_index}.",
                color="light_yellow",
            )
            continue
        project_type = jira_client.get_project_by_project_name(input_project_type)
        if project_type is None:
            cprint(
                f"ProjectType: {input_project_type} is not supported.",
                color="light_yellow",
            )
            continue
        issue_type: Optional[JiraIssueType] = None
        for item in jira_client.get_issue_types(project_type.name):
            if item.name.lower() == input_issue_type.lower():
                issue_type = item
                break
        if issue_type is None:
            cprint(
                f"IssueType: {input_issue_type} is not supported.", color="light_yellow"
            )
            continue

        (
            required_fields,
            not_required_fields,
        ) = jira_client.get_fields_by_project_id_and_issue_id(
            project_type.id_, issue_type.id_
        )

        new_story_fields: Dict[str, Any] = {}

        # Required fields
        all_fields_valid: bool = True
        for required_field in required_fields:
            excel_columns = excel_definition.get_column_by_jira_field_mapping_name(
                required_field.id_
            )

            if not excel_columns:
                cprint(
                    f"Excel definition missing required field: {required_field.id_}.",  # pylint: disable=line-too-long
                    color="light_red",
                )
                all_fields_valid = False
                continue

            for excel_column in excel_columns:
                excel_column_name = excel_column["name"]
                if not hasattr(story, standardize_column_name(excel_column_name)):
                    cprint(
                        f"Story missing required field: {excel_column_name}.",
                        color="light_red",
                    )
                    all_fields_valid = False
                    continue
                current_value = story[standardize_column_name(excel_column_name)]
                if not __check_allowed_value(
                    current_value,
                    required_field,
                    excel_column,
                    project_type.name,
                    input_issue_type,
                ):
                    all_fields_valid = False
                    continue
                __assign_new_story_field(
                    required_field.is_array,
                    new_story_fields,
                    excel_column,
                    current_value,
                )

        # Not required fields
        for not_required_field in not_required_fields:
            excel_columns = excel_definition.get_column_by_jira_field_mapping_name(
                not_required_field.id_
            )
            for excel_column in excel_columns:
                excel_column_name = excel_column["name"]
                if not hasattr(story, standardize_column_name(excel_column_name)):
                    continue
                is_array = not_required_field.is_array
                current_value = story[standardize_column_name(excel_column_name)]
                if current_value is None:
                    continue
                if not __check_allowed_value(
                    current_value,
                    not_required_field,
                    excel_column,
                    project_type.name,
                    input_issue_type,
                ):
                    all_fields_valid = False
                    continue
                __assign_new_story_field(
                    is_array, new_story_fields, excel_column, current_value
                )

        if not all_fields_valid:
            cprint("Please fix the above issues.", color="light_red")
            continue

        # Special fields
        new_story_fields["project.id"] = project_type.id_

        new_story = jira_client.create_story(new_story_fields)
        if new_story is not None:
            story["storyid"] = new_story.key
            cprint(
                f"New story: {jira_client.get_jira_browser_link(new_story.key)}",
                color="light_green",
            )
            continue
        return False
    return True


def __run_pre_steps(
    stories: List[Story],
    excel_definition: ExcelDefinition,
    env_file: Optional[Path] = None,
):
    # Execute pre-process steps
    pre_process_steps = excel_definition.get_pre_process_steps()

    for pre_process_step in pre_process_steps:
        cprint(f"Executing step: {pre_process_step.name}...")
        if strip_lower(pre_process_step.name) == strip_lower("RetrieveJiraInformation"):
            need_call_jira_api: bool = False
            for excel_definition_column in excel_definition.get_columns():
                if excel_definition_column["jira_field_mapping"] is not None:
                    need_call_jira_api = True
                    break

            if need_call_jira_api:
                stories_need_call_jira: List[Story] = []
                for story in stories:
                    if story.need_sort and story["storyid"] is not None:
                        stories_need_call_jira.append(story)
                if not __query_jira_information(
                    stories_need_call_jira, excel_definition, env_file
                ):
                    cprint("Retrieve jira information failed.", color="light_yellow")
                    return
        elif strip_lower(pre_process_step.name) == strip_lower(
            "FilterOutStoryWithoutId"
        ):
            for story in stories:
                if story["storyid"] is None:
                    story.need_sort = False
        elif strip_lower(pre_process_step.name) == strip_lower(
            "FilterOutStoryBasedOnJiraStatus"
        ):
            for story in stories:
                if (
                    story["status"] is not None
                    and pre_process_step.config is not None
                    and story["status"].upper()
                    in pre_process_step.config.get("JiraStatuses", [])
                ):
                    story.need_sort = False
        elif strip_lower(pre_process_step.name) == strip_lower("CreateJiraStory"):
            stories_need_to_create: List[Story] = []
            for story in stories:
                if story["storyid"] is None or story["storyid"].strip() == "":
                    stories_need_to_create.append(story)

            if stories_need_to_create:
                if not __create_jira_stories(
                    stories_need_to_create, excel_definition, env_file
                ):
                    cprint(
                        "Error occurred when creating Jira stories.",
                        color="light_yellow",
                    )
                    return
        cprint("Executing finish.")


def __run_sort_logics(
    stories: List[Story], excel_definition: ExcelDefinition
) -> Tuple[List[Story], List[Story]]:
    stories_no_need_sort = []
    stories_need_sort = []

    for story in stories:
        if story.need_sort:
            stories_need_sort.append(story)
        else:
            stories_no_need_sort.append(story)

    # Execute sorting logic.
    sort_strategies = excel_definition.get_sort_strategies()

    for sort_strategy in sort_strategies:
        cprint(f"Executing {sort_strategy.name} sorting...")
        if strip_lower(sort_strategy.name) == strip_lower("InlineWeights"):
            stories_need_sort = sort_stories_by_inline_weights(stories_need_sort)
        elif strip_lower(sort_strategy.name) == strip_lower("SortOrder"):
            sort_stories_by_property_and_order(
                stories_need_sort,
                excel_definition.get_columns(),
                sort_strategy,
            )
        elif strip_lower(sort_strategy.name) == strip_lower("RaiseRanking"):
            stories_need_sort = sort_stories_by_raise_ranking(
                stories_need_sort,
                excel_definition.get_columns(),
                sort_strategy,
            )
        cprint("Executing finish.")

    return stories_need_sort, stories_no_need_sort


def __pre_parse_excel_file(
    input_file: Union[str, Path],
    excel_definition_file: Optional[Union[str, Path]] = None,
    sprint_schedule_file: Optional[Union[str, Path]] = None,
) -> Tuple[ExcelDefinition, Optional[List[str]], Optional[List[Story]]]:
    sprint_schedule = SprintScheduleStore()
    if sprint_schedule_file is None:
        cprint("Using default sprint schedule...")
        sprint_schedule.load(DEFAULT_SPRINT_SCHEDULE_FILE.read_text(encoding="utf-8"))
    else:
        cprint("Using custom sprint schedule...")
        sprint_schedule.load_file(sprint_schedule_file)

    excel_definition = ExcelDefinition()
    if excel_definition_file is None:
        cprint("Using default excel definition...")
        excel_definition.load(DEFAULT_EXCEL_DEFINITION_FILE.read_text(encoding="utf-8"))
    else:
        cprint("Using custom excel definition...")
        excel_definition.load_file(excel_definition_file)

    validation_result = excel_definition.validate()
    if len(validation_result) != 0:
        cprint(
            """Validating excel definition failed.
Please check below information to fix first.""",
            color="light_red",
        )
        for index, item in enumerate(validation_result):
            cprint(f"{index + 1}. {item}", color="light_yellow")
        return excel_definition, None, None
    cprint("Validating excel definition success.", color="light_green")

    excel_columns, stories = read_excel_file(
        input_file, excel_definition, sprint_schedule
    )

    return excel_definition, excel_columns, stories


def run_steps_and_sort_excel_file(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    excel_definition_file: Optional[Union[str, Path]] = None,
    sprint_schedule_file: Optional[Union[str, Path]] = None,
    over_write: bool = True,
    env_file: Optional[Path] = None,
):
    """
    Sort the Excel file and output the result

    parm input_file:
        The Excel file need to be sorted. (Absolute path only)

    parm output_file:
        The sorted Excel file location. (Absolute path only)

    parm sprint_schedule_file:
        The JSON file which contains the priority list to
        calculate the :py:class:`Milestone`

    parm excel_definition_file:
        The JSON file which contains the input Excel file's structure.

    parm over_write:
        Whether the exist output file will be over-write.
    """
    excel_definition, excel_columns, stories = __pre_parse_excel_file(
        input_file, excel_definition_file, sprint_schedule_file
    )

    if stories is None or excel_columns is None:
        cprint("Parse excel file failed.", color="light_red")
        return

    if not stories:
        cprint("There are no stories inside the excel file.", color="light_yellow")
        return

    __run_pre_steps(stories, excel_definition, env_file)

    stories_need_sort, stories_no_need_sort = __run_sort_logics(
        stories, excel_definition
    )

    output_to_excel_file(
        output_file,
        stories_need_sort + stories_no_need_sort,  # First output the sorted stories.
        excel_column_names=excel_columns,
        over_write=over_write,
    )

    cprint(f"{output_file} has been saved.", color="light_green")


def generate_jira_field_mapping_file(
    file: Union[str, Path], over_write: bool = True, env_file: Optional[Path] = None
) -> bool:
    """Generate jira field mapping"""
    jira_client = __get_jira_client(env_file)

    if jira_client is None:
        return False

    output_file_path: Path = Path(file).absolute()

    if output_file_path.exists():
        if over_write:
            try:
                remove(file)
            except PermissionError as e:
                raise FileExistsError(
                    f"The exist jira field mapping file: {file} cannot be removed."
                ) from e
        else:
            raise FileExistsError(
                f"The jira field mapping file: {file} is already exist."
            )

    with open(output_file_path, mode="x", encoding="utf-8") as output_file:
        dump(
            jira_client.get_all_fields(),
            output_file,
            default=lambda o: o.__dict__,
            indent=DEFAULT_JSON_IDENT,
            sort_keys=True,
        )
        output_file.flush()
        output_file.close()

    return True


def dry_run_steps_and_sort_excel_file(
    input_file: Union[str, Path],
    excel_definition_file: Optional[Union[str, Path]] = None,
    sprint_schedule_file: Optional[Union[str, Path]] = None,
):
    """
    Analyze the input and print the result.

    parm input_file:
        The Excel file need to be sorted. (Absolute path only)

    parm output_file:
        The sorted Excel file location. (Absolute path only)

    parm sprint_schedule_file:
        The JSON file which contains the priority list to
        calculate the :py:class:`Milestone`

    parm excel_definition_file:
        The JSON file which contains the input Excel file's structure.

    """
    excel_definition, excel_columns, stories = __pre_parse_excel_file(
        input_file, excel_definition_file, sprint_schedule_file
    )

    cprint(f"There are {excel_definition.column_count} columns in the definition file.")
    if not excel_definition.count_of_pre_process_steps():
        cprint("No pre-process steps have been configured.", color="light_red")
    else:
        cprint("Pre-process steps:")
        for index, step in enumerate(excel_definition.get_pre_process_steps()):
            cprint(f"{index + 1}: {step.name}. Enabled: {step.enabled}.")

    if not excel_definition.count_of_sort_strategies():
        cprint("No sort strategies have been configured.", color="yellow")
    else:
        cprint("Sort strategies:")
        for index, strategy in enumerate(excel_definition.get_sort_strategies()):
            cprint(f"{index + 1}: {strategy.name}. Enabled: {strategy.enabled}.")

    if stories is None or excel_columns is None:
        cprint("Parse excel file failed.", color="light_red")
        return

    cprint(f"There are {len(excel_columns)} columns in the excel.")

    if not stories:
        cprint("There are no stories inside the excel file.", color="light_yellow")
    else:
        story_need_sort: int = 0
        for story in stories:
            if story.need_sort:
                story_need_sort += 1

        cprint(f"There are {story_need_sort} stories can be sorted.")
