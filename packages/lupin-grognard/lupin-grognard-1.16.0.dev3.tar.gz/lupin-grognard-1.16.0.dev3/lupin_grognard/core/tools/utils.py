import logging
import os
import re
import sys
from typing import List

from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.config import (
    COMMIT_DELIMITER,
    INITIAL_COMMIT,
    MAJOR_COMMIT_TYPES,
)
from lupin_grognard.core.git import Git


def read_file(file: str) -> str:
    with open(f"{file}", "r", encoding="utf-8") as file:
        data = file.read()
        return data


def write_file(file: str, content: str):
    with open(f"{file}", "w", encoding="utf-8") as outfile:
        outfile.write(content)


def get_version():
    """get version from setup.cfg file and
    update __version__ in lupin_grognard.__init__.py
    """
    setup_cfg = read_file("setup.cfg")
    _version = re.search(
        r"(^version = )(\d{1,2}\.\d{1,2}\.\d{1,2})(\.[a-z]{1,})?(\d{1,2})?",
        setup_cfg,
        re.MULTILINE,
    )
    version = ""
    for group in _version.group(2, 3, 4):
        if group is not None:
            version = version + str(group)
    content = f'__version__ = "{version}"\n'
    write_file(file="lupin_grognard/__init__.py", content=content)
    return version


def get_current_branch_name() -> str:
    branch_name = Git().get_branch_name()
    # branch name can be messing if running in CI
    if not branch_name:
        branch_name = os.getenv("CI_COMMIT_BRANCH")
    if not branch_name:
        branch_name = os.getenv("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME")
    if not branch_name:
        return ""
    return branch_name


def display_supported_commit_types() -> None:
    commit_type = [
        "build",
        "bump",
        "ci",
        "deps(add|change|remove)",
        "docs",
        "enabler",
        "feat(add|change|remove)",
        "fixbug",
        "refactor",
        "test",
    ]
    print("Supported commit types: " + ", ".join(commit_type))
    print(
        "Only one commit of a major type is allowed per merge branch: "
        f'{", ".join(MAJOR_COMMIT_TYPES[:-1])}, or {MAJOR_COMMIT_TYPES[-1]}.'
    )


def display_current_branch_name(current_branch_name: str) -> None:
    if current_branch_name:
        print(f"Current branch name is '{current_branch_name}'")
    else:
        print("Current branch name is not available")


def display_number_of_commits_to_check(commits: List[Commit]):
    number_commits_to_check = len(commits)
    if number_commits_to_check == 0:
        print("0 commit to check")
        sys.exit(0)
    elif number_commits_to_check == 1:
        print(f"Found {number_commits_to_check} commit to check:")
    else:
        print(f"Found {number_commits_to_check} commits to check:")


def generate_commit_list(commits_string: str) -> List[Commit]:
    """Geneartes the list of commits from Git().get_log().stdout value"""
    return [
        Commit(commit)
        for commit in commits_string.split(COMMIT_DELIMITER)
        if len(commit) > 0
    ]


def generate_commits_range_to_check(
    branch_list: List[str],
    commits: List[Commit],
    ci_mr_target_branch_name: str = "",
    initial_commits: List[str] = INITIAL_COMMIT,
) -> List:
    """
    generates a list of message ranges starting with INITIAL_COMMIT
    or the last merge into a branch contained in the branch list

    If ci_mr_target_branch_name is a main one, the function returns the commit range
    starting from the second merge found.

    If ci_mr_target_branch_name is a dev branches, the function returns the commit range
    starting with the second merge found and ending with the first commit after the first merge.
    """
    merge_count = 0
    merge_result_pipeline_main_branches = False
    merge_result_pipeline_dev_branches = False

    for index, commit in enumerate(commits):
        if commit.is_gitlab_merge_commit() and index == 0:
            if ci_mr_target_branch_name in ["main", "master"]:
                merge_result_pipeline_main_branches = True
            elif ci_mr_target_branch_name in ["dev", "develop", "development"]:
                merge_result_pipeline_dev_branches = True

        if merge_result_pipeline_main_branches:
            if commit.is_gitlab_merge_commit():
                merge_count += 1
                if merge_count == 2:
                    return commits[:index]  # with first merge commit
            elif commit.title in initial_commits:
                return commits[:index]
        elif merge_result_pipeline_dev_branches:
            if commit.is_gitlab_merge_commit():
                merge_count += 1
                if merge_count == 2:
                    return commits[1:index]  # skip first merge commit
            elif commit.title in initial_commits:
                return commits[1:index]
        else:
            if commit.is_gitlab_merge_commit():
                for branch in branch_list:
                    if commit.title.endswith(f"into '{branch}'"):
                        return commits[:index]
            elif commit.title in initial_commits:
                return commits[:index]
    return list()


def configure_logging():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO
    )
