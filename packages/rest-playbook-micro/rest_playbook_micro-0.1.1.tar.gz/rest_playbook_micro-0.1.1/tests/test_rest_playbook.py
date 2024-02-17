from src.rest_playbook_micro.rest_playbook import RESTPlaybook as RP

def test_no_input():
    rp = RP(
        "",
        "",
        ""
    )
    results = rp.run_playbook()
    assert len(results) == 0

def test_missing_scenario():
    rp = RP(
        "tests/no_scenario.playbook",
        "",
        "tests/file_test.vars"
    )
    results = rp.run_playbook()
    assert len(results) == 3
    assert results[0].body == 'aa - Scenario not found'
    assert results[1].body == 'ab - Scenario not found'
    assert results[2].body == 'ac - Scenario not found'

def test_missing_playbook():
    rp = RP(
        "",
        "tests/simple_test.scenario",
        "tests/file_test.vars"
    )
    results = rp.run_playbook()
    assert len(results) == 0

def test_success_playbook():
    rp = RP(
        "tests/simple.playbook",
        "tests/simple_test.scenario",
        "tests/file_test.vars"
    )
    results = rp.run_playbook()
    assert len(results) == 3
    assert results[0].status == 200
    assert results[0].body == ''
    assert results[1].status == 201
    assert results[1].body == ''
    assert results[2].status == 200
    assert results[2].body.startswith('[{"id": 1, "name": "Company One"}, {"id": 2,')
