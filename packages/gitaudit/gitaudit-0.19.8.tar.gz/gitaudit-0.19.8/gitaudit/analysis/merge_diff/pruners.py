"""Code for Pruning
"""

from typing import List, Callable
import re

from gitaudit.git.change_log_entry import ChangeLogEntry
from gitaudit.branch.hierarchy import sha_to_entry_map


class Pruner:
    """Generic class for pruning commits without matching"""

    def prune(self, hier_lin_log: List[ChangeLogEntry]) -> List[ChangeLogEntry]:
        """Prune change log entries

        Args:
            hier_lin_log (List[ChangeLogEntry]): hierarchy or linear log

        Raises:
            NotImplementedError: Abstract Placeholder

        Returns:
            List[ChangeLogEntry]: List of commits to be pruned
        """
        entry_map = sha_to_entry_map(hier_lin_log)
        prune_results = []

        for entry in entry_map.values():
            if self._do_prune_entry(entry):
                prune_results.append(entry)

        return prune_results

    def _do_prune_entry(self, entry: ChangeLogEntry) -> bool:
        raise NotImplementedError


class LambdaPruner(Pruner):
    """Pruning based on user defined function"""

    def __init__(self, func: Callable) -> None:
        super().__init__()
        self.func = func

    def _do_prune_entry(self, entry: ChangeLogEntry) -> bool:
        return self.func(entry)


class CommitSubjectBodyPruner(Pruner):
    """Pruning based on subject / body content"""

    def __init__(self, pattern, invert: bool = False) -> None:
        super().__init__()
        self.pattern = pattern
        self.invert = invert
        self.regexp = re.compile(self.pattern)

    def _do_prune_entry(self, entry: ChangeLogEntry) -> bool:
        if self.invert:
            return not (
                self.regexp.search(entry.subject) or self.regexp.search(entry.body)
            )

        return self.regexp.search(entry.subject) or self.regexp.search(entry.body)


class CommitFilePathPruner(Pruner):
    """Pruning based on file path content. All file pathes must match the regexp."""

    def __init__(self, pattern) -> None:
        super().__init__()
        self.pattern = pattern
        self.regexp = re.compile(self.pattern)

    def _do_prune_entry(self, entry: ChangeLogEntry) -> bool:
        if not entry.numstat:
            return False

        return all(map(lambda x: self.regexp.search(x.path), entry.numstat))
