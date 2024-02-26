# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
from pytest import raises

from jira_assistant.excel_definition import (
    ExcelDefinition,
    PreProcessStep,
    parse_json_item_to_pre_process_step,
    parse_json_item_to_sort_strategy,
)

from . import ASSETS_FILES


def test_pre_process_step():
    step = PreProcessStep("a", True, 1, None)
    step.name = "abc"
    assert step.name == "abc"
    step.enabled = False
    assert step.enabled is False
    step.priority = 2
    assert step.priority == 2
    step.config = {"key": "value"}
    assert step.config is not None


def test_parse_json_item_to_pre_process_step_invalid_name():
    with raises(ValueError) as err:
        parse_json_item_to_pre_process_step(
            {"Priority": 1, "Name": None, "Enabled": False, "Config": {}}
        )
    assert "The Name property in the pre-process step is invalid." in str(err.value)


def test_parse_json_item_to_pre_process_step_invalid_enabled():
    step = parse_json_item_to_pre_process_step(
        {"Priority": 1, "Name": "abc", "Enabled": "abc", "Config": {}}
    )
    assert step.enabled is False


def test_parse_json_item_to_pre_process_step_invalid_priority():
    with raises(ValueError) as err:
        parse_json_item_to_pre_process_step(
            {"Priority": None, "Name": "abc", "Enabled": False, "Config": {}}
        )
    assert "The Priority property in the pre-process step is invalid." in str(err.value)


def test_parse_json_item_to_sort_strategy_invalid_name():
    with raises(ValueError) as err:
        parse_json_item_to_sort_strategy(
            {"Priority": 1, "Name": None, "Enabled": False, "Config": {}}
        )
    assert "The Name property in the sort strategy is invalid." in str(err.value)


def test_parse_json_item_to_sort_strategy_invalid_enabled():
    strategy = parse_json_item_to_sort_strategy(
        {"Priority": 1, "Name": "abc", "Enabled": "abc", "Config": {}}
    )
    assert strategy.enabled is False


def test_parse_json_item_to_sort_strategy_invalid_priority():
    with raises(ValueError) as err:
        parse_json_item_to_sort_strategy(
            {"Priority": None, "Name": "abc", "Enabled": False, "Config": {}}
        )
    assert "The Priority property in the sort strategy is invalid." in str(err.value)


def test_load_happy_path():
    excel_definition_filename = ASSETS_FILES / "excel_definition.json"

    store = ExcelDefinition()
    with open(excel_definition_filename, encoding="utf-8") as file:
        store.load(file.read())
    assert store.total_count() > 0


def test_load_file():
    excel_definition_filename = ASSETS_FILES / "excel_definition.json"
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)
    assert store.total_count() > 0


def test_load_file_none():
    store = ExcelDefinition()
    file: str = None  # type: ignore
    with raises(FileNotFoundError) as err:
        store.load_file(file)
    assert (
        "Please make sure the excel definition file exist and the path should be absolute"
        in str(err.value)
    )


def test_iter():
    excel_definition_filename = ASSETS_FILES / "excel_definition.json"
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)
    items = []
    for item in store:
        items.append(item)
    assert len(items) > 0


def test_validate():
    excel_definition_filename = ASSETS_FILES / "excel_definition.json"
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 0


def test_validate_missing_story_id():
    excel_definition_filename = ASSETS_FILES / "excel_definition_missing_story_id.json"
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 1


def test_validate_duplicate_index():
    excel_definition_filename = ASSETS_FILES / "excel_definition_duplicate_index.json"
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 1


def test_validate_duplicate_jira_field():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_duplicate_jira_field.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 2


def test_validate_duplicate_column_name():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_duplicate_column_name.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 1


def test_validate_duplicate_inline_weights():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_duplicate_inline_weights.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 3
    assert (
        "Column do not support Inline Weights. Currently only Priority type support. Column: Entry/Last Updated Date"
        in validation_result
    )
    assert (
        "Column do not support Inline Weights. Currently only Priority type support. Column: productManager"
        in validation_result
    )
    assert (
        "Duplicate Inline Weights. Currently only support different line weights. Column: productManager"
        in validation_result
    )


def test_validate_invalid_name():
    excel_definition_filename = ASSETS_FILES / "excel_definition_invalid_name.json"
    store = ExcelDefinition()
    with raises(SyntaxError) as err:
        store.load_file(excel_definition_filename)

    assert (
        "The excel definition file has below issues need to be fixed"
        in err.value.args[0]
    )
    assert (
        "The Name property type in the column definition should be string."
        in err.value.args[0]
    )


def test_validate_invalid_raise_ranking():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_invalid_raise_ranking.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 1


def test_validate_invalid_require_sort():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_invalid_require_sort.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 2


def test_validate_invalid_type():
    excel_definition_filename = ASSETS_FILES / "excel_definition_invalid_type.json"
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 2


def test_validate_invalid_index():
    excel_definition_filename = ASSETS_FILES / "excel_definition_invalid_index.json"
    store = ExcelDefinition()
    with raises(SyntaxError) as err:
        store.load_file(excel_definition_filename)

    assert (
        "The excel definition file has below issues need to be fixed"
        in err.value.args[0]
    )
    assert (
        "The Index property type in the column definition is not integer."
        in err.value.args[0]
    )


def test_validate_index_not_continuation():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_index_not_continuation.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 1


def test_validate_strategy_duplicate_priority():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_strategy_duplicate_priority.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 1


def test_validate_strategy_invalid_name():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_strategy_invalid_name.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 1


def test_validate_invalid_json():
    excel_definition_filename = ASSETS_FILES / "excel_definition_invalid_json.txt"
    store = ExcelDefinition()

    with raises(Exception) as err:
        store.load_file(excel_definition_filename)

    assert (
        "The structure of excel definition file is wrong. Hint: Expecting ',' delimiter in line 49:1"
        in err.value.args[0]
    )


def test_validate_invalid_pre_process_step_name():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_invalid_pre_process_step_name.json"
    )
    store = ExcelDefinition()

    with raises(SyntaxError) as err:
        store.load_file(excel_definition_filename)

    assert (
        "The excel definition file has below issues need to be fixed"
        in err.value.args[0]
    )
    assert "The Name property in the pre-process step is invalid." in err.value.args[0]


def test_validate_invalid_pre_process_step_priority():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_invalid_pre_process_step_priority.json"
    )
    store = ExcelDefinition()

    store.load_file(excel_definition_filename)
    validation_result = store.validate()

    assert len(validation_result) == 1


def test_validate_strategy_duplicate_column_story_id():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_duplicate_column_story_id.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert len(validation_result) == 4
    assert "Column named storyId has been duplicated." in validation_result
    assert (
        "Column do not support Inline Weights. Currently only Priority type support. Column: Entry/Last Updated Date"
        in validation_result
    )
    assert (
        "Column do not support Inline Weights. Currently only Priority type support. Column: productManager"
        in validation_result
    )
    assert (
        "Column do not support Inline Weights. Currently only Priority type support. Column: storyId"
        in validation_result
    )


def test_validate_create_jira_story_missing_project_type():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_create_jira_story_missing_project_type.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert (
        "The PreProcessStep: CreateJiraStory must have a column named ProjectType."
        in validation_result[0]
    )


def test_validate_create_jira_story_missing_issue_type():
    excel_definition_filename = (
        ASSETS_FILES / "excel_definition_create_jira_story_missing_issue_type.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert (
        "The PreProcessStep: CreateJiraStory must have a column named IssueType."
        in validation_result[0]
    )


def test_validate_filter_out_story_based_on_jira_status_missing_status():
    excel_definition_filename = (
        ASSETS_FILES
        / "excel_definition_filter_out_story_based_on_jira_status_missing_status.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert (
        "The PreProcessStep: FilterOutStoryBasedOnJiraStatus must have a column named Status."
        in validation_result[0]
    )


def test_validate_filter_out_story_based_on_jira_status_missing_pre_step():
    excel_definition_filename = (
        ASSETS_FILES
        / "excel_definition_filter_out_story_based_on_jira_status_missing_pre_step.json"
    )
    store = ExcelDefinition()
    store.load_file(excel_definition_filename)

    validation_result = store.validate()

    assert (
        "The step named RetrieveJiraInformation must be processed before FilterOutStoryBasedOnJiraStatus."
        in validation_result[0]
    )
