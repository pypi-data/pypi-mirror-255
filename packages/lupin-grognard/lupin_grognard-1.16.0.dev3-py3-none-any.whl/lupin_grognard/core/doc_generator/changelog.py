from typing import Any, Dict, List, Tuple, Union

from lupin_grognard.core.commit.commit import Commit, classify_commits_by_version
from lupin_grognard.core.config import JAMA_TAG
from lupin_grognard.core.doc_generator.jinja_generator import JinjaGenerator
from lupin_grognard.core.git import Git
from lupin_grognard.core.tools.log_utils import info
from lupin_grognard.core.tools.utils import get_current_branch_name


class Changelog(JinjaGenerator):
    def __init__(self, commits: List[Commit]):
        self.commits = commits
        self.git = Git()

    def generate(self, path: str) -> None:
        """Generate changelog"""
        self.git.ensure_not_shallow_clone()

        project_details = self._get_project_details()
        classified_commits = self._classify_commits()
        self._generate_file(
            path=path,
            file_name="changelog.md",
            context={
                "version_details": classified_commits,
                "project_details": project_details,
            },
        )

    def _generate_file(self, path: str, file_name: str, context: Dict) -> None:
        return super()._generate_file(path, file_name, context)

    def _get_project_details(self) -> Dict[str, Union[str, int]]:
        project_url = self.git.get_remote_origin_url()
        project_name = project_url.split("/")[-1]
        info(msg=f"Collecting data from {project_name}")
        branch_name = get_current_branch_name()
        commit_count = self._count_commits()
        first_commit_date = self.git.get_first_commit_date()
        last_commit_date = self.git.get_last_commit_date()
        return {
            "name": project_name,
            "url": project_url,
            "branch_name": branch_name,
            "commit_count": commit_count,
            "first_commit_date": first_commit_date,
            "last_commit_date": last_commit_date,
        }

    def _count_commits(self) -> int:
        number_of_commits = 0
        for commit in self.commits:
            if not commit.is_gitlab_merge_commit():
                number_of_commits += 1
        return number_of_commits

    def _classify_commits(self) -> List[Dict[str, Any]]:
        """
        Classify commits by version and by type and scope
        Returns:
            ListList[Dict[str, Any]]: List of version with commits classified by type and scope

            Example:
            [
                {
                    "version": "v1.0.0",
                    "date": "2020-02-20",
                    "commits": {
                        "feature": {
                            "added": [
                                {
                                    "title": "Add a new feature",
                                    "description": ["line 1", "line 2"],
                                    "gitlab_issue_id": 1,
                                    "gitlab_issue_url": "https://gitlab.com/-/issues/1",
                                }
                            ],
                            "changed": [
                                {
                                    "title: "Change a new feature",
                                    "description": None,
                                    "gitlab_issue_id": 2,
                                    "gitlab_issue_url": "https://gitlab.com/-/issues/2",
                                }
                            ],
                            "removed": [
                                {
                                    "title: "Remove a new feature",
                                    "description": None,
                                }
                            ],
                        },
                        "fixbug": [
                            {
                                "title: "Fix a bug",
                                "description": None,
                            }
                        ],
                        "other": [
                            {
                                "title: "Other commit",
                                "description": None,
                                "gitlab_issue_id": 3,
                                "gitlab_issue_url": "https://gitlab.com/-/issues/3",
                            }
                        ],
                        "unspecified": [
                            {
                                "title: "Unspecified commit",
                                "description": None,
                                "gitlab_issue_id": 4,
                                "gitlab_issue_url": "https://gitlab.com/-/issues/4",
                            }
                        ],
                    },
                },
            ]
        """
        versioned_commits = classify_commits_by_version(self.commits, self.git)
        for v in versioned_commits:
            classified_commits = self._classify_commits_by_type_and_scope(v["commits"])
            v["commits"] = classified_commits
        self._display_number_of_commits_found_for_changelog(
            versioned_commits=versioned_commits
        )
        return versioned_commits

    def _separate_jama_ref(self, commit: Commit) -> Tuple[List[str], str]:
        """Separate jama reference from commit description

        :param commit: Commit object
        :type commit: Commit
        :return: Tuple of description without jama reference and jama reference
        :rtype: Tuple[List[str], str]
        """
        body_without_jama_ref = []
        jama_ref = ""
        if commit.body:
            for line in commit.body:
                if line.startswith(JAMA_TAG):
                    jama_ref = line.replace(JAMA_TAG, "").strip()
                else:
                    body_without_jama_ref.append(line)
        if jama_ref:
            return body_without_jama_ref, jama_ref
        return commit.body, ""

    def _append_title_and_description_with_matched_issue(
        self, commits: List[str], commit: Commit, issue_number: str
    ) -> None:
        """Append title without type and scope for feat and fixbug commit type,
        append title for other commit type. Append description if any
        and append issue number and url if issue number is found"""
        if commit.type == "feat" or commit.type == "fixbug":
            commit_title = commit.title_without_type_scope
        else:
            commit_title = commit.title

        description, jama_ref = self._separate_jama_ref(commit=commit)

        if not issue_number:
            commits.append(
                {
                    "title": commit_title,
                    "description": description,
                    **({"jama_ref": jama_ref} if jama_ref else {}),
                }
            )
        else:
            url = f"{self.git.get_remote_origin_url()}/-/issues/{issue_number}"
            commits.append(
                {
                    "title": commit_title,
                    "description": description,
                    **({"jama_ref": jama_ref} if jama_ref else {}),
                    "gitlab_issue_id": issue_number,
                    "gitlab_issue_url": url,
                }
            )

    def _classify_commits_by_type_and_scope(
        self, commits: List[Commit]
    ) -> Dict[str, Union[Dict[str, List[str]], List[str]]]:
        """Classify commits by type and scope and exclude merge commits"""
        commits_feat_add, commits_feat_change, commits_feat_remove = [], [], []
        commits_fixbug, commits_other, commits_unspecified = [], [], []
        for commit in commits:
            match (commit.type, commit.scope):
                case ("feat", "(add)"):
                    self._append_title_and_description_with_matched_issue(
                        commits=commits_feat_add,
                        commit=commit,
                        issue_number=commit.mr_details.associated_closed_issue,
                    )
                case ("feat", "(change)"):
                    self._append_title_and_description_with_matched_issue(
                        commits=commits_feat_change,
                        commit=commit,
                        issue_number=commit.mr_details.associated_closed_issue,
                    )
                case ("feat", "(remove)"):
                    self._append_title_and_description_with_matched_issue(
                        commits=commits_feat_remove,
                        commit=commit,
                        issue_number=commit.mr_details.associated_closed_issue,
                    )
                case ("fixbug", None):
                    self._append_title_and_description_with_matched_issue(
                        commits=commits_fixbug,
                        commit=commit,
                        issue_number=commit.mr_details.associated_closed_issue,
                    )
                case (_, _) if commit.type is not None:
                    self._append_title_and_description_with_matched_issue(
                        commits=commits_other,
                        commit=commit,
                        issue_number=commit.mr_details.associated_closed_issue,
                    )
                case (_, _) if commit.type is None:
                    if not commit.is_gitlab_merge_commit():
                        self._append_title_and_description_with_matched_issue(
                            commits=commits_unspecified,
                            commit=commit,
                            issue_number=commit.mr_details.associated_closed_issue,
                        )
        return self._create_commit_dict(
            commits_feat_add=commits_feat_add,
            commits_feat_change=commits_feat_change,
            commits_feat_remove=commits_feat_remove,
            commits_fixbug=commits_fixbug,
            commits_other=commits_other,
            commits_unspecified=commits_unspecified,
        )

    def _create_commit_dict(
        self,
        commits_feat_add: List[str],
        commits_feat_change: List[str],
        commits_feat_remove: List[str],
        commits_fixbug: List[str],
        commits_other: List[str],
        commits_unspecified: List[str],
    ) -> Dict[str, Union[Dict[str, List[str]], List[str]]]:
        result = {}
        if commits_feat_add or commits_feat_change or commits_feat_remove:
            result["feature"] = {}
            if commits_feat_add:
                result["feature"]["added"] = commits_feat_add
            if commits_feat_change:
                result["feature"]["changed"] = commits_feat_change
            if commits_feat_remove:
                result["feature"]["removed"] = commits_feat_remove
        if commits_fixbug:
            result["fixbug"] = commits_fixbug
        if commits_other:
            result["other"] = commits_other
        if commits_unspecified:
            result["unspecified"] = commits_unspecified
        return result

    def _display_number_of_commits_found_for_changelog(
        self, versioned_commits: List[Dict[str, List[str]]]
    ) -> None:
        total = 0
        for v in versioned_commits:
            total += len(v.get("commits", {}).get("feature", {}).get("added", []))
            total += len(v.get("commits", {}).get("feature", {}).get("changed", []))
            total += len(v.get("commits", {}).get("feature", {}).get("removed", []))
            total += len(v.get("commits", {}).get("fixbug", []))
            total += len(v.get("commits", {}).get("other", []))
            total += len(v.get("commits", {}).get("unspecified", []))
        info(msg=f"Found {total} commits")
