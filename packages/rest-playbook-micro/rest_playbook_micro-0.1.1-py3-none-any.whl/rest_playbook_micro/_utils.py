"""
Util repository
"""
import logging
import sys
import regex as re


from itertools import groupby


class utils():

    logging.basicConfig(
        format='%(asctime)s | %(levelname)s | %(message)s', level=logging.DEBUG)

    debug = False

    def _debug(self, message):
        if self.debug:
            logging.debug(str(message))

    def parse_vars_file(self, file: str) -> []:
        var_blocks = self._split_var_file(self.load_file(file))
        return list(map(self._split_var_file, var_blocks))

    def _split_var_file(self, e):
        split_row = str(e).split('=', 1)
        if len(split_row) == 2:
            return (f'%ENV_{split_row[0]}%', split_row[1])

    def find_mandatory(self, line: str) -> str:
        if line.startswith("%MANDATORY:") is False:
            return line
        x = re.findall(r"(%MANDATORY:ENV_[A-Z_0-9]+%)", line)
        var_to_find = f'%{str(x[0]).split(":")[1]}'
        filtered_list = filter(lambda c: c[0] == var_to_find, vars)
        filtered_list = list(filtered_list)
        if len(filtered_list) == 0:
            raise ValueError(f"Missing var {var_to_find}")
        return re.sub(r"(%MANDATORY:ENV_[A-Z_0-9]+%)", "", line)

    def find_optional(self, line: str) -> str:
        if line.startswith("%OPTIONAL:") is False:
            return line
        x = re.findall(r"(%OPTIONAL:ENV_[A-Z_0-9]+%)", line)
        var_to_find = f'%{str(x[0]).split(":")[1]}'
        filtered_list = filter(lambda c: c[0] == var_to_find, vars)
        filtered_list = list(filtered_list)
        if len(filtered_list) == 0:
            return ""
        return re.sub(r"(%OPTIONAL:ENV_[A-Z_0-9]+%)", "", line)

    def find_var(self, line: str) -> list:
        """Finds all the ENV variables in a provided string"""
        try:
            x = re.findall(r"(%ENV_[A-Z_0-9]+%)", line)
            return x
        except Exception as err:
            return []

    def set_properties(self, scenario_props: list) -> dict:
        props = {}
        for element in scenario_props:
            e = str(element).split('=', 1)
            props[e[0]] = e[1]
        return props

    def parse_scenario(self, entry: list, a: str, b: str) -> dict:
        properties = [list(g) for k, g in groupby(
            entry, key=lambda x: x != a and x != b) if k]
        # print(properties)
        return properties

    def split_scenario_file(self, file: str) -> list:
        raw_data = self.load_file(file)
        split_scenarios = [list(g) for k, g in groupby(
            raw_data, key=lambda x: x != "---") if k]
        return split_scenarios

    def read_file(self, file_name: str) -> list:
        """
        Uses a filepath + filename string to return a list of all
        the lines in the file, removes newlines in the strings
        """
        try:
            return_array = []
            open_file = file_name
            with open(open_file) as f:
                for line in f:
                    return_array.append(line.strip().replace('\n', ''))
            return return_array
        except Exception as err:
            self._debug(f"Error in readFileNoStrip {err=}, {type(err)=}")
            return []

    def load_file(self, file_name: str) -> list:
        file_data = self.read_file(file_name)
        if file_data is False:
            print('File invalid or not found')
            sys.exit()
        return file_data
