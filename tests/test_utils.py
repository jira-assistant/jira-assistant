from jira_assistant.utils import parse_index_range


def test_parse_index_range():
    result = parse_index_range("1-3")
    assert result is not None
    assert len(result) == 3
    assert 1 in result
    assert 2 in result
    assert 3 in result

    result = parse_index_range("1,3, 5")
    assert result is not None
    assert len(result) == 3
    assert 1 in result
    assert 3 in result
    assert 5 in result


def test_parse_index_range_invalid_cases():
    result = parse_index_range("")
    assert result is None

    result = parse_index_range("abc")
    assert result is None
