"""Statistics about the git repository."""

from typing import List, Dict, Tuple
from enum import Flag, auto

from pydantic import Field
from rich.progress import (
    Progress,
    TimeElapsedColumn,
    TimeRemainingColumn,
    BarColumn,
    MofNCompleteColumn,
)

from gitaudit.git.change_log_entry import ChangeLogEntry
from gitaudit.root import GitauditRootModel
from gitaudit.branch.hierarchy import iter_commits, hierarchy_log_to_linear_log


PROGRESS_COLUMNS = [
    MofNCompleteColumn(),
    BarColumn(bar_width=None),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
]


class IntegrationCommitType(Flag):
    """
    Define the type of a commit. Multiple may be used for a single commit.
    """

    MERGE = auto()
    SPLIT = auto()
    FIRST_PARENT = auto()
    BRANCH_OFF = auto()


class IntegrationBranchInfo(GitauditRootModel):
    """Information about a feature branch that was integrated into the base branch."""

    integration_commit: ChangeLogEntry
    branch_off_commits: List[ChangeLogEntry] = Field(default_factory=list)
    commits: List[ChangeLogEntry] = Field(default_factory=list)
    commit_lines_map: Dict[str, List[ChangeLogEntry]] = Field(default_factory=dict)
    commit_type_map: Dict[str, IntegrationCommitType] = Field(default_factory=dict)

    @property
    def commit_lines(self) -> List[ChangeLogEntry]:
        """Return the commit lines of the feature branch."""
        return list(self.commit_lines_map.values())

    def append_commit(
        self, commit: ChangeLogEntry, info: IntegrationCommitType
    ) -> None:
        """Append a commit to the feature branch."""
        self.commit_type_map[  # pylint: disable=unsupported-assignment-operation
            commit.sha
        ] = info

        if commit == self.integration_commit:
            self.commit_lines_map = {
                f"{commit.sha}-{sha}": [self.integration_commit]
                for sha in commit.parent_shas[1:]
            }
            return

        if IntegrationCommitType.BRANCH_OFF in info:
            self.branch_off_commits.append(commit)  # pylint: disable=no-member
        else:
            self.commits.append(commit)  # pylint: disable=no-member

        line_keys = list(
            filter(
                lambda x: x.endswith(f"-{commit.sha}"),
                self.commit_lines_map,
            )
        )

        for line_key in line_keys:
            line = self.commit_lines_map.pop(line_key)
            if IntegrationCommitType.BRANCH_OFF in info:
                line.append(commit)
                self.commit_lines_map[line_key + "#"] = line
            else:
                for sha in commit.parent_shas:
                    new_line = line.copy()
                    new_line.append(commit)

                    key_shas = list(map(lambda x: x.sha, new_line)) + [sha]

                    self.commit_lines_map["-".join(key_shas)] = new_line


class StatsHelper:
    """Helper class to calculate statistics about the git repository."""

    def __init__(self, hier_log: List[ChangeLogEntry]) -> None:
        self.hier_log = hier_log
        self.lin_log = hierarchy_log_to_linear_log(hier_log)
        self.sha_entry_map = {entry.sha: entry for entry in iter_commits(hier_log)}
        self.first_parent_shas = [entry.sha for entry in self.hier_log]
        self.commit_type_map: Dict[str, IntegrationCommitType] = {}
        self.childrens_map = {}
        self.integration_branch_info_map = {}

        for entry in iter_commits(hier_log):
            for parent_sha in entry.parent_shas:
                arr = self.childrens_map.get(parent_sha, [])
                arr.append(entry.sha)
                self.childrens_map[parent_sha] = arr

        for entry in iter_commits(hier_log):
            commit_info = IntegrationCommitType(0)

            if entry.other_parents:
                commit_info |= IntegrationCommitType.MERGE

            entry_children = self.childrens_map.get(entry.sha, [])
            if len(entry_children) > 1:
                commit_info |= IntegrationCommitType.SPLIT

            if entry.sha in self.first_parent_shas:
                commit_info |= IntegrationCommitType.FIRST_PARENT

            self.commit_type_map[entry.sha] = commit_info

        self._create_integration_branch_info(self.hier_log)

    @property
    def integration_branch_infos(self) -> List[IntegrationBranchInfo]:
        """Return the information about the integrated feature branches."""
        return list(self.integration_branch_info_map.values())

    def _create_integration_branch_info(self, hier_log) -> None:
        with Progress(*PROGRESS_COLUMNS) as progress:
            task = progress.add_task("[cyan]Processing...", total=len(self.lin_log))

            for entry, info, integration_sha in self.iter_commits_with_info(hier_log):
                integration_info = self.integration_branch_info_map.get(
                    integration_sha, None
                )

                if integration_info is None:
                    integration_info = IntegrationBranchInfo(
                        integration_commit=entry,
                    )
                    self.integration_branch_info_map[integration_sha] = integration_info

                integration_info.append_commit(entry, info)

                progress.update(task, advance=1)

    def iter_commits_with_info(
        self, hier_log: List[ChangeLogEntry] = None, integration_sha: str = None
    ) -> Tuple[ChangeLogEntry, IntegrationCommitType, str]:
        """
        Iterate over all integrated feature branches.

        Args:
            hier_log (List[ChangeLogEntry], optional): The hierarchy log to iterate over. Defaults
                to None.
            integration_sha (str, optional): The sha of the integration commit. Defaults to None.

        Yields:
            Tuple[ChangeLogEntry, IntegrationCommitType, str]: The commit, the type of the commit
                and the sha of the integration commit.
        """
        if hier_log is None:
            hier_log = self.hier_log

        len_hierarchy_log = len(hier_log)

        for index, entry in enumerate(hier_log):
            if entry.sha in self.first_parent_shas:
                integration_sha = entry.sha

            yield entry, self.commit_type_map[entry.sha], integration_sha

            if (
                index == len_hierarchy_log - 1
                and entry.sha not in self.first_parent_shas
            ):
                for branch_off_sha in entry.branch_offs:
                    if (
                        branch_off_sha in self.sha_entry_map
                        and branch_off_sha in self.first_parent_shas
                    ):
                        commit_info = self.commit_type_map[branch_off_sha]
                        commit_info |= IntegrationCommitType.BRANCH_OFF
                        yield (
                            self.sha_entry_map[branch_off_sha],
                            commit_info,
                            integration_sha,
                        )

            for sub_hier_log in entry.other_parents:
                for (
                    sub_entry,
                    sub_info,
                    sub_integration_sha,
                ) in self.iter_commits_with_info(
                    sub_hier_log,
                    integration_sha,
                ):
                    yield sub_entry, sub_info, sub_integration_sha


# def merge_split_commits_on_feature_branches(stats_helper: StatsHelper):
#     """
#     Count the merge commits and splits commits on a feature branch.

#     - Merge Commit: In case the main branch is merged into the feature branch or another feature
#       branch is merged into the feature branch.
#     - Split Commit: In case a feature branch is branched off another feature branch. In this case
#       this could mean that a critical change was needed in multiple branches.
#     """
#     count_normal_commits = 0
#     count_merge_commits = 0
#     count_split_commits = 0

#     for root_entry in stats_helper.hier_log:
#         for entry in iter_commits([root_entry]):
#             if entry == root_entry:
#                 continue

#             if entry.other_parents:
#                 count_merge_commits += 1
#             elif len(stats_helper.childrens_map.get(entry.sha, [])) > 1:
#                 count_split_commits += 1
#             else:
#                 count_normal_commits += 1

#     return count_normal_commits, count_merge_commits, count_split_commits


# def count_branches_branched_off_first_parent_line(stats_helper: StatsHelper):
#     """Count the number of branches that are branched off the first parent line."""
#     pass


# def feature_branch_time_range(stats_helper: StatsHelper):
#     """
#     Calculate the time range of a feature branch. This is the time between the first commit and
#     the last commit on the feature branch. Also the time between the branch off point of the feature
#     branch and the merge commit.
#     """
#     for branch_info in stats_helper.integration_branch_infos:
#         if len(branch_info.commit_lines) > 1:
#             print(branch_info.integration_commit.sha)
#         for line in branch_info.commit_lines:
#             if line[-1].sha in stats_helper.first_parent_shas:
#                 from_fp_line = True
#                 time_duration = line[1].commit_date - line[-1].commit_date
#             else:
#                 from_fp_line = False
#                 time_duration = line[0].commit_date - line[-1].commit_date
#             print(
#                 time_duration.total_seconds(),
#                 from_fp_line,
#                 len(branch_info.commit_lines),
#             )


# def feature_vs_test(stats_helper: StatsHelper):
#     """
#     Assumption! Tests ususally have a path that contains the word test. This is not always the case
#     but it is a good approximation. Counts for each commit the additions and deletions in files that
#     do not have test in the path (production code) and puts it into perspective of the additions and
#     deletions in files that have test in the path (test code).
#     """
