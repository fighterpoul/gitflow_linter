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

    def apply(self, visitor, *args, **kwargs):
        return visitor.visit(self, *args, **kwargs)


class RepositoryVisitor(ABC):

    @abstractmethod
    def visit(self, repo: Repository, *args, **kwargs):
        pass
