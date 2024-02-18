"""Utils for git operations"""

from typing import List, Tuple
import re

from pydantic import BaseModel


class GitModulesFileEntry(BaseModel):
    """
    Class to represent an entry in a `.gitmodules` file.

    Attributes:
        name (str): Name of the submodule as specified in the `.gitmodules` file.
        path (str): Path of the submodule within the repository.
        url (str): URL of the submodule's remote repository.
    """

    name: str
    path: str
    url: str


def read_git_modules_text(git_modules_text: str) -> List[GitModulesFileEntry]:
    """
    Retrieves the gitmodules file info from the .gitmodules file.

    Args:
        git_modules_text (str): The gitmodules file content

    Returns:
        List[GitModulesFileEntry]: A list of GitModulesFileEntry objects representing the info
            in the .gitmodules file.
    """
    res_modules_info = re.findall(
        r"submodule\s\"(.*?)\".*?path\s=\s(.*?)\n.*?url\s=\s(.*?)\n.*?branch\s=\s(.*?)",
        git_modules_text,
        re.DOTALL | re.MULTILINE,
    )

    return [
        GitModulesFileEntry.parse_obj(
            {
                "name": res[0],
                "path": res[1],
                "url": res[2],
            }
        )
        for res in res_modules_info
    ]


def get_submodule_url_from_parent_url(parent_url: str, git_url: str) -> str:
    """Create the url of the submodule from the parent url.

    Args:
        parent_url (str): Parent url
        git_url (str): Git url

    Returns:
        str: The url of the submodule
    """
    if (
        git_url.startswith("git@")
        or git_url.startswith("https://")
        or git_url.startswith("http://")
    ):
        return git_url

    sub_url_parts = list(
        filter(None, re.split(r"[/:]", re.sub(r"\.git$", r"", git_url)))
    )
    parent_url_parts = list(
        filter(None, re.split(r"[/:]", re.sub(r"\.git$", r"", parent_url)))
    )

    while sub_url_parts:
        sub_part = sub_url_parts.pop(0)

        if sub_part == "..":
            parent_url_parts = parent_url_parts[:-1]
        else:
            parent_url_parts.append(sub_part)

    if parent_url_parts[0] == "http" or parent_url_parts[0] == "https":
        parent_url_parts[0] += ":/"  # second "/" will be added by join at the end

    if parent_url_parts[0].startswith("git@"):
        parent_url_parts[1] = parent_url_parts[0] + ":" + parent_url_parts[1]
        parent_url_parts = parent_url_parts[1:]

    return "/".join(parent_url_parts) + ".git"


def get_submodule_owner_repo_from_parent_url(
    parent_url: str, git_url: str
) -> Tuple[str, str]:
    """Create the owner and repo of the submodule from the parent url.

    Args:
        parent_url (str): Parent url

    Returns:
        Tuple[str, str]: The owner and repo of the submodule
    """
    sub_url = get_submodule_url_from_parent_url(parent_url, git_url)

    sub_url_parts = re.split(r"[/:]", re.sub(r"\.git$", r"", sub_url))

    return sub_url_parts[-2], sub_url_parts[-1]
