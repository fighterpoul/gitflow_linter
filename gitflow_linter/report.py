import logging
from typing import List
from enum import Enum, unique


@unique
class Level(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'

    @property
    def to_log_level(self):
        return {
            Level.INFO: logging.INFO,
            Level.WARNING: logging.WARNING,
            Level.ERROR: logging.ERROR
        }.get(self, logging.DEBUG)


class Issue:

    @classmethod
    def info(cls, description: str):
        """
        Creates an ``Issue`` with INFO severity
        """
        return cls(Level.INFO, description)

    @classmethod
    def warning(cls, description: str):
        """
        Creates an ``Issue`` with WARNING severity
        """
        return cls(Level.WARNING, description)

    @classmethod
    def error(cls, description: str):
        """
        Creates an ``Issue`` with ERROR severity
        """
        return cls(Level.ERROR, description)

    def __init__(self, level: Level, description: str):
        """
        :param level: Describes severity of the Issue
        :param description: Explanation of what is wrong
        """
        self.level = level
        self.description = description

    def __repr__(self):
        return "Issue(level={level}, description='{desc}')".format(level=self.level, desc=self.description)


class Section:
    """
    Represents repository verification done for a single rule.
    Results are represented by list of :class:`Issues <Issue>`.
    """

    def __init__(self, rule: str, title: str, issues=None):
        if issues is None:
            issues = []
        self.rule = rule
        self.title = title
        self.issues = issues

    def append(self, issue: Issue):
        """
        Adds new issue detected

        :param issue: New issue detected
        :return:
        """
        self.issues.append(issue)

    def extend(self, issues: list):
        self.issues.extend(issues)

    @property
    def contains_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def contains_errors(self) -> bool:
        return len([issue for issue in self.issues if issue.level is Level.ERROR]) > 0

    @property
    def contains_warns(self) -> bool:
        return len([issue for issue in self.issues if issue.level is Level.WARNING]) > 0

    def __repr__(self):
        return "Section(rule={rule}, title='{title}')".format(rule=self.rule, title=self.title)


class Report:
    def __init__(self, working_dir: str, stats: dict, sections: list):
        self.working_dir = working_dir
        self.stats = stats
        self.sections = sections if sections else []

    def append(self, section: Section):
        self.sections.append(section)

    def contains_errors(self, are_warnings_errors) -> bool:
        errors = [section for section in self.sections if
                  section.contains_errors or (are_warnings_errors and section.contains_warns)]
        return len(errors) > 0
