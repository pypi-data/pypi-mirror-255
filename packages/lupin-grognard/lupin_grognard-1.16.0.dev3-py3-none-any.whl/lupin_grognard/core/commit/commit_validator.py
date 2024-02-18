import re
import string
from enum import Enum
from typing import List, Tuple

from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.commit.commit_error import BodyError, ErrorCount
from lupin_grognard.core.commit.commit_reporter import CommitReporter
from lupin_grognard.core.config import (
    COMMIT_TYPE_MUST_HAVE_SCOPE,
    COMMIT_TYPE_MUST_NOT_HAVE_SCOPE,
    COMMIT_WITH_SCOPE,
    INITIAL_COMMIT,
    IMPACT_TAG,
    JAMA_REGEX,
    JAMA_TAG,
    MAIN_BRANCHES_LIST,
    MAX_COMMIT_DESCR_LINES,
    MIN_COMMIT_DESCR_LENTH,
    PATTERN,
    TITLE_FAILED,
)


class CommitCheckModes(Enum):
    # Check all commits starting from the initial commit
    CHECK_ALL_COMMITS = 1
    # Check all commits of the current branch (until the last merge)
    CHECK_CURRENT_BRANCH_ONLY = 2


def define_commits_check_mode(
    current_branch: str, ci_mr_target_branch: str, CHECK_ALL_COMMITS_flag: bool
) -> CommitCheckModes:
    if (
        current_branch in MAIN_BRANCHES_LIST
        or ci_mr_target_branch in MAIN_BRANCHES_LIST
        or CHECK_ALL_COMMITS_flag
    ):
        return CommitCheckModes.CHECK_ALL_COMMITS
    else:
        return CommitCheckModes.CHECK_CURRENT_BRANCH_ONLY


def define_permissive_mode(
    check_mode: CommitCheckModes,
    permissive_mode: bool,
) -> bool:
    """
    Ensures that permissive mode can be enabled on a CommitCheckModes.CHECK_ALL_COMMITS
    if the --permissive flag is specified.

    Args:
        check_mode (CommitCheckModes): The check mode.
        permissive_mode (bool): The permissive flag.
    """
    return check_mode == CommitCheckModes.CHECK_ALL_COMMITS and permissive_mode


class CommitValidator(Commit):
    def __init__(
        self,
        commit: Commit,
        error_counter: ErrorCount,
        check_mode: CommitCheckModes,
        no_approvers: bool = False,
    ):
        super().__init__(commit=commit.commit)
        self.reporter = CommitReporter(commit=commit)
        self.error_counter = error_counter
        self.check_mode = check_mode
        self.no_approvers = no_approvers

    def perform_checks(self) -> None:
        if self.check_mode == CommitCheckModes.CHECK_ALL_COMMITS:
            if self.is_gitlab_merge_commit():
                if not self.no_approvers:
                    if not self._validate_commit_merge():
                        self.error_counter.increment_merge_error()
                else:
                    self.reporter.display_merge_report_with_no_approver_option()
            else:
                if not self._validate_commit_title():
                    self.error_counter.increment_title_error()
                if not self._validate_body():
                    self.error_counter.increment_body_error()

        if self.check_mode == CommitCheckModes.CHECK_CURRENT_BRANCH_ONLY:
            if not self._validate_commit_title():
                self.error_counter.increment_title_error()
            if not self.is_gitlab_merge_commit():
                if not self._validate_body():
                    self.error_counter.increment_body_error()

    def _validate_commit_title(self) -> bool:
        if self._validate_commit_message(self.title, self.type, self.scope):
            self.reporter.display_valid_title_report()
            return True
        else:
            return False

    def _validate_body(self) -> bool:
        self.body_error = BodyError(
            is_conventional=[],
            descr_is_too_short=[],
            num_empty_line=0,
            invalid_body_length=False,
            duplicate_jama_refs=[],
            invalid_jama_refs=False,
            impact_tag_is_missing=False,
            impact_content_line_is_short=False,
        )

        self._validate_tags_in_description()

        if self.body:
            if not self._is_commit_body_length_valid():
                self.body_error.invalid_body_length = True

            for message in self.body:
                if self._is_conventional_commit_body_valid(message=message):
                    self.body_error.is_conventional.append(
                        message
                    )  # must not start with a conventional message
                if not self._is_commit_body_line_length_valid(message=message):
                    if message != "":
                        self.body_error.descr_is_too_short.append(message)
                    else:
                        self.body_error.num_empty_line += 1
        if any(
            [
                self.body_error.is_conventional,
                self.body_error.descr_is_too_short,
                self.body_error.num_empty_line > 0,
                self.body_error.invalid_body_length,
                self.body_error.duplicate_jama_refs,
                self.body_error.invalid_jama_refs,
                self.body_error.impact_tag_is_missing,
                self.body_error.impact_content_line_is_short,
            ]
        ):
            self.reporter.display_body_report(self.body_error)
            return False
        return True

    def _validate_tags_in_description(self):
        if self._check_if_tag_exists(JAMA_TAG):
            self._validate_jama_referencing()

        if self.type == "fixbug":
            self._validate_impact_referencing_for_fixbug()

    def _check_if_tag_exists(self, tag: str) -> bool:
        if self.body:
            return any([line.startswith(tag) for line in self.body])

    def _validate_jama_referencing(self) -> None:
        """
        Validate JAMA referencing in the body text

        - Check if the signature line starts with a valid JAMA reference
        - Validate individual JAMA items by detecting duplicates and invalid references
        """
        (
            duplicate_jama_refs,
            invalid_jama_refs,
        ) = self._validate_jama_items()
        if duplicate_jama_refs:
            self.body_error.duplicate_jama_refs = duplicate_jama_refs
        if invalid_jama_refs:
            self.body_error.invalid_jama_refs = invalid_jama_refs

    def _validate_impact_referencing_for_fixbug(self) -> None:
        """
        Validate 'impact' referencing in the body text for fixbug commits type.

        - Check if the signature line starts with 'IMPACT:'
        - Check if the signature line is more than 10 characters long
        """
        if self._check_if_tag_exists(IMPACT_TAG):
            impact_ref_line = self._get_line_starting_with_tag(IMPACT_TAG)
            impact_line_content = impact_ref_line.replace(IMPACT_TAG, "").strip()
            if len(impact_line_content) <= 10:
                self.body_error.impact_content_line_is_short = True
        else:
            self.body_error.impact_tag_is_missing = True

    def _get_line_starting_with_tag(self, tag: str) -> str:
        """
        Get line starting with a given tag

        Args:
            tag (str): The tag to check for

        Returns:
            str: The line starting with the given tag
        """
        if self.body:
            for line in self.body:
                if line.startswith(tag):
                    return line
        return ""

    def _validate_jama_items(self) -> Tuple[List[str], List[str]]:
        """
        Validate individual JAMA items
        - Check if the JAMA item matches the JAMA reference pattern defined by JAMA_REGEX
        - Check for duplicate JAMA items and record them
        - Check for invalid JAMA items and record them

        Args:
            jama_ref_line (str): The line starting with 'JAMA:'

        Returns:
            A tuple containing two lists:
            - duplicate_jama_refs (List[str]): List of duplicate JAMA items
            - invalid_jama_refs (List[str]): List of invalid JAMA items
        """
        jama_ref_line = self._get_line_starting_with_tag(JAMA_TAG)
        content_jama_ref_line = jama_ref_line.replace(JAMA_TAG, "").strip()
        jama_refs = [
            ref for ref in re.split(r"[\s,]+", content_jama_ref_line) if ref != ""
        ]
        unique_jama_refs = set()
        duplicate_jama_refs = []
        invalid_jama_refs = []

        for jama_ref in jama_refs:
            if not re.match(JAMA_REGEX, jama_ref):
                invalid_jama_refs.append(jama_ref)
            elif jama_ref in unique_jama_refs and jama_ref not in duplicate_jama_refs:
                duplicate_jama_refs.append(jama_ref)
            else:
                unique_jama_refs.add(jama_ref)
        return duplicate_jama_refs, invalid_jama_refs

    def _validate_commit_message(self, commit_msg: str, type: str, scope: str) -> bool:
        if self._is_special_commit(commit_msg=commit_msg):
            return True

        match type:
            case None:
                self.reporter.display_invalid_title_report(error_message=TITLE_FAILED)
                return False
            case match_type if (match_type := type) in COMMIT_WITH_SCOPE:
                return self._validate_commit_message_for_specific_type(
                    scope=scope, type=match_type
                )
            case _:
                return self._validate_commit_message_for_generic_type(
                    type=type, scope=scope
                )

    def _is_conventional_commit_body_valid(self, message: str) -> bool:
        """Checks if the line in the body of a commit message starts with a conventional commit"""
        return bool(re.match(PATTERN, message))

    def _is_commit_body_line_length_valid(self, message: str) -> bool:
        """Checks if the body line is not less than MIN_COMMIT_DESCR_LENTH"""
        return len(message) >= MIN_COMMIT_DESCR_LENTH

    def _is_commit_body_length_valid(self) -> bool:
        """Checks if the body length is not greater than MAX_COMMIT_DESCR_LINES"""
        return len(self.body) <= MAX_COMMIT_DESCR_LINES

    def _is_special_commit(self, commit_msg: str) -> bool:
        """Checks if the commit is a Merge or in the list of initial commits"""
        return commit_msg.startswith("Merge") or commit_msg in INITIAL_COMMIT

    def _validate_commit_merge(self) -> bool:
        if len(self.approvers) < 1:
            self.reporter.display_merge_report_no_approver()
            return False
        else:
            if self._is_mr_approver_also_author():
                return False
            else:
                self.reporter.display_valid_merge_report(approvers=self.approvers)
                return True

    def _is_mr_approver_also_author(self) -> bool:
        """
        Check if the MR approver is also an author of the commit(s) associated with the MR.
        """
        rejected_user_emails = self._find_mr_approvers_that_are_also_authors()
        if rejected_user_emails:
            self.reporter.display_merge_approver_same_author_child_commit(
                rejected_user_emails
            )
            return True
        return False

    def _find_mr_approvers_that_are_also_authors(self) -> list[str]:
        """Find MR approvers that are also authors of the commit(s) associated with the MR."""
        rejected_user_emails = []
        for author in self.mr_details.associated_commits_authors:
            if author in self.approvers_mail:
                rejected_user_emails.append(author)
        return rejected_user_emails

    def _validate_commit_message_for_specific_type(self, scope: str, type: str) -> bool:
        """
        Validates the scope for a COMMIT_WITH_SCOPE list.
        If the scope is (change) then the commit title and description
        must not contain the words 'remove' or 'removed'
        """
        if scope is None or scope not in ["(add)", "(change)", "(remove)"]:
            self.reporter.display_invalid_title_report(
                error_message=COMMIT_TYPE_MUST_HAVE_SCOPE.format(type=type)
            )
            return False
        else:
            if scope == "(change)":
                return self._validate_change_scope_without_remove_word()
            return True

    def _remove_punctuation_around_words(self, words: List[str]) -> List[str]:
        """Removes punctuation around words"""
        return [word.strip(string.punctuation) for word in words if word != ""]

    def _contains_remove_words_in_commit_title(self) -> bool:
        """Checks if the title contains the words 'remove' or 'removed'"""
        words = self.title_without_type_scope.lower().split(" ")
        words_without_punctuation = self._remove_punctuation_around_words(words)
        return any(word in words_without_punctuation for word in ["remove", "removed"])

    def _validate_change_scope_without_remove_word(self):
        """
        Validate that a commit with the scope (change) does not contain the words
        'remove' and 'removed' in the title
        """
        if self._contains_remove_words_in_commit_title():
            self.reporter.display_invalid_title_report(
                error_message=(
                    "Found a commit title that talks about removing something while given "
                    "scope is 'change': change scope to 'remove' or update the commit title"
                )
            )
            return False
        return True

    def _validate_commit_message_for_generic_type(self, type, scope: str) -> bool:
        """Validates other commit types do not contain a scope"""
        if scope is None:
            return True
        else:
            error_message = COMMIT_TYPE_MUST_NOT_HAVE_SCOPE.format(type, type)
            self.reporter.display_invalid_title_report(error_message=error_message)
            return False
