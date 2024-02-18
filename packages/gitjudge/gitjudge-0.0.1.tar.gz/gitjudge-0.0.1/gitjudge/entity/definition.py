from datetime import datetime

class Definition:
    def __init__(self, name: str):
        self.name = name
        self.limit_date = None
        self.expected_commits = []

    def __str__(self):
        args = []

        args.append(f"name={self.name}")
        if self.limit_date:
            args.append(f"limit_date={self.limit_date}")
        if self.expected_commits:
            args.append(f"expected_commits={self.expected_commits}")
        return f"Definition({', '.join(args)})"

    def __repr__(self):
        return self.__str__()
