import os
from abc import ABC, abstractmethod

from git import Repo, Remote, RemoteReference, Commit, Head
from git.util import IterableList

from gitflow_linter import Gitflow


class Repository:
    def __init__(self, repo: Repo, gitflow: Gitflow, should_fetch=False, allow_dirty=False):
        self.repo = repo
        self.gitflow = gitflow
        self.assert_repo(allow_dirty)
        if should_fetch:
            self.remote.fetch('--prune')

    def assert_repo(self, allow_dirty: bool):
        if self.repo.bare:
            raise Exception('Given directory {} does not contain valid GIT repository.'.format(self.repo.working_dir))
        if not self.branch(self.gitflow.develop):
            raise Exception('Given repository {} does not contain expected {} branch'.format(self.repo.working_dir, self.gitflow.develop))
        if not self.branch(self.gitflow.master):
            raise Exception('Given repository {} does not contain expected {} branch'.format(self.repo.working_dir, self.gitflow.master))
        if self.repo.is_dirty(untracked_files=False) and not allow_dirty:
            raise Exception('Given repository {} is dirty.'.format(self.repo.working_dir))
        if len(self.repo.remotes) > 1:
            raise Exception(
                'Repo contains more than one remote: [{}]'.format(', '.join([r.name for r in self.repo.remotes])))

    @property
    def remote(self) -> Remote:
        return self.repo.remotes[0]

    def branches(self, folder: str = None) -> IterableList:
        path = None if folder is None else '{}/{}'.format(self.remote.name, folder)
        return self.remote.refs if path is None else [r for r in self.remote.refs if path in r.name]

    def branch(self, name: str = None) -> RemoteReference:
        path = name if '/' in name else '{}/{}'.format(self.remote.name, name)
        return next(iter([r for r in self.remote.refs if r.name.startswith(path)]), None)

    @property
    def master(self) -> Head:
        return self.repo.heads[self.gitflow.master]

    @property
    def develop(self) -> Head:
        return self.repo.heads[self.gitflow.develop]

    def unique_commits_for_branch(self, branch: RemoteReference, force_including_head=True) -> set[Commit]:
        """
        Returns set of unique commits for the given branch. Only commits that appear specifically on the branch will be
        returned. If a commit is included in the given branch and any other branch, it won't be taken into
        consideration.

        :param branch: the commits specific to the branch will be returned
        :param force_including_head: the flag will force including head commit of the branch. If a second branch has been started from branch passed as param, the flag set to True will ensure, that at least the one head commit will be returned, otherwise second/child branch will "consume" all commits and none will be considered as unique for the given branch.
        :return: set of unique commits for branch passed as the

        """
        other_heads = [head for head in self.branches() if not head.name == branch.name]
        all_commits = list(self.repo.iter_commits(branch.name, max_count=100))
        commits = set(all_commits)

        def _remove_commits_exist_in(other_branch: RemoteReference):
            other_branch_commits = self.repo.iter_commits(other_branch.name, max_count=100)
            for c in other_branch_commits:
                element = next((commit for commit in commits if commit.hexsha == c.hexsha), None)
                if element and (not force_including_head or element.hexsha != branch.commit.hexsha):
                    commits.remove(element)

        for other_branch in other_heads:
            _remove_commits_exist_in(other_branch=other_branch)
            if not commits:
                break

        return commits

    def raw_query(self, query: callable, predicate: callable = None, map_line: callable = None):
        """
        Let you run raw queries on GitPython's git object

        :param query: callable where you can run raw query,
            eg. ``lambda git: git.log('master')``
        :param predicate: optional callable where you can decide if given line should be included,
            eg. ``lambda commit: commit.startwith('Merged')``. All lines are included if predicate is not given.
        :param map_line: optional callable where you can map line to other object,
            eg. when query returns list of name of branches, you can map them to branch objects: ``lambda line: repo.branch(line)``
        :return: list of lines returned by query that matches optional predicate,
            eg. ``["sha-of-commit1", "sha-of-commit2", ...]``
        """
        return [line.strip() if not map_line else map_line(line.strip())
                for line in query(self.repo.git).split(os.linesep)
                if predicate is None or predicate(line)]

    def apply(self, visitor, *args, **kwargs):
        return visitor.visit(self, *args, **kwargs)


class RepositoryVisitor(ABC):

    @abstractmethod
    def visit(self, repo: Repository, *args, **kwargs):
        pass
