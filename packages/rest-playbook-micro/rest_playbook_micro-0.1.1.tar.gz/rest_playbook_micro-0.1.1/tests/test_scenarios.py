from src.rest_playbook_micro._scenarios import Scenarios as S
from src.rest_playbook_micro._variables import Variables as V


def test_scenario_mandatory_var():
    s = S("tests/scenario_substitute.scenario")
    v = V("tests/mandatory_test.vars")
    result = s.run_scenario("ae", v, True)
    assert result.body == ''


def test_scenario_optional_var():
    s = S("tests/scenario_substitute.scenario")
    v = V("tests/file_test.vars")
    result = s.run_scenario("ad", v, True)
    assert result.body == ''
    assert result.outbound == '{"order_id":"ORDER001","optional_property":"SERVICEORDER001"}'
    s = S("tests/scenario_substitute.scenario")
    v = V("tests/optional_test.vars")
    result = s.run_scenario("ad", v, True)
    assert result.body == ''
    asset_text = '{"order_id":"ORDER001","optional_property":"SERVICEORDER001","optional_property2":"SERVICEORDER002"}'
    assert result.outbound == asset_text


def test_scenario_missing_var():
    s = S("tests/scenario_substitute.scenario")
    v = V("tests/file_test.vars")
    result = s.run_scenario("ac", v, True)
    assert result.body == ''
    assert result.outbound == '{"order_id":"ORDER001","missing_property":""}'


def test_scenario_substitute():
    s = S("tests/scenario_substitute.scenario")
    v = V("tests/file_test.vars")
    result = s.run_scenario("aa", v, True)
    assert result.body == ''
    assert result.outbound == '{"order_id":"ORDER001"}'
    result = s.run_scenario("ab", v, True)
    assert result.body == ''
    assert result.outbound == '{"order_id":"ORDER001","untouched_property":"123TEST321"}'


def test_error_scenarios():
    s = S("tests/file_test.scenario")
    v = V("tests/file_test.vars")
    result = s.run_scenario("ab", v)
    assert result.body == ''


def test_success_scenarios():
    s = S("tests/file_test.scenario")
    v = V("tests/file_test.vars")
    result = s.run_scenario("ac", v)
    assert result.body is not None
    assert result.body.startswith('[{"id": 1, "name": "Company One"}')
