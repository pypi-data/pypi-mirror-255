"""Tree Creator
"""

import os
from typing import Optional, List, Callable

from pydantic import BaseModel

from gitaudit.git.controller import Git
from gitaudit.git.change_log_entry import ChangeLogEntry
from .serialization import load_log_from_file, save_log_to_file
from .tree import Tree
from .hierarchy import linear_log_to_hierarchy_log, changelog_hydration


class TreeCreatorConfig(BaseModel):
    """Tree Creator Config"""

    consider_local_branches: bool = False
    consider_remote_branches: bool = True
    consider_tags: bool = True
    local_branch_filter_func: Callable[[str], bool] = lambda x: True
    remote_branch_filter_func: Callable[[str], bool] = lambda x: True
    tag_filter_func: Callable[[str], bool] = lambda x: True
    root_ref: Optional[str] = None


CACHE_PARENT_LOG_FOLDER_NAME = "parent_log"
CACHE_CHANGE_LOG_FOLDER_NAME = "change_log"


class TreeCreatorCache:
    """Tree Creator Cache"""

    def __init__(self, root_location: str) -> None:
        self.root_location = root_location
        self.parent_log_location = os.path.join(
            self.root_location, CACHE_PARENT_LOG_FOLDER_NAME
        )
        self.change_log_location = os.path.join(
            self.root_location, CACHE_CHANGE_LOG_FOLDER_NAME
        )

        os.makedirs(self.parent_log_location, exist_ok=True)
        os.makedirs(self.change_log_location, exist_ok=True)

    def get_parent_log(self, git: Git, ref: str) -> List[ChangeLogEntry]:
        """Get the parent log

        Args:
            ref (str): reference name
            git (Git): git controller

        Returns:
            List[ChangeLogEntry]: Parent log
        """
        dashed_ref = ref.replace("/", "-")
        head_sha = git.show_parentlog_entry(ref).sha
        log_file_path = os.path.join(
            self.parent_log_location, f"{dashed_ref}...{head_sha}"
        )

        if os.path.isfile(log_file_path):
            log = load_log_from_file(log_file_path)
            if log[0].sha == head_sha:
                return log

        # if we are here we need to call git
        log = linear_log_to_hierarchy_log(git.log_parentlog(ref))
        save_log_to_file(log, log_file_path)

        return log

    def get_change_log(
        self, git: Git, end_sha: str, start_sha: str = None
    ) -> List[ChangeLogEntry]:
        """Gets the full change log of a ref section

        Args:
            end_ref (str): The end ref of the change log
            start_ref (str): The start ref of the change log (not included)
            git (Git): Git controller

        Returns:
            List[ChangeLogEntry]: Change log
        """
        log_file_path = os.path.join(
            self.change_log_location, f"{start_sha}...{end_sha}"
        )

        if os.path.isfile(log_file_path):
            log = load_log_from_file(log_file_path)

            end_sha_matches = end_sha == log[0]
            start_sha_matches = start_sha is None or start_sha == log[-1].parent_shas[0]
            assert end_sha_matches and start_sha_matches

            return log

        log = linear_log_to_hierarchy_log(
            git.log_changelog(
                end_ref=end_sha,
                start_ref=start_sha,
                first_parent=False,
                patch=True,
            )
        )
        save_log_to_file(log, log_file_path)

        return log


class TreeCreator:
    """Tree Creator"""

    def __init__(
        self, git: Git, config: TreeCreatorConfig, cache: TreeCreatorCache = None
    ) -> None:
        self.git = git
        self.config = config
        self.cache = cache

    def _get_refs(self):
        refs = []

        refs.extend(
            filter(
                self.config.local_branch_filter_func,
                self.git.local_ref_names(),
            )
        )
        refs.extend(
            filter(
                self.config.remote_branch_filter_func,
                self.git.remote_ref_names(),
            )
        )
        refs.extend(
            filter(
                self.config.tag_filter_func,
                self.git.tags(),
            )
        )

        return refs

    def create_tree(
        self,
        hydrate_with_changelog: bool = True,
        hydrate_root_segment: bool = False,
        patch: bool = True,
    ) -> Tree:
        """Create the tree

        Args:
        hydrate_with_changelog (bool): Determines wether to hydrate the tree log (which initially
            creates a parent log with the change log). Defaults to True.
        hydrate_root_segment (bool): When hydrating the log by default the root segment is not
            hydrated (due to performance reasons). The root segment can be hydrated by setting this
            option to True. Defaults to False.
        patch (bool): Wether or not the hydration shall be done with the patch option of git
            enabled. If deactivated numstats and submodule updates cannot be determined and are thus
            not part of the hydration. Defaults to True.

        Returns:
            Tree: Created Tree
        """
        refs = self._get_refs()

        if self.config.root_ref:
            assert self.config.root_ref in refs
            refs.remove(self.config.root_ref)
            refs.insert(0, self.config.root_ref)

        tree = Tree()

        for ref in refs:
            log = self.cache.get_parent_log(self.git, ref)
            tree.append_log(log, ref)

        if not hydrate_with_changelog:
            return tree

        for seg in tree.iter_segments():
            if seg.empty or (
                not hydrate_root_segment and seg.end_sha == tree.root.end_sha
            ):
                continue
            changelog_hydration(seg.entries, self.git, patch=patch)

        return tree
