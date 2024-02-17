import datetime
import os
from typing import TypedDict, Union
from urllib.parse import urljoin

import click
import giturlparse
from git import InvalidGitRepositoryError
from git.repo import Repo


class GitInfo(TypedDict):
    gitHash: str
    gitRemoteOriginHTTPS: str
    gitSSHRepo: str
    gitUser: str
    localRepoRootDir: str
    mergedAt: datetime.datetime


def strip_git_suffix(s: str) -> str:
    return s[:-4] if s.endswith(".git") else s


def join_repo_and_path(repo: str, path: str) -> str:
    # Remove trailing and preceding slashes
    repo_clean = repo.strip("/")
    clean_path = path.strip("/")

    # Join the two
    return urljoin(f"{repo_clean}/", clean_path)


def get_git_repo_info(path: Union[os.PathLike, str]) -> GitInfo:
    """Returns a dictionary with information about the git repo at the given path.
    If the given path is not in a git repo, or the repo doesn't have an origin remote,
    an exception is raised."""
    try:
        repo = Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise click.ClickException(
            f"The directory '{path}' must be within a git repository."
        )

    if "origin" not in [r.name for r in repo.remotes]:
        raise click.ClickException(
            f"The git repository containing '{path}' must have an 'origin' remote."
        )

    if not repo.head.is_valid():
        raise click.ClickException(
            f"The git repository containing '{path}' must have a commit at HEAD."
        )
    parsed_repo = giturlparse.parse(repo.remotes.origin.url)
    return {
        "gitHash": repo.head.commit.hexsha,
        "gitRemoteOriginHTTPS": parsed_repo.url2https,
        "gitSSHRepo": strip_git_suffix(parsed_repo.url2ssh),
        "gitUser": repo.head.commit.author.name or "unknown-git-user",
        "localRepoRootDir": os.path.dirname(repo.git_dir),
        "mergedAt": repo.head.commit.committed_datetime,
    }


def get_git_ssh_file_path(git_info: GitInfo, local_file_path: str) -> str:
    absolute_file_path = os.path.abspath(local_file_path)
    relative_path = os.path.relpath(absolute_file_path, git_info["localRepoRootDir"])
    return join_repo_and_path(git_info["gitSSHRepo"], relative_path)
