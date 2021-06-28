import sys
import logging
import os

# GitPython, click, pyyaml
import click
from git import Repo
import yaml

import output
from report import Report, Section, Issue
from visitor import StatsRepositoryVisitor

FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

_DEFAULT_LINTER_OPTIONS = 'gitflow_linter.yaml'


def _validate_settings(value, working_dir):
    if value:
        return value

    potential_settings = os.path.join(working_dir, _DEFAULT_LINTER_OPTIONS)
    if not os.path.exists(potential_settings):
        raise click.BadParameter("Working git directory {} does not contain {} file. ".format(working_dir,
                                                                                              _DEFAULT_LINTER_OPTIONS) +
                                 "Please provide path to the settings by using --settings option")


@click.command()
@click.argument('git_directory',
                type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True,
                                allow_dash=False, path_type=None))
@click.option('--settings', type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
def main(git_directory, settings):
    """Evaluate given repository and check if gitflow is respected"""
    try:
        from repository import Repository
        import visitor
        from rules import RulesContainer, Gitflow
        settings = _validate_settings(settings, working_dir=git_directory)
        yaml_settings = yaml.load(settings, Loader=yaml.SafeLoader)
        gitflow = Gitflow(settings=yaml_settings)
        repo = Repository(Repo(git_directory), settings=gitflow)
        rules = RulesContainer(rules=yaml_settings)
        report = Report(working_dir=git_directory, stats=repo.apply(StatsRepositoryVisitor(settings=gitflow)), sections=[])

        visitors = [visitor for visitor in visitor.visitors(settings=gitflow) if visitor.rule in rules.rules]
        for visitor in visitors:
            try:
                kwargs = rules.args_for(visitor.rule)
                section: Section = repo.apply(visitor, **kwargs if kwargs else {})
                if section is not None:
                    report.append(section)
            except BaseException as err:
                error_section = Section(rule=visitor.rule, title='ERROR!')
                error_section.append(Issue.error('💀 Cannot be checked because of error: {err}'.format(err=err)))
                report.append(error_section)
        output.create_output('console')(report)
        return sys.exit(1 if report.contains_errors(are_warnings_errors=False) else 0)
    except BaseException as err:
        log.error(err)
        return sys.exit(1)


if __name__ == '__main__':
    main()
