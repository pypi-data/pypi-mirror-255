from gitjudge.entity import Commit, CheckResult

class ExpectedCommit:
    def __init__(self, id: str, message: str = None, starting_point: str = None):
        self.id = id
        self.message = message
        self.starting_point = starting_point

        self.parents = []
        self.branches = []
        self.tags = []

        self.checks = None

    def set_message(self, message):
        self.message = message

    def add_branch(self, branch):
        self.branches.append(branch)

    def add_tag(self, tag):
        self.tags.append(tag)

    def add_parent(self, parent):
        self.parents.append(parent)

    def __str__(self):
        args = []
        args.append(f"id={self.id}")
        if self.message:
            args.append(f"message={self.message}")
        if self.starting_point:
            args.append(f"starting_point={self.starting_point}")
        if self.parents:
            args.append(f"parents={self.parents}")
        if self.branches:
            args.append(f"branches={self.branches}")
        if self.tags:
            args.append(f"tags={self.tags}")
        if self.checks:
            args.append(f"checks={self.checks}")
        return f"ExpectedCommit({', '.join(args)})"

    def __repr__(self):
        return self.__str__()

    def validate(self, commit: Commit, found_commits: dict = {}) -> bool:
        if not isinstance(commit, Commit):
            raise TypeError("ExpectedCommit.validate requires a Commit object")

        if not isinstance(found_commits, dict):
            raise TypeError("ExpectedCommit.validate requires a dict object")

        if self.checks:
            return self.checks.validate(commit, found_commits)

        return CheckResult(commit)

