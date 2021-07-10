class AttributeDict(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, dictionary: dict = {}):
        super().__init__()
        self.update(dictionary)


_defaults = AttributeDict({
        "master": "master",
        "develop": "develop",
        "features": "feature",
        "fixes": "bugfix",
        "releases": "release",
        "hotfixes": "hotfix",
        "others": ["spike"],
    })


class Gitflow(AttributeDict):
    """
    Contains all settings related to branches from YAML file.
    It extends :class:`AttributeDict <AttributeDict>`, so settings may be accessed like properties: ``gitflow.features``

    It will contain custom settings if you add them in YAML file as a child of ``branches`` node.
    """

    def __init__(self, settings: dict):
        defaults = _defaults.copy()
        if settings and settings.get('branches', None):
            defaults.update(settings['branches'])
        super().__init__(dictionary=defaults)


class RulesContainer:

    def __init__(self, rules: dict):
        if not rules or not rules.get('rules', None):
            raise KeyError('Yaml file does not contain rules')
        self._rules = rules['rules']

    @property
    def rules(self):
        return self._rules.keys()

    def args_for(self, rule) -> dict:
        return self._rules.get(rule, {})

    def consume(self, rule: str):
        del self._rules[rule]
