# -*- coding: utf-8 -*-
"""
This module is used to store excel column definition information.
"""
# pylint: disable=line-too-long
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from json import loads
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union

from .milestone import Milestone
from .priority import Priority
from .utils import (
    dict_has_key,
    is_absolute_path_valid,
    is_index_range_valid,
    standardize_column_name,
    strip_lower,
)

__all__ = ["ExcelDefinition", "ExcelDefinitionColumn", "SortStrategy"]


class BasicStep:
    def __init__(
        self, name: str, enabled: bool, priority: int, config: Optional[Dict[str, Any]]
    ) -> None:
        self.__name: str = name
        self.__enabled: bool = enabled
        self.__priority: int = priority
        self.__config: Optional[Dict[str, Any]] = config

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def enabled(self) -> bool:
        return self.__enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.__enabled = value

    @property
    def priority(self) -> int:
        return self.__priority

    @priority.setter
    def priority(self, value: int):
        self.__priority = value

    @property
    def config(self) -> Optional[Dict[str, Any]]:
        return self.__config

    @config.setter
    def config(self, value: Dict[str, Any]):
        self.__config = value

    def get_config(self, name: str) -> Optional[Any]:
        if self.__config is not None:
            for key in self.__config.keys():
                if strip_lower(key) == strip_lower(name):
                    return self.__config[key]
        return None


class PreProcessStep(BasicStep):
    pass


def parse_json_item_to_pre_process_step(json_item: Any) -> PreProcessStep:
    pre_process_step_name = ""
    pre_process_step_enabled = False
    pre_process_step_priority = 0
    pre_process_step_config: Dict[str, Any] = {}

    for key, value in json_item.items():
        if strip_lower(key) == strip_lower("name"):
            if value is None or not isinstance(value, str):
                raise ValueError(
                    "The Name property in the pre-process step is invalid."
                )
            pre_process_step_name = value
        if strip_lower(key) == strip_lower("enabled"):
            if value is None or not isinstance(value, bool):
                pre_process_step_enabled = False
            else:
                pre_process_step_enabled = value
        if strip_lower(key) == strip_lower("priority"):
            if value is None or not isinstance(value, int):
                raise ValueError(
                    "The Priority property in the pre-process step is invalid."
                )
            pre_process_step_priority = value
        if strip_lower(key) == strip_lower("config"):
            pre_process_step_config = {}
            if value is not None and isinstance(value, dict):
                for key_, value_ in value.items():
                    pre_process_step_config[key_] = value_

    return PreProcessStep(
        name=pre_process_step_name,
        enabled=pre_process_step_enabled,
        priority=pre_process_step_priority,
        config=pre_process_step_config,
    )


class SortStrategy(BasicStep):
    pass


def parse_json_item_to_sort_strategy(json_item: Any) -> SortStrategy:
    strategy_name = ""
    strategy_priority = 0
    strategy_enabled = False
    strategy_config: Dict[str, Any] = {}

    for key, value in json_item.items():
        if strip_lower(key) == strip_lower("name"):
            if value is None or not isinstance(value, str):
                raise ValueError("The Name property in the sort strategy is invalid.")
            strategy_name = value
        if strip_lower(key) == strip_lower("enabled"):
            if value is None or not isinstance(value, bool):
                strategy_enabled = False
            else:
                strategy_enabled = value
        if strip_lower(key) == strip_lower("priority"):
            if value is None or not isinstance(value, int):
                raise ValueError(
                    "The Priority property in the sort strategy is invalid."
                )
            strategy_priority = value
        if strip_lower(key) == strip_lower("config"):
            strategy_config = {}
            if value is not None and isinstance(value, dict):
                for key_, value_ in value.items():
                    strategy_config[key_] = value_

    return SortStrategy(
        name=strategy_name,
        priority=strategy_priority,
        enabled=strategy_enabled,
        config=strategy_config,
    )


class ExcelDefinitionColumnJiraFieldMapping(TypedDict):
    name: str
    path: str


class ExcelDefinitionColumn(TypedDict):
    index: int
    name: str
    type: Optional[type]
    require_sort: bool
    sort_order: bool
    scope_require_sort: bool
    scope_sort_order: bool
    inline_weights: int
    raise_ranking: int
    scope_raise_ranking: int
    jira_field_mapping: Optional[ExcelDefinitionColumnJiraFieldMapping]
    query_jira_info: bool
    update_jira_info: bool
    delimiter: str


_DEFAULT_VALUE_DELIMITER = "|"


def parse_json_item_to_excel_definition_column(json_item: Any) -> ExcelDefinitionColumn:
    column_index = 0
    column_name = ""
    column_type = None
    column_require_sort = False
    column_sort_order = False
    column_scope_require_sort = False
    column_scope_sort_order = False
    column_inline_weights = -1
    column_raise_ranking = -1
    column_scope_raise_ranking = -1
    column_jira_field_mapping = None
    column_query_jira_info = False
    column_update_jira_info = False
    column_delimiter = _DEFAULT_VALUE_DELIMITER

    for key, value in json_item.items():
        if strip_lower(key) == strip_lower("index"):
            if value is None:
                raise ValueError("Column definition must has an index.")
            if isinstance(value, int):
                column_index = value
            else:
                raise TypeError(
                    "The Index property type in the column definition is not integer."
                )
        elif strip_lower(key) == strip_lower("name"):
            if value is None:
                raise ValueError("Column definition must has a name.")
            if isinstance(value, str):
                column_name = value
            else:
                raise TypeError(
                    "The Name property type in the column definition should be string."
                )
        elif strip_lower(key) == strip_lower("type"):
            column_type = ExcelDefinition.convert_str_to_type(value)
        elif strip_lower(key) == strip_lower("RequireSort"):
            column_require_sort = value
        elif strip_lower(key) == strip_lower("SortOrder"):
            column_sort_order = value
        elif strip_lower(key) == strip_lower("ScopeRequireSort"):
            column_scope_require_sort = value
        elif strip_lower(key) == strip_lower("ScopeSortOrder"):
            column_scope_sort_order = value
        elif strip_lower(key) == strip_lower("InlineWeights"):
            column_inline_weights = value
        elif strip_lower(key) == strip_lower("RaiseRanking"):
            column_raise_ranking = value
        elif strip_lower(key) == strip_lower("ScopeRaiseRanking"):
            column_scope_raise_ranking = value
        elif strip_lower(key) == strip_lower("JiraFieldMapping"):
            column_jira_field_mapping = value
        elif strip_lower(key) == strip_lower("QueryJiraInfo"):
            if value is not None:
                column_query_jira_info = value
        elif strip_lower(key) == strip_lower("UpdateJiraInfo"):
            if value is not None:
                column_update_jira_info = value
        elif strip_lower(key) == strip_lower("Delimiter"):
            if value is not None:
                column_delimiter = strip_lower(value)

    return ExcelDefinitionColumn(
        index=column_index,
        name=column_name,
        type=column_type,
        require_sort=column_require_sort,
        sort_order=column_sort_order,
        scope_require_sort=column_scope_require_sort,
        scope_sort_order=column_scope_sort_order,
        inline_weights=column_inline_weights,
        raise_ranking=column_raise_ranking,
        scope_raise_ranking=column_scope_raise_ranking,
        jira_field_mapping=column_jira_field_mapping,
        query_jira_info=column_query_jira_info,
        update_jira_info=column_update_jira_info,
        delimiter=column_delimiter,
    )


class ExcelDefinition:
    def __init__(self) -> None:
        self.__version = 1
        self.__columns: list[ExcelDefinitionColumn] = []
        self.__sort_strategies: list[SortStrategy] = []
        self.__pre_process_steps: list[PreProcessStep] = []

    def load(self, content: str) -> "ExcelDefinition":
        """
        Load json string to generate the Excel definition

        :param content:
            JSON string content
        """

        try:
            raw_data = loads(s=content)
        except JSONDecodeError as e:
            raise SyntaxError(
                f"The structure of excel definition file is wrong. Hint: {e.msg} in line {e.lineno}:{e.colno}."
            ) from e

        parse_errors = []

        for raw_part in raw_data:
            if not isinstance(raw_part, dict):
                continue
            for name, configuration in raw_part.items():
                if strip_lower(name) == strip_lower("Version") and isinstance(
                    configuration, int
                ):
                    self.__version = configuration
                elif strip_lower(name) == strip_lower("PreProcessSteps"):
                    for item in configuration:
                        try:
                            self.__pre_process_steps.append(
                                parse_json_item_to_pre_process_step(item)
                            )
                        except (TypeError, ValueError) as e:
                            parse_errors.append(e.args[0])
                elif strip_lower(name) == strip_lower("SortStrategies"):
                    for item in configuration:
                        try:
                            self.__sort_strategies.append(
                                parse_json_item_to_sort_strategy(item)
                            )
                        except (TypeError, ValueError) as e:
                            parse_errors.append(e.args[0])
                elif strip_lower(name) == strip_lower("Columns"):
                    for item in configuration:
                        try:
                            self.__columns.append(
                                parse_json_item_to_excel_definition_column(item)
                            )
                        except (TypeError, ValueError) as e:
                            parse_errors.append(e.args[0])

        if parse_errors:
            # Avoid duplicate error messages.
            parse_error_message = "\n".join(
                [f"{index + 1}. {err}" for index, err in enumerate(set(parse_errors))]
            )
            raise SyntaxError(
                f"The excel definition file has below issues need to be fixed:\n{parse_error_message}"
            )

        return self

    def load_file(self, file: Union[str, Path]) -> "ExcelDefinition":
        """
        Load json file to generate the Excel definition

        :param file:
            JSON file location
        """

        if not is_absolute_path_valid(file):
            raise FileNotFoundError(
                f"Please make sure the excel definition file exist and the path should be absolute. File: {file}."
            )

        with open(file=file, mode="r", encoding="utf-8") as table_definition_file:
            try:
                self.load(table_definition_file.read())
            finally:
                table_definition_file.close()

        return self

    def validate(self) -> "List[str]":
        return (
            self.__validate_pre_process_steps()
            + self.__validate_sort_strategies()
            + self.__validate_column_definitions()
        )

    def __validate_pre_process_steps(self) -> "List[str]":
        invalid_definitions: List[str] = []
        valid_pre_process_steps = [
            "CreateJiraStory".lower(),
            "FilterOutStoryWithoutId".lower(),
            "RetrieveJiraInformation".lower(),
            "FilterOutStoryBasedOnJiraStatus".lower(),
        ]

        # Validate PreProcessSteps
        pre_process_step_priorities: List[int] = []
        for pre_process_step in self.__pre_process_steps:
            if pre_process_step.name.lower() not in valid_pre_process_steps:
                invalid_definitions.append("The PreProcessStep name is invalid.")
                continue

            # Validate CreateJiraStory
            if (
                pre_process_step.name.lower() == "CreateJiraStory".lower()
                and pre_process_step.enabled
            ):
                # ProjectType: ProjectIdOrName
                if (
                    standardize_column_name("ProjectType")
                    not in self.get_columns_name()
                ):
                    invalid_definitions.append(
                        "The PreProcessStep: CreateJiraStory must have a column named ProjectType."
                    )
                # IssueType: IssueIdOrName
                if standardize_column_name("IssueType") not in self.get_columns_name():
                    invalid_definitions.append(
                        "The PreProcessStep: CreateJiraStory must have a column named IssueType."
                    )
                continue

            # Validate FilterOutStoryBasedOnJiraStatus
            if (
                pre_process_step.name.lower()
                == "FilterOutStoryBasedOnJiraStatus".lower()
                and pre_process_step.enabled
            ):
                # ProjectType: ProjectIdOrName
                if standardize_column_name("Status") not in self.get_columns_name():
                    invalid_definitions.append(
                        "The PreProcessStep: FilterOutStoryBasedOnJiraStatus must have a column named Status."
                    )

                retrieve_jira_info_step = self.get_pre_process_step_by_name(
                    "RetrieveJiraInformation"
                )
                if (
                    retrieve_jira_info_step is None
                    or retrieve_jira_info_step.priority >= pre_process_step.priority
                ):
                    invalid_definitions.append(
                        "The step named RetrieveJiraInformation must be processed before FilterOutStoryBasedOnJiraStatus."
                    )
                continue

            if (
                pre_process_step.priority is None
                or not isinstance(pre_process_step.priority, int)
                or pre_process_step.priority < 0
            ):
                invalid_definitions.append(
                    f"The pre-process step priority is invalid. PreProcessStep: {pre_process_step.name}"
                )
            else:
                if pre_process_step.priority in pre_process_step_priorities:
                    invalid_definitions.append(
                        f"The pre-process step priority is duplicate. PreProcessStep: {pre_process_step.name}"
                    )
                else:
                    pre_process_step_priorities.append(pre_process_step.priority)

            if pre_process_step.config is not None and dict_has_key(
                pre_process_step.config, "JiraStatuses"
            ):
                if (
                    pre_process_step.name.lower()
                    != "FilterOutStoryBasedOnJiraStatus".lower()
                ):
                    invalid_definitions.append(
                        f"Only FilterOutStoryBasedOnJiraStatus step support JiraStatuses config. PreProcessStep: {pre_process_step.name}."
                    )

                if not isinstance(pre_process_step.config["JiraStatuses"], list):
                    invalid_definitions.append(
                        f"The format of the Jira Statuses is invalid. PreProcessStep: {pre_process_step.name}. Supported format like: ['CLOSED', 'PENDING RELEASE']."
                    )

        return invalid_definitions

    def __validate_sort_strategies(self) -> "List[str]":
        invalid_definitions: List[str] = []

        # Validate Strategies
        strategy_priorities: List[int] = []
        for strategy in self.__sort_strategies:
            if strategy.name.isspace() or len(strategy.name) == 0:
                invalid_definitions.append("The strategy name is invalid.")
                # If strategy name is invalid, no need to check more.
                continue

            if (
                strategy.priority is None
                or not isinstance(strategy.priority, int)
                or strategy.priority < 0
            ):
                invalid_definitions.append(
                    f"The strategy priority is invalid. Strategy: {strategy.name}"
                )
            else:
                if strategy.priority in strategy_priorities:
                    invalid_definitions.append(
                        f"The strategy priority is duplicate. Strategy: {strategy.name}"
                    )
                else:
                    strategy_priorities.append(strategy.priority)

            if strategy.config is not None and dict_has_key(
                strategy.config, "ParentScopeIndexRange"
            ):
                if (
                    strategy.name.lower() != "SortOrder".lower()
                    and strategy.name.lower() != "RaiseRanking".lower()
                ):
                    invalid_definitions.append(
                        f"Only RaiseRanking and SortOrder strategy support ParentScopeIndexRange config. Strategy: {strategy.name}."
                    )
                if not is_index_range_valid(
                    strategy.get_config("ParentScopeIndexRange")
                ):
                    invalid_definitions.append(
                        f"The format of the Parent Level Index Range is invalid. Strategy: {strategy.name}. Supported format strings like: 1-20 or 20,30."
                    )

        return invalid_definitions

    def __validate_column_definitions(  # pylint: disable=too-many-branches
        self,
    ) -> "List[str]":
        invalid_definitions: List[str] = []

        # Validate the Columns
        exist_story_id_column = False
        exist_indexes = []
        exist_column_names = []
        exist_inline_weights = []
        exist_jira_field_names = []
        exist_jira_field_paths = []
        for column in self.get_columns():
            column_index: int = column["index"]
            column_name: str = column["name"]
            column_type: Optional[type] = column["type"]
            column_require_sort: bool = column["require_sort"]
            column_sort_order: bool = column["sort_order"]
            column_scope_require_sort: bool = column["scope_require_sort"]
            column_scope_sort_order: bool = column["scope_sort_order"]
            column_inline_weights: int = column["inline_weights"]
            column_raise_ranking: int = column["raise_ranking"]
            column_scope_raise_ranking: int = column["scope_raise_ranking"]
            column_jira_field_mapping: Optional[
                ExcelDefinitionColumnJiraFieldMapping
            ] = column["jira_field_mapping"]

            # Check Name cannot be empty
            if len(column_name) == 0:
                invalid_definitions.append(
                    f"Column name cannot be empty. Index: {column_index}"
                )
                continue

            if standardize_column_name(column_name) in exist_column_names:
                invalid_definitions.append(
                    f"Column named {column_name} has been duplicated."
                )
                continue
            exist_column_names.append(standardize_column_name(column_name))

            if standardize_column_name(column_name) == standardize_column_name(
                "StoryId"
            ):
                exist_story_id_column = True

            # Check Missing/Duplicate Index
            if not isinstance(column_index, int):
                invalid_definitions.append(
                    f"Column Index can only be number. Column: {column_name}"
                )
            elif column_index is None:
                invalid_definitions.append(f"Missing Index. Column: {column_name}")
            elif column_index in exist_indexes:
                invalid_definitions.append(f"Duplicate Index. Column: {column_name}")
            else:
                exist_indexes.append(column_index)
            # Check Property Type
            if column_type not in (
                str,
                bool,
                datetime,
                Priority,
                Milestone,
                float,
            ):
                invalid_definitions.append(
                    f"Invalid Column Type. Column: {column_name}"
                )

            # Check Sort
            if not isinstance(column_require_sort, bool):
                invalid_definitions.append(
                    f"Require Sort can only be True/False. Column: {column_name}"
                )

            if not isinstance(column_sort_order, bool):
                invalid_definitions.append(
                    f"Sort Order can only be True(Descending)/False(Ascending). Column: {column_name}"
                )

            # Check Sort
            if not isinstance(column_scope_require_sort, bool):
                invalid_definitions.append(
                    f"Scope Require Sort can only be True/False. Column: {column_name}"
                )

            if not isinstance(column_scope_sort_order, bool):
                invalid_definitions.append(
                    f"Scope Sort Order can only be True(Descending)/False(Ascending). Column: {column_name}"
                )

            # Check InlineWeights
            if not isinstance(column_inline_weights, int):
                invalid_definitions.append(
                    f"Inline Weights can only be number. Column: {column_name}"
                )
            else:
                if column_type not in (Priority,) and column_inline_weights > 0:
                    invalid_definitions.append(
                        f"Column do not support Inline Weights. Currently only Priority type support. Column: {column_name}"
                    )
                if (
                    column_inline_weights > 0
                    and column_inline_weights in exist_inline_weights
                ):
                    invalid_definitions.append(
                        f"Duplicate Inline Weights. Currently only support different line weights. Column: {column_name}"
                    )
                exist_inline_weights.append(column_inline_weights)

            # Check RaiseRanking
            if not isinstance(column_raise_ranking, int):
                invalid_definitions.append(
                    f"Raise Ranking can only be number. Column: {column_name}"
                )
            else:
                # Check Support RaiseRanking or not
                if column_type not in (bool,) and column_raise_ranking > 0:
                    invalid_definitions.append(
                        f"Column do not support Raise Ranking feature. Column: {column_name}"
                    )

            if not isinstance(column_scope_raise_ranking, int):
                invalid_definitions.append(
                    f"Scope Raise Ranking can only be number. Column: {column_name}"
                )
            else:
                # Check Support RaiseRanking or not
                if column_type not in (bool,) and column_scope_raise_ranking > 0:
                    invalid_definitions.append(
                        f"Column do not support Scope Raise Ranking feature. Column: {column_name}"
                    )

            if column_jira_field_mapping is None:
                continue
            if column_jira_field_mapping is not None and not isinstance(
                column_jira_field_mapping, dict
            ):
                invalid_definitions.append(
                    f"Jira Field Mapping can only be dictionary. Column: {column_name}"
                )
            else:
                jira_field_name = column_jira_field_mapping.get("name", None)
                if jira_field_name is None or jira_field_name.isspace():
                    invalid_definitions.append(
                        f"Jira Field Mapping has the invalid name. Column: {column_name}"
                    )
                if jira_field_name in exist_jira_field_names:
                    invalid_definitions.append(
                        f"Column has duplicate jira field name. Name: {jira_field_name}, Column: {column_name}"
                    )
                exist_jira_field_names.append(jira_field_name)

                jira_field_path = column_jira_field_mapping.get("path", None)
                if jira_field_path is None or jira_field_path.isspace():
                    invalid_definitions.append(
                        f"Jira Field Mapping has the invalid path. Column: {column_name}"
                    )
                if jira_field_path in exist_jira_field_paths:
                    invalid_definitions.append(
                        f"Column has duplicate jira field path. Path: {jira_field_path}, Column: {column_name}"
                    )
                exist_jira_field_paths.append(jira_field_path)

        # If there is step name 'CreateJiraStory' or 'RetrieveJiraInformation'
        # or 'FilterOutStoryWithoutId', the StoryId must exist.
        if (
            (
                self.get_pre_process_step_by_name("CreateJiraStory")
                or self.get_pre_process_step_by_name("FilterOutStoryWithoutId")
                or self.get_pre_process_step_by_name("RetrieveJiraInformation")
            )
            and len(self.__columns) > 0
            and exist_story_id_column is False
        ):
            invalid_definitions.append(
                "Must have a column named StoryId so that program can identify the record."
            )

        if len(invalid_definitions) == 0:
            self.__columns.sort(key=lambda c: c["index"], reverse=False)

            if len(self.__columns) > 0 and (
                self.__columns[0]["index"] != 1
                or self.__columns[len(self.__columns) - 1]["index"]
                != len(self.__columns)
            ):
                invalid_definitions.append(
                    "Column Index must be in continuation and starts from 1."
                )

        return invalid_definitions

    @staticmethod
    def convert_str_to_type(type_str: str) -> Optional[type]:
        if type_str is None or not isinstance(type_str, str):
            return None
        type_str = strip_lower(type_str)
        if type_str == "str":
            return str
        if type_str == "bool":
            return bool
        if type_str == "datetime":
            return datetime
        if type_str == "priority":
            return Priority
        if type_str == "milestone":
            return Milestone
        # Currently, only support float/double
        if type_str == "number":
            return float
        return None

    def __iter__(self):
        yield from self.__columns

    def get_columns(self) -> "List[ExcelDefinitionColumn]":
        return deepcopy(self.__columns)

    def get_column_by_jira_field_mapping_name(
        self, name: str
    ) -> "List[ExcelDefinitionColumn]":
        result: List[ExcelDefinitionColumn] = []
        for item in self.__columns:
            jira_field_mapping = item.get("jira_field_mapping", None)
            if jira_field_mapping is not None and standardize_column_name(
                jira_field_mapping["path"].split(".")[0]
            ) == standardize_column_name(name):
                result.append(deepcopy(item))
        return result

    def get_columns_name(self, standardized: bool = True) -> "List[str]":
        if standardized:
            return [
                standardize_column_name(item.get("name", ""))
                for item in self.__columns
            ]
        return [item["name"] for item in self.__columns]

    @property
    def max_column_index(self) -> int:
        return self.__columns[len(self.__columns) - 1]["index"]

    @property
    def column_count(self) -> int:
        return len(self.__columns)

    def count_of_sort_strategies(self) -> int:
        return len(self.__sort_strategies)

    def get_sort_strategies(self, enabled: bool = True) -> "List[SortStrategy]":
        result: list[SortStrategy] = []
        for sort_strategy in self.__sort_strategies:
            if sort_strategy.enabled == enabled:
                result.append(deepcopy(sort_strategy))
        result.sort(key=ExcelDefinition.__sort_priority_map, reverse=False)
        return result

    def count_of_pre_process_steps(self) -> int:
        return len(self.__pre_process_steps)

    def get_pre_process_steps(self, enabled: bool = True) -> "List[PreProcessStep]":
        result: list[PreProcessStep] = []
        for pre_process_step in self.__pre_process_steps:
            if pre_process_step.enabled == enabled:
                result.append(deepcopy(pre_process_step))
        result.sort(key=ExcelDefinition.__sort_priority_map, reverse=False)
        return result

    def get_pre_process_step_by_name(
        self, step_name: str, enabled: bool = True
    ) -> "Optional[PreProcessStep]":
        for pre_process_step in self.__pre_process_steps:
            if (
                strip_lower(pre_process_step.name) == strip_lower(step_name)
                and pre_process_step.enabled == enabled
            ):
                return deepcopy(pre_process_step)
        return None

    @staticmethod
    def __sort_priority_map(item: BasicStep) -> int:
        return item.priority

    def total_count(self):
        return len(self.__columns)

    @property
    def version(self) -> int:
        return self.__version
