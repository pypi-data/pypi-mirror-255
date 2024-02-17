from src.rest_playbook_micro._variables import Variables as VS
from src.rest_playbook_micro._variable import Variable as V


def test_variable():
    v = V(name="NAME", value="VALUE")
    assert v.name == "NAME"


def test_variables():
    v = VS("./tests/file_test.vars")
    assert v.variables[0].name == "PAGE"
    assert v.variables[0].value == "1"
    assert v.variables[2].name == "SERVICE_ID"
    assert v.variables[2].value == "SERVICEORDER001"
    assert v.variables[3].name == "DOUBLE_EQUALS"
    assert v.variables[3].value == "123=456===ABC"
