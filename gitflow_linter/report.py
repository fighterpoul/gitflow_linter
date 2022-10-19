from datetime import datetime
import logging
from git import Reference
from typing import List, Optional
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
    def info(cls, description: str, obj: Optional[Reference]=None):
        """
        Creates an ``Issue`` with INFO severity for related git object
        """
        return cls(Level.INFO, description, obj)

    @classmethod
    def warning(cls, description: str, obj: Optional[Reference]=None):
        """
        Creates an ``Issue`` with WARNING severity for related git object
        """
        return cls(Level.WARNING, description, obj)

    @classmethod
    def error(cls, description: str, obj: Optional[Reference]=None):
        """
        Creates an ``Issue`` with ERROR severity for related git object
        """
        return cls(Level.ERROR, description, obj)

    def __init__(self, level: Level, description: str, obj: Optional[Reference]=None):
        """
        :param level: Describes severity of the Issue
        :param description: Explanation of what is wrong
        """
        self.level = level
        self.description = description
        self.obj = obj

    def is_created_between(self, date_from: datetime, date_to: datetime) -> bool:
        if self.obj:
            obj_date = None

            if hasattr(self.obj, 'committed_datetime'):
                obj_date = self.obj.committed_datetime
            elif hasattr(self.obj, 'commit'):
                obj_date = self.obj.commit.committed_datetime
            elif hasattr(self.obj.object, 'committed_datetime'):
                obj_date = self.obj.object.committed_datetime
            
            return date_from < obj_date.replace(tzinfo=None) < date_to if obj_date else True
        
        return True

    def __repr__(self):
        return "Issue(level={level}, description='{desc}', obj='{obj}')".format(level=self.level, desc=self.description, obj=self.obj)


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

    def change_severity(self, to: Level):
        for issue in self.issues:
            issue.level = to
    
    def consider_issues_in_period(self, date_from: datetime, date_to: datetime):
        self.issues = [issue for issue in self.issues if issue.is_created_between(date_from, date_to)]

    def __repr__(self):
        return "Section(rule={rule}, title='{title}')".format(rule=self.rule, title=self.title)


class Report:
    def __init__(self, working_dir: str, stats: dict, sections: List[Section]):
        self.working_dir = working_dir
        self.stats = stats
        self.sections = sections if sections else []

    def append(self, section: Section):
        self.sections.append(section)

    def contains_errors(self, are_warnings_errors) -> bool:
        errors = [section for section in self.sections if
                  section.contains_errors or (are_warnings_errors and section.contains_warns)]
        return len(errors) > 0

    def consider_issues_only_in_period(self, date_from: datetime, date_to: datetime):
        for section in self.sections:
            section.consider_issues_in_period(date_from, date_to)
