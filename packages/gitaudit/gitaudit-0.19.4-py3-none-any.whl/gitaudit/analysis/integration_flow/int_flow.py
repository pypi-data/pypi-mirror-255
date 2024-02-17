"""This module contains the logic for the integration flow analysis."""

from typing import Union, List, Callable, Dict

from gitaudit.root import GitauditRootModel
from gitaudit.github.graphql_objects import (
    PullRequest,
    StatusContext,
    CheckRun,
)


class RequiredStatusCheck(GitauditRootModel):
    """Required status check"""

    name: str


class IntflowStatusCheck(GitauditRootModel):
    """A wrapper around StatusContext and CheckRun to make them more similar."""

    context: Union[StatusContext, CheckRun, RequiredStatusCheck]

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


class IntflowPullRequest(GitauditRootModel):
    """A wrapper around PullRequest to make it more similar to StatusContext."""

    pull_request: PullRequest
    status_checks: List[IntflowStatusCheck]
    pre_merge_status_checks: List[IntflowStatusCheck]
    post_merge_status_checks: List[IntflowStatusCheck]
    required_status_checks: List[IntflowStatusCheck]

    @property
    def group_key(self):
        """The group key for the pull request."""
        return (
            self.pull_request.repository.name_with_owner,
            self.pull_request.base_ref_name,
        )

    @classmethod
    def from_pull_request(
        cls, pull_request: PullRequest, required_status_checks: List[str]
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

        # Remove Duplicates
        status_checks_map: Dict[str, IntflowStatusCheck] = {}

        for status_check in status_checks:
            if status_check.name not in status_checks_map:
                status_checks_map[status_check.name] = status_check
            else:
                if (
                    status_check.triggered_at
                    > status_checks_map[status_check.name].triggered_at
                ):
                    status_checks_map[status_check.name] = status_check

        status_checks = sorted(
            list(status_checks_map.values()),
            key=lambda x: x.triggered_at,
        )

        pre_merge_status_checks = list(
            filter(lambda x: x.triggered_at < pull_request.merged_at, status_checks)
        )
        post_merge_status_checks = list(
            filter(lambda x: x.triggered_at >= pull_request.merged_at, status_checks)
        )
        required_status_checks = list(
            filter(
                lambda x: x.name in required_status_checks,
                pre_merge_status_checks,
            )
        )

        return cls(
            pull_request=pull_request,
            status_checks=status_checks,
            pre_merge_status_checks=pre_merge_status_checks,
            post_merge_status_checks=post_merge_status_checks,
            required_status_checks=required_status_checks,
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
