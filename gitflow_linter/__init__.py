import sys
import os

# GitPython, click, pyyaml
import click
from git import Repo
import yaml

from gitflow_linter import output
from gitflow_linter.rules import RulesContainer, Gitflow

DEFAULT_LINTER_OPTIONS = 'gitflow_linter.yaml'
__version__ = '0.0.3'


def _validate_settings(value, working_dir):
    if value:
        return value

    potential_settings = os.path.join(working_dir, DEFAULT_LINTER_OPTIONS)
    if not os.path.exists(potential_settings):
        raise click.BadParameter("Working git directory {} does not contain {} file. ".format(working_dir,
                                                                                              DEFAULT_LINTER_OPTIONS) +
                                 "Please provide path to the settings by using --settings option")
    return open(potential_settings, 'r')


@click.command()
@click.argument('git_directory',
                type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True,
                                allow_dash=False, path_type=None))
@click.option('-s', '--settings', type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('-o', '--output', 'out',
              type=click.Choice(output.outputs.keys(), case_sensitive=False), default=next(iter(output.outputs.keys())))
@click.option('-p', '--fetch-prune', 'fetch', is_flag=True, default=False, help="Linter will refresh the repo before "
                                                                                "checking")
@click.option('-d', '--allow-dirty', is_flag=True, default=False, help="Linter will ignore the fact that the given "
                                                                       "repo is considered dirty")
def main(git_directory, settings, out, fetch, allow_dirty):
    """Evaluate given repository and check if gitflow is respected"""
    from gitflow_linter.report import Report, Section, Issue
    from gitflow_linter.visitor import StatsRepositoryVisitor
    from gitflow_linter.repository import Repository

    try:
        settings = _validate_settings(settings, working_dir=git_directory)
        gitflow, rules = parse_yaml(settings)
        repo = Repository(Repo(git_directory), gitflow=gitflow, should_fetch=fetch, allow_dirty=allow_dirty)
        report = Report(working_dir=git_directory, stats=repo.apply(StatsRepositoryVisitor(gitflow=gitflow)), sections=[])

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


def __get_all_visitors(gitflow: Gitflow, rules: RulesContainer) -> dict:
    from gitflow_linter import visitor
    from gitflow_linter import plugins
    visitors = [visitor for visitor in visitor.visitors(gitflow=gitflow) if visitor.rule in rules.rules]
    plugin_visitors = [plugin.visitors(gitflow=gitflow)
                       for plugin in plugins.discovered_plugins.values()
                       if plugins.is_plugin_valid(plugin_module=plugin)]
    flatten = lambda t: [item for sublist in t for item in sublist]
    all_visitors = visitors + [plugin_visitor
                               for plugin_visitor in flatten(plugin_visitors)
                               if plugin_visitor.rule in rules.rules]
    return {
        v.rule: v
        for v in all_visitors
    }


@click.command()
def available_plugins():
    from gitflow_linter import plugins
    available_plugins = plugins.discovered_plugins.keys()
    output.stdout_log.info('Available gitflow-linter plugins:')
    if not available_plugins:
        output.stdout_log.info('No plugins found.')
    for plugin in available_plugins:
        try:
            plugins.validate_plugin(plugin_module=plugins.discovered_plugins[plugin])
            plugin_visitors = plugins.discovered_plugins[plugin].visitors(gitflow={})
            log_fmt = '- {} handles following rules: ' + os.linesep + '\t* {}'
            output.stdout_log.info(log_fmt.format(plugin, '\t* '.join([v.rule for v in plugin_visitors])))
        except BaseException as err:
            output.stdout_log.error('❌ {} cannot be used because of error: {}'.format(plugin, err))
    return sys.exit(0)


if __name__ == '__main__':
    main()
