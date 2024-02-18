from gitjudge.entity import ExpectedCommit
from gitjudge.mapper import map_checks

def map_expected_commit(id: str, d: dict) -> ExpectedCommit:
    if not isinstance(d, dict):
        raise TypeError('Expected dict object')

    expected_commit = ExpectedCommit(id)

    if 'message' in d:
        expected_commit.message = d.get('message')
        if not expected_commit.message:
            raise ValueError('Expected commit message cannot be empty')

    expected_commit.starting_point = d.get('starting-point')

    # Parent and parents are mutually exclusive
    if 'parent' in d and 'parents' in d:
        raise ValueError('Expected commit cannot have both parent and parents')

    parents = d.get('parents', [])
    parent = d.get('parent')
    if parent:
        parents.append(parent)
    expected_commit.parents = parents

    if len(parents) > 2:
        raise ValueError('Expected commit cannot have more than 2 parents')

    # Tag and tags are mutually exclusive
    if 'tag' in d and 'tags' in d:
        raise ValueError('Expected commit cannot have both tag and tags')

    tags = d.get('tags', [])
    tag = d.get('tag')
    if tag:
        tags.append(tag)
    expected_commit.tags = tags

    checks = d.get('check', None)
    if checks:
        expected_commit.checks = map_checks(checks)

    return expected_commit
