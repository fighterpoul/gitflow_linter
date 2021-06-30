import importlib
import pkgutil
import sys
import os

# GitPython, click, pyyaml
import click
from git import Repo
import yaml

from gitflow_linter import output

DEFAULT_LINTER_OPTIONS = 'gitflow_linter.yaml'
__version__ = '0.0.1'

__discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('gitflow_linter_')
}

__available_plugins = __discovered_plugins.keys()


def _validate_settings(value, working_dir):
    if value:
        return value

    potential_settings = os.path.join(working_dir, DEFAULT_LINTER_OPTIONS)
    if not os.path.exists(potential_settings):
        raise click.BadParameter("Working git directory {} does not contain {} file. ".format(working_dir,
                                                                                              DEFAULT_LINTER_OPTIONS) +
                                 "Please provide path to the settings by using --settings option")


@click.command()
@click.argument('git_directory',
                type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True,
                                allow_dash=False, path_type=None))
@click.option('-s', '--settings', type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('-o', '--output', 'out',
              type=click.Choice(output.outputs.keys(), case_sensitive=False), default=next(iter(output.outputs.keys())))
def main(git_directory, settings, out):
    """Evaluate given repository and check if gitflow is respected"""
    from gitflow_linter.report import Report, Section, Issue
    from gitflow_linter.visitor import StatsRepositoryVisitor
    from gitflow_linter.repository import Repository
    from gitflow_linter import visitor
    from gitflow_linter.rules import RulesContainer, Gitflow

    try:
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
            finally:
                rules.consume(visitor.rule)

        if rules.rules:
            output.log.warning('Some of rules cannot be validated because corresponding validators could not be found: '
                               + ', '.join(rules.rules))
        output.create_output(out)(report)
        return sys.exit(1 if report.contains_errors(are_warnings_errors=False) else 0)
    except BaseException as err:
        output.log.error(err)
        return sys.exit(1)


@click.command()
def plugins():
    output.log.info(', '.join(sorted(__available_plugins)))
    output.log.info('Available gitflow-linter plugins:')
    if not __available_plugins:
        output.log.info('No plugins found.')
    for plugin in __available_plugins:
        output.log.info('- {plugin} handles rule {rule}'.format(plugin=plugin, rule=__discovered_plugins[plugin].visitor.rule))
    return sys.exit(0)


if __name__ == '__main__':
    main()
