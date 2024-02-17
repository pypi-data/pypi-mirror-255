"""Change Log Entry
"""

from __future__ import annotations

from typing import List, Optional, Dict, Tuple, Any, Type, Callable
from datetime import datetime
import re
import pytz
from pydantic import BaseModel, Field


def extract_line_content(line: str, id_character: str) -> str:
    """Extracts the line content of git log with the format
    "<character>:[<content>]"

    Args:
        line (str): Line to be extracted from
        id_character (str): Single character for controll
            the extraction

    Returns:
        str: Returns the extracted content
    """
    matches = re.findall(
        r"(?<=^" + id_character + r":\[).*?(?=\]$)",
        line,
    )
    assert len(matches) == 1
    return matches[0]


def split_and_strip(text: str, splitby: str = ",") -> List[str]:
    """Split by character and strip each list element

    Args:
        text (str): Text to be split
        splitby (str): character to be split by. Defaults to ','.

    Returns:
        List[str]: List of splitted and stripped strings
    """
    return list(
        filter(
            lambda x: x,
            map(
                lambda x: x.strip(),
                text.split(splitby),
            ),
        )
    )


def extract_tags_refs(tag_line: str) -> Tuple[List[str], List[str]]:
    """Extracts tags and refs from log line

    Args:
        tag_line (str): Line containing the tag and ref tags

    Returns:
        Tuple[List[str], List[str]]: List of tags and refs
    """
    line_content = extract_line_content(tag_line, "T")
    refs = split_and_strip(line_content)
    tags = list(filter(lambda x: x.startswith("tag: "), refs))
    tags = list(map(lambda x: x[5:], tags))
    refs = list(filter(lambda x: not x.startswith("tag: "), refs))
    refs = list(map(lambda x: x.replace("HEAD -> ", ""), refs))

    return tags, refs


def extract_additions_deletions(numstat_text: str) -> List[FileAdditionsDeletions]:
    """Extract additions and deletions from numstat text

    Args:
        numstat_text (str): Multiline text block containing the git
            log num stat information

    Returns:
        List[FileAdditionsDeletions]: List of dictionaries
    """
    content = re.findall(r"(\d+)\t(\d+)\t(.+)", numstat_text)
    return list(
        map(
            lambda x: FileAdditionsDeletions(
                additions=int(x[0]),
                deletions=int(x[1]),
                path=x[2],
            ),
            content,
        )
    )


def extract_submodule_update(numstat_text: str) -> Dict[str, SubmoduleUpdate]:
    """Extract submodule updates from numstat text

    Args:
        numstat_text (str): Multiline text block containing the git
            log num stat and patch information

    Returns:
        Dict[str, SubmoduleUpdate]: List of dictionaries
    """
    content = re.findall(
        r"Submodule\s*(.*?)\s*([a-f0-9]+)\.{3}([a-f0-9]+)",
        numstat_text,
    )
    submodule_list = list(
        map(
            lambda x: SubmoduleUpdate(
                path=x[0],
                from_sha=x[1],
                to_sha=x[2],
            ),
            content,
        )
    )
    return {x.path: x for x in submodule_list}


class FileAdditionsDeletions(BaseModel):
    """Dataclass for storing file additions and deletions"""

    path: str
    additions: int
    deletions: int


class SubmoduleUpdate(BaseModel):
    """Dataclass for storing submodule updates"""

    path: str
    from_sha: str
    to_sha: str
    entries: List[ChangeLogEntry] = Field(default_factory=list)


class SubmoduleInfo(BaseModel):
    """Dataclass for storing submodule information"""

    path: str
    sha: str
    url: str
    name: str

    @property
    def subproject_commit_oid(self) -> str:
        """
        Returns the subproject commit oid

        Returns:
            str: Returns the subproject commit oid
        """
        return self.sha

    @property
    def git_url(self) -> str:
        """
        Returns the git url

        Returns:
            str: Returns the git url
        """
        return self.url


class Issue(BaseModel):
    """Dataclass for storing issue key, title, domains, and url."""

    key: str
    title: Optional[str] = None
    domains: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    fix_versions: List[str] = Field(default_factory=list)
    affected_versions: List[str] = Field(default_factory=list)
    issue_type: Optional[str] = None
    created_at: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    labels: List[str] = Field(default_factory=list)


class IntegrationRequest(BaseModel):
    "Dataclass for storing integration request data"
    owner: str
    repo: str
    number: int
    title: str
    url: str
    body: Optional[str] = None
    labels: List[str] = Field(default_factory=list)

    @property
    def uri(self) -> str:
        """
        Uri of the integration request

        Returns:
            str: Returns an uri for the given integration request based on the owner/org,
                repo name and integration request number.
        """
        return f"{self.owner}/{self.repo}#{self.number}"


UrlProviderCallable = Callable[[str], str]
IssueProviderCallable = Callable[[str, str], List[Issue]]


class ChangeLogEntry(BaseModel):
    """Dataclass for storing change log data"""

    sha: str
    url: Optional[str] = None
    parent_shas: List[str] = Field(default_factory=list)
    cherry_pick_sha: Optional[str] = None
    other_parents: List[List[ChangeLogEntry]] = Field(default_factory=list)
    branch_offs: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    refs: List[str] = Field(default_factory=list)
    subject: Optional[str] = None
    commit_date: Optional[datetime] = None
    author_date: Optional[datetime] = None
    author_name: Optional[str] = None
    author_mail: Optional[str] = None
    body: Optional[str] = ""
    numstat: List[FileAdditionsDeletions] = Field(default_factory=list)
    submodule_updates: Dict[str, SubmoduleUpdate] = Field(default_factory=dict)
    issues: List[Issue] = Field(default_factory=list)
    integration_request: Optional[IntegrationRequest] = None

    @property
    def sorted_numstat(self) -> List[FileAdditionsDeletions]:
        """Path sorted File NumStat

        Returns:
            List[FileAdditionsDeletions]: Sorted numstat
        """
        return sorted(self.numstat, key=lambda x: x.path)

    def copy_without_hierarchy(self) -> ChangeLogEntry:
        """Copy Itself without hierarchy elements
        (branch_offs, other_parents)

        Returns:
            ChangeLogEntry: the copied entry
        """
        copy_dict = self.dict(exclude={"branch_offs", "other_parents"})
        return ChangeLogEntry.parse_obj(copy_dict)

    def copy_as_parentlog_entry(self) -> ChangeLogEntry:
        """Creates a copy of itself but only containing the parent log information

        Returns:
            ChangeLogEntry: Copy with parent log information
        """
        return ChangeLogEntry(
            sha=self.sha,
            parent_shas=self.parent_shas,
            commit_date=self.commit_date,
        )

    def to_save_dict(self) -> Dict[str, Any]:
        """Saves content to dictionary

        Returns:
            Dict[str, any]: dict content of entry
        """
        local_dict = self.dict(
            exclude_defaults=True,
        )

        other_parents_dict = []

        for other_p in self.other_parents:  # pylint: disable=not-an-iterable
            other_parents_dict.append(list(map(lambda x: x.to_save_dict(), other_p)))

        if other_parents_dict:
            local_dict["other_parents"] = other_parents_dict
        return local_dict

    @classmethod
    def from_log_text(
        cls,
        log_text: str,
        url_provider: Optional[UrlProviderCallable] = None,
        issues_provider: Optional[IssueProviderCallable] = None,
        instance_class: Optional[Type[ChangeLogEntry]] = None,
    ) -> ChangeLogEntry:
        """Create ChangeLogEntry from logging text

        Args:
            log_text (str): Logging text
            url_provider (UrlProviderCallable, optional): Url provider callable. Defaults to None.
            issues_provider (IssueProviderCallable, optional): Issue provider callable. Defaults to None.
            instance_class (ChangeLogEntry, optional): Instance class. Defaults to None.

        Returns:
            ChangeLogEntry: Change log entry dataclass
        """
        item_text, rest_text = log_text.split("#SB#", 1)
        body_text, numstat_text = rest_text.split("#EB#", 1)

        cherry_picked_commits = re.findall(
            r"(?<=\(cherry\spicked\sfrom\scommit\s)[a-f0-9]+(?=\))",
            body_text,
        )

        (
            sha_line,
            parents_line,
            tags_line,
            subject_line,
            commit_date_line,
            author_date_line,
            author_name_line,
            author_mail_line,
        ) = item_text.strip().split("\n")

        tags, refs = extract_tags_refs(tags_line)
        sha = extract_line_content(sha_line, "H")

        if not instance_class:
            instance_class = ChangeLogEntry

        subject = extract_line_content(subject_line, "S")
        body = body_text.strip()

        return instance_class(
            sha=sha,
            url=url_provider(sha) if url_provider else None,
            parent_shas=split_and_strip(
                extract_line_content(parents_line, "P"), splitby=" "
            ),
            tags=tags,
            refs=refs,
            subject=subject,
            commit_date=datetime.fromisoformat(
                extract_line_content(commit_date_line, "D")
            ).astimezone(pytz.utc),
            author_date=datetime.fromisoformat(
                extract_line_content(author_date_line, "U")
            ).astimezone(pytz.utc),
            author_name=extract_line_content(author_name_line, "A"),
            author_mail=extract_line_content(author_mail_line, "M"),
            body=body,
            cherry_pick_sha=(
                cherry_picked_commits[0] if len(cherry_picked_commits) == 1 else None
            ),
            numstat=extract_additions_deletions(numstat_text),
            submodule_updates=extract_submodule_update(numstat_text),
            issues=issues_provider(subject, body) if issues_provider else [],
        )

    @classmethod
    def from_head_log_text(
        cls,
        log_text: str,
        instance_class: Optional[Type[ChangeLogEntry]] = None,
    ) -> ChangeLogEntry:
        """Create ChangeLogEntry from logging text

        Args:
            log_text (str): Logging text
            instance_class (ChangeLogEntry, optional): Instance class. Defaults to None.

        Returns:
            ChangeLogEntry: Change log entry dataclass
        """
        res = re.findall(r"([a-f0-9]+)\[(?:([a-f0-9\s]+))?\](?:\((.*?)\))?", log_text)

        if not instance_class:
            instance_class = ChangeLogEntry

        return instance_class(
            sha=res[0][0],
            parent_shas=res[0][1].split(" ") if res[0][1] else [],
            commit_date=datetime.fromisoformat(res[0][2]) if res[0][2] else None,
        )

    @classmethod
    def list_from_objects(
        cls,
        items: List[dict],
        instance_class: Optional[Type[ChangeLogEntry]] = None,
    ) -> List[ChangeLogEntry]:
        """Given a list of dict objects create a list of ChangeLogEntries

        Args:
            items (List[dict]): List of dict objects
            instance_class (ChangeLogEntry, optional): Instance class. Defaults to None.

        Returns:
            List[ChangeLogEntry]: List of ChangeLogEntries
        """

        if not instance_class:
            instance_class = ChangeLogEntry

        return [instance_class.parse_obj(x) for x in items]


SubmoduleUpdate.update_forward_refs()
