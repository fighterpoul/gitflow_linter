class AttributeDict(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, dictionary: dict = {}):
        self.update(dictionary)


_minor_major_patch_regex = r'^\d+\.\d+(\.\d+)?$'

settings = AttributeDict({
    "gitflow": AttributeDict({
        "main": "master",
        "dev": "develop",
        "features": "feature",
        "fixes": "bugfix",
        "releases": "release",
        "hotfixes": "hotfix",
        "others": "spike, test",
        "versions_reg": _minor_major_patch_regex,
    }),
    "smells": AttributeDict({
        "max_days_features": 30
    })
})
