"""Gets required status checks for a pull request"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta

from gitaudit.root import GitauditRootModel
from gitaudit.github.instance import Github
from gitaudit.github.graphql_objects import PullRequest, CheckRun


class RequiredNameResult(GitauditRootModel):
    """Result of a required name query"""

    names: List[str]
    last_updated: datetime


class GithubPullRequestRequired:
    """Gets required status checks for a pull request"""

    # for (owner, repo, branch)
    # if not existing
    #     query last merged PR on owner/repo with base:branch
    #     query required check runs for PR

    def __init__(
        self, github: Github, refresh_time_delta: timedelta = timedelta(minutes=30)
    ) -> None:
        self.github = github
        self.refresh_time_delta = refresh_time_delta

        self.repo_branch_map: Dict[Tuple[str, str, str], RequiredNameResult] = {}

    def _get_cached_value(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> List[str]:
        repo_branch_key = (
            owner,
            repo,
            branch,
        )

        if repo_branch_key in self.repo_branch_map:
            res = self.repo_branch_map[repo_branch_key]
            if datetime.utcnow() - res.last_updated < self.refresh_time_delta:
                return res.names
            else:
                self.repo_branch_map.pop(repo_branch_key)

        return None

    def _get_required_for_commit(
        self,
        owner: str,
        repo: str,
        sha: str,
        number: int,
    ) -> List[str]:
        commit = self.github.get_commit_for_expression(
            owner=owner,
            repo=repo,
            expression=sha,
            querydata=f"""
            statusCheckRollup {{
                contexts (last:100) {{
                    nodes {{
                        ... on CheckRun {{
                            name
                            isRequired (pullRequestNumber: {number})
                        }}
                        ... on StatusContext {{
                            context
                            isRequired (pullRequestNumber: {number})
                        }}
                    }}
                }}
            }}
            """,
        )

        if not commit.status_check_rollup:
            return []

        return list(
            map(
                lambda y: y.name if isinstance(y, CheckRun) else y.context,
                filter(lambda x: x.is_required, commit.status_check_rollup.contexts),
            )
        )

    def get_required_status_checks_for_branch(
        self, owner: str, repo: str, branch: str
    ) -> List[str]:
        """
        Gets required check run names for a branch

        Args:
            owner: Owner of the repository
            repo: Repository name
            branch: Branch name

        Returns:
            list[str]: List of required check run names
        """

        names = self._get_cached_value(owner, repo, branch)

        if names is not None:
            return names

        pull_requests = self.github.search_pull_requests(
            search_query=f"repo:{owner}/{repo} base:{branch} is:pr is:merged",
            querydata="headRefOid number repository { nameWithOwner } baseRefName state",
            count=1,
        )

        if not pull_requests:
            pull_requests = self.github.search_pull_requests(
                search_query=f"repo:{owner}/{repo} base:{branch} is:pr",
                querydata="headRefOid number repository { nameWithOwner } baseRefName state",
                count=1,
            )

        if not len(pull_requests) == 1:
            return []

        pull_request = pull_requests[0]

        names = self._get_required_for_commit(
            owner=owner,
            repo=repo,
            sha=pull_request.head_ref_oid,
            number=pull_request.number,
        )

        self.repo_branch_map[(owner, repo, branch)] = RequiredNameResult(
            names=names,
            last_updated=datetime.utcnow(),
        )

        return list(set(names))

    def get_required_status_checks_for_pull_request(
        self, pull_request: PullRequest
    ) -> List[str]:
        """
        Gets required check run names for a pull request

        Args:
            pull_request: Pull request to get required check run names for

        Returns:
            list[str]: List of required check run names"""

        owner, repo = pull_request.repository.name_with_owner.split("/")

        return self.get_required_status_checks_for_branch(
            owner=owner, repo=repo, branch=pull_request.base_ref_name
        )
