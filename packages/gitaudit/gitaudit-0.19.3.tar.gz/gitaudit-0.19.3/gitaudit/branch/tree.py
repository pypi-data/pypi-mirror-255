"""Calculate Branch Trees
"""

# pylint: disable=unsupported-assignment-operation

from __future__ import annotations
import itertools

from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field
from gitaudit.git.change_log_entry import ChangeLogEntry


class Segment(BaseModel):
    """Class for Storing a Branch Segment"""

    entries: List[ChangeLogEntry]
    children_sha_map: Dict[str, Segment] = Field(default_factory=dict)
    empty_children: List[Segment] = Field(default_factory=list)
    ref_name: str
    parent: Optional[Segment] = None

    @property
    def has_children(self):
        """Returns True if this segment has children"""
        return bool(self.children_sha_map) or bool(self.empty_children)

    @property
    def children_ref_names(self):
        """Returns a list of all children ref names"""
        return list(
            map(
                lambda x: x.ref_name,
                self.children_sha_map.values(),  # pylint: disable=no-member
            )
        ) + list(map(lambda x: x.ref_name, self.empty_children))

    @property
    def length(self):
        """Returns the number of entries in this segment"""
        return len(self.entries)

    @property
    def empty(self):
        """Returns True if this segment is empty"""
        return not bool(self.entries)

    @property
    def end_sha(self):
        """Returns the sha of the last entry in this segment"""
        return self.entries[0].sha

    @property
    def end_entry(self):
        """Returns the last entry in this segment"""
        return self.entries[0]

    @property
    def start_sha(self):
        """Returns the sha of the first entry in this segment"""
        return self.entries[-1].sha

    @property
    def start_entry(self):
        """Returns the first entry in this segment"""
        return self.entries[-1]

    @property
    def shas(self):
        """Returns all first parent shas in this segment as a list"""
        return list(map(lambda x: x.sha, self.entries))

    def append_segment(self, segment: Segment) -> None:
        """Append a segment to this segment

        Args:
            segment (Segment): Segment to be appended
        """
        if segment.empty:
            self.empty_children.append(segment)  # pylint: disable=no-member
        else:
            self.children_sha_map[segment.start_sha] = segment


def split_segments_at_index(
    current_segment: Segment, new_segment: Segment, index: int
) -> Tuple[Segment, Segment, Segment]:
    """Split two segments at a given index

    Args:
        current_segment (Segment): Current segment
        new_segment (Segment): New segment
        index (int): Index to split at

    Returns:
        Tuple[Segment, Segment, Segment]: The split segments
    """
    # split at current index
    current_segment_pre = Segment(
        entries=current_segment.entries[(index + 1) :],
        ref_name=current_segment.ref_name,
        parent=current_segment.parent,
    )
    current_segment_post = Segment(
        entries=current_segment.entries[: (index + 1)],
        ref_name=current_segment.ref_name,
        children_sha_map=current_segment.children_sha_map,
        empty_children=current_segment.empty_children,
    )
    new_segment_post = Segment(
        entries=new_segment.entries[: (index + 1)],
        ref_name=new_segment.ref_name,
    )

    if current_segment_post.empty:
        current_segment_pre = current_segment

        if current_segment_post.ref_name in current_segment.children_ref_names:
            # in case the current_segment_post ref_name is already used in the current segment
            # we can not add the post to the pre segment
            current_segment_post = None

    if current_segment_post:
        current_segment_pre.append_segment(current_segment_post)
        current_segment_post.parent = current_segment_pre

    current_segment_pre.append_segment(new_segment_post)
    new_segment_post.parent = current_segment_pre

    return current_segment_pre, current_segment_post, new_segment_post


class Tree(BaseModel):
    """Branching tree out of segments"""

    root: Segment = None
    end_segments_map: Dict[str, Segment] = Field(default_factory=dict)

    def append_log(self, hier_log: List[ChangeLogEntry], ref_name: str):
        """Append a new hierarchy log history to the tre

        Args:
            hier_log (List[ChangeLogEntry]): to be appended log
            ref_name (str): name of the branch / ref
        """
        assert (
            ref_name
            not in self.end_segments_map  # pylint: disable=unsupported-membership-test
        ), f'Branch name "{ref_name}" is already used by an end segment!'

        new_segment = Segment(
            entries=hier_log,
            ref_name=ref_name,
        )

        if not self.root:
            self.root = new_segment
            self.end_segments_map[ref_name] = new_segment
        else:
            self._merge_segment(new_segment)

    def _merge_segment(self, new_segment: Segment):
        index = -1

        assert (
            self.root.entries[index].sha == new_segment.entries[index].sha
        ), "Initial shas do not match which is a prerequisite!"

        current_segment = self.root

        while new_segment:
            while (
                len(current_segment.entries) > (-index - 1)
                and len(new_segment.entries) > (-index - 1)
                and current_segment.entries[index].sha == new_segment.entries[index].sha
            ):
                index -= 1

            cursor_length = -index - 1

            if (
                current_segment.length
                <= cursor_length  # current segment is finished at cursor
                and new_segment.length
                > cursor_length  # new segment is longer than current cursor
                # the current segment has a child with the continue sha of the new segment
                and new_segment.entries[index].sha in current_segment.children_sha_map
            ):
                current_segment = current_segment.children_sha_map[
                    new_segment.entries[index].sha
                ]
                new_segment = Segment(
                    entries=new_segment.entries[: (index + 1)],
                    ref_name=new_segment.ref_name,
                )
                index = -1
                continue

            # Split segments at current index
            (
                current_segment_pre,
                current_segment_post,
                new_segment_post,
            ) = split_segments_at_index(current_segment, new_segment, index)

            # handle the parent of the start of the split
            if current_segment_pre.parent:
                current_segment_pre.parent.children_sha_map[
                    current_segment_pre.start_sha
                ] = current_segment_pre
            else:
                self.root = current_segment_pre

            # Update the end segment reference
            if current_segment_post:
                self.end_segments_map[current_segment_post.ref_name] = (
                    current_segment_post
                )

            self.end_segments_map[new_segment_post.ref_name] = new_segment_post

            new_segment = None

    def iter_segments(self):
        """Iterate Tree Segments

        Yields:
            Segment: Iterated Tree Segment
        """
        queue = [self.root]

        while queue:
            seg = queue.pop(0)
            yield seg
            queue.extend(seg.children_sha_map.values())
            queue.extend(seg.empty_children)

    def flatten_segments(self) -> List[Segment]:
        """Return all child segments of root as a flattened list

        Returns:
            List[Segment]: Flattened segments
        """
        return list(self.iter_segments())

    def end_segments(self) -> List[Segment]:
        """Return a list of end segments

        Returns:
            List[Segment]: end segments
        """
        return list(self.end_segments_map.values())  # pylint: disable=no-member

    def get_segment_trace(self, ref_name: str) -> List[Segment]:
        """Returns the segment trace from a branch name until the root segment (also including it)

        Args:
            ref_name (str): The name of the end segment (branch name)

        Returns:
            List[Segment]: List of segments from end segment (first) to root (last)
        """
        assert (
            ref_name
            in self.end_segments_map  # pylint: disable=unsupported-membership-test
        ), f'Branch name "{ref_name}" is not used by any end segment!'

        segments = [
            self.end_segments_map[ref_name]  # pylint: disable=unsubscriptable-object
        ]

        while segments[-1].parent:
            segments.append(segments[-1].parent)

        return segments

    def get_segments_trace_until_merge_base(
        self,
        head_ref_name: str,
        base_ref_name: str,
    ) -> Tuple[List[Segment], List[Segment]]:
        """Gets the trace of two end refs (head and base) and returns the segments until the
        first combined segments (thus extracting the individual head and base segment traces).

        Args:
            head_ref_name (str): The head branch name
            base_ref_name (str): The base branch name

        Returns:
            Tuple[List[Segment], List[Segment]]: The individual segment lists (head, base)
        """
        head_segments = self.get_segment_trace(head_ref_name)
        base_segments = self.get_segment_trace(base_ref_name)

        index = -1

        while head_segments[index].end_sha == base_segments[index].end_sha:
            index -= 1

        index += 1

        return head_segments[:index], base_segments[:index]

    def get_entries_until_merge_base(
        self,
        head_ref_name: str,
        base_ref_name: str,
    ) -> Tuple[List[ChangeLogEntry], List[ChangeLogEntry]]:
        """Gets the change log of both branches until the
        first combined segments (thus extracting the individual head and base changelogs).

        Args:
            head_ref_name (str): The head branch name
            base_ref_name (str): The base branch name

        Returns:
            Tuple[List[ChangeLogEntry], List[ChangeLogEntry]]: The individual changelogs
                (head, base)
        """
        head_segments, base_segments = self.get_segments_trace_until_merge_base(
            head_ref_name,
            base_ref_name,
        )

        head_entries_arr = map(lambda x: x.entries, head_segments)
        base_entries_arr = map(lambda x: x.entries, base_segments)

        head_entries = list(itertools.chain.from_iterable(head_entries_arr))
        base_entries = list(itertools.chain.from_iterable(base_entries_arr))

        return head_entries, base_entries
