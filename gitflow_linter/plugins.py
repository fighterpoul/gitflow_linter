import importlib
import pkgutil

discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('gitflow_') and name.endswith('_linter') and name != 'gitflow_linter'
}


def validate_plugin(plugin_module):
    visitors = plugin_module.visitors(gitflow={})
    from gitflow_linter.visitor import BaseVisitor
    invalid = [visitor
               for visitor in plugin_module.visitors(gitflow={})
               if not isinstance(visitor, BaseVisitor) or not visitor.rule]
    if not visitors:
        raise ValueError('Plugin is invalid because it has no visitors')
    if len(invalid) > 0:
        raise ValueError('Plugin is invalid because it has visitors that evaluate no rule or do not extend '
                         'BaseVisitor: {} '
                         .format(', '.join([str(type(v)) for v in invalid])))


def is_plugin_valid(plugin_module) -> bool:
    try:
        validate_plugin(plugin_module=plugin_module)
    except BaseException:
        return False
    else:
        return True
