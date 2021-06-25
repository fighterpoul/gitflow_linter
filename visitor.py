from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import os

from git import Head
from git.util import IterableList

from repository import Repository, RepositoryVisitor

from functools import wraps


def arguments_checker(keywords):
    def wrap(f):
        @wraps(f)
        def new_function(*args, **kw):
            missing = [keyword for keyword in keywords if keyword not in kw.keys()]
            if len(missing) > 0:
                raise ValueError(
                    "Following arguments are missing: {}".format(', '.join(keywords)))
            return f(*args, **kw)

        return new_function

    return wrap


class BaseVisitor(RepositoryVisitor, ABC):

    @property
    @abstractmethod
    def rule(self) -> str:
        pass

    def __init__(self, settings: dict):
        self.settings = settings


class StatsRepositoryVisitor(BaseVisitor):

    @property
    def rule(self) -> str:
        pass

    def visit(self, repo: Repository):
        def names(branches: IterableList):
            return [b.name for b in branches]

        return {
            "references": {
                "main": names(branches=repo.branches(folder=self.settings.main)),
                "dev": names(branches=repo.branches(folder=self.settings.dev)),
                "features": names(branches=repo.branches(folder=self.settings.features)),
                "fixes": names(branches=repo.branches(folder=self.settings.fixes)),
                "releases": names(branches=repo.branches(folder=self.settings.releases)),
                "hotfixes": names(branches=repo.branches(folder=self.settings.hotfixes)),
            },
            "counts": {
                "main": len(repo.branches(folder=self.settings.main)),
                "dev": len(repo.branches(folder=self.settings.dev)),
                "features": len(repo.branches(folder=self.settings.features)),
                "fixes": len(repo.branches(folder=self.settings.fixes)),
                "releases": len(repo.branches(folder=self.settings.releases)),
                "hotfixes": len(repo.branches(folder=self.settings.hotfixes)),
            }
        }


class SingleBranchesVisitor(BaseVisitor):

    @property
    def rule(self) -> str:
        return 'single_master_and_develop'

    def visit(self, repo: Repository, **kwargs):
        issues = []
        # TODO add more smart checking
        if len(repo.branches(folder=self.settings.main)) > 1:
            issues.append('Repository contains more than one main branch')
        if len(repo.branches(folder=self.settings.dev)) > 1:
            issues.append('Repository contains more than one dev branch')

        if len(issues) > 0:
            raise Exception(', '.join(issues))


class OldDevelopmentBranchesVisitor(BaseVisitor):

    @property
    def rule(self) -> str:
        return 'no_old_development_branches'

    @arguments_checker(['max_days_features'])
    def visit(self, repo: Repository, **kwargs):
        issues = []
        deadline = datetime.now() - timedelta(days=kwargs['max_days_features'])
        merged_branches = [branch.strip() for branch in
                           repo.repo.git.branch('-r', '--merged', repo.dev.name).split(os.linesep)]

        def _check_for_issues(branches: IterableList, name: str):
            for branch in branches:
                if deadline > branch.commit.authored_datetime.replace(tzinfo=None) \
                        and branch.name not in merged_branches:
                    issues.append(
                        '{} {} has not been touched since {}'.format(name, branch.name,
                                                                     branch.commit.authored_datetime))

        _check_for_issues(branches=repo.branches(folder=self.settings.features), name='Feature')
        _check_for_issues(branches=repo.branches(folder=self.settings.fixes), name='Fix')

        if len(issues) > 0:
            raise Exception(os.linesep.join(issues))


class NotScopedBranchesVisitor(BaseVisitor):

    @property
    def rule(self) -> str:
        return 'no_orphan_branches'

    def visit(self, repo: Repository, **kwargs):
        expected_prefix_template = '{remote}/{branch}'
        expected_prefixes = [
                                expected_prefix_template.format(remote=repo.remote.name, branch='HEAD'),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.main),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.dev),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.features),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.fixes),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.hotfixes),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.releases),
                            ] + [expected_prefix_template.format(remote=repo.remote.name, branch=branch.strip())
                                 for branch in self.settings.others]

        def has_expected_prefix(branch: Head) -> bool:
            for prefix in expected_prefixes:
                if branch.name.startswith(prefix):
                    return True
            return False

        orphan_branches = [branch.name for branch in repo.branches() if not has_expected_prefix(branch=branch)]
        if len(orphan_branches) > 0:
            raise Exception('Following branches look like orphans, namely they exist out of expected folders:\n{}'
                            .format(os.linesep.join(orphan_branches)))


class MainCommitsAreTaggedVisitor(BaseVisitor):

    @property
    def rule(self) -> str:
        return 'master_must_have_tags'

    def visit(self, repo: Repository, **kwargs):
        main_branch = '{}/{}'.format(repo.remote.name, self.settings.main)
        query_for_main_commits = repo.repo.git.log(main_branch, '--merges', '--format=format:%H', '--first-parent') \
            .split(os.linesep)
        main_commits = [sha.strip() for sha in query_for_main_commits if sha]
        tags = repo.repo.tags
        tags_sha = [tag.commit.hexsha for tag in tags]
        tags_not_on_main_branch = [sha for sha in tags_sha if sha not in main_commits]
        main_commits_not_tagged = [commit for commit in main_commits if commit not in tags_sha]

        def _shorten(shas) -> str:
            return os.linesep.join([sha[:7] for sha in shas])

        if len(main_commits_not_tagged) > 0:
            raise Exception('Following commits from master branch are not tagged:'
                            + os.linesep
                            + _shorten(main_commits_not_tagged))

        if len(tags_not_on_main_branch) > 0:
            return 'Following tags were not added on the main branch: {}'.format(_shorten(tags_not_on_main_branch))


class VersionNamesConventionVisitor(BaseVisitor):

    @property
    def rule(self) -> str:
        return 'version_names_follow_convention'

    @arguments_checker(['version_regex'])
    def visit(self, repo: Repository, *args, **kwargs):
        import re
        releases = [branch.name for branch in repo.branches(self.settings.releases)]
        tags = [tag.name for tag in repo.repo.tags]
        version_reg = kwargs['version_regex']

        def _validate_version(v: str) -> bool:
            return re.search(version_reg, v) is not None

        release_issues = [release for release in releases if not _validate_version(release.split('/')[-1])]
        tags_issues = [tag for tag in tags if not _validate_version(tag)]

        if len(release_issues) > 0 or len(tags_issues) > 0:
            message = '' if len(release_issues) <= 0 else 'Following releases do not follow version name ' \
                                                          'convention: {}'.format(
                os.linesep.join(release_issues)) + os.linesep
            message += '' if len(
                tags_issues) <= 0 else 'Following tags do not follow version name convention:'\
                                       + os.linesep \
                                       + os.linesep.join(tags_issues)
            raise Exception(message)


class DeadReleasesVisitor(BaseVisitor):

    @property
    def rule(self) -> str:
        return 'no_dead_releases'

    @arguments_checker(['deadline_to_close_release'])
    def visit(self, repo: Repository, *args, **kwargs):
        deadline = datetime.now() - timedelta(days=kwargs['deadline_to_close_release'])
        main_branch = '{}/{}'.format(repo.remote.name, self.settings.main)
        release_branch = '{}/{}/'.format(repo.remote.name, self.settings.releases)

        query_for_not_merged_to_main = [r.strip() for r in
                                        repo.repo.git.branch('-r', '--no-merged', main_branch).split(os.linesep)]
        potential_dead_releases = [repo.branch(release) for release in query_for_not_merged_to_main if
                                   release.strip().startswith(release_branch)]
        dead_releases = [dead_release for dead_release in potential_dead_releases if
                         deadline > dead_release.commit.authored_datetime.replace(tzinfo=None)]

        if len(dead_releases) > 0:
            message = 'Following releases look like abandoned - they have never been merged to the main branch:' \
                      + os.linesep \
                      + os.linesep.join([r.name for r in dead_releases])
            raise Exception(message)


def visitors(settings: dict):
    return [
        SingleBranchesVisitor(settings=settings),
        OldDevelopmentBranchesVisitor(settings=settings),
        NotScopedBranchesVisitor(settings=settings),
        MainCommitsAreTaggedVisitor(settings=settings),
        VersionNamesConventionVisitor(settings=settings),
        DeadReleasesVisitor(settings=settings),
    ]
