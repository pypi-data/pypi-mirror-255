from src.rest_playbook_micro._playbook import Playbook as P


def test_parse_play_list():
    p = P()
    plays = p._parse_play_list("tests/file_test.playbook")
    assert len(plays) == 3
    assert plays[0].NAME == "aa"
    assert plays[1].WAIT == 1
    assert plays[1].STEP == "2"
    assert plays[1].NEXT_STEP is '3'


def test_playbook():
    p = P("tests/file_test.playbook")
    assert len(p.plays) == 3
