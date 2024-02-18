import os


def get_ci_mr_target_branch() -> str:
    mr_target_branch = os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
    if not mr_target_branch:
        return ""
    return mr_target_branch
