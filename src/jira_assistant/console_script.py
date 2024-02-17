# -*- coding: utf-8 -*-
"""
This module is used to provide the console program.
"""
import os
import pathlib
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
from shutil import copyfile
from typing import Optional
from urllib.parse import ParseResult, urlparse

from dotenv import set_key

from .assistant import (
    generate_jira_field_mapping_file,
    run_steps_and_sort_excel_file,
    dry_run_steps_and_sort_excel_file,
)
from .excel_definition import ExcelDefinition
from .excel_operation import output_to_excel_file

__all__ = ["process_excel_file", "generate_template", "update_jira_info"]

if sys.version_info < (3, 8):
    import importlib_metadata as metadata

    version_ = metadata.version
else:
    from importlib.metadata import version

    version_ = version


def get_package_version() -> str:
    return version_("jira_assistant")


def get_args_for_process_excel_file() -> Namespace:
    """Process console command's arguments. Command: process_excel_file"""
    parser = ArgumentParser(
        description="Jira tool: Used to pre-process and sort stories",
        formatter_class=ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )

    parser.add_argument(
        "input_file", metavar="input_file", type=pathlib.Path, help="Source Excel file."
    )
    parser.add_argument(
        "-o",
        "--output_folder",
        metavar="",
        type=pathlib.Path,
        required=False,
        help="Output folder.",
    )
    parser.add_argument(
        "--excel_definition_file",
        metavar="",
        type=pathlib.Path,
        required=False,
        help="Excel definition file. File format: JSON.",
    )
    parser.add_argument(
        "--sprint_schedule_file",
        metavar="",
        type=pathlib.Path,
        required=False,
        help="Milestone priority file. File format: JSON.",
    )
    parser.add_argument(
        "--over_write",
        metavar="",
        type=bool,
        required=False,
        default=True,
        help="Whether or not to over write existing file.",
    )
    parser.add_argument(
        "--env_file",
        metavar="",
        type=pathlib.Path,
        required=False,
        help="Env file which contains info like jira url.",
    )
    parser.add_argument(
        "--dry_run",
        metavar="",
        type=bool,
        required=False,
        default=False,
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
            print(f"Please provide an Excel file. File: {input_file_absolute_path}.")
            sys.exit(1)

        if not os.path.exists(input_file_absolute_path):
            print(f"Input file is not exist. File: {input_file_absolute_path}.")
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

        # Over write parameter.
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
        print(e)
        sys.exit(1)


def get_args_for_generate_template() -> Namespace:
    """Process console command's arguments. Command: generate_template"""
    parser = ArgumentParser(
        description="Jira tool: Used to generate templates",
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
        "--output_folder",
        metavar="",
        type=pathlib.Path,
        required=False,
        help="Output folder.",
    )
    parser.add_argument(
        "--env_file",
        metavar="",
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
            result = _generate_excel_template(
                _generate_timestamp_filename(output_folder, "excel-template", ".xlsx")
            )
        elif template_type == "excel-definition":
            result = copyfile(
                SRC_ASSETS / "excel_definition.json",
                _generate_timestamp_filename(
                    output_folder, "excel-definition-template", ".json"
                ),
            )
        elif template_type == "sprint-schedule":
            result = copyfile(
                SRC_ASSETS / "sprint_schedule.json",
                _generate_timestamp_filename(
                    output_folder, "sprint-schedule-template", ".json"
                ),
            )
        elif template_type == "jira-field-mapping":
            result = _generate_jira_field_mapping_template(
                _generate_timestamp_filename(
                    output_folder, "jira-field-mapping", ".json"
                ),
                args.env_file,
            )
        else:
            print(
                """Invalid template type.
                Choices: excel, excel-definition or sprint-schedule."""
            )

        if result is not None and result.is_file():
            print(f"Generate success! Template type: {template_type}.")
            sys.exit(0)
        else:
            print(f"Generate failed! Template type: {template_type}.")
            sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


def _generate_timestamp_filename(
    output_folder: Path, prefix: str, extension: str
) -> "Path":
    return (
        output_folder
        / f'{prefix}-{datetime.now().strftime("%y-%m-%d-%H-%M-%S")}{extension}'
    ).resolve()


def _generate_excel_template(output_file: "Path") -> Optional[Path]:
    try:
        excel_definition = ExcelDefinition().load_file(
            SRC_ASSETS / "excel_definition.json"
        )
        output_to_excel_file(
            output_file,
            [],
            excel_column_names=excel_definition.get_columns_name(standardlized=False),
        )
        return output_file
    except Exception as e:
        print(e)
        return None


def _generate_jira_field_mapping_template(
    output_file: "Path", env_file: Optional[Path] = None
) -> Optional[Path]:
    try:
        if generate_jira_field_mapping_file(output_file, env_file=env_file):
            return output_file
    except Exception as e:
        print(e)
    return None


def get_args_for_update_jira_info() -> Namespace:
    """Process console command's arguments. Command: update_jira_info"""
    parser = ArgumentParser(
        description="Jira tool: Used to add/update jira url or access token.",
        formatter_class=ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )

    parser.add_argument(
        "--access_token",
        metavar="",
        type=str,
        required=False,
        help="Please follow the documentation to get your own access token.",
    )

    parser.add_argument(
        "--url",
        metavar="",
        type=str,
        required=False,
        help="Please provide the JIRA website url.",
    )
    parser.add_argument(
        "--env_file",
        metavar="",
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
                print("Please check the jira url.")
            else:
                result, _, _ = set_key(
                    env_file,
                    key_to_set="JIRA_URL",
                    value_to_set=f"{parsed_url.scheme}://{parsed_url.netloc}",
                    quote_mode="never",
                )

                if result is True:
                    print("Add/Update jira url success!")
                else:
                    print("Add/Update jira url failed!")

        # ACCESS TOKEN Part
        if args.access_token is not None:
            access_token: str = str(args.access_token)

            if len(access_token.strip()) == 0 or access_token.isspace():
                print("Please check the access token.")
                sys.exit(1)
            else:
                result, _, _ = set_key(
                    env_file,
                    key_to_set="JIRA_ACCESS_TOKEN",
                    value_to_set=access_token,
                    quote_mode="never",
                )

                if result is True:
                    print("Add/Update jira access token success!")
                    sys.exit(0)
                else:
                    print("Add/Update jira access token failed!")
                    sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)
