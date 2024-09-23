"""Provide basic access to git functions."""

import datetime
import shlex
import subprocess
from pathlib import Path

import dominate.tags as dom
import dominate.util as dom_util


def diff_html(file_path: Path, commit: str) -> str:
    """Return djot for a git diff between commits."""

    html_result = ""
    command = f"git show --word-diff=porcelain --no-color --pretty=format:%b {commit} -- {file_path}"
    if diff := subprocess.run(
        shlex.split(command, posix=False), capture_output=True, text=True, check=True
    ).stdout.splitlines():
        while not diff[0].startswith("@@ "):
            diff.pop(0)
        with dom.div(cls="highlight") as diff_div:
            with dom.pre(cls="diff"):
                dom.p(diff[0], cls="diff-header")
                with dom.p(cls="diff-content"):
                    for line in diff[1:]:
                        match line[:1]:
                            case " ":  # Unmodified
                                dom_util.text(line[1:])
                            case "+":  # Insertion
                                dom.ins(line[1:])
                            case "-":  # Deletion
                                dom.del_(line[1:])
                            case "~":  # Newline
                                dom_util.text("\n")

        html_result += diff_div.render()

    return html_result


def get_file_at_commit(file_path: Path, commit: str) -> str:
    """Get an entire files contents at the time of a commit."""
    command = f"git show {commit}:{file_path}"
    return subprocess.run(shlex.split(command, posix=False), capture_output=True, text=True, check=True).stdout


def get_file_commits(file_path: Path) -> list[tuple[str, datetime.datetime, str]]:
    """Get a files commits in the form: hash,iso date,subject"""

    def convert_commit(commit: str) -> tuple[str, datetime.datetime, str]:
        """Convert a commit line."""
        result = commit[1:-1].split(",", 2)
        result[1] = datetime.datetime.fromisoformat(result[1])
        return result

    # print(file_path, str(file_path), shlex.split(str(file_path), posix=False))
    commits = subprocess.run(
        shlex.split(f'git log --pretty="%H,%aI,%s" {str(file_path)}', posix=False),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [convert_commit(commit) for commit in commits.splitlines()]
