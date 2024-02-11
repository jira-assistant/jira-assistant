# -*- coding: utf-8 -*-
from decimal import Decimal

from pytest import raises
from jira_assistant.excel_definition import SortStrategy

from jira_assistant.story import (
    compare_story_based_on_inline_weights,
    convert_to_bool,
    convert_to_datetime,
    convert_to_decimal,
    sort_stories_by_property_and_order,
    sort_stories_by_raise_ranking,
)
from tests.utils import (
    mock_story_data,
    mock_story_data_for_property_sorting,
    mock_story_data_for_property_sorting_consider_parent_index,
    mock_story_data_for_raise_ranking,
)


def test_compare_story_based_on_inline_weight():
    data, _ = mock_story_data()
    s_1 = data[0]
    s_2 = data[1]
    s_3 = data[2]
    s_4 = data[3]
    s_5 = data[4]
    s_6 = data[5]
    s_7 = data[6]
    s_8 = data[7]
    s_9 = data[8]
    assert compare_story_based_on_inline_weights(s_1, s_2) < 0
    assert compare_story_based_on_inline_weights(s_1, s_3) < 0
    assert compare_story_based_on_inline_weights(s_2, s_3) < 0
    assert compare_story_based_on_inline_weights(s_3, s_5) < 0
    assert compare_story_based_on_inline_weights(s_2, s_5) < 0
    assert compare_story_based_on_inline_weights(s_4, s_5) < 0
    assert compare_story_based_on_inline_weights(s_1, s_5) < 0
    assert compare_story_based_on_inline_weights(s_6, s_7) < 0
    assert compare_story_based_on_inline_weights(s_8, s_9) < 0


def test_compare_story_property():
    data, _ = mock_story_data()
    s_8 = data[7]
    s_9 = data[8]
    assert s_8["name"] < s_9["name"]
    assert s_8["productValue"] < s_9["productValue"]


def test_str():
    data, _ = mock_story_data()

    assert "s1, N/A" in str(data[0])


def test_lt_le_gt_ge_eq():
    data, _ = mock_story_data()
    s_1 = data[0]
    s_2 = data[1]

    with raises(TypeError):
        assert s_1 < s_2
    with raises(TypeError):
        assert s_1 <= s_2
    with raises(TypeError):
        assert s_1 > s_2
    with raises(TypeError):
        assert s_1 >= s_2
    with raises(TypeError):
        assert s_1 == s_2


def test_convert_to_bool_using_correct_type():
    assert convert_to_bool(True) is True


def test_convert_to_decimal():
    assert Decimal.compare(convert_to_decimal(Decimal(1.2)), Decimal(1.2)) == Decimal(
        "0"
    )
    assert Decimal.compare(convert_to_decimal("1.2"), Decimal("1.2")) == Decimal("0")
    assert Decimal.compare(convert_to_decimal("good"), Decimal(0)) == Decimal("0")


def test_convert_to_datetime():
    assert convert_to_datetime(None) is None


def test_sort_stories_by_property_and_order():
    stories, factory = mock_story_data_for_property_sorting()

    sort_stories_by_property_and_order(stories, factory.columns, None)

    assert len(stories) == 2
    assert stories[0]["name"] == "s2"
    assert stories[1]["name"] == "s1"


def test_sort_stories_by_property_and_order_consider_parent_index():
    stories, factory = mock_story_data_for_property_sorting_consider_parent_index()

    sort_stories_by_property_and_order(
        stories,
        factory.columns,
        SortStrategy("SortOrder", True, 1, {"ParentScopeIndexRange": "2, 5"}),
    )

    assert len(stories) == 2
    assert stories[0]["name"] == "s1"
    assert stories[1]["name"] == "s2"


def test_sort_stories_by_raise_ranking():
    stories, factory = mock_story_data_for_raise_ranking()

    result = sort_stories_by_raise_ranking(stories, factory.columns, None)

    assert len(result) == 2
    assert result[0]["name"] == "s2"
    assert result[1]["name"] == "s1"
