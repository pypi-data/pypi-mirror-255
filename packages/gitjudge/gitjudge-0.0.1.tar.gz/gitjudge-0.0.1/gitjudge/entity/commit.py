import re

class Commit:
    def __init__(self, id, message="", diff="", tags=[]):
        self.id = id
        self.message = message
        self.hash = ""
        self.committed_date = None
        self._diff = diff

        self.branches = []
        self.tags = tags
        self.parents = []


    def short_hash(self):
        return self.hash[:7]


    def short_message(self):
        return self.message.split("\n")[0]

    def __str__(self):
        args = []
        args.append(f"id={self.id}")
        if self.hash:
            args.append(f"hash={self.hash}")
        if self.message:
            args.append(f"message={self.message}")
        if self.branches:
            args.append(f"branches={self.branches}")
        if self.tags:
            args.append(f"tas={self.tags}")
        if self.parents:
            args.append(f"parents={self.parents}")
        return f"Commit({', '.join(args)})"


    def __repr__(self):
        return self.__str__()


    def show_diff(self, colored=True):
        print(self.diff(colored=colored))


    def diff(self, colored=False):
        if not colored:
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            return ansi_escape.sub('', self._diff)
        return self._diff


    def is_cherry_picked_from(self, other_commit):
        """
        Check if this commit is a cherry-pick of the given commit.

        There's no way to know for sure if a commit is a cherry-pick of another,
        but we can make an educated guess by comparing the diff of the two commits.
        If they are the same, then it's very likely that this commit is
        a cherry-pick of the given commit.

        Args:
            commit (Commit): The commit to check if this commit is a cherry-pick of.

        Returns:
            bool: True if this commit is a cherry-pick of the given commit, False otherwise.
        """
        if not self.diff() or not other_commit:
            return False
        return self.diff() == other_commit.diff()


    def reverts(self, commit):
        """
        Check if this commit reverts the given commit.

        There's no way to know for sure if a commit reverts another, but we can make
        an educated guess by comparing the diff of the two commits. If the diff of this
        commit contains the diff of the given commit with the signs inverted, then it's
        very likely that this commit reverts the given commit.

        Args:
            commit (Commit): The commit to check if this commit reverts.

        Returns:
            bool: True if this commit reverts the given commit, False otherwise.
        """
        self_diff_lines = set(self.diff().splitlines())
        commit_diff_lines = set(commit.diff().splitlines())

        expected_revert_lines = { \
                    "-" + line[1:] if line.startswith("+") \
                else \
                    "+" + line[1:] \
                for line in self_diff_lines \
                if line.startswith(("+", "-")) \
        }

        return expected_revert_lines <= commit_diff_lines

