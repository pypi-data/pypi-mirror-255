"""Reporting code for merge diff
"""

from __future__ import annotations

from enum import Enum
from typing import List, Tuple
import os
import itertools
import jinja2

from pydantic import BaseModel, Field

from gitaudit.git.change_log_entry import ChangeLogEntry
from .matchers import MatchResult


class MergeDiffReportAlertSeverity(Enum):
    """Merge diff Severity"""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class MergeDiffAlert(BaseModel):
    """Merge diff Report Alert"""

    match: MatchResult
    severity: MergeDiffReportAlertSeverity
    message: str

    @classmethod
    def info(cls, match, message):
        """Create Info Merge diff Report Alert

        Args:
            match (MatchResult): Match Result
            message (str): Message

        Returns:
            MergeDiffAlert: Alert
        """
        return MergeDiffAlert(
            match=match,
            severity=MergeDiffReportAlertSeverity.INFO,
            message=message,
        )

    @classmethod
    def warning(cls, match, message):
        """Create Warning Merge diff Report Alert

        Args:
            match (MatchResult): Match Result
            message (str): Message

        Returns:
            MergeDiffAlert: Alert
        """
        return MergeDiffAlert(
            match=match,
            severity=MergeDiffReportAlertSeverity.WARNING,
            message=message,
        )

    @classmethod
    def error(cls, match, message):
        """Create Error Merge diff Report Alert

        Args:
            match (MatchResult): Match Result
            message (str): Message

        Returns:
            MergeDiffAlert: Alert
        """
        return MergeDiffAlert(
            match=match,
            severity=MergeDiffReportAlertSeverity.ERROR,
            message=message,
        )


class RefInfo(BaseModel):
    """Reference Info"""

    ref_name: str
    sha: str
    merge_commit_count: int
    individual_commit_count: int
    total_commit_count: int
    additions: int
    deletions: int

    @classmethod
    def combine(cls, arr: List[RefInfo]) -> RefInfo:
        """Combine multiple ref infos into one

        Args:
            arr (List[RefInfo]): list of ref infos

        Returns:
            RefInfo: combined ref info
        """
        ref_names = list(map(lambda x: x.ref_name, arr))
        assert all(
            map(lambda x: ref_names[0] == x, ref_names)
        ), "All ref names must be the same!"

        merge_commit_count = sum(map(lambda x: x.merge_commit_count, arr))
        individual_commit_count = sum(map(lambda x: x.individual_commit_count, arr))
        total_commit_count = sum(map(lambda x: x.total_commit_count, arr))
        additions = sum(map(lambda x: x.additions, arr))
        deletions = sum(map(lambda x: x.deletions, arr))

        return RefInfo(
            ref_name=ref_names[0],
            sha="plural",
            merge_commit_count=merge_commit_count,
            individual_commit_count=individual_commit_count,
            total_commit_count=total_commit_count,
            additions=additions,
            deletions=deletions,
        )


class MergeDiffReport(BaseModel):
    """Merge Report class"""

    name: str
    head_info: RefInfo
    base_info: RefInfo
    matches: List[Tuple[str, List[MatchResult]]] = Field(default_factory=list)
    alerts: List[MergeDiffAlert] = Field(default_factory=list)
    head_prunes: List[Tuple[str, List[ChangeLogEntry]]] = Field(default_factory=list)
    base_prunes: List[Tuple[str, List[ChangeLogEntry]]] = Field(default_factory=list)
    head_unmatched: List[ChangeLogEntry] = Field(default_factory=list)
    base_unmatched: List[ChangeLogEntry] = Field(default_factory=list)

    @property
    def matches_count(self) -> int:
        """Match count"""
        return sum(map(lambda x: len(x[1]), self.matches))

    @property
    def head_prunes_count(self) -> int:
        """Head prune count"""
        return sum(map(lambda x: len(x[1]), self.head_prunes))

    @property
    def base_prunes_count(self) -> int:
        """Base prune count"""
        return sum(map(lambda x: len(x[1]), self.base_prunes))

    def append_match(self, matcher_id: str, matches: List[MatchResult]):
        """Append match result to report

        Args:
            match (MatchResult): Match result to be added
        """
        self.matches.append((matcher_id, matches))  # pylint: disable=no-member

    def append_alert(self, alert: MergeDiffAlert):
        """Append merge diff report alert

        Args:
            alert (MergeDiffReportEntry): Merge diff Report Alert
        """
        self.alerts.append(alert)  # pylint: disable=no-member

    def append_head_prune(self, pruner_id: str, entries: List[ChangeLogEntry]):
        """Append a head prune entry
        Args:
            entry (ChangeLogEntry): Pruned change log entry
        """
        self.head_prunes.append((pruner_id, entries))  # pylint: disable=no-member

    def append_base_prune(self, pruner_id: str, entries: List[ChangeLogEntry]):
        """Append a base prune entry
        Args:
            entry (ChangeLogEntry): Pruned change log entry
        """
        self.base_prunes.append((pruner_id, entries))  # pylint: disable=no-member

    def set_head_unmatched(self, entries: List[ChangeLogEntry]):
        """Sets the head change log entries that could not be matched

        Args:
            entries (List[ChangeLogEntry]): Unmatched change log entries
        """
        self.head_unmatched = entries

    def set_base_unmatched(self, entries: List[ChangeLogEntry]):
        """Sets the base change log entries that could not be matched

        Args:
            entries (List[ChangeLogEntry]): Unmatched change log entries
        """
        self.base_unmatched = entries

    def to_dict(self):
        """Converts the Report into a dictionary

        Returns:
            Dict: Report serialized as a dictionary
        """
        rep_dict = self.dict()
        rep_dict["matches_count"] = self.matches_count
        rep_dict["head_prunes_count"] = self.head_prunes_count
        rep_dict["base_prunes_count"] = self.base_prunes_count
        return rep_dict

    def render_to_text(self) -> str:
        """Render the html report to text

        Returns:
            str: Html report as text
        """
        template_root = os.path.join(os.path.dirname(__file__), "report_templates")

        template_loader = jinja2.FileSystemLoader(searchpath=template_root)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("single_report.html")
        return template.render(report=self.to_dict())

    def render_to_file(self, file_path: str) -> None:
        """Write html report to file

        Args:
            file_path (str): File path for report to be save to
        """
        with open(file_path, "w", encoding="utf-8") as file_p:
            file_p.write(self.render_to_text())

    @classmethod
    def combine(cls, arr: List[MergeDiffReport]) -> MergeDiffReport:
        """Combine multiple merge diff reports into one

        Args:
            arr (List[MergeDiffReport]): list of merge diff reports

        Returns:
            MergeDiffReport: single merge diff report
        """
        head_info = RefInfo.combine(list(map(lambda x: x.head_info, arr)))
        base_info = RefInfo.combine(list(map(lambda x: x.base_info, arr)))

        matches = list(itertools.chain.from_iterable(map(lambda x: x.matches, arr)))
        alerts = list(itertools.chain.from_iterable(map(lambda x: x.alerts, arr)))
        head_prunes = list(
            itertools.chain.from_iterable(map(lambda x: x.head_prunes, arr))
        )
        base_prunes = list(
            itertools.chain.from_iterable(map(lambda x: x.base_prunes, arr))
        )
        head_unmatched = list(
            itertools.chain.from_iterable(map(lambda x: x.head_unmatched, arr))
        )
        base_unmatched = list(
            itertools.chain.from_iterable(map(lambda x: x.base_unmatched, arr))
        )

        return MergeDiffReport(
            name="Combined",
            head_info=head_info,
            base_info=base_info,
            matches=matches,
            alerts=alerts,
            head_prunes=head_prunes,
            base_prunes=base_prunes,
            head_unmatched=head_unmatched,
            base_unmatched=base_unmatched,
        )


def render_combined_report_to_text(reports: List[MergeDiffReport]) -> str:
    """Render multiple reports to a single text report

    Returns:
        str: Html report as text
    """
    combined = MergeDiffReport.combine(reports)

    template_root = os.path.join(os.path.dirname(__file__), "report_templates")

    template_loader = jinja2.FileSystemLoader(searchpath=template_root)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("combined_report.html")
    return template.render(combined=combined, reports=reports)


def render_combined_report_to_file(
    reports: List[MergeDiffReport], file_path: str
) -> None:
    """Writemultiple reports as single html to file

    Args:
        file_path (str): File path for report to be save to
    """
    with open(file_path, "w", encoding="utf-8") as file_p:
        file_p.write(render_combined_report_to_text(reports))
