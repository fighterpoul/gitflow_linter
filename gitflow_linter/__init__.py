import importlib
import pkgutil
import sys
import os

# GitPython, click, pyyaml
import click
from git import Repo
import yaml

from gitflow_linter import output
from gitflow_linter.rules import RulesContainer, Gitflow

DEFAULT_LINTER_OPTIONS = 'gitflow_linter.yaml'
__version__ = '0.0.1'

__discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('gitflow_') and name.endswith('_linter') and name != 'gitflow_linter'
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

    try:
        settings = _validate_settings(settings, working_dir=git_directory)
        gitflow, rules = parse_yaml(settings)
        repo = Repository(Repo(git_directory), settings=gitflow)
        report = Report(working_dir=git_directory, stats=repo.apply(StatsRepositoryVisitor(settings=gitflow)), sections=[])

        visitors = __get_all_visitors(gitflow=gitflow, rules=rules)
        for visitor in visitors.values():
            try:
                kwargs = rules.args_for(visitor.rule)
                section: Section = repo.apply(visitor, **kwargs if kwargs else {})
                if section is not None:
                    report.append(section)
                else:
                    output.log.warning('⚠️ Rule {} checked but result was not returned'.format(visitor.rule))
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


def parse_yaml(settings):
    yaml_settings = yaml.load(settings, Loader=yaml.SafeLoader)
    gitflow = Gitflow(settings=yaml_settings)
    rules = RulesContainer(rules=yaml_settings)
    return gitflow, rules


def __get_all_visitors(gitflow, rules) -> dict:
    from gitflow_linter import visitor
    visitors = [visitor for visitor in visitor.visitors(settings=gitflow) if visitor.rule in rules.rules]
    plugin_visitors = [plugin.visitors(settings=gitflow)
                       for plugin in __discovered_plugins.values()
                       if __is_plugin_valid(plugin_module=plugin)]
    flatten = lambda t: [item for sublist in t for item in sublist]
    all_visitors = visitors + [plugin_visitor
                               for plugin_visitor in flatten(plugin_visitors)
                               if plugin_visitor.rule in rules.rules]
    return {
        v.rule: v
        for v in all_visitors
    }


@click.command()
def plugins():
    output.log.info(', '.join(sorted(__available_plugins)))
    output.log.info('Available gitflow-linter plugins:')
    if not __available_plugins:
        output.log.info('No plugins found.')
    for plugin in __available_plugins:
        try:
            __validate_plugin(plugin_module=__discovered_plugins[plugin])
            plugin_visitors = __discovered_plugins[plugin].visitors(settings={})
            log_fmt = '- {} handles following rules: ' + os.linesep + '\t* {}'
            output.log.info(log_fmt.format(plugin, '\t* '.join([v.rule for v in plugin_visitors])))
        except BaseException as err:
            output.log.error('❌ {} cannot be used because of error: {}'.format(plugin, err))
    return sys.exit(0)


def __validate_plugin(plugin_module):
    visitors = plugin_module.visitors(settings={})
    from gitflow_linter.visitor import BaseVisitor
    invalid = [visitor
               for visitor in plugin_module.visitors(settings={})
               if not isinstance(visitor, BaseVisitor) or not visitor.rule]
    if not visitors:
        raise ValueError('Plugin is invalid because it has no visitors')
    if len(invalid) > 0:
        raise ValueError('Plugin is invalid because it has visitors that evaluate no rule or do not extend '
                         'BaseVisitor: {} '
                         .format(', '.join([str(type(v)) for v in invalid])))


def __is_plugin_valid(plugin_module) -> bool:
    try:
        __validate_plugin(plugin_module=plugin_module)
    except BaseException:
        return False
    else:
        return True


if __name__ == '__main__':
    main()
