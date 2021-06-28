import logging
from os import linesep
from report import Report, Section

FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)


def _console_output(report: Report):
    def _section_icon(s: Section) -> str:
        if s.contains_issues and not section.contains_errors and not section.contains_warns:
            return 'ℹ️'
        elif s.contains_errors:
            return '❌'
        elif s.contains_warns:
            return '⚠️'
        else:
            return '✅'

    title = 'Report for git repository: {}'.format(report.working_dir)
    log.info('=' * len(title))
    log.info(title)
    log.info('=' * len(title))
    log.info('Statistics: {}'.format(report.stats))
    log.info('=' * len(title))
    log.info(linesep + 'Results:')
    for section in report.sections:
        log.info(linesep + _section_icon(section) + '\t' + section.rule)
        log.info('\t' + section.title)
        if section.issues:
            log.info('\tIssues detected:')
            for issue in section.issues:
                log.log(issue.level.to_log_level, '\t\t- ' + issue.description)


def _json_output(report: Report):
    import json
    log.info(json.dumps({
        'repository': report.working_dir,
        'statistics': report.stats,
        'sections': [
            {
                'rule': section.rule,
                'title': section.title,
                'issues': [
                    {
                        'level': issue.level,
                        'description': issue.description,
                    } for issue in section.issues
                ]
            } for section in report.sections
        ]
    }, indent=2))


outputs = {
    'console': _console_output,
    'json': _json_output,
}


def create_output(out_type) -> callable:
    return outputs.get(out_type, _console_output)
