"""Provide class GitRepo
"""

from collections import namedtuple
import datetime
import os
from pathlib import Path
import subprocess
from .version import Version


class GitError(Exception):
    pass


VersionMeta = namedtuple('VersionMeta', ['version', 'count', 'node', 'dirty'])


class GitRepo:
    """Determine properties of the git repository.
    """

    def _exec(self, cmd):
        try:
            proc = subprocess.run(cmd.split(),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  cwd=self.root,
                                  check=True,
                                  env=dict(os.environ, LC_ALL='C'),
                                  universal_newlines=True)
            return proc.stdout.strip()
        except subprocess.CalledProcessError as exc:
            msg = "git command '%s' failed:\n%s" % (cmd, exc.stderr)
            raise GitError(msg) from exc

    def __init__(self, root="."):
        self.root = Path(root).resolve()
        # Run git version mostly in order to fail early should the git
        # command not be available
        self.git_version = self._exec("git version")
        self.root = Path(self._exec("git rev-parse --show-toplevel"))

    def get_commit(self, ref='HEAD'):
        return self._exec("git rev-list -n 1 %s" % ref)

    def get_last_version_tag(self):
        candidate_tags = set()
        shadowed_tags = set()
        try:
            tags = self._exec("git tag --merged").split('\n')
        except GitError:
            return None
        for t in tags:
            # Ignore all tags that do not parse as Version
            try:
                v = Version(t)
            except ValueError:
                continue
            # Ignore post-releases
            if v.is_postrelease:
                continue
            candidate_tags.add(t)
            commit = self.get_commit(t)
            for t1 in self._exec("git tag --merged %s" % t).split('\n'):
                if self.get_commit(t1) == commit:
                    continue
                shadowed_tags.add(t1)
        version_tags = candidate_tags - shadowed_tags
        if version_tags:
            # Pick the last tag in Version ordering
            return sorted(version_tags, key=Version)[-1]
        else:
            return None

    def get_rev_count(self, base=None):
        if base:
            cmd = "git rev-list --count %s..HEAD" % base
        else:
            cmd = "git rev-list --count HEAD"
        return int(self._exec(cmd))

    def is_dirty(self):
        return bool(self._exec("git status --porcelain --untracked-files=no"))

    def get_version_meta(self):
        version_tag = self.get_last_version_tag()
        try:
            if version_tag:
                version = Version(version_tag)
                count = self.get_rev_count(base=version_tag)
            else:
                version = None
                count = self.get_rev_count()
            commit = self.get_commit()
            node = 'g' + commit[:7]
        except GitError:
            version = None
            count = 0
            node = None
        return VersionMeta(version, count, node, self.is_dirty())

    def get_date(self):
        if self.is_dirty():
            return datetime.date.today()
        else:
            try:
                ts = int(self._exec("git log -1 --format=%ad --date=unix"))
                return datetime.date.fromtimestamp(ts)
            except GitError:
                return None
