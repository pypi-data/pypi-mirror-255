import sys

import typer

from ghmeister.services.GitHubService import get_github
from ghmeister.tui.GHMeisterApp import RepoMeisterApp

cli = typer.Typer(no_args_is_help=True, add_completion=False)


@cli.command(help="Login")
def login():
    github = get_github()
    user = github.get_user()
    print(f'Logged in as {user.login}')


@cli.command(help="Create a changelog")
def changelog(repository: str = typer.Argument(help='Full repository name, for example: my-org/my-repo'),
              from_sha: str = typer.Argument(help='From SHA'),
              to_sha: str = typer.Argument(help='To SHA')):
    github = get_github()
    repo = github.get_repo(repository)
    comparison = repo.compare(from_sha, to_sha)
    print(f'## Changelog for {repository}')
    print(f'### Commits {from_sha}...{to_sha}')
    commits = comparison.commits
    for commit in commits:
        message = commit.commit.message
        header = message.split('\n')[0]
        title = header[:72]
        print(f'- {title}')


@cli.callback(invoke_without_command=False)
def callback(ctx: typer.Context):
    """GH Meister: GitHub Manager."""
    if ctx.invoked_subcommand:
        print('Running subcommand')
    else:
        print('Running default')


def main():
    if len(sys.argv) == 1:
        app = RepoMeisterApp()
        app.run()
    else:
        cli()


if __name__ == '__main__':
    main()
