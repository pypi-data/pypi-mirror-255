"""Render Change Logs
"""

from typing import List
import os

from pydantic import BaseModel
import jinja2

from gitaudit.git.change_log_entry import ChangeLogEntry, FileAdditionsDeletions


class ChangeLogRenderConfig(BaseModel):
    """Determines wich elements of the changelog are visible"""

    show_sha: bool = True
    show_headline: bool = True
    show_integration_request_title_instead_of_headline: bool = True
    show_integration_request_labels: bool = False
    show_additions_deletions: bool = True
    show_commit_date: bool = True
    show_commit_author: bool = False
    show_commit_body: bool = False
    show_numstat: bool = False
    show_issues: bool = True
    show_other_parents: bool = False
    show_submodule_update: bool = True
    show_submodule_changelog: bool = True


def calculate_total_additions(numstat: List[FileAdditionsDeletions]):
    """
    Calculate the total number of additions for a given list of file additions and deletions.

    Args:
        numstat (List[FileAdditionsDeletions]): A list of objects containing the additions and
            deletions for each file.

    Returns:
        int: The total number of additions across all files.
    """
    return sum(item.additions for item in numstat)


def calculate_total_deletions(numstat: List[FileAdditionsDeletions]):
    """
    Calculate the total number of deletions for a given list of file additions and deletions.

    Args:
        numstat (List[FileAdditionsDeletions]): A list of objects containing the additions and
            deletions for each file.

    Returns:
        int: The total number of deletions across all files.
    """
    return sum(item.deletions for item in numstat)


def render_change_log_to_text(
    entries: List[ChangeLogEntry],
    render_config: ChangeLogRenderConfig = None,
    root_repo_name: str = None,
) -> str:
    """Renders the change log entries as a formatted text using a Jinja2 template.

    Args:
        entries (List[ChangeLogEntry]): A list of ChangeLogEntry objects to be included in the
            rendered text.

    Returns:
        str: A string containing the rendered change log entries as formatted text.
    """
    if not render_config:
        render_config = ChangeLogRenderConfig()

    template_root = os.path.join(os.path.dirname(__file__), "templates")

    template_loader = jinja2.FileSystemLoader(searchpath=template_root)
    template_env = jinja2.Environment(
        loader=template_loader, undefined=jinja2.StrictUndefined
    )
    template_env.globals["calculate_total_additions"] = calculate_total_additions
    template_env.globals["calculate_total_deletions"] = calculate_total_deletions
    template = template_env.get_template("change_log.html")
    return template.render(
        root_repo_name=root_repo_name,
        change_log_entries=entries,
        config=render_config,
    )


def render_change_log_to_file(
    entries: List[ChangeLogEntry],
    file_path: str,
    render_config: ChangeLogRenderConfig = None,
    root_repo_name: str = None,
):
    """Renders the change log entries as a formatted text using a Jinja2 template and saves the
        result to a file.

    Args:
        entries (List[ChangeLogEntry]): A list of ChangeLogEntry objects to be included in the
            rendered text.
        file_path (str): The path to the file where the rendered text will be saved.

    Returns:
        None
    """
    with open(file_path, "w", encoding="utf-8") as file_p:
        file_p.write(
            render_change_log_to_text(
                entries=entries,
                render_config=render_config,
                root_repo_name=root_repo_name,
            )
        )
