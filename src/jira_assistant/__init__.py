# -*- coding: utf-8 -*-
"""
This module is used to list all exported classes/methods.
"""
from sys import version_info

from .assistant import (
    run_steps_and_sort_excel_file,
    dry_run_steps_and_sort_excel_file,
    generate_jira_field_mapping_file,
)
from .console_script import generate_template, process_excel_file, update_jira_info
from .excel_definition import ExcelDefinition, ExcelDefinitionColumn
from .excel_operation import output_to_excel_file, read_excel_file
from .milestone import Milestone
from .priority import Priority
from .sprint_schedule import SprintScheduleStore
from .story import Story, StoryFactory


if version_info < (3, 8):
    import importlib_metadata as metadata

    version_ = metadata.version
else:
    from importlib.metadata import version

    version_ = version


__version__ = version_("jira_assistant")

__all__ = [
    "ExcelDefinition",
    "ExcelDefinitionColumn",
    "read_excel_file",
    "output_to_excel_file",
    "run_steps_and_sort_excel_file",
    "dry_run_steps_and_sort_excel_file",
    "generate_jira_field_mapping_file",
    "Milestone",
    "Priority",
    "SprintScheduleStore",
    "Story",
    "StoryFactory",
    "process_excel_file",
    "generate_template",
    "update_jira_info",
]
