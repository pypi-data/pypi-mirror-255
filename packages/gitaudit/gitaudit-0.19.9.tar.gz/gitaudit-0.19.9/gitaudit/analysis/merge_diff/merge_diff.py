"""This code helps identifying missing merges
in main that have already been merged in a
release branch
"""

from __future__ import annotations
from typing import List

from gitaudit.branch.hierarchy import (
    linear_log_to_hierarchy_log,
    hierarchy_log_to_linear_log,
    changelog_hydration,
    log_commit_stats,
)
from gitaudit.git.controller import Git
from gitaudit.branch.tree import Tree
from gitaudit.branch.prune import HierarchyPrune

from .matchers import Matcher, MatchResult
from .report import MergeDiffReport, MergeDiffAlert, RefInfo
from .pruners import Pruner


def get_head_base_hier_logs(git: Git, head_ref: str, base_ref: str):
    """Gets the head and base hierarchy logs from a git instance
    as preparation for the merge diff analysis

    Args:
        git (Git): Git instance
        head_ref (str): name of the head ref
        base_ref (str): name of the base ref

    Returns:
        Tuple[List[ChangeLogEntry], List[ChangeLogEntry]]: head and base
            hierarchy log
    """
    head_hier_log = linear_log_to_hierarchy_log(git.log_parentlog(head_ref))
    base_hier_log = linear_log_to_hierarchy_log(git.log_parentlog(base_ref))

    tree = Tree()
    tree.append_log(base_hier_log, base_ref)
    tree.append_log(head_hier_log, head_ref)

    ref_segment_map = {x.ref_name: x for x in tree.root.children_sha_map.values()}

    head_segment = ref_segment_map[head_ref]
    base_segment = ref_segment_map[base_ref]

    head_hier_log = changelog_hydration(
        head_segment.entries,
        git,
    )
    base_hier_log = changelog_hydration(
        base_segment.entries,
        git,
    )

    return head_hier_log, base_hier_log


class MergeDiff:
    """Calculates the merge diff by finding commits that are merged in head but not in base"""

    def __init__(
        self,
        name,
        head_hier_log,
        base_hier_log,
        head_ref_name,
        base_ref_name,
    ) -> None:
        self.head_hier_log = head_hier_log
        self.base_hier_log = base_hier_log

        self.head_hier_prune = HierarchyPrune(self.head_hier_log)
        self.base_hier_prune = HierarchyPrune(self.base_hier_log)

        (
            head_merge_count,
            head_normal_count,
            head_add,
            head_del,
        ) = log_commit_stats(self.head_hier_log)
        (
            base_merge_count,
            base_normal_count,
            base_add,
            base_del,
        ) = log_commit_stats(self.base_hier_log)

        self._report = MergeDiffReport(
            name=name,
            head_info=RefInfo(
                ref_name=head_ref_name,
                sha=self.head_hier_log[0].sha,
                merge_commit_count=head_merge_count,
                individual_commit_count=head_normal_count,
                total_commit_count=head_merge_count + head_normal_count,
                additions=head_add,
                deletions=head_del,
            ),
            base_info=RefInfo(
                ref_name=base_ref_name,
                sha=self.base_hier_log[0].sha,
                merge_commit_count=base_merge_count,
                individual_commit_count=base_normal_count,
                total_commit_count=base_merge_count + base_normal_count,
                additions=base_add,
                deletions=base_del,
            ),
        )

    @property
    def report(self) -> MergeDiffReport:
        """Returns the Merge diff Report as Property

        Returns:
            MergeDiffReport: Merge diff Report
        """
        self._report.set_head_unmatched(
            hierarchy_log_to_linear_log(
                self.head_hier_prune.hierarchy_log,
            )
        )
        self._report.set_base_unmatched(
            hierarchy_log_to_linear_log(
                self.base_hier_prune.hierarchy_log,
            )
        )
        return self._report

    def prune_head_sha(self, sha):
        """Prunes a sha from the head bucket list

        Args:
            sha (str): sha to be pruned
        """
        self.head_hier_prune.prune_sha(sha)

    def prune_base_sha(self, sha):
        """Prunes a sha from the base bucket list

        Args:
            sha (str): sha to be pruned
        """
        self.base_hier_prune.prune_sha(sha)

    def validate_match(self, match: MatchResult):
        """Validate Match Result

        Args:
            match (MatchResult): Macth Result

        Returns:
            MatchResult: Augmented Match Result
        """
        if match.head.sorted_numstat != match.base.sorted_numstat:
            self._report.append_alert(
                MergeDiffAlert.warning(
                    match,
                    "Files changes / numstats do not match!",
                )
            )

        return match

    def execute_matcher(self, matcher: Matcher):
        """Executes a matcher

        Args:
            matcher (Matcher): Matcher which will return commit match results
        """
        sub_matches = matcher.match(
            self.head_hier_prune.hierarchy_log,
            self.base_hier_prune.hierarchy_log,
        )

        sub_matches = list(map(self.validate_match, sub_matches))
        self._report.append_match(type(matcher).__name__, sub_matches)

        for match in sub_matches:
            self.prune_head_sha(match.head.sha)
            self.prune_base_sha(match.base.sha)

    def execute_matchers(self, matchers: List[Matcher]):
        """Executed a list of matchers

        Args:
            matchers (List[Matcher]): List of matcher which will return commit match results
        """
        for matcher in matchers:
            self.execute_matcher(matcher)

    def execute_head_pruner(self, pruner: Pruner):
        """Runs pruner on head entries

        Args:
            pruner (Pruner): Pruner
        """
        entries = pruner.prune(self.head_hier_prune.hierarchy_log)
        self._report.append_head_prune(type(pruner).__name__, entries)
        for entry in entries:
            self.prune_head_sha(entry.sha)

    def execute_base_pruner(self, pruner: Pruner):
        """Runs pruner on base entries

        Args:
            pruner (Pruner): Pruner
        """
        entries = pruner.prune(self.base_hier_prune.hierarchy_log)
        self._report.append_base_prune(type(pruner).__name__, entries)
        for entry in entries:
            self.prune_base_sha(entry.sha)

    def execute_pruner(self, pruner: Pruner):
        """Prunes shas after running a provided pruner for selection

        Args:
            pruner (Pruner): The pruner to select the entries to be removed
        """
        self.execute_head_pruner(pruner)
        self.execute_base_pruner(pruner)

    @classmethod
    def from_tree(
        cls,
        name: str,
        tree: Tree,
        head_ref: str,
        base_ref: str,
    ):
        """Generate a merge diff instance by providing a tree object and the head and base ref
        names.

        Args:
            tree (Tree): Tree object the logs are taken from
            head_ref (str): head ref name
            base_ref (str): base ref name

        Returns:
            MergeDiff: Merged diff Instance
        """
        head_hier_log, base_hier_log = tree.get_entries_until_merge_base(
            head_ref, base_ref
        )
        return MergeDiff(
            name=name,
            head_hier_log=head_hier_log,
            base_hier_log=base_hier_log,
            head_ref_name=head_ref,
            base_ref_name=base_ref,
        )
