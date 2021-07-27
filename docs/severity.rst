Severity
--------

Each rule (even a custom one handled by a :ref:`plugin<Plugins>`) might be optionally configured by using ``severity`` option:

.. code-block:: yaml

    rules:
      a_rule:
        severity: info

If provided, level of **all** detected issues for a rule will be changed, according to provided value.

Provided severity value must correspond to one of ``Level`` enum cases:

.. autoclass:: gitflow_linter.report.Level
    :members:
    :undoc-members:
    :exclude-members: to_log_level