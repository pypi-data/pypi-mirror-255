#!/usr/bin/env python3.8
import argparse

from gitjudge.mapper.definition import load_definition
from gitjudge.entity import Repository, Validator

class GitJudge:
    def __init__(self, args):
        self.args = args
        self.definition = load_definition(args.definition_file)

    def validate(self, repo_dir):
        repo = Repository(repo_dir)
        validator = Validator(repo, self.definition)
        validator.validate()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("definition_file", help="Path to the definition file.")
    parser.add_argument("dir", nargs="+", help="Git Directory to validate.")
    # parser.add_argument("--verbose", action="store_true")
    # parser.add_argument("--remove-color", action="store_true", default=False)
    # parser.add_argument("-g", "--disable-git", action="store_true", default=False)
    # parser.add_argument("-i", "--interactive", action="store_true", default=False)
    # parser.add_argument("-v", "--volume", action="append", default=[])
    # parser.add_argument("--copy", action="store_true", default=False)
    # parser.add_argument("--save", nargs="?", default=False)
    # parser.add_argument("--light", help="Enables lightmode syntax highlighting",  action="store_true", default=False)
    args = parser.parse_args()

    gitjudge = GitJudge(args)
    for repo_dir in args.dir:
        gitjudge.validate(repo_dir)

if __name__ == '__main__':
    main()
