


from itertools import groupby
from ._utils import utils
from ._play import Play as P
from ._result import Result as R
from ._scenarios import Scenarios as S
from ._variables import Variables as V


class Playbook():
    """Parent playbook class, manages each of the steps provided
    """

    plays: list[P]
    u: utils = utils()

    def __init__(self, playbook_file: str = None) -> None:
        self._parse_playbook_file(playbook_file)
        self.step = None

    def _parse_playbook_file(self, file: str):
        self.plays = self._parse_play_list(file)

    def _parse_play_list(self, file:str):
        playbook_blocks = self._split_playbook_file(file)
        return list(map(self._parse_block, playbook_blocks))


    def _split_playbook_file(self, file: str) -> list:
        raw_data = self.u.load_file(file)
        split_scenarios = [list(g) for k, g in groupby(
            raw_data, key=lambda x: x != "----") if k]
        return split_scenarios

    def _parse_block(self, entry: list):
        p = P()
        props = self.u.set_properties(entry)
        if props.get('NAME', None) is None:
            raise ValueError("Play is missing NAME")
        p.NAME = props.get('NAME')
        p.WAIT = int(props.get('WAIT', 30))
        p.STEP = props.get('STEP')
        p.ASSERT = props.get('ASSERT')
        p.NEXT_STEP = props.get('NEXT_STEP',None)

        return p

    def run(self, scenarios: S, variables: V) -> list[R]:
        ret_val = []
        for p in self.plays:
            ret_val.append(p.run(scenarios, variables))
        return ret_val
