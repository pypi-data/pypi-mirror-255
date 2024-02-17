
from ._variable import Variable as V
from._utils import utils

class Variables():

    var_file: str

    u = utils()
    variables: list[V]

    def __init__(self, var_file: str) -> None:
        self.set_variables(var_file)

    def set_variables(self, var_file: str) -> None:
        self.var_file = var_file
        self._parse_var_file(self.var_file)

    def _parse_var_file(self, file: str) -> None:
        var_blocks = self._split_var_file(file)
        self.variables = list(map(self._parse_block, var_blocks))

    def _parse_block(self, block: str):
        block = block.split('=',1)
        v = V()
        v.name = block[0]
        v.value = block[-1]
        return v

    def _split_var_file(self, file) -> list:
        return self.u.load_file(file)

    def print(self) -> None:
        for v in self.variables:
            v.print()