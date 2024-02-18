from gitjudge.entity import Definition, Repository
from gitjudge.formatter.stdout import print_commit, print_expected_commit

from colorama import Fore, Style

class Validator:
    def __init__(self, repo, definition):
        if not isinstance(repo, Repository):
            raise ValueError(f"Expected Repository, got {type(repo)}")
        self.repo = repo

        if not isinstance(definition, Definition):
            raise TypeError(f"Expected Definition, got {type(definition)}")
        self.definition = definition
        self.found_commits = {}

    def validate(self):
        for expected_commit in self.definition.expected_commits:
            # print(expected_commit)
            print(f"{Fore.CYAN}Validating commit {expected_commit.id}{Fore.RESET}")
            commit = self.repo.find_commit(expected_commit)
            if not commit:
                print(f"{Fore.RED}Commit {expected_commit.id} not found in repository{Fore.RESET}")
                print_expected_commit(expected_commit)
                print()
                continue

            self.found_commits[expected_commit.id] = commit
            check_result = expected_commit.validate(commit, self.found_commits)
            print_commit(commit, check_result)

            print()

        min_id = min(self.found_commits.keys())
        first_commit = self.found_commits[min_id]
        max_id = max(self.found_commits.keys())
        last_commit = self.found_commits[max_id]

        print("# Repository log:")
        self.repo.print_log(start=first_commit, end=last_commit)
