import sys
from typing import List

from lupin_grognard.core.commit.commit import Commit, fill_authors_for_mr_commits
from lupin_grognard.core.commit.commit_error import ErrorCount
from lupin_grognard.core.commit.commit_validator import (
    CommitValidator,
    CommitCheckModes,
)
from lupin_grognard.core.tools.log_utils import die


def check_max_allowed_major_commits(
    commits: List[Commit], major_commit_limit: int
) -> bool:
    """Check if the number of major commits in `commits` exceeds `major_commit_limit`.

    Args:
        commits (List[Commit]): The list of commit object.
        major_commit_limit (int): The maximum number of major commits allowed.

    Returns:
        bool: True if the number of major commits is within the limit, else False.
    """
    if major_commit_limit == 0:  # --all option
        return True

    major_commit_count = 0
    for commit in commits:
        if commit.is_major_commit():
            major_commit_count += 1

    if major_commit_count > major_commit_limit:
        print(
            f"Error: found {major_commit_count} major commits to check in the "
            f"current branch while the maximum allowed number is {major_commit_limit}"
        )
        sys.exit(1)
    return True


def check_same_author_from_current_branch(commits: List[Commit]) -> None:
    """Check that all commits to be checked on the current branch come from the same author.

    Args:
        commits (List[Commit]): The list of commits to check.

    Returns:
        None
    """
    commits_author = set(commit.author_mail for commit in commits).union(
        commit.committer_mail for commit in commits
    )
    if len(commits_author) > 1:
        die(
            msg=(
                "Found multiple authors for the commits in the current branch: please do not mix "
                "commits from different authors in the same merge request."
            )
        )


def check_commit(
    commits: List[Commit],
    check_mode: CommitCheckModes,
    permissive_mode: bool,
    no_approvers: bool,
) -> None:
    """
    check_commit performs validation checks on each commit.
    If merge_option is set to 0, the function checks that merge commits
    have approvers.
    If merge_option is 1, the function only validates the title for a merge,
    the title and the body of the commit if it is a simple commit.
    The function also calls the error_report method of the ErrorCount
    class to output any errors found during validation.
    If any errors are found, it will call sys.exit(1)
    Args:
        commits (List): List of commits to check
        merge_option (int): 0 or 1
        permissive_mode (bool): If True, the function will not call sys.exit(1)
    """
    error_counter = ErrorCount()
    commits = [
        CommitValidator(
            commit=c,
            error_counter=error_counter,
            check_mode=check_mode,
            no_approvers=no_approvers,
        )
        for c in commits
    ]

    if check_mode == CommitCheckModes.CHECK_ALL_COMMITS:
        commits = fill_authors_for_mr_commits(commits=commits)

    for commit in commits:
        commit.perform_checks()

    error_counter.error_report(
        permissive_mode=permissive_mode,
    )
