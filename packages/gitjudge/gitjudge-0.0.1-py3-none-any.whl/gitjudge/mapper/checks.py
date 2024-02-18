from gitjudge.entity import Checks

def map_checks(d: dict) -> Checks:
    if not isinstance(d, dict):
        raise TypeError('Expected dict object')

    checks = Checks()
    # Parent and parents are mutually exclusive
    if 'parent' in d and 'parents' in d:
        raise ValueError('Expected commit cannot have both parent and parents')

    parents = d.get('parents', [])
    parent = d.get('parent')
    if parent:
        parents.append(parent)
    checks.parents = parents

    if len(parents) > 2:
        raise ValueError('Expected commit cannot have more than 2 parents')

    # Tag and tags are mutually exclusive
    if 'tag' in d and 'tags' in d:
        raise ValueError('Expected commit cannot have both tag and tags')

    tags = d.get('tags', [])
    tag = d.get('tag')
    if tag:
        tags.append(tag)
    checks.tags = tags

    checks.cherry_pick = d.get('cherry-pick', None)
    checks.reverts = d.get('reverts', None)

    return checks
