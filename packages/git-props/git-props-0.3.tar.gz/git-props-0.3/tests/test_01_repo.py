"""Test module gitprops.repo
"""

import pytest
from gitprops.repo import GitError, GitRepo
from gitprops.version import Version


def test_repo_commit(repo_case):
    repo = repo_case.repo
    if repo_case.commit is not None:
        assert repo.get_commit() == repo_case.commit
    else:
        with pytest.raises(GitError):
            repo.get_commit()

def test_repo_last_version(repo_case):
    repo = repo_case.repo
    if repo_case.tag is None:
        assert repo.get_last_version_tag() is None
    else:
        assert Version(repo.get_last_version_tag()) == repo_case.tag

def test_repo_dirty(repo_case):
    repo = repo_case.repo
    assert repo.is_dirty() == repo_case.dirty

def test_repo_version_meta(repo_case):
    repo = repo_case.repo
    meta = repo.get_version_meta()
    assert meta.version == repo_case.tag
    assert meta.count == repo_case.count
    assert meta.node == repo_case.node
    assert meta.dirty == repo_case.dirty

def test_repo_date(repo_case):
    repo = repo_case.repo
    assert repo.get_date() == repo_case.date
