import logging
from datetime import datetime, timedelta
import os

from git import Head
from git.util import IterableList

from repository import Repository, RepositoryVisitor


class BaseVisitor(RepositoryVisitor):

    def __init__(self, settings: dict):
        self.settings = settings


class StatsRepositoryVisitor(BaseVisitor):

    def visit(self, repo: Repository):
        def names(branches: IterableList):
            return [b.name for b in branches]

        return {
            "references": {
                "main": names(branches=repo.branches(folder=self.settings.gitflow.main)),
                "dev": names(branches=repo.branches(folder=self.settings.gitflow.dev)),
                "features": names(branches=repo.branches(folder=self.settings.gitflow.features)),
                "fixes": names(branches=repo.branches(folder=self.settings.gitflow.fixes)),
                "releases": names(branches=repo.branches(folder=self.settings.gitflow.releases)),
                "hotfixes": names(branches=repo.branches(folder=self.settings.gitflow.hotfixes)),
            },
            "counts": {
                "main": len(repo.branches(folder=self.settings.gitflow.main)),
                "dev": len(repo.branches(folder=self.settings.gitflow.dev)),
                "features": len(repo.branches(folder=self.settings.gitflow.features)),
                "fixes": len(repo.branches(folder=self.settings.gitflow.fixes)),
                "releases": len(repo.branches(folder=self.settings.gitflow.releases)),
                "hotfixes": len(repo.branches(folder=self.settings.gitflow.hotfixes)),
            }
        }


class SingleBranchesVisitor(BaseVisitor):

    def visit(self, repo: Repository):
        issues = []
        # TODO add more smart checking
        if len(repo.branches(folder=self.settings.gitflow.main)) > 1:
            issues.append('Repository contains more than one main branch')
        if len(repo.branches(folder=self.settings.gitflow.dev)) > 1:
            issues.append('Repository contains more than one dev branch')

        if len(issues) > 0:
            raise Exception(', '.join(issues))


class OldSupportBranchesVisitor(BaseVisitor):

    def visit(self, repo: Repository):
        issues = []
        deadline = datetime.now() - timedelta(days=self.settings.smells.max_days_features)
        merged_branches = [branch.strip() for branch in
                           repo.repo.git.branch('-r', '--merged', repo.dev.name).split(os.linesep)]

        def _check_for_issues(branches: IterableList, name: str):
            for branch in branches:
                if deadline > branch.commit.authored_datetime.replace(tzinfo=None) \
                        and branch.name not in merged_branches:
                    issues.append(
                        '{} {} has not been touched since {}'.format(name, branch.name,
                                                                     branch.commit.authored_datetime))

        _check_for_issues(branches=repo.branches(folder=self.settings.gitflow.features), name='Feature')
        _check_for_issues(branches=repo.branches(folder=self.settings.gitflow.fixes), name='Fix')

        if len(issues) > 0:
            raise Exception(os.linesep.join(issues))


class NotScopedBranchesVisitor(BaseVisitor):

    def visit(self, repo: Repository):
        expected_prefix_template = '{remote}/{branch}'
        expected_prefixes = [
                                expected_prefix_template.format(remote=repo.remote.name, branch='HEAD'),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.gitflow.main),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.gitflow.dev),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.gitflow.features),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.gitflow.fixes),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.gitflow.hotfixes),
                                expected_prefix_template.format(remote=repo.remote.name,
                                                                branch=self.settings.gitflow.releases),
                            ] + [expected_prefix_template.format(remote=repo.remote.name, branch=branch.strip())
                                 for branch in self.settings.gitflow.others.split(',')]

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

    def visit(self, repo: Repository):
        main_branch = '{}/{}'.format(repo.remote.name, self.settings.gitflow.main)
        query_for_main_commits = repo.repo.git.log(main_branch, '--merges', '--format=format:%H', '--first-parent') \
            .split(os.linesep)
        main_commits = [sha.strip() for sha in query_for_main_commits if sha]
        tags = repo.repo.tags
        tags_sha = [tag.commit.hexsha for tag in tags]
        tags_not_on_main_branch = [sha for sha in tags_sha if sha not in main_commits]
        main_commits_not_tagged = [commit for commit in main_commits if commit not in tags_sha]

        def _shorten(shas) -> str:
            return os.linesep.join([sha[:7] for sha in shas])

        if len(tags_not_on_main_branch) > 0:
            logging.getLogger().warning('Following tags were not added on the main branch: {}'
                                        .format(_shorten(tags_not_on_main_branch)))

        if len(main_commits_not_tagged) > 0:
            raise Exception('Following commits from master branch are not tagged: {}'
                            .format(_shorten(main_commits_not_tagged)))


class VersionNamesConventionVisitor(BaseVisitor):

    def visit(self, repo: Repository):
        releases = [branch.name for branch in repo.branches(self.settings.gitflow.releases)]
        tags = [tag.name for tag in repo.repo.tags]
        if self.settings.gitflow.versions_reg:
            import re
            version_reg = self.settings.gitflow.versions_reg

            def _validate_version(v: str) -> bool:
                return re.search(version_reg, v) is not None

            release_issues = [release for release in releases if not _validate_version(release.split('/')[-1])]
            tags_issues = [tag for tag in tags if not _validate_version(tag)]

            if len(release_issues) > 0 or len(tags_issues) > 0:
                message = '' if len(release_issues) <= 0 else 'Following releases do not follow version name ' \
                                                              'convention: {}'.format(os.linesep.join(release_issues))
                message += '' if len(tags_issues) <= 0 else 'Following tags do not follow version name convention: {}'.format(os.linesep.join(tags_issues))
                raise Exception(message)


def visitors(settings: dict):
    return [
        StatsRepositoryVisitor(settings=settings),
        SingleBranchesVisitor(settings=settings),
        OldSupportBranchesVisitor(settings=settings),
        NotScopedBranchesVisitor(settings=settings),
        MainCommitsAreTaggedVisitor(settings=settings),
        VersionNamesConventionVisitor(settings=settings),
    ]
