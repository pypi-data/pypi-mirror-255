
from itertools import groupby
from ._utils import utils
from ._scenario import Scenario as S
from ._variables import Variables as V
from ._result import Result as R


class Scenarios():

    scenarios: list[S] = []
    u: utils = utils()

    def __init__(self, scenario_file: str) -> None:
        self._parse_scenario_file(scenario_file)

    def _parse_scenario_file(self, file: str):
        scenario_blocks = self._split_scenario_file(file)
        self.scenarios = list(map(self._parse_block, scenario_blocks))

    def _split_scenario_file(self, file: str) -> list:
        raw_data = self.u.load_file(file)
        split_scenarios = [list(g) for k, g in groupby(
            raw_data, key=lambda x: x != "---") if k]
        return split_scenarios

    def _parse_block(self, entry: list):
        s = S()
        s.properties = self._parse_properties(
            self._parse_scenario(
                entry, "SCENARIO=", "=SCENARIO"
            )[0]
        )
        s.headers = self._parse_scenario(entry, "HEADER=", "=HEADER")[1]
        s.params = self._parse_scenario(entry, "PARAMS=", "=PARAMS")[1]
        s.body = self._parse_scenario(entry, "BODY=", "=BODY")[1]
        return s

    def _parse_properties(self, scenario_props: list) -> dict:
        props = {}
        for element in scenario_props:
            e = str(element).split('=', 1)
            props[e[0]] = e[1]
        return props

    def _parse_scenario(self, entry: list, a: str, b: str) -> dict:
        properties = [list(g) for k, g in groupby(
            entry, key=lambda x: x != a and x != b) if k]
        # print(properties)
        return properties

    def print(self):
        for s in self.scenarios:
            s.print()

    def list_scenarios(self) -> list[str]:
        return []

    def run_scenario(self, scenario_name: str, variables: V, return_body=False) -> R:
        for s in self.scenarios:
            if s.properties.get('NAME', None) == scenario_name:
                return s.run_scenario(variables,return_body=return_body)
        return R(response=f"{scenario_name} - Scenario not found")
