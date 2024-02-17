"""Maps Git Shas to a software version by traversing the git tree
"""

from typing import Callable, List, Dict, Tuple

from gitaudit.branch.tree import Tree, Segment
from gitaudit.branch.hierarchy import hierarchy_log_to_linear_log
from gitaudit.git.change_log_entry import ChangeLogEntry


class ShaVersionMapper:
    """Maps Git Shas to a software version by traversing the git tree"""

    def __init__(
        self,
        tree: Tree,
        tag_to_fix_version_func: Callable[[str], str],
        sort_ref_func: Callable[[List[str]], List[str]],
        sort_fix_version_func: Callable[[List[str]], List[str]],
        ref_to_fix_version_func: Callable[[str], str],
    ) -> None:
        """_summary_

        Args:
            tree (Tree): The tree object which is used to extract the fix versions from
            tag_to_fix_version_func (Callable[[str], str]): A function that receives a tag name and
                provides a fix version back. If no fix version is associated to the tag then the
                function shall return none. The function is called for every tag.
            sort_ref_func (Callable[[List[str]], List[str]]): This function sorts the
                branches by their priority. The function shall sort in a wa that the lowest priority
                branch will be in the first element with the index zero. The highest priority branch
                will be the last element with the index [n-1]. The lowest priority branch is
                regarded to be the mainline branch and will open up a new fix version. The highest
                priority branch will be the branched of release branch thus getting the fix version
                from the mainline. Normally the function will only have to sort 2 elements but
                theoretically more are possible.
            sort_fix_version_func (Callable[[List[str]], List[str]]): It may happen that two tags
                that are relevant have the same sha. In these situations a function must be provided
                that returns the lowest / earliest fix version. The function must sort them by the
                lowest fix version (to be taken) to the highest fix version. Except for the lowest
                fix version that is taken in the analysis all others are ignored.
            ref_to_fix_version_func (Callable[[str], str]): A branch name or an end of life tag name
                is a reference to an end of a git log. This git log should be associated to a fix
                version. This has to be provided by a function. In case none is returned for a ref
                then it is assumed that no more deliveries were done from the branch / ref and thus
                the remaining commits are just to support infrastructure / or are ommitted /
                ignored.
        """
        self.tree = tree
        self.tag_to_fix_version_func = tag_to_fix_version_func
        self.sort_ref_func = sort_ref_func
        self.sort_fix_version_func = sort_fix_version_func
        self.ref_to_fix_version_func = ref_to_fix_version_func
        self._used_fix_versions = set()

    def _internal_tag_to_fix_version_func(self, tag):
        fix_version = self.tag_to_fix_version_func(tag)
        assert (
            fix_version not in self._used_fix_versions or fix_version is None
        ), f'Fix version "{fix_version}" already used!'
        self._used_fix_versions.add(fix_version)
        return fix_version

    def _internal_ref_to_fix_version_func(self, ref):
        fix_version = self.ref_to_fix_version_func(ref)
        assert (
            fix_version not in self._used_fix_versions or fix_version is None
        ), f'Fix version "{fix_version}" already used!'
        self._used_fix_versions.add(fix_version)
        return fix_version

    def _trace_in_segment_fix_version(
        self, segment: Segment, fix_version: str
    ) -> Tuple[str, Dict[str, ChangeLogEntry]]:
        # This function gets a segment and returns the following data
        # - The fix version active at the beginning of the segment
        # - a map where the keys are fix versions and the values are the first parent change log
        #   entries (the child change log entries will be part in the hierarchy)
        current_fix_version = fix_version
        entry_map = {}

        for entry in segment.entries:
            if entry.tags:
                tag_fix_versions = list(
                    filter(
                        None, map(self._internal_tag_to_fix_version_func, entry.tags)
                    )
                )
                tag_fix_versions = self.sort_fix_version_func(tag_fix_versions)

                if tag_fix_versions:
                    current_fix_version = tag_fix_versions[0]

            entry_arr = entry_map.get(current_fix_version, [])
            entry_arr.append(entry)
            entry_map[current_fix_version] = entry_arr

        return current_fix_version, entry_map

    def calculate(self, ignore_merge_commits: bool = True) -> Dict[str, str]:
        """Calculate the sha version map

        Args:
            ignore_merge_commits (bool, optional): If set to true merge commits will not appear in
                the sha version map. Defaults to True.

        Returns:
            Dict[str, str]: Sha version map where the key is the commit sha and the value is the
                assigned version.
        """

        untraced_segments = [
            (segment, self._internal_ref_to_fix_version_func(segment.ref_name))
            for segment in self.tree.end_segments()
        ]
        branch_off_points = {}

        fix_version_change_log_map = {}

        # The idea is the following: For every tracked segment trace the change log items and find
        # tags in them. Find the corresponding fix version and trace this in the segment.
        # When reaching the base of the segment we have reached a branch off point. We have to wait
        # until all child segments of the branch off point have been processed. Only then we can
        # properly calculate the lowest and highest prio branch in order to determine the correct
        # flow of the fix version

        while untraced_segments:
            segment, segment_end_fix_version = untraced_segments.pop()

            # we still have untraced segments
            (
                segment_start_fix_version,
                segment_fix_version_map,
            ) = self._trace_in_segment_fix_version(segment, segment_end_fix_version)

            # update the fix_version_change_log_map
            for fix_v, entries in segment_fix_version_map.items():
                arr = fix_version_change_log_map.get(fix_v, [])
                arr.extend(entries)
                fix_version_change_log_map[fix_v] = arr

            if segment.parent:
                # there is a parent sha there is a parent segment
                parent_segment = segment.parent

                if parent_segment.end_sha not in branch_off_points:
                    # it is not yet in so we have to create a structure. The child map works with
                    child_map = {
                        seg.ref_name: None
                        for seg in parent_segment.children_sha_map.values()
                    }
                    branch_off_points[parent_segment.end_sha] = child_map

                branch_off_points[parent_segment.end_sha][segment.ref_name] = (
                    segment,
                    segment_start_fix_version,
                )

                if all(branch_off_points[parent_segment.end_sha].values()):
                    # figure out the fix version that will propagate
                    ref_segment_map = {
                        seg.ref_name: fv
                        for seg, fv in branch_off_points[
                            parent_segment.end_sha
                        ].values()
                        if fv
                    }

                    if ref_segment_map:
                        sorted_refs = self.sort_ref_func(ref_segment_map)

                        low_ref = sorted_refs[0]
                        high_ref = sorted_refs[-1]

                        # update the ref_name of the parent segment to ensure its correct
                        parent_segment.ref_name = low_ref
                        untraced_segments.append(
                            (parent_segment, ref_segment_map[high_ref])
                        )
                    else:
                        ref_segment_map = [
                            seg.ref_name
                            for seg, _ in branch_off_points[
                                parent_segment.end_sha
                            ].values()
                        ]
                        sorted_refs = self.sort_ref_func(ref_segment_map)

                        low_ref = sorted_refs[0]
                        high_ref = sorted_refs[-1]

                        # update the ref_name of the parent segment to ensure its correct
                        parent_segment.ref_name = low_ref
                        untraced_segments.append((parent_segment, None))

        sha_fix_version_map = {}

        for fix_version, hier_entries in fix_version_change_log_map.items():
            lin_entries = hierarchy_log_to_linear_log(hier_entries)

            if ignore_merge_commits:
                lin_entries = list(
                    filter(lambda x: len(x.parent_shas) <= 1, lin_entries)
                )

            for entry in lin_entries:
                sha_fix_version_map[entry.sha] = (fix_version, entry)

        return sha_fix_version_map
