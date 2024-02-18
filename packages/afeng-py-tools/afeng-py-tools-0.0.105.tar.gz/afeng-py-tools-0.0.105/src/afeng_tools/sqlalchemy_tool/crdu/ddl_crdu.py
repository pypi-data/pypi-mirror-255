import re


def create_table(sql):
    if re.findall(r"CREATE (\w+)", sql) in ["SEQUENCE", "TABLE"]:
        pass
    raise NotImplementedError


def drop_table(sql):
    if re.findall(r"DROP (\w+)", sql) in ["SEQUENCE", "TABLE"]:
        pass
    raise NotImplementedError


