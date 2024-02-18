"""Prune changelogs"""

from typing import List, Optional, Union, Dict
from enum import Enum

from pydantic import BaseModel

from gitaudit.git.change_log_entry import ChangeLogEntry
from gitaudit.branch.hierarchy import (
    hierarchy_log_to_linear_log_entry,
)


def match_in_entry(entry: ChangeLogEntry, file_list: List[str]) -> bool:
    """Determines if any numstat entry matches the file list

    Args:
        entry (ChangeLogEntry): Change log entry to be analysed for numstat entries
        file_list (List[str]): The list of file paths used for pruning. If a changelog entry is
            associated with a file in this list, it remains in the pruned changelog.

    Returns:
        bool: True if any numstat entries matches the filelist
    """
    return any(map(lambda x: x.path in file_list, entry.numstat))


def first_parent_prune_by_file_list(
    changelog: List[ChangeLogEntry], file_list: List[str]
):
    """
    Prune entries from the changelog based on a provided file list.

    This function traverses the given changelog, and checks whether each entry
    has any associated file in the provided file list. If an entry does not
    have any associated file in the file list either in its numstat or in its
    submodule updates, the entry is pruned from the changelog.

    Additionally, if a submodule update becomes empty after pruning, it is
    also removed from the changelog entry.

    Parameters
    ----------
    changelog : List[ChangeLogEntry]
        The changelog entries to be pruned. Each entry contains 'numstat'
        and 'submodule_updates' attributes.
    file_list : List[str]
        The list of file paths used for pruning. If a changelog entry is
        associated with a file in this list, it remains in the pruned changelog.

    Returns
    -------
    List[ChangeLogEntry]
        The pruned changelog.

    Notes
    -----
    This function directly modifies the given changelog, rather than creating
    a new one.
    """
    remove_indices = []

    for index, entry in enumerate(changelog):
        entry_to_linlog = hierarchy_log_to_linear_log_entry(entry)
        matches_in_numstat = any(
            map(
                lambda x: match_in_entry(x, file_list),
                entry_to_linlog,
            )
        )

        remove_submodules = []

        for sub_path, sub_module_update in entry.submodule_updates.items():
            sub_module_update.entries = first_parent_prune_by_file_list(
                sub_module_update.entries,
                file_list,
            )

            if not sub_module_update.entries:
                remove_submodules.append(sub_path)

        for sub_path in remove_submodules:
            entry.submodule_updates.pop(sub_path)

        matches_in_submodules = any(
            filter(
                lambda sub: sub.entries,
                entry.submodule_updates.values(),
            )
        )

        if not matches_in_numstat and not matches_in_submodules:
            remove_indices.append(index)

    for index in reversed(remove_indices):
        changelog.pop(index)

    return changelog


class PruneType(str, Enum):
    """
    Enumeration of the different types of branches that can be pruned.
    """

    ROOT = "root"
    LEAF = "leaf"
    SUBMODULE = "submodule"


class PruneableItem(BaseModel):
    """
    Represents an item that can be pruned from a Git branch.

    Attributes:
        prune_type (PruneType): The type of pruning to perform.
        sha (str): The SHA hash of the Git commit.
        entry (ChangeLogEntry): The changelog entry associated with the commit.
        upper_entry (Optional[ChangeLogEntry]): The changelog entry associated with the parent commit, if any.
        upper_index_path (Optional[Union[int, str]]): The index path of the parent commit, if any.
    """

    prune_type: PruneType
    sha: str
    entry: ChangeLogEntry
    upper_entry: Optional[ChangeLogEntry] = None
    upper_index_path: Optional[Union[int, str]] = None


class HierarchyPrune:
    """This class is used for handling and pruning the hierarchy logs.

    Attributes:
        hierarchy_log (List[ChangeLogEntry]): The list of change log entries forming a hierarchy.
        linear_log: The linear version of the hierarchy log.
        sha_to_entry_map (dict): Mapping from SHA to the corresponding change log entry.
        sha_to_parent_map (dict): Mapping from SHA to the parent change log entry.
    """

    def __init__(self, hierarchy_log: List[ChangeLogEntry]) -> None:
        """Initializes the HierarchyPrune with the given hierarchy log.

        Args:
            hierarchy_log (List[ChangeLogEntry]): The list of change log entries forming a
                hierarchy.
        """
        self.hierarchy_log = hierarchy_log

        self.prunables: Dict[str, PruneableItem] = {}

        self._create_prunables_map(self.hierarchy_log)

    def _create_prunables_map(
        self,
        hier_log: List[ChangeLogEntry],
        upper_entry: ChangeLogEntry = None,
        upper_index_path: Union[str, int] = None,
    ):
        """Recursively creates parent mapping for the given hierarchy log.

        Args:
            hier_log (List[ChangeLogEntry]): List of change log entries for mapping.
            upper_entry (ChangeLogEntry, optional): The current hierarchical upper change log entry.
                Defaults to None.
        """

        prune_type = PruneType.ROOT

        if isinstance(upper_index_path, str):
            prune_type = PruneType.SUBMODULE

        if isinstance(upper_index_path, int):
            prune_type = PruneType.LEAF

        for entry in hier_log:
            self.prunables[entry.sha] = PruneableItem(
                prune_type=prune_type,
                sha=entry.sha,
                upper_entry=upper_entry,
                entry=entry,
                upper_index_path=upper_index_path,
            )

            for other_parents_index, sub_hier_log in enumerate(entry.other_parents):
                self._create_prunables_map(
                    hier_log=sub_hier_log,
                    upper_entry=entry,
                    upper_index_path=other_parents_index,
                )

            for sub_path, sub_module_update in entry.submodule_updates.items():
                self._create_prunables_map(
                    hier_log=sub_module_update.entries,
                    upper_entry=entry,
                    upper_index_path=sub_path,
                )

    def prune_sha(self, sha: str) -> None:
        """Prunes the hierarchy log by removing the change log entry with the given SHA.

        If the SHA is found in the hierarchy, the method recursively prunes other parent
            entries if necessary.

        Args:
            sha (str): The SHA identifier of the change log entry to be pruned.
        """
        prunable = self.prunables[sha]

        if prunable.prune_type == PruneType.ROOT:
            self.hierarchy_log = list(
                filter(lambda x: x.sha != sha, self.hierarchy_log)
            )

        if prunable.prune_type == PruneType.LEAF:
            prunable.upper_entry.other_parents[prunable.upper_index_path] = list(
                filter(
                    lambda x: x.sha != sha,
                    prunable.upper_entry.other_parents[prunable.upper_index_path],
                )
            )

        if prunable.prune_type == PruneType.SUBMODULE:
            prunable.upper_entry.submodule_updates[
                prunable.upper_index_path
            ].entries = list(
                filter(
                    lambda x: x.sha != sha,
                    prunable.upper_entry.submodule_updates[
                        prunable.upper_index_path
                    ].entries,
                )
            )

        if prunable.upper_entry:
            all_other_parents_empty = all(
                map(lambda x: not x, prunable.upper_entry.other_parents)
            )
            all_submodule_updates_empty = all(
                map(
                    lambda x: not x.entries,
                    prunable.upper_entry.submodule_updates.values(),
                )
            )
            if all_other_parents_empty and all_submodule_updates_empty:
                self.prune_sha(prunable.upper_entry.sha)
