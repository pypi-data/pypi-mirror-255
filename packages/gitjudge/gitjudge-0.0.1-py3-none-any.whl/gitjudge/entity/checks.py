from gitjudge.entity import Commit, CheckResult

class Checks:
    def __init__(self):
        self.tags = []
        self.branches = []
        self.cherry_pick = None
        self.reverts = None

    def __str__(self):
        args = []
        if self.tags:
            args.append(f"tags={self.tags}")
        if self.branches:
            args.append(f"branches={self.branches}")
        if self.cherry_pick:
            args.append(f"cherry_pick={self.cherry_pick}")
        if self.reverts:
            args.append(f"reverts={self.reverts}")
        return f"Checks({', '.join(args)})"

    def __repr__(self):
        return self.__str__()

    def validate(self, commit: Commit, found_commits:dict = {}) -> bool:
        check_result = CheckResult(commit)
        if not isinstance(commit, Commit):
            raise TypeError("Checks.validate requires a Commit object")

        if self.tags:
            for tag in self.tags:
                tag_present = tag in commit.tags
                check_result.add_tag(tag, tag_present)

        if self.cherry_pick:
            referenced_commit = found_commits.get(self.cherry_pick)
            is_cherry_picked = commit.is_cherry_picked_from(referenced_commit)
            check_result.set_cherry_picked(referenced_commit, is_cherry_picked)

        if self.reverts:
            referenced_commit = found_commits.get(self.reverts)
            is_reverted = commit.reverts(referenced_commit)
            check_result.set_reverted(referenced_commit, is_reverted)

        return check_result
