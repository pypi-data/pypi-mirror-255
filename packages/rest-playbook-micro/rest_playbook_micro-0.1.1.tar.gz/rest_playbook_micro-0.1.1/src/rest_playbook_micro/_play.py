import time
from ._result import Result as R
from ._scenarios import Scenarios as S
from ._variables import Variables as V


class Play():
    """
    Invidual step in a playbook, does not have direct knowledge of the
    scenario it relates to, but instead a unique reference to a name.
    Manages parsing of the response and time to the next step
    """

    NAME: str
    WAIT: int
    ASSERT: str
    STEP: int
    RETURN_BODY: bool
    result: R
    scenario: S

    def __init__(self, return_body=False) -> None:
        self.RETURN_BODY = return_body
        pass

    def run(self, scenarios: S, variables: V) -> R:
        ret_val = scenarios.run_scenario(
            self.NAME, variables, return_body=self.RETURN_BODY)
        time.sleep(self.WAIT)
        return ret_val
