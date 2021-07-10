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
git checkout 0.0.1
python setup.py install
```

## Usages

```
Usage: gitflow-linter [OPTIONS] GIT_DIRECTORY

  Evaluate given repository and check if gitflow is respected

Options:
  -s, --settings FILENAME
  -o, --output [console|json]
  --help                       Show this message and exit.
```

Standard use case looks pretty simple:

```
gitflow-linter /path/to/git/repository
```

**WARNING**: URL to a remote is not supported. Passing [https://github.com/fighterpoul/gitflow_linter.git](https://github.com/fighterpoul/gitflow_linter.git) as the argument will fail.

**HINT**: Run `git fetch --prune` before to make the repo clean and clear

# Documentation

A bit more detailed documentation can be found here: [https://fighterpoul.github.io/gitflow_linter/](https://fighterpoul.github.io/gitflow_linter/)

# License

The MIT License (MIT)
Copyright © 2021 Paweł Walczak

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
