from datetime import datetime
import yaml

from gitjudge.entity.definition import Definition
from gitjudge.entity.expected_commit import ExpectedCommit
from gitjudge.mapper.expected_commit import map_expected_commit

def parse_date(date_str):
    formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M" ,"%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError("No valid date format found")


def map_definition(d: dict) -> Definition:
    name = d.get("name")
    if not name:
        raise TypeError("name is required in definition")

    definition = Definition(name)

    limit_date = d.get("limit_date")
    if limit_date:
        try:
            limit_date = parse_date(limit_date)
        except ValueError:
            raise TypeError("limit_date is not a valid date")
    definition.limit_date = limit_date

    expected_commits = []
    for id_commit, commit in d.get("commits", {}).items():
        expected_commit = map_expected_commit(id_commit, commit)
        expected_commits.append(expected_commit)
    definition.expected_commits = expected_commits

    return definition

def load_definition(file_path: str) -> Definition:
    """
    Load a definition from a YAML file

    :param file_path: The path to the file
    :return: The definition
    :raises: TypeError if the file is not a valid definition
    :raises: YAMLError if the file is not a valid YAML file
    :raises: FileNotFoundError if the file does not exist
    """
    with open(file_path, "r") as file:
        d = yaml.safe_load(file)
        return map_definition(d)
