Results
~~~~~~~

By default once job is done a report is printed as a text in a human readable form:

.. code-block:: console

    ============================================================
    Report for git repository: GIT_DIRECTORY
    ============================================================
    Statistics:
        main: 1 branch(es)
        dev: 1 branch(es)
        features: 154 branch(es)
        fixes: 77 branch(es)
        releases: 5 branch(es)
        hotfixes: 3 branch(es)
    ============================================================

    Results:

    ✅	/* rule from yaml that has been checked */
        Quick info on what was checked

    ❌	/* next rule from yaml */
        Quick info
        Issues detected:
            - Details of an issue, usually with the name of a problematic branch

    ❌	/* rule with error, eg. bad yaml config */
        ERROR!
        Issues detected:
            - 💀 Cannot be checked because of error: /* reason, eg. missing argument */

You can change it by providing a desired output

.. parsed-literal::

    |command| /path/to/git/repository --output=json >> results.json

Then you should see in the console something that contains the same data as above but might be further processed.

Either way, in case of any issues the exit code will be 1. If repo is all good then 0 is returned.
