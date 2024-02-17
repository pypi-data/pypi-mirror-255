"""
Private module providing Scenario class
"""

import regex as re

from rest_client_micro.rest_client import RESTClient as rc
from rest_client_micro.rest_object import RESTObject as ro

from ._result import Result as R
from ._utils import utils
from ._variables import Variables as V


class Scenario():

    properties: dict
    headers: list
    params: list
    body: list
    raw_body: list
    u: utils = utils()

    def __init__(self) -> None:
        self.properties = {}
        self.headers = []
        self.params = []
        self.body = []
        self.raw_body = []

    def run_scenario(self, variables: V, return_body=False) -> R:
        # print(f"Running {self.properties['NAME']}")
        self.apply_variables_body(variables)
        client = rc()
        # client.debug = True
        rest_object = ro()
        rest_object.endpoint = self.properties.get(
            'ENDPOINT', 'localhost:3000')
        rest_object.payload = self.get_raw_body()
        rest_result = client.execute(rest_object)
        if rest_result.error:
            result = R(response=rest_result.error_text)
        else:
            result = R(response=rest_result.response, status=rest_result.status)
        if return_body:
            result.outbound = rest_result.outbound
        return result

    def apply_variables_body(self, v: V):
        for line in self.body:
            new_line = line
            # new_line = self._find_mandatory(new_line, v)
            new_line = self.find_optional(new_line, v)
            if len(new_line) == 0:
                continue
            line_vars = self.u.find_var(line)
            if len(line_vars) == 0:
                self.raw_body.append(new_line)
                continue
            # print(line_vars)
            self.raw_body.append(self._generate_line(new_line, v.variables))

    def _find_mandatory(self, line: str, v: V) -> str:
        if line.startswith("%MANDATORY:") is False:
            return line
        x = re.findall(r"(%MANDATORY:ENV_[A-Z_0-9]+%)", line)
        var_to_find = f'%{str(x[0]).split(":")[1]}'
        filtered_list = filter(lambda c: f"%ENV_{c.name}%" == var_to_find, v.variables)
        filtered_list = list(filtered_list)
        if len(filtered_list) == 0:
            raise ValueError(f"Missing var {var_to_find}")
        return re.sub(r"(%MANDATORY:ENV_[A-Z_0-9]+%)", "", line)

    def find_optional(self, line: str, v: V) -> str:
        if line.startswith("%OPTIONAL:") is False:
            return line
        
        x = re.findall(r"(%OPTIONAL:ENV_[A-Z_0-9]+%)", line)
        var_to_find = f'%{str(x[0]).split(":")[1]}'
        filtered_list = filter(lambda c: f"%ENV_{c.name}%" == var_to_find, v.variables)
        filtered_list = list(filtered_list)
        if len(filtered_list) == 0:
            return ""
        return re.sub(r"(%OPTIONAL:ENV_[A-Z_0-9]+%)", "", line)

    def _generate_line(self, line: str, variables: list[V]) -> str:
        line_vars = self.u.find_var(line)
        if len(line_vars) == 0:
            return line
        for v in variables:
            if f"%ENV_{v.name}%" in line_vars:
                line = line.replace(f"%ENV_{v.name}%", v.value)
                break
        for v in line_vars:
            if v in line:
                line = line.replace(v, "")
        return line

    def get_raw_body(self) -> str:
        return "".join(self.raw_body)

    def get_body(self) -> str:
        return "".join(self.body)

    def print(self) -> None:
        print(
            f"""--
            {self.properties}
{self.headers}
{self.params}
{self.get_raw_body()}
{self.get_body()}
--"""
        )
