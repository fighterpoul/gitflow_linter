import os
from abc import ABC, abstractmethod

from git import Repo, Remote, RemoteReference
from git.util import IterableList


class Repository:
    def __init__(self, repo: Repo, settings: dict):
        self.repo = repo
        self.settings = settings
        self.assert_repo()
        self.remote.fetch()

    def assert_repo(self):
        if self.repo.bare:
            raise Exception('Given directory {} does not contain valid GIT repository.'.format(self.repo.working_dir))
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
    def main(self) -> RemoteReference:
        return self.repo.heads[self.settings.main]

    @property
    def dev(self) -> RemoteReference:
        return self.repo.heads[self.settings.dev]

    def commits_in_branch(self, branch: RemoteReference) -> IterableList:
        heads_commits = [head.commit for head in self.branches()]
        all_commits = iter(self.repo.iter_commits(branch.name, max_count=300))
        commits = [next(all_commits)]
        for commit in all_commits:
            if commit in heads_commits:
                break
            commits.append(commit)
        return commits

    def raw_query(self, query: callable, predicate: callable = None, map_line: callable = None):
        """
        Let you run raw queries on GitPython's git object

        :param query: callable where you can run raw query,
            eg. `lambda git: git.log('master')`
        :param predicate: optional callable where you can decide if given line should be included,
            eg lambda commit: `commit.startwith('Merged')`. All lines included if predicate is not given.
        :param map_line: optional callable where you can map line to other object,
            eg when query returns list of name of branches, you can map them to branch objects: `lambda line: repo.branch(line)`
        :return: list of lines returned by query that matches optional predicate,
            eg. ["sha-of-commit1", "sha-of-commit2", ...]
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
