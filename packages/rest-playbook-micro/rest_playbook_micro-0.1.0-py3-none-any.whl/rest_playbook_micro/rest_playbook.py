"""
Module providing RESTClient class
"""
import os

from pathlib import Path
from ._scenarios import Scenarios as S
from ._variables import Variables as V
from ._playbook import Playbook as P
from ._result import Result as R


class RESTPlaybook():
    """Top level class for running playbooks, manages the orchestration
    of each file
    """
    app_name: str = 'rest_playbook_micro'
    config_dir: str = os.path.join(
        str(Path.home()),
        ".config/",
        app_name
    )

    scenario_file: str = ''
    var_file: str = ''
    playbook_file: str = ''

    scenarios: S
    variables: V
    playbook: P

    def __init__(self, p_file: str, s_file: str, v_file: str) -> None:
        self.set_scenario_file(s_file)
        self.set_var_file(v_file)
        self.set_playbook_file(p_file)

    def set_playbook_file(self, playbook_file: str) -> None:
        self.playbook_file = playbook_file
        self.generate_playbook(self.playbook_file)

    def generate_playbook(self, playbook_file: str) -> None:
        self.playbook = P(playbook_file)

    def set_scenario_file(self, scenario_file: str) -> None:
        self.scenario_file = scenario_file
        self.generate_scenarios(self.scenario_file)

    def set_var_file(self, var_file: str) -> None:
        self.var_file = var_file
        self.generate_variables(self.var_file)

    def generate_variables(self, var_file: str) -> None:
        self.variables = V(var_file)

    def generate_scenarios(self, scenario_file: str) -> None:
        self.scenarios = S(scenario_file)

    def run_scenario(self, scenario_name: str) -> R:
        return self.scenarios.run_scenario(
            scenario_name, self.variables
        )
    
    def run_playbook(self) -> list[R]:
        return self.playbook.run(self.scenarios, self.variables)

    def print(self) -> None:
        self.scenarios.print()
        self.variables.print()
