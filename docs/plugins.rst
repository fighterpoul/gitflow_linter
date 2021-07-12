Plugins
=======

|command| is by design open for extensions, you can write a plugin and define your own rules as well as override implementation of existing ones.

.. hint::
    The module that is installed and has name `gitflow_{name}_linter` will be considered as a plugin.

General principles
------------------

|command| is written by using `Visitor pattern <https://refactoring.guru/design-patterns/visitor>`__.
Plugin is just a list of visitors that are subscribed to check corresponding rules.

.. code-block:: python

    # gitflow_my_awesome_plugin_linter/__init__.py

    class MyAwesomeRuleVisitor(gitflow_linter.visitor.BaseVisitor):

        @property
        def rule(self):
            return 'my_awesome_rule_that_can_be_added_into_yaml_file'

        @gitflow_linter.visitor.arguments_checker('my_awesome_rule_argument')
        def visit(self, repo: gitflow_linter.repository.Repository, args, **kwargs) -> gitflow_linter.report.Section:
            # visit repository and return a ``Section`` with results of inspection
            # you can read ``Gitflow`` options by using self.gitflow (eg. name of branches): self.gitflow.develop
            # you can read your rule settings by using kwargs['my_awesome_rule_argument']

    def visitors(gitflow: Gitflow) -> List[gitflow_linter.visitor.BaseVisitor]:
        return [MyAwesomeRuleVisitor(settings=settings)]

Example visitor will be ran if :ref:`yaml settings file<Settings>` contains the rule:

.. code-block:: yaml

    rules:
        my_awesome_rule_that_can_be_added_into_yaml_file:
            my_awesome_rule_argument: 20

.. hint::
    If your plugin's visitor returns an :ref:`existing, pre-configured rule<Rules>`, it will be ran **instead of** default visitor. This is how you can override default behaviour.

To verify if a plugin is properly installed and recognized you can run ``gitflow-linter-plugins``

.. literalinclude:: plugins.txt

API Reference
-------------

From a plugin perspective, those are the most important classes:

.. autoclass:: gitflow_linter.repository.Repository
    :members:

.. autoclass:: gitflow_linter.rules.Gitflow

.. autoclass:: gitflow_linter.visitor.BaseVisitor
    :members:

.. autoclass:: gitflow_linter.report.Section
    :members:

.. autoclass:: gitflow_linter.report.Issue
    :members:
