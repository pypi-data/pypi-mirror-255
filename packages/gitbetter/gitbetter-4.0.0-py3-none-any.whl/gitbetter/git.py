from datetime import datetime
from urllib.parse import urlparse

from morbin import Morbin, Output
from pathier import Pathier, Pathish


class Git(Morbin):
    # Seat |===================================================Core===================================================|
    @property
    def program(self) -> str:
        return "git"

    # def git(self, command: str) -> Output:
    #    """Base function for executing git commands.
    #    Use this if another function doesn't meet your needs.
    #    >>> git {command}"""
    #    return self.run(command)

    # Seat

    def add(self, args: str = "") -> Output:
        """>>> git add {args}"""
        return self.run(f"add {args}")

    def am(self, args: str = "") -> Output:
        """>>> git am {args}"""
        return self.run(f"am {args}")

    def annotate(self, args: str = "") -> Output:
        """>>> git annotate {args}"""
        return self.run(f"annotate {args}")

    def archive(self, args: str = "") -> Output:
        """>>> git archive {args}"""
        return self.run(f"archive {args}")

    def bisect(self, args: str = "") -> Output:
        """>>> git bisect {args}"""
        return self.run(f"bisect {args}")

    def blame(self, args: str = "") -> Output:
        """>>> git blame {args}"""
        return self.run(f"blame {args}")

    def branch(self, args: str = "") -> Output:
        """>>> git branch {args}"""
        return self.run(f"branch {args}")

    def bugreport(self, args: str = "") -> Output:
        """>>> git bugreport {args}"""
        return self.run(f"bugreport {args}")

    def bundle(self, args: str = "") -> Output:
        """>>> git bundle {args}"""
        return self.run(f"bundle {args}")

    def checkout(self, args: str = "") -> Output:
        """>>> git checkout {args}"""
        return self.run(f"checkout {args}")

    def cherry_pick(self, args: str = "") -> Output:
        """>>> git cherry-pick {args}"""
        return self.run(f"cherry-pick {args}")

    def citool(self, args: str = "") -> Output:
        """>>> git citool {args}"""
        return self.run(f"citool {args}")

    def clean(self, args: str = "") -> Output:
        """>>> git clean {args}"""
        return self.run(f"clean {args}")

    def clone(self, args: str = "") -> Output:
        """>>> git clone {args}"""
        return self.run(f"clone {args}")

    def commit(self, args: str = "") -> Output:
        """>>> git commit {args}"""
        return self.run(f"commit {args}")

    def config(self, args: str = "") -> Output:
        """>>> git config {args}"""
        return self.run(f"config {args}")

    def count_objects(self, args: str = "") -> Output:
        """>>> git count-objects {args}"""
        return self.run(f"count-objects {args}")

    def describe(self, args: str = "") -> Output:
        """>>> git describe {args}"""
        return self.run(f"describe {args}")

    def diagnose(self, args: str = "") -> Output:
        """>>> git diagnose {args}"""
        return self.run(f"diagnose {args}")

    def diff(self, args: str = "") -> Output:
        """>>> git diff {args}"""
        return self.run(f"diff {args}")

    def difftool(self, args: str = "") -> Output:
        """>>> git difftool {args}"""
        return self.run(f"difftool {args}")

    def fast_export(self, args: str = "") -> Output:
        """>>> git fast-export {args}"""
        return self.run(f"fast-export {args}")

    def fast_import(self, args: str = "") -> Output:
        """>>> git fast-import {args}"""
        return self.run(f"fast-import {args}")

    def fetch(self, args: str = "") -> Output:
        """>>> git fetch {args}"""
        return self.run(f"fetch {args}")

    def filter_branch(self, args: str = "") -> Output:
        """>>> git filter-branch {args}"""
        return self.run(f"filter-branch {args}")

    def format_patch(self, args: str = "") -> Output:
        """>>> git format-patch {args}"""
        return self.run(f"format-patch {args}")

    def fsck(self, args: str = "") -> Output:
        """>>> git fsck {args}"""
        return self.run(f"fsck {args}")

    def gc(self, args: str = "") -> Output:
        """>>> git gc {args}"""
        return self.run(f"gc {args}")

    def gitk(self, args: str = "") -> Output:
        """>>> git gitk {args}"""
        return self.run(f"gitk {args}")

    def gitweb(self, args: str = "") -> Output:
        """>>> git gitweb {args}"""
        return self.run(f"gitweb {args}")

    def grep(self, args: str = "") -> Output:
        """>>> git grep {args}"""
        return self.run(f"grep {args}")

    def gui(self, args: str = "") -> Output:
        """>>> git gui {args}"""
        return self.run(f"gui {args}")

    def help(self, args: str = "") -> Output:
        """>>> git help {args}"""
        return self.run(f"help {args}")

    def init(self, args: str = "") -> Output:
        """>>> git init {args}"""
        return self.run(f"init {args}")

    def instaweb(self, args: str = "") -> Output:
        """>>> git instaweb {args}"""
        return self.run(f"instaweb {args}")

    def log(self, args: str = "") -> Output:
        """>>> git log {args}"""
        return self.run(f"log {args}")

    def maintenance(self, args: str = "") -> Output:
        """>>> git maintenance {args}"""
        return self.run(f"maintenance {args}")

    def merge(self, args: str = "") -> Output:
        """>>> git merge {args}"""
        return self.run(f"merge {args}")

    def merge_tree(self, args: str = "") -> Output:
        """>>> git merge-tree {args}"""
        return self.run(f"merge-tree {args}")

    def mergetool(self, args: str = "") -> Output:
        """>>> git mergetool {args}"""
        return self.run(f"mergetool {args}")

    def mv(self, args: str = "") -> Output:
        """>>> git mv {args}"""
        return self.run(f"mv {args}")

    def notes(self, args: str = "") -> Output:
        """>>> git notes {args}"""
        return self.run(f"notes {args}")

    def pack_refs(self, args: str = "") -> Output:
        """>>> git pack-refs {args}"""
        return self.run(f"pack-refs {args}")

    def prune(self, args: str = "") -> Output:
        """>>> git prune {args}"""
        return self.run(f"prune {args}")

    def pull(self, args: str = "") -> Output:
        """>>> git pull {args}"""
        return self.run(f"pull {args}")

    def push(self, args: str = "") -> Output:
        """>>> git push {args}"""
        return self.run(f"push {args}")

    def range_diff(self, args: str = "") -> Output:
        """>>> git range-diff {args}"""
        return self.run(f"range-diff {args}")

    def rebase(self, args: str = "") -> Output:
        """>>> git rebase {args}"""
        return self.run(f"rebase {args}")

    def reflog(self, args: str = "") -> Output:
        """>>> git reflog {args}"""
        return self.run(f"reflog {args}")

    def remote(self, args: str = "") -> Output:
        """>>> git remote {args}"""
        return self.run(f"remote {args}")

    def repack(self, args: str = "") -> Output:
        """>>> git repack {args}"""
        return self.run(f"repack {args}")

    def replace(self, args: str = "") -> Output:
        """>>> git replace {args}"""
        return self.run(f"replace {args}")

    def request_pull(self, args: str = "") -> Output:
        """>>> git request-pull {args}"""
        return self.run(f"request-pull {args}")

    def rerere(self, args: str = "") -> Output:
        """>>> git rerere {args}"""
        return self.run(f"rerere {args}")

    def reset(self, args: str = "") -> Output:
        """>>> git reset {args}"""
        return self.run(f"reset {args}")

    def restore(self, args: str = "") -> Output:
        """>>> git restore {args}"""
        return self.run(f"restore {args}")

    def revert(self, args: str = "") -> Output:
        """>>> git revert {args}"""
        return self.run(f"revert {args}")

    def rm(self, args: str = "") -> Output:
        """>>> git rm {args}"""
        return self.run(f"rm {args}")

    def scalar(self, args: str = "") -> Output:
        """>>> git scalar {args}"""
        return self.run(f"scalar {args}")

    def shortlog(self, args: str = "") -> Output:
        """>>> git shortlog {args}"""
        return self.run(f"shortlog {args}")

    def show(self, args: str = "") -> Output:
        """>>> git show {args}"""
        return self.run(f"show {args}")

    def show_branch(self, args: str = "") -> Output:
        """>>> git show-branch {args}"""
        return self.run(f"show-branch {args}")

    def sparse_checkout(self, args: str = "") -> Output:
        """>>> git sparse-checkout {args}"""
        return self.run(f"sparse-checkout {args}")

    def stash(self, args: str = "") -> Output:
        """>>> git stash {args}"""
        return self.run(f"stash {args}")

    def status(self, args: str = "") -> Output:
        """>>> git status {args}"""
        return self.run(f"status {args}")

    def submodule(self, args: str = "") -> Output:
        """>>> git submodule {args}"""
        return self.run(f"submodule {args}")

    def switch(self, args: str = "") -> Output:
        """>>> git switch {args}"""
        return self.run(f"switch {args}")

    def tag(self, args: str = "") -> Output:
        """>>> git tag {args}"""
        return self.run(f"tag {args}")

    def verify_commit(self, args: str = "") -> Output:
        """>>> git verify-commit {args}"""
        return self.run(f"verify-commit {args}")

    def verify_tag(self, args: str = "") -> Output:
        """>>> git verify-tag {args}"""
        return self.run(f"verify-tag {args}")

    def version(self, args: str = "") -> Output:
        """>>> git version {args}"""
        return self.run(f"version {args}")

    def whatchanged(self, args: str = "") -> Output:
        """>>> git whatchanged {args}"""
        return self.run(f"whatchanged {args}")

    def worktree(self, args: str = "") -> Output:
        """>>> git worktree {args}"""
        return self.run(f"worktree {args}")

    # Seat |=================================================Convenience=================================================|

    @property
    def current_branch(self) -> str:
        """Returns the name of the currently active branch."""
        current_branch = ""
        with self.capturing_output():
            branches = self.branch().stdout.splitlines()
            for branch in branches:
                if branch.startswith("*"):
                    current_branch = branch[2:]
                    break
        return current_branch

    @property
    def dob(self) -> datetime:
        """Date of this repo's first commit."""
        with self.capturing_output():
            output = self.log("--pretty=format:'%cs'")
            return datetime.strptime(output.stdout.splitlines()[-1], "%Y-%m-%d")

    @property
    def origin_url(self) -> Output:
        """The remote origin url for this repo
        >>> git remote get-url origin"""
        return self.remote("get-url origin")

    def add_all(self) -> Output:
        """Stage all modified and untracked files.
        >>> git add ."""
        return self.add(".")

    def add_files(self, files: list[Pathish]) -> Output:
        """Stage a list of files."""
        args = " ".join([str(file) for file in files])
        return self.add(args)

    def add_remote_url(self, url: str, name: str = "origin") -> Output:
        """Add remote url to repo.
        >>> git remote add {name} {url}"""
        return self.remote(f"add {name} {url}")

    def amend(self, files: list[Pathish] | None = None) -> Output:
        """Stage and commit changes to the previous commit.

        If `files` is `None`, all files will be staged.

        >>> git add {files} or git add .
        >>> git commit --amend --no-edit
        """
        return (self.add_files(files) if files else self.add_all()) + self.commit(
            "--amend --no-edit"
        )

    def commit_all(self, message: str) -> Output:
        """Stage and commit all files with `message`.
        >>> git add .
        >>> git commit -m "{message}" """
        return self.add_all() + self.commit(f'-m "{message}"')

    def commit_files(self, files: list[Pathish], message: str) -> Output:
        """Commit a list of files or file patterns with commit message `message`.
        >>> git commit {files} -m "{message}" """
        files_arg = " ".join(str(file) for file in files)
        return self.commit(f'{files_arg} -m "{message}"')

    def create_new_branch(self, branch_name: str) -> Output:
        """Create and switch to a new branch named with `branch_name`.
        >>> git checkout -b {branch_name} --track"""
        return self.checkout(f"-b {branch_name} --track")

    def delete_branch(self, branch_name: str, local_only: bool = True) -> Output:
        """Delete `branch_name` from repo.

        #### :params:

        `local_only`: Only delete the local copy of `branch`, otherwise also delete the remote branch on origin and remote-tracking branch.
        >>> git branch --delete {branch_name}

        Then if not `local_only`:
        >>> git push origin --delete {branch_name}
        """
        output = self.branch(f"--delete {branch_name}")
        if not local_only:
            return output + self.push(f"origin --delete {branch_name}")
        return output

    def ignore(self, patterns: list[str]):
        """Add `patterns` to `.gitignore`."""
        gitignore = Pathier(".gitignore")
        if not gitignore.exists():
            gitignore.touch()
        ignores = gitignore.split()
        ignores += [pattern for pattern in patterns if pattern not in ignores]
        gitignore.join(ignores)

    def initcommit(self, files: list[Pathish] | None = None) -> Output:
        """Stage and commit `files` with the message `Initial commit`.

        If `files` is not given, all files will be added and committed.
        >>> git add {files} or git add .
        >>> git commit -m "Initial commit" """
        return (self.add_files(files) if files else self.add_all()) + self.commit(
            '-m "Initial commit"'
        )

    def list_branches(self) -> Output:
        """>>> git branch -vva"""
        return self.branch("-vva")

    def loggy(self) -> Output:
        """>>> git log --graph --abbrev-commit --name-only --pretty=tformat:'%C(auto)%h %C(green)(%cs|%cr)%C(auto)%d %C(magenta)%s'"""
        return self.log(
            "--graph --abbrev-commit --name-only --pretty=tformat:'%C(auto)%h %C(green)(%cs|%cr)%C(auto)%d %C(magenta)%s'"
        )

    def merge_to(self, branch: str = "main") -> Output:
        """Merge the current branch with `branch` after switching to `branch`.

        i.e. If on branch `my-feature`,
        >>> git.merge_to()

        will switch to `main` and merge `my-feature` into `main`."""
        current_branch = self.current_branch
        output = self.switch(branch)
        output += self.merge(current_branch)
        return output

    def new_repo(self) -> Output:
        """Initialize a new repo in current directory.
        >>> git init -b main"""
        return self.init("-b main")

    def push_new_branch(self, branch: str) -> Output:
        """Push a new branch to origin with tracking.
        >>> git push -u origin {branch}"""
        return self.push(f"-u origin {branch}")

    def switch_branch(self, branch_name: str) -> Output:
        """Switch to the branch specified by `branch_name`.
        >>> git checkout {branch_name}"""
        return self.checkout(branch_name)

    def undo(self) -> Output:
        """Undo uncommitted changes.
        >>> git checkout ."""
        return self.checkout(".")

    def untrack(self, *paths: Pathish) -> Output:
        """Remove any number of `paths` from the index.

        Equivalent to
        >>> git rm --cached {path}

        for each path in `paths`."""
        paths_ = [str(path) for path in paths]
        return sum(
            [self.rm(f"--cached {path}") for path in paths_[1:]],
            self.rm(f"--cached {paths_[0]}"),
        )

    def rename_file(self, file: Pathish, new_name: str) -> Output:
        """Rename `file` to `new_name` and add renaming to staging index.

        `new_name` should include the file suffix.

        Equivalent to renaming `old_file.py` to `new_file.py` then executing
        >>> git add new_file.py
        >>> git rm old_file.py"""
        file = Pathier(file)
        new_file = file.replace(file.with_name(new_name))
        return self.add_files([new_file]) + self.rm(str(file))


# |===============================Requires GitHub CLI to be installed and configured===============================|
class GitHub(Morbin):
    @property
    def program(self) -> str:
        return "gh"

    @property
    def owner(self) -> str:
        return self._owner_reponame().split("/")[0]

    @property
    def repo_name(self) -> str:
        return self._owner_reponame().split("/")[1]

    def _change_visibility(self, visibility: str) -> Output:
        return self.run(
            f"repo edit {self.owner}/{self.repo_name} --visibility {visibility}"
        )

    def _owner_reponame(self) -> str:
        """Returns "owner/repo-name", assuming there's one remote origin url and it's for github."""
        git = Git()
        with git.capturing_output():
            return urlparse(git.origin_url.stdout.strip("\n")).path.strip("/")

    def create_remote(self, name: str, public: bool = False) -> Output:
        """Uses GitHub CLI (must be installed and configured) to create a remote GitHub repo.

        #### :params:

        `name`: The name for the repo.

        `public`: Set to `True` to create the repo as public, otherwise it'll be created as private.
        """
        visibility = "--public" if public else "--private"
        return self.run(f"repo create {name} {visibility}")

    def create_remote_from_cwd(self, public: bool = False) -> Output:
        """Use GitHub CLI (must be installed and configured) to create a remote GitHub repo from
        the current working directory repo and add its url as this repo's remote origin.

        #### :params:

        `public`: Create the GitHub repo as a public repo, default is to create it as private.
        """
        visibility = "--public" if public else "--private"
        return self.run(f"repo create --source . {visibility} --push")

    def delete_remote(self) -> Output:
        """Uses GitHub CLI (must be isntalled and configured) to delete the remote for this repo."""
        return self.run(f"repo delete {self.owner}/{self.repo_name} --yes")

    def make_private(self) -> Output:
        """Uses GitHub CLI (must be installed and configured) to set the repo's visibility to private."""
        return self._change_visibility("private")

    def make_public(self) -> Output:
        """Uses GitHub CLI (must be installed and configured) to set the repo's visibility to public."""
        return self._change_visibility("public")
