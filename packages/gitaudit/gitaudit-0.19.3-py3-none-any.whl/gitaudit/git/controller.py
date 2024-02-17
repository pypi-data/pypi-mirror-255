"""Class that communicated with local git installation."""

import os
from typing import List, Optional, Iterator, Type
import subprocess
import io
import re
import logging
from datetime import datetime

from rich.progress import (
    Progress,
    TimeElapsedColumn,
    TimeRemainingColumn,
    BarColumn,
    MofNCompleteColumn,
)

from gitaudit.utils.git import read_git_modules_text
from .change_log_entry import (
    ChangeLogEntry,
    SubmoduleInfo,
    IssueProviderCallable,
    UrlProviderCallable,
)


PROGRESS_COLUMNS = [
    MofNCompleteColumn(),
    BarColumn(bar_width=None),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
]

logger = logging.getLogger(__name__)


class GitError(Exception):
    """Generic git error for exceptions raised by the git class."""


def exec_sub_process(args: List[str], verbose: bool) -> str:
    """Executes Subprocess Popen call and stores the communication
    and stores communication of output and error

    Args:
        args (list[str]): arguments as list of strings
        verbose (bool): whether the output shall be
            printed to the console

    Raises:
        GitError: In case git returns an error output a GitError
            is raised with the message

    Returns:
        str: Git output as text decoded to utf-8 and stripped
            from leading and trailing whitespace
    """
    process = subprocess.Popen(
        args=args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, _ = process.communicate()

    output_text = output.decode(encoding="utf-8", errors="ignore").strip()

    if verbose:
        print(output_text)

    if process.returncode != 0:
        command_text = " ".join(args)
        raise GitError(f'Error executing git command: "{command_text}"')

    return output_text


def exec_sub_process_yield(args: List[str], verbose: bool) -> Iterator[str]:
    """Executes Subprocess Popen call and stores the communication
    and yields the output line by line

    Args:
        args (list[str]): arguments as list of strings
        verbose (bool): whether the output shall be
            printed to the console

    Raises:
        GitError: In case git returns an error output a GitError
            is raised with the message

    Yields:
        str: Git output as text yielded line by line and decoded to utf-8 and stripped
            from leading and trailing whitespace
    """
    process = subprocess.Popen(
        args=args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    p_stdout = process.stdout
    if p_stdout is not None:
        for line in io.TextIOWrapper(p_stdout, encoding="utf-8", errors="ignore"):
            if verbose:
                print(line)
            yield line

    return_code = process.wait()

    if return_code != 0:
        command_text = " ".join(args)
        raise GitError(f'Error executing git command: "{command_text}"')


class Git:
    """Class that communicated with local git installation."""

    def __init__(
        self,
        local: str,
        remote: Optional[str] = None,
        verbose: bool = False,
        commit_url_provider: Optional[UrlProviderCallable] = None,
        issues_provider: Optional[IssueProviderCallable] = None,
    ):
        self.remote = remote
        self.local = local
        self.verbose = verbose
        self.commit_url_provider = commit_url_provider
        self.issues_provider = issues_provider
        self.local_git = os.path.join(self.local, ".git")
        self._clone_if_required()

    def _clone_if_required(self):
        if os.path.isdir(self.local):
            return

        logger.info('Cloning "%s" into "%s"', self.remote, self.local)
        exec_sub_process(
            [
                "git",
                "clone",
                "-q",
                "-n",
                self.remote,
                self.local,
            ],
            self.verbose,
        )

    def _execute_git_cmd(self, *args: str):
        full_args = [
            "git",
            f"--git-dir={self.local_git}",
        ] + list(args)
        logger.debug(" ".join(full_args))
        return exec_sub_process(full_args, self.verbose)

    def _execute_git_cmd_yield(self, *args: str):
        full_args = [
            "git",
            f"--git-dir={self.local_git}",
        ] + list(args)
        logger.debug(" ".join(full_args))
        for line in exec_sub_process_yield(full_args, self.verbose):
            yield line

    def _execute_git_cmd_split_strip(self, *args):
        return list(
            map(lambda x: x.strip(), (self._execute_git_cmd(*args).split("\n")))
        )

    def fetch(self):
        """Fetch the repository. Will also fetch all tags
        and force override of local remote branches if they have
        been rebased on the remote.

        Returns:
            str: git output of the fetch command
        """
        logger.info('Fetching from "%s"', self.remote)
        return self._execute_git_cmd(
            "fetch", "--tags", "--force", "-q", "--no-recurse-submodules"
        )

    def gc(self, *options: str):  # pylint: disable=invalid-name
        """
        Cleanup unnecessary files and update the local repository

        Args:
            options (Tuple[str, ...]): Options to pass to git gc
        """
        logger.info('Executing gc for "%s"', self.local)
        self._execute_git_cmd("gc", *options)

    def pull(self):
        """Execute git pull"""
        logger.info('Pulling from "%s"', self.remote)
        self._execute_git_cmd("pull", "--no-recurse-submodules")

    def checkout(self, ref: str, create_branch: bool = False):
        """Git checkout ref

        Args:
            ref (str): Ref (Branch / Tag / Sha)
            create_branch (bool): Set true if branch shall be created.
                Defaults to False.
        """
        args = ["checkout", "--no-recurse-submodules"]

        if create_branch:
            args.append("-b")
            logger.info('Creating branch "%s"', ref)
        else:
            logger.info('Checking out "%s"', ref)

        self._execute_git_cmd(*args, ref)

    def push(self, ref_name: str, remote="origin"):
        """Execute Git Push

        Args:
            ref_name (str): Name of the branch
            remote (str, optional): Name of the remote. Defaults to "origin".
        """
        logger.info('Pushing "%s" to "%s"', ref_name, remote)
        self._execute_git_cmd("push", remote, f"{ref_name}:{ref_name}")

    def add(self, path: str):
        """Execute git add

        Args:
            path (str): the path to the file to the staged (relative).
                "." for all.
        """
        logger.info('Adding "%s"', path)
        self._execute_git_cmd("add", path)

    def commit_exists(self, sha: str) -> bool:
        """
        Check if a commit exists in the Git repository.

        This method uses the `git cat-file -e` command to check if a commit exists.
        If the commit exists, the command will return successfully, and the method
        will return True. If the command fails (which would be the case if the commit
        does not exist), an AssertionError is raised and the method returns False.

        Args:
            sha (str): The SHA-1 hash of the commit to check.

        Returns:
            bool: True if the commit exists, False otherwise.
        """
        try:
            self._execute_git_cmd("cat-file", "-e", f"{sha}^{{commit}}")
            return True
        except GitError:
            return False

    def commit(
        self, subject: str, body: Optional[str] = None, allow_empty: bool = False
    ):
        """Execute Git Commit

        Args:
            subject (str): Subject / Title / Headline of the commit
            body (str, optional): The body of the commit message. Defaults to None.
            allow_empty (bool): Set true if empty commits shall be allowed.
                Defaults to False.
        """
        args = []
        if allow_empty:
            args.append("--allow-empty")
        args.extend(["-m", subject])
        if body:
            args.extend(["-m", body])

        logger.info('Commit "%s"', subject)
        self._execute_git_cmd("commit", *args)

    def rev_parse(self, *args: str):
        """Execute rev parse. By default will execute "git rev-parse HEAD"

        Args:
            args (Tuple[str, ...]): Arguments to rev-parse command. Default HEAD

        Returns:
            str: Rev-parse output
        """
        if not args:
            args = ("HEAD",)

        return self._execute_git_cmd("rev-parse", *args)

    def remotes(self):
        """Returns remotes as list of strings

        Returns:
            List(str): Remotes of the repository
        """
        return self._execute_git_cmd_split_strip("remote")

    def local_ref_names(self):
        """Returns list of local branch names.

        Returns:
            List(str): List of locally checked out branches.
        """
        local_branches = self._execute_git_cmd_split_strip("branch")
        local_branches = list(map(lambda x: x.replace("* ", ""), local_branches))
        return local_branches

    def remote_ref_names(self):
        """Returns list of remote branches including remote name
        (e.g. <remote>/<ref_name>)

        Returns:
            List(str): List of branches across all remotes
        """
        remotes = self.remotes()
        remote_branches = self._execute_git_cmd_split_strip("branch", "-r")

        for remote in remotes:
            repl_text = f"{remote}/HEAD -> "
            remote_branches = [x.replace(repl_text, "") for x in remote_branches]

        return remote_branches

    def tags(self):
        """Returns list of tags

        Returns:
            List(str): List of tags checked out locally
        """
        arr = self._execute_git_cmd_split_strip("tag", "-l")
        arr = list(filter(lambda x: x, arr))
        return arr

    def commit_count(self, end_ref, start_ref=None, first_parent=False) -> int:
        """
        Calculates the commit count between two git references.

        Args:
            end_ref (str): The git reference to stop counting.
            start_ref (str, optional): The git reference from where to start counting.
                If not specified, count will start from the first commit. Defaults to None.
            first_parent (bool, optional): If True, the function only follows the
                first parent commit upon seeing a merge commit. Defaults to False.

        Returns:
            int: The number of commits between the start and end git references.
        """
        args = ["rev-list"]

        if start_ref:
            args.append(f"{start_ref}...{end_ref}")
        else:
            args.append(end_ref)

        args.append("--count")

        if first_parent:
            args.append("--first-parent")

        out_str = self._execute_git_cmd(*args)

        return int(out_str)

    def log(
        self,
        pretty,
        end_ref,
        start_ref=None,
        first_parent=False,
        submodule=None,
        patch=False,
        other=None,
    ):
        """Execute git log

        Args:
            pretty (str): Pretty format
            end_ref (str): git reference where to start going backwards
            start_ref (str, optional): git reference where stop going backwards.
                Defaults to None.
            first_parent (bool, optional): If true git log only follows the
                first parent. Defaults to False.
            submodule (str, optional): Option for submodule diff. Defaults to None.
            patch (bool, optional): Enable patch output or not. Defaults to False.
            other (List[str], optional): Additional git log commands. Defaults to None.

        Returns:
            str: Git log as text
        """
        return "".join(
            self._yield_line_log(
                pretty=pretty,
                end_ref=end_ref,
                start_ref=start_ref,
                first_parent=first_parent,
                submodule=submodule,
                patch=patch,
                other=other,
            )
        )

    def _yield_line_log(
        self,
        pretty,
        end_ref,
        start_ref=None,
        first_parent=False,
        submodule=None,
        patch=False,
        other=None,
    ):
        args = [
            "--no-pager",
            "log",
            f"--pretty={pretty}",
            "--first-parent" if first_parent else None,
            f"--submodule={submodule}" if submodule else None,
            "-p" if patch else None,
            f"{start_ref}...{end_ref}" if start_ref else end_ref,
        ] + (other if other else [])
        args = list(filter(lambda x: x is not None, args))

        for line in self._execute_git_cmd_yield(*args):
            yield line

    def show(
        self,
        pretty,
        ref,
        submodule=None,
        patch=False,
        other=None,
    ):
        """Shows information for a single commit / ref

        Args:
            pretty (str): Pretty Text for Logging
            ref (str): Ref (branch, tag, sha)
            submodule (str, optional): How subodule changes are shown.
                Defaults to None.
            patch (bool, optional): Whether to show patch info.
                Defaults to False.
            other (List[str], optional): Additional arguments.
                Defaults to None.

        Returns:
            str: git show information as text
        """
        args = [
            "show",
            f"--pretty={pretty}",
            f"--submodule={submodule}" if submodule else None,
            "-p" if patch else None,
            ref,
        ] + (other if other else [])
        args = list(filter(lambda x: x is not None, args))

        output = self._execute_git_cmd(*args)
        return output

    def get_last_sha_before(
        self, ref: str, date_time: datetime, first_parent: bool = False
    ) -> str:
        """Get last sha before a given date time

        Args:
            ref (str): Ref (branch, tag, sha)
            date_time (datetime): Date Time
            first_parent (bool): If true git log only follows the
                first parent. Defaults to False.

        Returns:
            str: sha of the last commit before the given date time
        """
        return self.log(
            pretty=r"%H",
            end_ref=ref,
            first_parent=first_parent,
            other=["--until", date_time.isoformat(), "-n", "1"],
        ).strip()

    def log_changelog(
        self,
        end_ref: str,
        start_ref: Optional[str] = None,
        first_parent: bool = False,
        patch: bool = False,
        instance_class: Type[ChangeLogEntry] = ChangeLogEntry,
    ):
        """Create changelog

        Args:
            end_ref (str): git reference where to start going backwards
            start_ref (str, optional): git reference where stop going backwards.
                Defaults to None.
            first_parent (bool): If true git log only follows the
                first parent. Defaults to False.
            patch (bool): Enable patch output or not. Defaults to False.
            instance_class (ChangeLogEntry): Type of the changelog entry class

        Returns:
            List[ChangeLogEntry]: the changelog
        """
        pretty = r"#CS#%nH:[%H]%nP:[%P]%nT:[%D]%nS:[%s]%nD:[%cI]%nU:[%aI]%nA:[%an]%nM:[%ae]%n#SB#%n%b%n#EB#%n"

        entries: List[ChangeLogEntry] = []
        collect_lines: List[str] = []

        other = ["--numstat"]

        other.append("--cc")

        commit_count = self.commit_count(end_ref, start_ref, first_parent)

        with Progress(*PROGRESS_COLUMNS) as progress:
            task = progress.add_task("[cyan]Processing...", total=commit_count)

            for line in self._yield_line_log(
                pretty=pretty,
                end_ref=end_ref,
                start_ref=start_ref,
                submodule="diff",
                other=other,
                patch=patch,
                first_parent=first_parent,
            ):
                if line == "#CS#\n":
                    if collect_lines:
                        entries.append(
                            instance_class.from_log_text(
                                log_text="".join(collect_lines),
                                url_provider=self.commit_url_provider,
                                issues_provider=self.issues_provider,
                                instance_class=instance_class,
                            )
                        )
                        progress.update(task, advance=1)

                    collect_lines = []
                else:
                    collect_lines.append(line)

            if collect_lines:
                entries.append(
                    instance_class.from_log_text(
                        log_text="".join(collect_lines),
                        url_provider=self.commit_url_provider,
                        issues_provider=self.issues_provider,
                        instance_class=instance_class,
                    )
                )
                progress.update(task, advance=1)

        return entries

    def show_changelog_entry(
        self,
        ref: str,
        patch: bool = False,
        instance_class: Type[ChangeLogEntry] = ChangeLogEntry,
    ):
        """Show single changelog entry

        Args:
            ref (str): Ref (branch, tag, sha)
            patch (bool): Whether to show patch information.
                Defaults to False.
            instance_class (Type[ChangeLogEntry]): Type of the changelog entry class

        Returns:
            ChangeLogEntry: change log entry
        """
        pretty = r"H:[%H]%nP:[%P]%nT:[%D]%nS:[%s]%nD:[%cI]%nU:[%aI]%nA:[%an]%nM:[%ae]%n#SB#%n%b%n#EB#%n"

        log_text = self.show(
            pretty=pretty,
            ref=ref,
            submodule="diff",
            other=["--numstat"],
            patch=patch,
        )

        return instance_class.from_log_text(
            log_text=log_text,
            url_provider=self.commit_url_provider,
            issues_provider=self.issues_provider,
            instance_class=instance_class,
        )

    def log_parentlog(
        self,
        end_ref,
        start_ref=None,
        first_parent=False,
        instance_class: Type[ChangeLogEntry] = ChangeLogEntry,
    ):
        """Given an end_ref this function
        will return ChangeLogEntry list (linear log)
        with sha and parent shas which can
        be used to construct a hierarchy log

        Args:
            end_ref (str): End Ref
            start_ref(str): Start Ref
            first_parent (bool, optional): If true git log only follows the first parent.
            instance_class (Type[ChangeLogEntry], optional): ChangeLogEntry class to use for parsing the
                log text into objects (e.g. ChangeLogEntry or ChangeLogEntryWithParent)

        Returns:
            List[ChangeLogEntry]: Linear ChangeLogEntry log
        """

        entries = []

        commit_count = self.commit_count(end_ref, start_ref)

        with Progress(*PROGRESS_COLUMNS) as progress:
            task = progress.add_task("[cyan]Processing...", total=commit_count)

            for line in self._yield_line_log(
                pretty=r"%H[%P](%cI)",
                end_ref=end_ref,
                start_ref=start_ref,
                first_parent=first_parent,
            ):
                entries.append(
                    instance_class.from_head_log_text(
                        line,
                        instance_class=instance_class,
                    )
                )
                progress.update(task, advance=1)

        return entries

    def show_parentlog_entry(
        self,
        ref: str,
        instance_class: Type[ChangeLogEntry] = ChangeLogEntry,
    ):
        """Show parent log entry information

        Args:
            ref (str): Ref (branch, tag, sha)
            instance_class (Type[ChangeLogEntry]): ChangeLogEntry class to use for parsing the
                log text into objects (e.g. ChangeLogEntry or ChangeLogEntryWithParent)

        Returns:
            ChangeLogEntry: change log entry with parent
                information
        """
        log_text = self.show(
            pretty=r"%H[%P](%cI)",
            ref=ref,
        )
        return instance_class.from_head_log_text(
            log_text,
            instance_class=instance_class,
        )

    def get_submodule_infos(self, ref: str) -> List[SubmoduleInfo]:
        """Returns list of submodules

        Args:
            ref (str): Ref (branch, tag, sha)

        Returns:
            List[SubmoduleInfo]: List of submodule infos
        """
        try:
            git_modules_content = self._execute_git_cmd("show", f"{ref}:.gitmodules")
        except GitError:
            return []
        git_modules_info_map = {
            module.path: module for module in read_git_modules_text(git_modules_content)
        }

        # this call has to be done without the --work-tree option that is automatically added
        submodule_state_content = self._execute_git_cmd(
            "submodule", "summary", "--cached", ref
        )

        submodule_infos = []

        text: str  # mypy requires type annotation (for loops need this before the loop)
        for text in filter(None, submodule_state_content.split("\n")):
            findings = re.findall(r"^\*\s(.*)\s([a-f0-9]+)\.{3}[a-f0-9]+:$", text)
            assert len(findings) == 1

            path, sha = findings[0]

            submodule_infos.append(
                SubmoduleInfo(
                    path=path,
                    sha=sha,
                    name=git_modules_info_map[path].name,
                    url=git_modules_info_map[path].url,
                )
            )

        return submodule_infos
