import os

__TEMPLATE = """
.. GENERATED, DO NOT EDIT MANUALLY!!!

Rules
~~~~~

.. csv-table:: Available rules
    :header: "Rule", "Description"
    :widths: 15, 30

@@rules@@
"""


def main():
    from gitflow_linter import visitor
    import re
    file = 'rules.rst'
    file_path = os.path.join(os.path.dirname(__file__), file)
    rules = {
        'rules': [
            (v.rule, v.__doc__.strip() if v.__doc__ else '')
            for v in visitor.visitors(gitflow={})
        ]
    }
    with open(file_path, 'w+') as file:
        file.write(re.sub(r"@@(\w+)@@", lambda match: __rules_to_csv_rows(rules[match.group(1)]), __TEMPLATE))


def __rules_to_csv_rows(rules) -> str:
    row_fmt = '\t"``{rule}``","{desc}"'
    return os.linesep.join([row_fmt.format(rule=rule[0], desc=rule[1]) for rule in rules])


if __name__ == '__main__':
    main()
