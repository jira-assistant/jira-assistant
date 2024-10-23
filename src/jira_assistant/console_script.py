# -*- coding: utf-8 -*-
"""
This module is used to provide the console program.
"""
import os
import pathlib
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from shutil import copyfile
from typing import Optional
from urllib.parse import ParseResult, urlparse

from dotenv import set_key
from termcolor import cprint

from .assistant import (
    dry_run_steps_and_sort_excel_file,
    generate_jira_field_mapping_file,
    run_steps_and_sort_excel_file,
)
from .excel_definition import ExcelDefinition
from .excel_operation import output_to_excel_file

__all__ = [
    "process_excel_file",
    "generate_template",
    "update_jira_info",
    "get_package_version",
]


def get_package_version() -> str:
    return version("jira_assistant")


def get_args_for_process_excel_file() -> Namespace:
    """Process console command's arguments. Command: process_excel_file"""
    parser = ArgumentParser(
        description="Used to pre-process and sort stories",
        formatter_class=ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )

    parser.add_argument("input_file", type=pathlib.Path, help="Source Excel file.")
    parser.add_argument(
        "-o",
        "--output-folder",
        "--output_folder",
        metavar="<path>",
        type=pathlib.Path,
        required=False,
        help="Output folder.",
    )
    parser.add_argument(
        "--excel-definition-file",
        "--excel_definition_file",
        metavar="<path>",
        type=pathlib.Path,
        required=False,
        help="Excel definition file. File format: JSON.",
    )
    parser.add_argument(
        "--sprint-schedule-file",
        "--sprint_schedule_file",
        metavar="<path>",
        type=pathlib.Path,
        required=False,
        help="Milestone priority file. File format: JSON.",
    )
    parser.add_argument(
        "--over-write",
        "--over_write",
        metavar="True|False",
        type=bool,
        required=False,
        default=True,
        help="Whether or not to over write existing file.",
    )
    parser.add_argument(
        "--env-file",
        "--env_file",
        metavar="<path>",
        type=pathlib.Path,
        required=False,
        help="Env file which contains info like jira url.",
    )
    parser.add_argument(
        "--dry-run",
        "--dry_run",
        required=False,
        action="store_true",
        help="Only analyze the input and definition files. No side effects at all.",
    )
    parser.add_argument(
        "--v",
        "--version",
        action="version",
        version=f"%(prog)s {get_package_version()}",
    )

    args = parser.parse_args()

    return args


def process_excel_file() -> None:
    """Console command: process_excel_file"""
    try:
        args = get_args_for_process_excel_file()

        # Pre-Process input file
        input_file_absolute_path: pathlib.Path = (
            pathlib.Path.cwd() / args.input_file.as_posix()
        ).resolve()

        if input_file_absolute_path.suffix.lower() != ".xlsx":
            cprint(
                f"Please provide an Excel file. File: {input_file_absolute_path}.",
                color="light_yellow",
            )
            sys.exit(1)

        if not os.path.exists(input_file_absolute_path):
            cprint(
                f"Input file is not exist. File: {input_file_absolute_path}.",
                color="light_yellow",
            )
            sys.exit(1)

        input_file_name_without_extension = input_file_absolute_path.stem

        # Pre-Process output file
        output_folder_absolute_path: pathlib.Path = (
            input_file_absolute_path.parent.absolute()
        )

        if args.output_folder is not None:
            output_folder_absolute_path = (
                pathlib.Path(args.output_folder).resolve().absolute()
            )

        if not output_folder_absolute_path.exists():
            output_folder_absolute_path.mkdir(parents=True, exist_ok=True)

        output_file_absolute_path: pathlib.Path = (
            output_folder_absolute_path
            / f"{input_file_name_without_extension}_sorted.xlsx"
        ).resolve()

        # Fix duplicate output file issue.
        test_output_file_absolute_path = pathlib.Path(
            output_file_absolute_path
        ).resolve()

        copy_count = 1
        while test_output_file_absolute_path.exists():
            test_output_file_absolute_path = (
                output_folder_absolute_path
                / f"{ output_file_absolute_path.stem }_{copy_count}.xlsx"
            )
            copy_count += 1

        output_file_absolute_path = pathlib.Path(
            test_output_file_absolute_path
        ).resolve()

        excel_definition_file_absolute_path = None

        if args.excel_definition_file is not None:
            excel_definition_file_absolute_path = pathlib.Path(
                pathlib.Path.cwd() / args.excel_definition_file.as_posix()
            ).resolve()

        sprint_schedule_file_absolute_path = None

        if args.sprint_schedule_file is not None:
            sprint_schedule_file_absolute_path = pathlib.Path(
                pathlib.Path.cwd() / args.sprint_schedule_file.as_posix()
            ).resolve()

        # Overwrite parameter.
        over_write = True
        if args.over_write is not None:
            over_write = args.over_write

        # Env file parameter.
        env_file = None
        if args.env_file is not None:
            env_file = args.env_file

        # Dry run
        if args.dry_run is True:
            dry_run_steps_and_sort_excel_file(
                input_file_absolute_path,
                excel_definition_file_absolute_path,
                sprint_schedule_file_absolute_path,
            )
        else:
            run_steps_and_sort_excel_file(
                input_file_absolute_path,
                output_file_absolute_path,
                excel_definition_file_absolute_path,
                sprint_schedule_file_absolute_path,
                over_write,
                env_file,
            )

        sys.exit(0)
    except Exception as e:
        cprint(e, color="light_red")
        sys.exit(1)


def get_args_for_generate_template() -> Namespace:
    """Process console command's arguments. Command: generate_template"""
    parser = ArgumentParser(
        description="Used to generate templates",
        formatter_class=ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )

    parser.add_argument(
        "template_type",
        metavar="template_type",
        type=str,
        help="""What kind of file template you want to generate.
Choices: excel, excel-definition, sprint-schedule or jira-field-mapping.""",
        choices=["excel", "excel-definition", "sprint-schedule", "jira-field-mapping"],
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        "--output_folder",
        metavar="<path>",
        type=pathlib.Path,
        required=False,
        help="Output folder.",
    )
    parser.add_argument(
        "--env-file",
        "--env_file",
        metavar="<path>",
        type=pathlib.Path,
        required=False,
        help="Env file which contains info like jira url.",
    )
    parser.add_argument(
        "--v",
        "--version",
        action="version",
        version=f"%(prog)s {get_package_version()}",
    )

    return parser.parse_args()


HERE = pathlib.Path(__file__).resolve().parent
SRC_ASSETS = HERE / "assets"


def generate_template():
    """Console command: generate_template"""
    try:
        args = get_args_for_generate_template()

        template_type: str = str(args.template_type).lower()
        output_folder = Path.cwd()

        if args.output_folder is not None:
            output_folder = args.output_folder

        result: Optional[Path] = None
        if template_type == "excel":
            result = __generate_excel_template(
                __generate_timestamp_filename(output_folder, "excel-template", ".xlsx")
            )
        elif template_type == "excel-definition":
            result = copyfile(
                SRC_ASSETS / "excel_definition.json",
                __generate_timestamp_filename(
                    output_folder, "excel-definition-template", ".json"
                ),
            )
        elif template_type == "sprint-schedule":
            result = copyfile(
                SRC_ASSETS / "sprint_schedule.json",
                __generate_timestamp_filename(
                    output_folder, "sprint-schedule-template", ".json"
                ),
            )
        elif template_type == "jira-field-mapping":
            result = __generate_jira_field_mapping_template(
                __generate_timestamp_filename(
                    output_folder, "jira-field-mapping", ".json"
                ),
                args.env_file,
            )
        else:
            cprint(
                """Invalid template type.
Choices: excel, excel-definition or sprint-schedule.""",
                color="light_red",
            )

        if result is not None and result.is_file():
            cprint(
                f"Generate success! Template type: {template_type}.",
                color="light_green",
            )
            sys.exit(0)
        else:
            cprint(
                f"Generate failed! Template type: {template_type}.", color="light_red"
            )
            sys.exit(1)
    except Exception as e:
        cprint(e, color="light_red")
        sys.exit(1)


def __generate_timestamp_filename(
    output_folder: Path, prefix: str, extension: str
) -> "Path":
    return (
        output_folder
        / f'{prefix}-{datetime.now().strftime("%y-%m-%d-%H-%M-%S")}{extension}'
    ).resolve()


def __generate_excel_template(output_file: "Path") -> Optional[Path]:
    try:
        excel_definition = ExcelDefinition().load_file(
            SRC_ASSETS / "excel_definition.json"
        )
        output_to_excel_file(
            output_file,
            [],
            excel_column_names=excel_definition.get_columns_name(standardized=False),
        )
        return output_file
    except Exception as e:
        cprint(e, color="light_red")
        return None


def __generate_jira_field_mapping_template(
    output_file: "Path", env_file: Optional[Path] = None
) -> Optional[Path]:
    try:
        if generate_jira_field_mapping_file(output_file, env_file=env_file):
            return output_file
    except Exception as e:
        cprint(e, color="light_red")
    return None


def get_args_for_update_jira_info() -> Namespace:
    """Process console command's arguments. Command: update_jira_info"""
    parser = ArgumentParser(
        description="Used to add/update jira url or access token.",
        formatter_class=ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )

    parser.add_argument(
        "--access-token",
        "--access_token",
        metavar="<token>",
        type=str,
        required=False,
        help="Please follow the documentation to get your own access token.",
    )

    parser.add_argument(
        "--url",
        metavar="<jira url>",
        type=str,
        required=False,
        help="Please provide the JIRA website url.",
    )
    parser.add_argument(
        "--env-file",
        "--env_file",
        metavar="<path>",
        type=pathlib.Path,
        required=False,
        help="Custom env file",
    )
    parser.add_argument(
        "--v",
        "--version",
        action="version",
        version=f"%(prog)s {get_package_version()}",
    )

    return parser.parse_args()


def update_jira_info():
    """Console command: update_jira_info"""
    try:
        args = get_args_for_update_jira_info()

        env_file: Path
        if args.env_file is not None:
            env_file = args.env_file
        else:
            env_file = SRC_ASSETS / ".env"

        if not env_file.exists():
            env_file.touch()

        # URL Part
        if args.url is not None:
            parsed_url: ParseResult = urlparse(str(args.url))

            if parsed_url.scheme not in ("https", "http"):
                cprint("Please check the jira url.", color="light_red")
            else:
                result, _, _ = set_key(
                    env_file,
                    key_to_set="JIRA_URL",
                    value_to_set=f"{parsed_url.scheme}://{parsed_url.netloc}",
                    quote_mode="never",
                )

                if result is True:
                    cprint("Add/Update jira url success!", color="light_green")
                else:
                    cprint("Add/Update jira url failed!", color="light_red")

        # ACCESS TOKEN Part
        if args.access_token is not None:
            access_token: str = str(args.access_token)

            if len(access_token.strip()) == 0 or access_token.isspace():
                cprint("Please check the access token.", color="light_red")
                sys.exit(1)
            else:
                result, _, _ = set_key(
                    env_file,
                    key_to_set="JIRA_ACCESS_TOKEN",
                    value_to_set=access_token,
                    quote_mode="never",
                )

                if result is True:
                    cprint("Add/Update jira access token success!", color="light_green")
                    sys.exit(0)
                else:
                    cprint("Add/Update jira access token failed!", color="light_red")
                    sys.exit(1)
    except Exception as e:
        cprint(e, color="light_red")
        sys.exit(1)
