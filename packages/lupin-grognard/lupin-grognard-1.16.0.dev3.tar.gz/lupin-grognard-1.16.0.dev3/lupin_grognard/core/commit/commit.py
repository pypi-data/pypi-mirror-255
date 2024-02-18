import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from lupin_grognard.core.config import (
    INITIAL_COMMIT,
    MAJOR_COMMIT_TYPES,
    PATTERN,
)
from lupin_grognard.core.git import Git
from lupin_grognard.core.tools.log_utils import info


class GitLabMergeRequestDetails:
    def __init__(self):
        self.associated_closed_issue: Optional[str] = None
        self.associated_approvers: Optional[str] = None
        self.associated_approvers_date: Optional[str] = None
        self.associated_commits_authors: Optional[List[str]] = list()


class Commit:
    def __init__(self, commit: str):
        self.commit = commit
        self.parents: Optional[List[str]] = None
        self.mr_details: Optional[GitLabMergeRequestDetails] = (
            GitLabMergeRequestDetails()
        )

    @property
    def hash(self) -> str:
        return self._extract(start="hash>>")

    @property
    def author(self) -> str:
        return self._extract(start="author>>")

    @property
    def author_mail(self) -> str:
        return self._extract(start="author_mail>>")

    @property
    def author_date(self) -> str:
        timestamp = self._extract(start="author_date>>")
        date_object = datetime.fromtimestamp(int(timestamp))
        return date_object.strftime("%d/%m/%y %I:%M %p")

    @property
    def committer_mail(self) -> str:
        return Git().get_committer_mail(self.hash)

    @property
    def title(self) -> str:
        return self._extract(start="title>>")

    @property
    def title_without_type_scope(self) -> str:
        """Returns commit title without type and scope"""
        start = self.title.find(":") + 1
        title = self.title[start:].strip()
        return title[0].upper() + title[1:]

    @property
    def type(self) -> str | None:
        """Returns the conventional commit type if present"""
        match = re.match(PATTERN, self.title)
        return match.groups()[0] if match else None

    @property
    def scope(self) -> str | None:
        """Returns the conventional commit scope if present"""
        match = re.match(PATTERN, self.title)
        return match.groups()[1] if match else None

    @property
    def body(self) -> List[str] | None:
        body = self._extract(start="body>>", end="<<body")
        if body == "":
            return None

        # remove last \n if present cause 'git commit -m "description"' or other git software adds it automatically
        body = body.rstrip("\n")

        return [
            self._remove_markdown_list_markers(message) for message in body.split("\n")
        ]

    @property
    def closes_issues(self) -> List | None:
        """Returns the list of issues closed by the commit"""
        if self.body:
            for line in self.body:
                if line.startswith("Closes #"):  # Closes #465, #190 and #400
                    return re.findall(r"#(\d+)", line)  # ['465', '190', '400']
        return None

    @property
    def approvers(self) -> List[str]:
        approvers = []
        if self.body:
            for line in self.body:
                if line.startswith("Approved-by: "):
                    approver = line.split("Approved-by: ")[1]
                    approver = approver.translate(str.maketrans("", "", "<>"))
                    approvers.append(approver)
            return approvers
        return list()

    @property
    def approvers_name(self) -> List[str]:
        if self.approvers:
            return [" ".join(approver.split(" ")[:-1]) for approver in self.approvers]
        return list()

    @property
    def approvers_mail(self) -> List[str]:
        if self.approvers:
            return [approver.split(" ")[-1] for approver in self.approvers]
        return list()

    def _extract(self, start: str, end: str = "\n") -> str:
        start_index = self.commit.find(start) + len(start)
        return self.commit[start_index : self.commit.find(end, start_index)]

    def is_gitlab_merge_commit(self) -> bool:
        return self.title.startswith("Merge branch")

    def is_major_commit(self) -> bool:
        """Returns if the commit is a major commit type"""
        return self.type in MAJOR_COMMIT_TYPES

    def is_not_initial_commit(self) -> bool:
        """Returns if the commit is not an initial commit"""
        return self.title not in INITIAL_COMMIT

    def _remove_markdown_list_markers(self, message: str) -> str:
        return message.lstrip("-* ")


def add_additional_commit_info(commits: List["Commit"]) -> List["Commit"]:
    """
    Returns a list of Commit objects with additional information such as closed issues, approvers,
    and date it was approved for each commit from associated merge request

    :param commits: List of Commit objects
    :return: List of Commit objects with additional information

    additional information:
        self.mr_details.associated_closed_issue = None if merge commit else "1"
        self.mr_details.associated_approvers = None if merge commit else "John Doe"
        self.mr_details.associated_approvers_date = None if merge commit else "10/03/23 06:48 PM"
        self.parrents = ["hash1", "hash2"] if merge commit else ["hash1"]
    """
    commits = get_parents_for_commits(commits=commits)
    merge_commits_hash, merge_commits_mapping = get_data_from_merge_commit(
        commits=commits
    )
    commits = add_associated_data_to_commit_from_merge(
        merge_commits_hash=merge_commits_hash,
        merge_commits_mapping=merge_commits_mapping,
        commits=commits,
    )
    return commits


def get_data_from_merge_commit(
    commits: List["Commit"],
) -> Tuple[List[str], Dict[str, Dict[str, Union[str, List[str], str]]]]:
    """
    Return a tuple containing a dictionary with information about merge commits and a list of merge commit hashes.

    The merge commit information dictionary has commit parent hash as keys, and the following information as values:
        - "mr_details.associated_closed_issue": L'id of the gitlab closed issue.
        - "approvers": A list of the usernames who approved the merge commit.
        - "date": The date the merge commit was approved.

    :param commits: A list of Commit objects.
    :type commits: List["Commit"]
    :return:
        - merge_commits_hash, merge_commits_mapping
        - A tuple containing the list of merge commit hashes and a merge commit information dictionary.
    :rtype: Tuple[List[str], Dict[str, Dict[str, Union[str, List[str], str]]]]
    """
    merge_commits_hash = []
    merge_commits_mapping = {}
    for commit in commits:
        if len(commit.parents) == 2:  # check if it is a merge commit
            merge_commits_hash.append(commit.hash)
            if commit.closes_issues:
                merge_commits_mapping[commit.parents[1]] = {
                    "close_issue": commit.closes_issues[0],
                    "approvers": commit.approvers,
                    "date": commit.author_date,
                }
    return merge_commits_hash, merge_commits_mapping


def add_associated_data_to_commit_from_merge(
    merge_commits_hash: List[str],
    merge_commits_mapping: Dict[str, Dict[str, Union[str, List[str], str]]],
    commits: List["Commit"],
) -> List["Commit"]:
    for commit in commits:
        if (
            len(commit.parents) == 1  # check if it is not a merge commit
            and commit.hash in merge_commits_mapping
            and commit.title not in INITIAL_COMMIT
        ):
            commit.mr_details.associated_closed_issue = merge_commits_mapping[
                commit.hash
            ]["close_issue"]
            commit.mr_details.associated_approvers = merge_commits_mapping[commit.hash][
                "approvers"
            ]
            commit.mr_details.associated_approvers_date = merge_commits_mapping[
                commit.hash
            ]["date"]
            if (
                commit.parents[0] not in merge_commits_mapping
                and commit.parents[0] not in merge_commits_hash
            ):  # the commit parent shares the same merge commit
                merge_commits_mapping[commit.parents[0]] = merge_commits_mapping[
                    commit.hash
                ]
    return commits


def fill_authors_for_mr_commits(commits: List["Commit"]) -> List["Commit"]:
    """
    For each merge commit in the list, fill the authors of its children commits
    (that are associated to the merge request).

    Args:
        commits (List[Commit]): The list of commits to check.

    Returns:
        List[Commit]: The modified list of commits with the authors added to each merge commit.
    """

    commits = get_parents_for_commits(commits=commits)

    for commit in commits:
        if commit.is_gitlab_merge_commit():
            add_author_to_merge_request(
                merge_request=commit, hash=commit.parents[1], commits=commits
            )
    return commits


def find_commit_by_hash(hash: str, commits: List["Commit"]) -> Commit:
    """Find a commit in a list of commits by its hash.

    Args:
        hash (str): The hash of the commit to retrieve.
        commits (List[Commit]): The list of commits to search in.

    Returns:
        Commit: The commit with the given hash.
    """
    for commit in commits:
        if commit.hash == hash:
            return commit


def add_author_to_merge_request(
    merge_request: Commit, hash: str, commits: List["Commit"]
) -> None:
    """
    Recursively adds the author of a child commit to the associated merge request.

    Args:
        merge_request (Commit): The merge request to add the author.
        hash (str): The hash of the child commit.
        commits (List[Commit]): The list of commits.

    Returns:
        None
    """
    child_commit = find_commit_by_hash(hash=hash, commits=commits)
    if (
        not child_commit.is_gitlab_merge_commit()
        and child_commit.is_not_initial_commit()
    ):
        merge_request.mr_details.associated_commits_authors.append(
            child_commit.author_mail
        )

        if len(child_commit.parents) == 1:
            add_author_to_merge_request(
                merge_request=merge_request,
                hash=child_commit.parents[0],
                commits=commits,
            )


def get_parents_for_commits(commits: List["Commit"]) -> List["Commit"]:
    """Get the parents for each commit in the list.

    Args:
        commits (List[Commit]): The list of commits.

    Returns:
        List[Commit]: The list of commits with the parents added.
    """
    for commit in commits:
        commit.parents = Git().get_parents(commit_hash=commit.hash)
    return commits


def classify_commits_by_version(
    commits: List[Commit], git: Git
) -> List[Dict[str, List[Commit]]]:
    """
    Classify a list of commits by version.

    Args:
        commits (List[Commit]): A list of Commit objects to classify.
        git (Git): An instance of the Git.

    Returns:
        List[Dict[str, List[Commit]]]: A list of dictionaries, each representing a version
        containing the commits associated with that version.

    This function iterates through a list of commits and classifies them based on the tags
    present in the provided Git instance. It groups the commits by version and returns
    a list of dictionaries where each dictionary contains information about a version
    along with the commits associated with that version.
    """
    versions = []
    current_version = {}
    tag_list = git.get_tags()
    for commit in commits:
        for tag in tag_list:
            if commit.hash in tag[1]:
                info(msg=f"Found tag {tag[0]}")
                commit_tag = tag[0]
                date_tag = tag[2]
                if current_version:
                    versions.append(current_version)
                current_version = {
                    "version": commit_tag,
                    "date": date_tag,
                    "commits": [],
                }
                current_version["commits"].append(commit)
                break
        else:
            if not current_version:
                current_version = {
                    "version": "Unreleased",
                    "date": "",
                    "commits": [],
                }
            current_version["commits"].append(commit)
    if current_version:
        versions.append(current_version)
    return versions
