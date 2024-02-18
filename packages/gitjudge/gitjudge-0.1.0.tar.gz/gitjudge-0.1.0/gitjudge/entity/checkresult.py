from enum import Enum, auto

from gitjudge.entity import Commit

class CherryPickState(Enum):
    NO_CHERRYPICK_CHECK = auto()
    CHERRYPICK_COMMIT_NOT_FOUND = auto()
    NO_CHERRYPICKED = auto()
    CHERRYPICKED = auto()

class RevertState(Enum):
    NO_REVERT_CHECK = auto()
    REVERT_COMMIT_NOT_FOUND = auto()
    NO_REVERTED = auto()
    REVERTED = auto()


class CheckResult:
    def __init__(self, commit):
        self.commit = commit
        if not isinstance(commit, Commit):
            raise TypeError("CheckResult must be initialized with a Commit object.")

        self.tags = {}

        """
        cherry_picked_from_commit is the commit that was cherry-picked from.
        checked_cherry_status is a CherryPickState indicating the state of the cherry-pick check.
        """
        self.cherry_picked_from_commit = None
        self.checked_cherry_status = CherryPickState.NO_CHERRYPICK_CHECK

        """
        reverted_from_commit is the commit that was reverted from.
        checked_revert_status is a RevertState indicating the state of the revert check.
        """
        self.reverted_from_commit = None
        self.checked_revert_status = RevertState.NO_REVERT_CHECK


    def __str__(self):
        args = []
        args.append(f"commit={self.commit}")
        if self.tags:
            args.append(f"tags={self.tags}")

        args.append(f"checked_cherry_status={self.checked_cherry_status}")
        if self.has_checked_cherry_pick():
            args.append(f"cherry_picked_from_commit={self.cherry_picked_from_commit}")


        args.append(f"checked_revert_status={self.checked_revert_status}")
        if self.has_checked_revert():
            args.append(f"reverted_from_commit={self.reverted_from_commit}")
        return f"CheckResult({', '.join(args)})"

    def __repr__(self):
        return self.__str__()


    def has_found_cherry_pick_commit(self):
        return self.checked_cherry_status in [
            CherryPickState.NO_CHERRYPICKED,
            CherryPickState.CHERRYPICKED
        ]

    def set_cherry_picked(self, commit, is_cherry_picked):
        if not commit:
            self.checked_cherry_status = CherryPickState.CHERRYPICK_COMMIT_NOT_FOUND
        elif not is_cherry_picked:
            self.cherry_picked_from_commit = commit
            self.checked_cherry_status = CherryPickState.NO_CHERRYPICKED
        else:
            self.cherry_picked_from_commit = commit
            self.checked_cherry_status = CherryPickState.CHERRYPICKED

    def has_checked_cherry_pick(self):
        return self.checked_cherry_status in [
            CherryPickState.CHERRYPICK_COMMIT_NOT_FOUND,
            CherryPickState.NO_CHERRYPICKED,
            CherryPickState.CHERRYPICKED
        ]

    def is_cherry_picked(self):
        return self.checked_cherry_status == CherryPickState.CHERRYPICKED


    def has_found_reverted_commit(self):
        return self.checked_revert_status in [
            RevertState.REVERTED,
            RevertState.NO_REVERTED

        ]

    def set_reverted(self, commit, is_reverted):
        if not commit:
            self.checked_revert_status = RevertState.REVERT_COMMIT_NOT_FOUND
        elif not is_reverted:
            self.reverted_from_commit = commit
            self.checked_revert_status = RevertState.NO_REVERTED
        else:
            self.reverted_from_commit = commit
            self.checked_revert_status = RevertState.REVERTED

    def has_checked_revert(self):
        return self.checked_revert_status in [
            RevertState.REVERT_COMMIT_NOT_FOUND,
            RevertState.NO_REVERTED,
            RevertState.REVERTED
        ]

    def is_reverted(self):
        return self.checked_revert_status == RevertState.REVERTED

    def add_tag(self, tag, present):
        self.tags[tag] = present

    def is_correct(self):
        correct = True
        correct = correct and all(self.tags.values())
        if self.has_checked_cherry_pick():
            correct = correct and self.is_cherry_picked()
        if self.has_checked_revert():
            correct = correct and self.is_reverted()
        return correct
