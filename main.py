import sys
import logging
import os

# GitPython, click
import click
from git import Repo

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


@click.command()
@click.argument('git_directory',
                type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True,
                                allow_dash=False, path_type=None))
@click.option('--stats/--no-stats', default=True)
def main(git_directory, stats):
    """Evaluate given repository and check if gitflow is respected"""
    try:
        from repository import Repository
        from settings import settings
        import visitor
        repo = Repository(Repo(git_directory), settings=settings)

        log.info('Working on git repository: {}'.format(git_directory))

        issues = []
        for visitor in visitor.visitors(settings=settings):
            try:
                result = repo.apply(visitor)
                if result is not None:
                    log.info(result)
            except BaseException as err:
                issues.append(err)
        if len(issues) > 0:
            log.error(os.linesep.join([str(issue) for issue in issues]))
    except BaseException as err:
        log.error(err)
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
