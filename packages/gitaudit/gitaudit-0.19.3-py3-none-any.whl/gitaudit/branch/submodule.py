"""Submodule Handling
"""

from typing import List
from gitaudit.git.change_log_entry import ChangeLogEntry


def insert_submodule_updates(
    root_change_log: List[ChangeLogEntry],
    path: str,
    sub_change_log: List[ChangeLogEntry],
):
    """
    Insert submodule change log entries into the root change log based on the submodule update SHA.

    Args:
        root_change_log (List[ChangeLogEntry]): A list of ChangeLogEntry objects for the root
            repository.
        path (str): The name of the submodule for which the updates are being added.
        sub_change_log (List[ChangeLogEntry]): A list of ChangeLogEntry objects for the submodule
            repository.

    This function iterates through the submodule change log entries (sub_change_log) and appends
    them to the corresponding root change log entries (root_change_log) based on the submodule
    update SHA. It assumes that the submodule updates in the root change log are using short SHA
    values.
    """
    bump_commits = list(
        filter(
            lambda x: path in x.submodule_updates,
            root_change_log,
        )
    )

    index_bump_commits = -1

    for sub_entry in sub_change_log:
        if index_bump_commits + 1 == len(bump_commits):
            pass
        elif (
            bump_commits[index_bump_commits + 1].submodule_updates[path].to_sha
            in sub_entry.sha
        ):
            index_bump_commits += 1
        else:
            pass

        if index_bump_commits >= 0:
            bump_commits[index_bump_commits].submodule_updates[path].entries.append(
                sub_entry
            )
