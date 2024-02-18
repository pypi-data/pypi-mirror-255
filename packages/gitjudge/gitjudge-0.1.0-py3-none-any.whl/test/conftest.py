import pytest
import os
from pathlib import Path

from gitjudge.entity.repository import Repository
from gitjudge.entity.definition import Definition
from gitjudge.entity.expected_commit import ExpectedCommit

@pytest.fixture()
def empty_repo(tmp_path):
    d = tmp_path / "empty_repository"
    d.mkdir()
    os.system(f"git init {d}")
    return Repository(d)

@pytest.fixture()
def repo(tmp_path):
    d = tmp_path / "repository"
    d.mkdir()
    os.system(f"git init {d}")
    repo = Repository(d)

    Path.touch(repo.directory_path / "file1.md")
    repo.repo.git.add('--all')
    repo.repo.git.commit(m="1. added file1.md")
    repo.repo.git.tag("T1")

    repo.repo.git.branch("-m", "main")

    with open(repo.directory_path / "file1.md", "a") as f:
        f.write("# Populated repo")
    repo.repo.git.add('--all')
    repo.repo.git.commit(m="2. modified file1.md")
    repo.repo.git.tag("T2")
    repo.repo.git.tag("T3")

    repo.repo.git.checkout("-b", "branch1")
    Path.touch(repo.directory_path / "branch1.md")
    repo.repo.git.add('--all')
    repo.repo.git.commit(m="3. added branch1.md")


    repo.repo.git.checkout("main")
    return repo

@pytest.fixture()
def definition():
    definition = Definition("test-definition")
    definition.expected_commits = [
        ExpectedCommit(id="1", message="1."),
        ExpectedCommit(id="2", message="2."),
        ExpectedCommit(id="3", message="3.", starting_point="branch1"),
    ]
    return definition
