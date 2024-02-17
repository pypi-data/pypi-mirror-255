import re


def pascal_to_snake_case(string: str) -> str:
    return "_".join(re.findall("[A-Z]{1}[a-z]*", string)).lower()
