"""Github GraphQL Objects"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
import re

from typing import List, Optional, Union, Tuple

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import root_validator, Field
from gitaudit.git.change_log_entry import IntegrationRequest
from .graphql_base import GraphQlBase


class GitActor(GraphQlBase):
    """Represents an actor in a Git commit (ie. an author or committer)."""

    name: Optional[str] = None
    email: Optional[str] = None
    date: Optional[datetime] = None


class Actor(GraphQlBase):
    """Represents an object which can
    take actions on GitHub. Typically a User or Bot."""

    login: Optional[str] = None


class Team(GraphQlBase):
    """Github Team"""

    name: Optional[str] = None


RequestedReviewer = Union[Actor, Team]


class Label(GraphQlBase):
    """A label for categorizing Issues, Pull Requests,
    Milestones, or Discussions with a given Repository."""

    name: Optional[str] = None
    color: Optional[str] = None
    id: Optional[str] = None


class Comment(GraphQlBase):
    """Represents a comment."""

    author: Optional[Actor] = None
    created_at: Optional[datetime] = None
    body: Optional[str] = None


class PullRequestReviewState(str, Enum):
    """Pull Request Review State"""

    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    COMMENTED = "COMMENTED"
    DISMISSED = "DISMISSED"
    PENDING = "PENDING"


class PullRequestReview(GraphQlBase):
    """A review object for a given pull request."""

    author: Optional[Actor] = None
    created_at: Optional[datetime] = None
    body: Optional[str] = None
    state: Optional[str] = None


class Submodule(GraphQlBase):
    """A submodule reference"""

    name: Optional[str] = None
    subproject_commit_oid: Optional[str] = None
    branch: Optional[str] = None
    git_url: Optional[str] = None
    path: Optional[str] = None

    def get_owner_repo_from_parent_url(self, parent_url: str) -> Tuple[str, str]:
        """Create the owner and repo of the submodule from the parent url.

        Args:
            parent_url (str): Parent url

        Returns:
            Tuple[str, str]: The owner and repo of the submodule
        """
        sub_url = re.split(r"[/:]", re.sub(r"\.git$", r"", self.git_url))
        parent_url = re.split(r"[/:]", re.sub(r"\.git$", r"", parent_url))

        while sub_url:
            sub_part = sub_url.pop(0)

            if sub_part == "..":
                parent_url = parent_url[:-1]
            else:
                parent_url.append(sub_part)

        return parent_url[-2], parent_url[-1]


class StatusState(str, Enum):
    """Status State"""

    ERROR = "ERROR"
    EXPECTED = "EXPECTED"
    FAILURE = "FAILURE"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"


class CheckConclusionState(str, Enum):
    """Check Conclusion State"""

    ACTION_REQUIRED = "ACTION_REQUIRED"
    CANCELLED = "CANCELLED"
    FAILURE = "FAILURE"
    NEUTRAL = "NEUTRAL"
    SKIPPED = "SKIPPED"
    STALE = "STALE"
    STARTUP_FAILURE = "STARTUP_FAILURE"
    SUCCESS = "SUCCESS"
    TIMED_OUT = "TIMED_OUT"


class CheckStatusState(str, Enum):
    """Check Status State"""

    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    REQUESTED = "REQUESTED"
    WAITING = "WAITING"


class PullRequestState(str, Enum):
    """Pull Request State"""

    CLOSED = "CLOSED"
    MERGED = "MERGED"
    OPEN = "OPEN"


class CheckRun(GraphQlBase):
    """A CheckRun"""

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    name: Optional[str] = None
    conclusion: Optional[CheckConclusionState] = None
    status: Optional[CheckStatusState] = None
    is_required: Optional[bool] = None
    name: Optional[str] = None
    summary: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None


class StatusContext(GraphQlBase):
    """A StatusContext"""

    context: Optional[str] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    state: Optional[StatusState] = None


class StatusCheckRollup(GraphQlBase):
    """The Status Check Rollup"""

    state: Optional[StatusState] = None
    contexts: List[Union[CheckRun, StatusContext]] = Field(default_factory=list)


class Commit(GraphQlBase):
    """Represents a Git commit."""

    oid: Optional[str] = None
    additions: Optional[int] = None
    deletions: Optional[int] = None
    message: Optional[str] = None
    message_body: Optional[str] = None
    message_headline: Optional[str] = None
    author: Optional[GitActor] = None
    committed_date: Optional[datetime] = None
    status_check_rollup: Optional[StatusCheckRollup] = None


class Issue(GraphQlBase):
    """An issue"""


class PullRequest(GraphQlBase):
    """A repository pull request."""

    author: Optional[Actor] = None
    number: Optional[int] = None
    comments: List[Comment] = Field(default_factory=list)
    commits: List[Commit] = Field(default_factory=list)
    labels: List[Label] = Field(default_factory=list)
    base_ref_name: Optional[str] = None
    head_ref_name: Optional[str] = None
    head_ref_oid: Optional[str] = None
    merge_commit: Optional[Commit] = None
    created_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    body: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    id: Optional[str] = None
    repository: Optional[Repository] = None
    reviews: Optional[List[PullRequestReview]] = None
    status_check_rollup: Optional[StatusCheckRollup] = None
    state: Optional[PullRequestState] = None
    timeline_items: Optional[
        List[
            Union[
                AddedToMergeQueueEvent,
                AddedToProjectEvent,
                AssignedEvent,
                AutoMergeDisabledEvent,
                AutoMergeEnabledEvent,
                AutoRebaseEnabledEvent,
                AutoSquashEnabledEvent,
                AutomaticBaseChangeFailedEvent,
                AutomaticBaseChangeSucceededEvent,
                BaseRefChangedEvent,
                BaseRefDeletedEvent,
                BaseRefForcePushedEvent,
                ClosedEvent,
                CommentDeletedEvent,
                ConnectedEvent,
                ConvertToDraftEvent,
                ConvertedNoteToIssueEvent,
                ConvertedToDiscussionEvent,
                CrossReferencedEvent,
                DemilestonedEvent,
                DeployedEvent,
                DeploymentEnvironmentChangedEvent,
                DisconnectedEvent,
                HeadRefDeletedEvent,
                HeadRefForcePushedEvent,
                HeadRefRestoredEvent,
                IssueComment,
                LabeledEvent,
                LockedEvent,
                MarkedAsDuplicateEvent,
                MentionedEvent,
                MergedEvent,
                MilestonedEvent,
                MovedColumnsInProjectEvent,
                PinnedEvent,
                PullRequestCommit,
                PullRequestCommitCommentThread,
                PullRequestReview,
                PullRequestReviewThread,
                PullRequestRevisionMarker,
                ReadyForReviewEvent,
                ReferencedEvent,
                RemovedFromMergeQueueEvent,
                RemovedFromProjectEvent,
                RenamedTitleEvent,
                ReopenedEvent,
                ReviewDismissedEvent,
                ReviewRequestRemovedEvent,
                ReviewRequestedEvent,
                SubscribedEvent,
                TransferredEvent,
                UnassignedEvent,
                UnlabeledEvent,
                UnlockedEvent,
                UnmarkedAsDuplicateEvent,
                UnpinnedEvent,
                UnsubscribedEvent,
                UserBlockedEvent,
            ]
        ]
    ] = Field(default_factory=list)

    @property
    def uri(self) -> str:
        """Returns the uri of the pull request.

        Returns:
            str: The uri of the pull request
        """
        return f"{self.repository.name_with_owner}#{self.number}"

    @root_validator(pre=True)
    def prep_pull_request_data(cls, data: dict):  # pylint: disable=no-self-argument
        """Prep Pull Request Data

        Args:
            data (dict): The to be validated input data

        Returns:
            dict: The valiated and transformed input data
        """

        if "commits" in data:
            if "nodes" in data["commits"]:
                data["commits"] = data["commits"]["nodes"]

            data["commits"] = list(
                map(
                    lambda x: x["commit"] if "commit" in x else x,
                    data["commits"],
                )
            )

            if "headRefOid" in data and all(map(lambda x: "oid" in x, data["commits"])):
                commit_map = {c["oid"]: c for c in data["commits"]}

                head_commit = commit_map[data["headRefOid"]]

                if (
                    "statusCheckRollup" in head_commit
                    and "contexts" in head_commit["statusCheckRollup"]
                ):
                    data["statusCheckRollup"] = head_commit["statusCheckRollup"]

        return data

    def to_integration_request(self) -> IntegrationRequest:
        """Converts the pull request into a generic integration request.

        Returns:
            IntegrationRequest: The created integration request
        """
        return IntegrationRequest(
            owner=self.repository.owner.login,
            repo=self.repository.name,
            number=self.number,
            title=self.title,
            url=self.url,
            body=self.body,
            labels=list(map(lambda x: x.name, self.labels)),
        )


class PullRequestList(GraphQlBase):
    """Wrapper Class to save/load list of pull requests"""

    root: List[PullRequest] = Field(default_factory=list)


class Ref(GraphQlBase):
    """A Git reference object."""

    name: Optional[str] = None
    prefix: Optional[str] = None


class Repository(GraphQlBase):
    """A repository contains the content for a project."""

    id: Optional[str] = None
    name: Optional[str] = None
    owner: Optional[Actor] = None
    pull_requests: List[PullRequest] = Field(default_factory=list)
    name_with_owner: Optional[str] = None
    pull_request: Optional[PullRequest] = None
    ssh_url: Optional[str] = None
    default_branch_ref: Optional[Ref] = None


class AddedToMergeQueueEvent(GraphQlBase):
    """AddedToMergeQueueEvent"""

    typename: Literal["AddedToMergeQueueEvent"]


class AddedToProjectEvent(GraphQlBase):
    """AddedToProjectEvent"""

    typename: Literal["AddedToProjectEvent"]


class AssignedEvent(GraphQlBase):
    """AssignedEvent"""

    typename: Literal["AssignedEvent"]
    actor: Optional[Actor] = None
    assignee: Optional[Actor] = None
    created_at: Optional[datetime] = None


class AutoMergeDisabledEvent(GraphQlBase):
    """AutoMergeDisabledEvent"""

    typename: Literal["AutoMergeDisabledEvent"]


class AutoMergeEnabledEvent(GraphQlBase):
    """AutoMergeEnabledEvent"""

    typename: Literal["AutoMergeEnabledEvent"]


class AutoRebaseEnabledEvent(GraphQlBase):
    """AutoRebaseEnabledEvent"""

    typename: Literal["AutoRebaseEnabledEvent"]


class AutoSquashEnabledEvent(GraphQlBase):
    """AutoSquashEnabledEvent"""

    typename: Literal["AutoSquashEnabledEvent"]


class AutomaticBaseChangeFailedEvent(GraphQlBase):
    """AutomaticBaseChangeFailedEvent"""

    typename: Literal["AutomaticBaseChangeFailedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    new_base: Optional[str] = None
    old_base: Optional[str] = None


class AutomaticBaseChangeSucceededEvent(GraphQlBase):
    """AutomaticBaseChangeSucceededEvent"""

    typename: Literal["AutomaticBaseChangeSucceededEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    new_base: Optional[str] = None
    old_base: Optional[str] = None


class BaseRefChangedEvent(GraphQlBase):
    """BaseRefChangedEvent"""

    typename: Literal["BaseRefChangedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    current_ref_name: Optional[str] = None
    previous_ref_name: Optional[str] = None


class BaseRefDeletedEvent(GraphQlBase):
    """BaseRefDeletedEvent"""

    typename: Literal["BaseRefDeletedEvent"]


class BaseRefForcePushedEvent(GraphQlBase):
    """BaseRefForcePushedEvent"""

    typename: Literal["BaseRefForcePushedEvent"]


class ClosedEvent(GraphQlBase):
    """ClosedEvent"""

    typename: Literal["ClosedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None


class CommentDeletedEvent(GraphQlBase):
    """CommentDeletedEvent"""

    typename: Literal["CommentDeletedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None


class ConnectedEvent(GraphQlBase):
    """ConnectedEvent"""

    typename: Literal["ConnectedEvent"]


class ConvertToDraftEvent(GraphQlBase):
    """ConvertToDraftEvent"""

    typename: Literal["ConvertToDraftEvent"]


class ConvertedNoteToIssueEvent(GraphQlBase):
    """ConvertedNoteToIssueEvent"""

    typename: Literal["ConvertedNoteToIssueEvent"]


class ConvertedToDiscussionEvent(GraphQlBase):
    """ConvertedToDiscussionEvent"""

    typename: Literal["ConvertedToDiscussionEvent"]


class CrossReferencedEvent(GraphQlBase):
    """CrossReferencedEvent"""

    typename: Literal["CrossReferencedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    is_cross_repository: Optional[bool] = None
    referenced_at: Optional[datetime] = None
    source: Optional[Union[PullRequest, Issue]] = None
    target: Optional[Union[PullRequest, Issue]] = None


class DemilestonedEvent(GraphQlBase):
    """DemilestonedEvent"""

    typename: Literal["DemilestonedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    milestone_title: Optional[str] = None


class DeployedEvent(GraphQlBase):
    """DeployedEvent"""

    typename: Literal["DeployedEvent"]


class DeploymentEnvironmentChangedEvent(GraphQlBase):
    """DeploymentEnvironmentChangedEvent"""

    typename: Literal["DeploymentEnvironmentChangedEvent"]


class DisconnectedEvent(GraphQlBase):
    """DisconnectedEvent"""

    typename: Literal["DisconnectedEvent"]


class HeadRefDeletedEvent(GraphQlBase):
    """HeadRefDeletedEvent"""

    typename: Literal["HeadRefDeletedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    head_ref_name: Optional[str] = None


class HeadRefForcePushedEvent(GraphQlBase):
    """HeadRefForcePushedEvent"""

    typename: Literal["HeadRefForcePushedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    before_commit: Optional[Commit] = None
    after_commit: Optional[Commit] = None


class HeadRefRestoredEvent(GraphQlBase):
    """HeadRefRestoredEvent"""

    typename: Literal["HeadRefRestoredEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None


class IssueComment(Comment):
    """IssueComment"""

    typename: Literal["IssueComment"]


class LabeledEvent(GraphQlBase):
    """LabeledEvent"""

    typename: Literal["LabeledEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    label: Optional[Label] = None


class LockedEvent(GraphQlBase):
    """LockedEvent"""

    typename: Literal["LockedEvent"]


class MarkedAsDuplicateEvent(GraphQlBase):
    """MarkedAsDuplicateEvent"""

    typename: Literal["MarkedAsDuplicateEvent"]


class MentionedEvent(GraphQlBase):
    """MentionedEvent"""

    typename: Literal["MentionedEvent"]


class MergedEvent(GraphQlBase):
    """MergedEvent"""

    typename: Literal["MergedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    commit: Optional[Commit] = None


class MilestonedEvent(GraphQlBase):
    """MilestonedEvent"""

    typename: Literal["MilestonedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    milestone_title: Optional[str] = None


class MovedColumnsInProjectEvent(GraphQlBase):
    """MovedColumnsInProjectEvent"""

    typename: Literal["MovedColumnsInProjectEvent"]


class PinnedEvent(GraphQlBase):
    """PinnedEvent"""

    typename: Literal["PinnedEvent"]


class PullRequestCommit(GraphQlBase):
    """PullRequestCommit"""

    typename: Literal["PullRequestCommit"]
    commit: Optional[Commit] = None


class PullRequestCommitCommentThread(GraphQlBase):
    """PullRequestCommitCommentThread"""

    typename: Literal["PullRequestCommitCommentThread"]


class PullRequestReviewThread(GraphQlBase):
    """PullRequestReviewThread"""

    typename: Literal["PullRequestReviewThread"]


class PullRequestRevisionMarker(GraphQlBase):
    """PullRequestRevisionMarker"""

    typename: Literal["PullRequestRevisionMarker"]


class ReadyForReviewEvent(GraphQlBase):
    """ReadyForReviewEvent"""

    typename: Literal["ReadyForReviewEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None


class ReferencedEvent(GraphQlBase):
    """ReferencedEvent"""

    typename: Literal["ReferencedEvent"]


class RemovedFromMergeQueueEvent(GraphQlBase):
    """RemovedFromMergeQueueEvent"""

    typename: Literal["RemovedFromMergeQueueEvent"]


class RemovedFromProjectEvent(GraphQlBase):
    """RemovedFromProjectEvent"""

    typename: Literal["RemovedFromProjectEvent"]


class RenamedTitleEvent(GraphQlBase):
    """RenamedTitleEvent"""

    typename: Literal["RenamedTitleEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    current_title: Optional[str] = None
    previous_title: Optional[str] = None


class ReopenedEvent(GraphQlBase):
    """ReopenedEvent"""

    typename: Literal["ReopenedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None


class ReviewDismissedEvent(GraphQlBase):
    """ReviewDismissedEvent"""

    typename: Literal["ReviewDismissedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    dismissal_message: Optional[str] = None
    review: Optional[PullRequestReview]


class ReviewRequestRemovedEvent(GraphQlBase):
    """ReviewRequestRemovedEvent"""

    typename: Literal["ReviewRequestRemovedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    requested_reviewer: Optional[RequestedReviewer] = None


class ReviewRequestedEvent(GraphQlBase):
    """ReviewRequestedEvent"""

    typename: Literal["ReviewRequestedEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    requested_reviewer: Optional[RequestedReviewer] = None


class SubscribedEvent(GraphQlBase):
    """SubscribedEvent"""

    typename: Literal["SubscribedEvent"]


class TransferredEvent(GraphQlBase):
    """TransferredEvent"""

    typename: Literal["TransferredEvent"]


class UnassignedEvent(GraphQlBase):
    """UnassignedEvent"""

    typename: Literal["UnassignedEvent"]
    actor: Optional[Actor] = None
    assignee: Optional[Actor] = None
    created_at: Optional[datetime] = None


class UnlabeledEvent(GraphQlBase):
    """UnlabeledEvent"""

    typename: Literal["UnlabeledEvent"]
    actor: Optional[Actor] = None
    created_at: Optional[datetime] = None
    label: Optional[Label] = None


class UnlockedEvent(GraphQlBase):
    """UnlockedEvent"""

    typename: Literal["UnlockedEvent"]


class UnmarkedAsDuplicateEvent(GraphQlBase):
    """UnmarkedAsDuplicateEvent"""

    typename: Literal["UnmarkedAsDuplicateEvent"]


class UnpinnedEvent(GraphQlBase):
    """UnpinnedEvent"""

    typename: Literal["UnpinnedEvent"]


class UnsubscribedEvent(GraphQlBase):
    """UnsubscribedEvent"""

    typename: Literal["UnsubscribedEvent"]


class UserBlockedEvent(GraphQlBase):
    """UserBlockedEvent"""

    typename: Literal["UserBlockedEvent"]


PullRequest.update_forward_refs()
