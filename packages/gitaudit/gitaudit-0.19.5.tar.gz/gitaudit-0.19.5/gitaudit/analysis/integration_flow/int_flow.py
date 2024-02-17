"""This module contains the logic for the integration flow analysis."""

from typing import Union, List, Callable, Dict
from datetime import datetime
import itertools

from pydantic import Field

from gitaudit.root import GitauditRootModel
from gitaudit.github.graphql_objects import (
    PullRequest,
    StatusContext,
    CheckRun,
    PullRequestState,
)


def partition(pred, iterable):
    """
    Use a predicate to partition entries into false entries and true entries.

    Args:
        pred: The predicate to use.
        iterable: The iterable to partition.

    Returns:
        A tuple of two lists. The first list contains the elements that satisfy the predicate.
        The second list contains the elements that do not satisfy the predicate.
    """
    t1, t2 = itertools.tee(iterable)
    return list(filter(pred, t1)), list(itertools.filterfalse(pred, t2))


class RequiredStatusCheck(GitauditRootModel):
    """Required status check"""

    name: str


class IntflowStatusCheck(GitauditRootModel):
    """A wrapper around StatusContext and CheckRun to make them more similar."""

    context: Union[RequiredStatusCheck, StatusContext, CheckRun]

    @property
    def name(self):
        """The name of the status check."""
        return (
            self.context.context
            if isinstance(self.context, StatusContext)
            else self.context.name
        )

    @property
    def has_triggered(self):
        """Whether the status check was triggered."""
        if isinstance(self.context, StatusContext):
            return self.context.created_at is not None
        elif isinstance(self.context, CheckRun):
            return self.context.started_at is not None
        else:
            # RequiredStatusCheck
            return False

    @property
    def triggered_at(self):
        """The time the status check triggered."""
        if isinstance(self.context, StatusContext):
            return self.context.created_at
        elif isinstance(self.context, CheckRun):
            return self.context.started_at
        else:
            # RequiredStatusCheck
            return None

    @property
    def has_finished(self):
        """Whether the status check has finished."""
        if isinstance(self.context, StatusContext):
            return self.context.created_at is not None
        elif isinstance(self.context, CheckRun):
            return self.context.completed_at is not None
        else:
            # RequiredStatusCheck
            return False

    @property
    def finished_at(self):
        """The time the status check completed."""
        if isinstance(self.context, StatusContext):
            return self.context.created_at
        elif isinstance(self.context, CheckRun):
            return self.context.completed_at
        else:
            # RequiredStatusCheck
            return None

    @property
    def running_range(self):
        """The time range the status check was running."""
        return (self.triggered_at, self.finished_at)


def sort_intflow_status_checks(
    status_checks: List[IntflowStatusCheck],
) -> List[IntflowStatusCheck]:
    """
    Sorts the status checks by triggered_at.

    Args:
        status_checks: The status checks to sort.

    Returns:
        The sorted status checks.
    """
    triggered_status_checks = list(filter(lambda x: x.has_triggered, status_checks))
    untriggered_status_checks = list(
        filter(lambda x: not x.has_triggered, status_checks)
    )

    return (
        sorted(
            triggered_status_checks,
            key=lambda x: x.triggered_at,
        )
        + untriggered_status_checks
    )


class IntflowPullRequest(GitauditRootModel):
    """A wrapper around PullRequest to make it more similar to StatusContext."""

    pull_request: PullRequest
    updated_at: datetime
    dependencies: List[str] = Field(default_factory=list)

    status_checks: List[IntflowStatusCheck]
    pre_merge_status_checks: List[IntflowStatusCheck]
    post_merge_status_checks: List[IntflowStatusCheck]
    required_status_checks: List[IntflowStatusCheck]

    @property
    def is_open(self) -> bool:
        """
        Returns True if pull request is open

        Returns:
            bool: True if pull request is open
        """
        return self.pull_request.state == PullRequestState.OPEN

    @property
    def group_key(self):
        """The group key for the pull request."""
        return (
            self.pull_request.repository.name_with_owner,
            self.pull_request.base_ref_name,
        )

    @classmethod
    def from_pull_request(
        cls,
        pull_request: PullRequest,
        required_status_checks: List[str],
        dependencies: List[str] = None,
        updated_at: datetime = None,
    ) -> "IntflowPullRequest":
        """
        Create an IntflowPullRequest from a PullRequest.

        Args:
            pull_request: The PullRequest object.
            required_status_checks: The required status checks for the pull request.

        Returns:
            An IntflowPullRequest object.
        """
        status_checks = [
            IntflowStatusCheck(context=x)
            for x in pull_request.commits[-1].status_check_rollup.contexts
        ]

        # Initialize with required status checks
        status_checks_map: Dict[str, IntflowStatusCheck] = {
            name: IntflowStatusCheck(context=RequiredStatusCheck(name=name))
            for name in required_status_checks
        }

        # Update with the latest status checks (which overrides the required status checks if they exist)
        for status_check in status_checks:
            if status_check.name not in status_checks_map:
                # unrequired status checks are added if not already present
                status_checks_map[status_check.name] = status_check
            else:
                if isinstance(
                    status_checks_map[status_check.name].context, RequiredStatusCheck
                ):
                    # required status checks are overridden
                    status_checks_map[status_check.name] = status_check

                if (
                    status_check.triggered_at
                    > status_checks_map[status_check.name].triggered_at
                ):
                    # latest status checks are overridden
                    status_checks_map[status_check.name] = status_check

        status_checks = sort_intflow_status_checks(
            list(status_checks_map.values()),
        )

        [pre_merge_status_checks, post_merge_status_checks] = partition(
            # RequiredStatusChecks are considered post merge
            lambda x: not (
                isinstance(x.context, RequiredStatusCheck)
                or x.triggered_at >= pull_request.merged_at
            ),
            status_checks,
        )

        required_status_checks = list(
            filter(
                lambda x: x.name in required_status_checks,
                status_checks,
            )
        )

        return cls(
            pull_request=pull_request,
            updated_at=updated_at if updated_at else datetime.utcnow(),
            status_checks=status_checks,
            pre_merge_status_checks=pre_merge_status_checks,
            post_merge_status_checks=post_merge_status_checks,
            required_status_checks=required_status_checks,
            dependencies=dependencies if dependencies else [],
        )


RequiredStatusChecksCallback = Callable[[str, str, str], List[str]]


class IntFlowCreator:
    """A class to create the integration flow."""

    def __init__(
        self,
        pull_requests,
        required_status_checks_callback: RequiredStatusChecksCallback,
    ) -> None:
        self.pull_requests = list(
            map(
                lambda x: IntflowPullRequest.from_pull_request(
                    x,
                    required_status_checks_callback(
                        *x.repository.name_with_owner.split("/"), x.base_ref_name
                    ),
                ),
                pull_requests,
            )
        )

        self.pull_requests_group_map = self._group_pull_requests()

    def _group_pull_requests(self):
        group_map = {}

        for pull_request in self.pull_requests:
            group_key = pull_request.group_key

            if group_key not in group_map:
                group_map[group_key] = []

            group_map[group_key].append(pull_request)

        return group_map
