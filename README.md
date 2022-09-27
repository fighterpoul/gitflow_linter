# gitflow-linter

# About

gitflow-linter is command line tool written in Python. It checks given repository against provided rules to ensure that Gitflow is respected.

What is Gitflow? [Based on Atlassian:](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

> The Gitflow Workflow defines a **strict branching model** designed around the project release.

> […]

> It assigns **very specific roles to different branches and defines how and when they should interact**. In addition to feature branches, it uses individual branches for preparing, maintaining, and recording releases.

As they wrote: *Gitflow is ideally suited for projects that have a scheduled release cycle*. It means that Gitflow is not always recommended, but when it is, you’d better stick to the rules!

And this is when gitflow-linter can help ;-)

# Quick Start

## Installation

You can install the linter from


* pip

```
pip install gitflow-linter
```


* or the source code

```
git clone [https://github.com/fighterpoul/gitflow_linter.git](https://github.com/fighterpoul/gitflow_linter.git)
cd gitflow_linter
git checkout 0.0.6
python setup.py install
```

## Usages

```
Usage: gitflow-linter [OPTIONS] GIT_DIRECTORY

  Evaluate given repository and check if gitflow is respected

Options:
  -s, --settings FILENAME
  -o, --output [console|json]
  -p, --fetch-prune            Linter will refresh the repo before checking
  -d, --allow-dirty            Linter will ignore the fact that the given repo
                               is considered dirty

  -w, --fatal-warnings         Returned code will be 1 anyway, even if there
                               are warnings but no errors

  --help                       Show this message and exit.
```

Standard use case looks pretty simple:

```
gitflow-linter /path/to/git/repository
```

**WARNING**: URL to a remote is not supported. Passing [https://github.com/fighterpoul/gitflow_linter.git](https://github.com/fighterpoul/gitflow_linter.git) as the argument will fail.

**HINT**: Run `git fetch --prune` before to make the repo clean and clear
**HINT**: In some cases it might be usefull to pull master and develop firstly, before running the linter: `git checkout master && git checkout develop`

# Documentation

A bit more detailed documentation can be found here: [https://fighterpoul.github.io/gitflow_linter/](https://fighterpoul.github.io/gitflow_linter/)
