from typing import List

from emoji import emojize

from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.commit.commit_error import BodyError
from lupin_grognard.core.config import EMOJI_CHECK, EMOJI_CROSS


class CommitReporter(Commit):
    def __init__(self, commit: Commit):
        super().__init__(commit=commit.commit)

    def display_valid_title_report(self) -> None:
        print(emojize(f"{EMOJI_CHECK} Commit {self.hash[:6]}: {self.title}"))

    def display_invalid_title_report(self, error_message) -> None:
        print(emojize(f"{EMOJI_CROSS} Commit {self.hash[:6]}: {self.title}"))
        print(f"   {error_message}")

    def display_body_report(self, body_error: BodyError) -> None:
        print(emojize(f"{EMOJI_CROSS} Error in message discription:"))

        for message in body_error.is_conventional:
            print(f"    The line can't start with a conventional commit: '{message}'")
        for message in body_error.descr_is_too_short:
            print(f"    Text is too short in the commit description: '{message}'")

        if body_error.num_empty_line == 1:
            print("    Found an empty line in the commit description")
        elif body_error.num_empty_line > 1:
            print(
                f"    Found {body_error.num_empty_line} empty lines in the commit description"
            )

        if body_error.invalid_body_length:
            print("    The description should not exceed 20 lines")

        if body_error.invalid_jama_refs:
            if len(body_error.invalid_jama_refs) == 1:
                print(
                    (
                        f"    Found that one JAMA reference was invalid: {body_error.invalid_jama_refs[0]}"
                    )
                )
            else:
                print(
                    (
                        "    Found that several JAMA references were "
                        f"invalid: {', '.join(body_error.invalid_jama_refs)}"
                    )
                )

        if body_error.duplicate_jama_refs:
            if len(body_error.duplicate_jama_refs) == 1:
                print(
                    (
                        f"    Found duplicate JAMA reference: {body_error.duplicate_jama_refs[0]}"
                    )
                )
            else:
                print(
                    (
                        f"    Found duplicate JAMA references: {', '.join(body_error.duplicate_jama_refs)}"
                    )
                )

        if body_error.impact_tag_is_missing:
            print(
                (
                    "    Commits of type 'fixbug' must contain in their description a line starting with 'IMPACT:' "
                    "that describes the impact of the fix."
                )
            )

        if body_error.impact_content_line_is_short:
            print("    The details provided in the 'IMPACT:' section is too short.")

    def display_merge_info(self) -> None:
        print(f"   - Merged on {self.author_date} by {self.author}, {self.author_mail}")
        print(
            f"   - Closes issue: {self.closes_issues if self.closes_issues else 'Not found'}"
        )
        print(f"   - Commit title: {self.title}")

    def display_valid_merge_report(self, approvers: List[str]) -> None:
        if len(approvers) == 1:
            print(
                emojize(
                    f"{EMOJI_CHECK} Merge commit {self.hash[:6]}: Approver: {approvers[0]}"
                )
            )
        else:
            many_pprovers = ", ".join(approvers[:-1]) + " and " + approvers[-1]
            print(
                emojize(
                    f"{EMOJI_CHECK} Merge commit {self.hash[:6]}: Approvers: {many_pprovers}"
                )
            )
        self.display_merge_info()

    def display_merge_report_with_no_approver_option(self) -> None:
        print(emojize(f"{EMOJI_CHECK} Merge commit {self.hash[:6]}:"))
        self.display_merge_info()

    def display_merge_approver_same_author_child_commit(
        self, author_child_commit_same_mr_approver
    ) -> None:
        if len(author_child_commit_same_mr_approver) > 1:
            print(
                emojize(
                    (
                        f"{EMOJI_CROSS} Merge commit {self.hash[:6]}: "
                        f"The authors of the child commit '{', '.join(author_child_commit_same_mr_approver)}' "
                        "also approves the merge commit."
                    )
                )
            )
        else:
            print(
                emojize(
                    (
                        f"{EMOJI_CROSS} Merge commit {self.hash[:6]}: "
                        f"The author of the child commits '{author_child_commit_same_mr_approver[0]}' "
                        "also approve the merge commit."
                    )
                )
            )
        self.display_merge_info()

    def display_merge_report_no_approver(self) -> None:
        print(emojize(f"{EMOJI_CROSS} Merge commit {self.hash[:6]}: No approver found"))
        self.display_merge_info()
