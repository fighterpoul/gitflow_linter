Settings
~~~~~~~~

You can manipulate how linter works by using yaml file with settings.

* place the settings file in a root folder of your repo as |settings_file|

.. parsed-literal::

    repo_dir/
    \|__ .git/
    \|__ |settings_file|
    \|__ other files and folders

or

* wherever you want and pass as an option.

.. parsed-literal::

    |command| /path/to/git/repository --settings=my_settings.yaml

Example file:

.. literalinclude:: ../rules.yaml
    :language: yaml
