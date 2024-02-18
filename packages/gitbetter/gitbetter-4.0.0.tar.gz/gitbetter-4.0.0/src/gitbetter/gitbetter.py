import os
from datetime import datetime

from argshell import ArgShell, Namespace, with_parser
from noiftimer import Timer
from pathier import Pathier

from gitbetter import Git, GitHub, parsers


class GitArgShell(ArgShell):
    git_header = "Built in Git commands (type '{command} -h' or '{command} --help'):"
    convenience_header = "Convenience commands (type 'help {command}'):"

    def do_help(self, arg):
        """List available commands with "help" or detailed help with "help cmd".
        If using 'help cmd' and the cmd is decorated with a parser, the parser help will also be printed.
        """
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, "help_" + arg)
            except AttributeError:
                try:
                    func = getattr(self, "do_" + arg)
                    doc = func.__doc__
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                    # =========================Modification start=========================
                    # Check for decorator and call decorated function with "--help"
                    if hasattr(func, "__wrapped__"):
                        self.stdout.write(
                            f"Parser help for {func.__name__.replace('do_','')}:\n"
                        )
                        func("--help")
                    if doc or hasattr(func, "__wrapped__"):
                        return
                    # |=========================Modification stop=========================|
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            topics = set()
            for name in names:
                if name[:5] == "help_":
                    topics.add(name[5:])
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ""
            for name in names:
                if name[:3] == "do_":
                    if name == prevname:
                        continue
                    prevname = name
                    cmd = name[3:]
                    if cmd in topics:
                        cmds_doc.append(cmd)
                        topics.remove(cmd)
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            # |========================Modification Start========================|
            content = Pathier(__file__).read_text()
            convenience_index = content.rfind("=Convenience=")
            git_commands = []
            convenience_commands = []
            for cmd in cmds_doc:
                if content.find(f"do_{cmd}") < convenience_index:
                    git_commands.append(cmd)
                else:
                    convenience_commands.append(cmd)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.git_header, git_commands, 15, 80)
            self.print_topics(self.convenience_header, convenience_commands, 15, 80)
            # |========================Modification Stop========================|
            self.print_topics(self.misc_header, sorted(topics), 15, 80)
            self.print_topics(self.undoc_header, cmds_undoc, 15, 80)


class GitBetter(GitArgShell):
    """GitBetter Shell."""

    execute_in_terminal_if_unrecognized = True
    git = Git()
    intro = "Starting gitbetter...\nEnter 'help' or '?' for command help."
    prompt = f"gitbetter::{Pathier.cwd()}>"

    @property
    def unrecognized_command_behavior_status(self):
        return f"Unrecognized command behavior: {('Execute in shell with os.system()' if self.execute_in_terminal_if_unrecognized else 'Print unknown syntax error')}"

    def default(self, line: str):
        if self.execute_in_terminal_if_unrecognized:
            os.system(line)
        else:
            super().default(line)

    def do_cd(self, path: str):
        """Change current working directory to `path`."""
        os.chdir(path)
        self.prompt = f"gitbetter::{Pathier.cwd()}>"

    def do_help(self, arg: str):
        """List available commands with "help" or detailed help with "help cmd"."""
        super().do_help(arg)
        if not arg:
            print(self.unrecognized_command_behavior_status)
            if self.execute_in_terminal_if_unrecognized:
                print(
                    "^Essentially makes this shell function as a super-shell of whatever shell you launched gitbetter from.^"
                )
        print()

    def do_toggle_unrecognized_command_behavior(self, arg: str):
        """Toggle whether the shell will attempt to execute unrecognized commands as system commands in the terminal.
        When on (the default), `GitBetter` will treat unrecognized commands as if you added the `sys` command in front of the input, i.e. `os.system(your_input)`.
        When off, an `unknown syntax` message will be printed and no commands will be executed.
        """
        self.execute_in_terminal_if_unrecognized = (
            not self.execute_in_terminal_if_unrecognized
        )
        print(self.unrecognized_command_behavior_status)

    # Seat |================================================Core================================================|

    def do_git(self, args: str):
        """Directly execute `git {args}`.

        i.e. You can still do everything directly invoking git can do."""
        self.git.run(args)

    # Seat

    def do_add(self, args: str):
        """>>> git add {args}"""
        self.git.add(args)

    def do_am(self, args: str):
        """>>> git am {args}"""
        self.git.am(args)

    def do_annotate(self, args: str):
        """>>> git annotate {args}"""
        self.git.annotate(args)

    def do_archive(self, args: str):
        """>>> git archive {args}"""
        self.git.archive(args)

    def do_bisect(self, args: str):
        """>>> git bisect {args}"""
        self.git.bisect(args)

    def do_blame(self, args: str):
        """>>> git blame {args}"""
        self.git.blame(args)

    def do_branch(self, args: str):
        """>>> git branch {args}"""
        self.git.branch(args)

    def do_bugreport(self, args: str):
        """>>> git bugreport {args}"""
        self.git.bugreport(args)

    def do_bundle(self, args: str):
        """>>> git bundle {args}"""
        self.git.bundle(args)

    def do_checkout(self, args: str):
        """>>> git checkout {args}"""
        self.git.checkout(args)

    def do_cherry_pick(self, args: str):
        """>>> git cherry_pick {args}"""
        self.git.cherry_pick(args)

    def do_citool(self, args: str):
        """>>> git citool {args}"""
        self.git.citool(args)

    def do_clean(self, args: str):
        """>>> git clean {args}"""
        self.git.clean(args)

    def do_clone(self, args: str):
        """>>> git clone {args}"""
        self.git.clone(args)

    def do_commit(self, args: str):
        """>>> git commit {args}"""
        self.git.commit(args)

    def do_config(self, args: str):
        """>>> git config {args}"""
        self.git.config(args)

    def do_count_objects(self, args: str):
        """>>> git count_objects {args}"""
        self.git.count_objects(args)

    def do_describe(self, args: str):
        """>>> git describe {args}"""
        self.git.describe(args)

    def do_diagnose(self, args: str):
        """>>> git diagnose {args}"""
        self.git.diagnose(args)

    def do_diff(self, args: str):
        """>>> git diff {args}"""
        self.git.diff(args)

    def do_difftool(self, args: str):
        """>>> git difftool {args}"""
        self.git.difftool(args)

    def do_fast_export(self, args: str):
        """>>> git fast_export {args}"""
        self.git.fast_export(args)

    def do_fast_import(self, args: str):
        """>>> git fast_import {args}"""
        self.git.fast_import(args)

    def do_fetch(self, args: str):
        """>>> git fetch {args}"""
        self.git.fetch(args)

    def do_filter_branch(self, args: str):
        """>>> git filter_branch {args}"""
        self.git.filter_branch(args)

    def do_format_patch(self, args: str):
        """>>> git format_patch {args}"""
        self.git.format_patch(args)

    def do_fsck(self, args: str):
        """>>> git fsck {args}"""
        self.git.fsck(args)

    def do_gc(self, args: str):
        """>>> git gc {args}"""
        self.git.gc(args)

    def do_gitk(self, args: str):
        """>>> git gitk {args}"""
        self.git.gitk(args)

    def do_gitweb(self, args: str):
        """>>> git gitweb {args}"""
        self.git.gitweb(args)

    def do_grep(self, args: str):
        """>>> git grep {args}"""
        self.git.grep(args)

    def do_gui(self, args: str):
        """>>> git gui {args}"""
        self.git.gui(args)

    def do_init(self, args: str):
        """>>> git init {args}"""
        self.git.init(args)

    def do_instaweb(self, args: str):
        """>>> git instaweb {args}"""
        self.git.instaweb(args)

    def do_log(self, args: str):
        """>>> git log {args}"""
        self.git.log(args)

    def do_maintenance(self, args: str):
        """>>> git maintenance {args}"""
        self.git.maintenance(args)

    def do_merge(self, args: str):
        """>>> git merge {args}"""
        self.git.merge(args)

    def do_merge_tree(self, args: str):
        """>>> git merge_tree {args}"""
        self.git.merge_tree(args)

    def do_mergetool(self, args: str):
        """>>> git mergetool {args}"""
        self.git.mergetool(args)

    def do_mv(self, args: str):
        """>>> git mv {args}"""
        self.git.mv(args)

    def do_notes(self, args: str):
        """>>> git notes {args}"""
        self.git.notes(args)

    def do_pack_refs(self, args: str):
        """>>> git pack_refs {args}"""
        self.git.pack_refs(args)

    def do_prune(self, args: str):
        """>>> git prune {args}"""
        self.git.prune(args)

    def do_pull(self, args: str):
        """>>> git pull {args}"""
        self.git.pull(args)

    def do_push(self, args: str):
        """>>> git push {args}"""
        self.git.push(args)

    def do_range_diff(self, args: str):
        """>>> git range_diff {args}"""
        self.git.range_diff(args)

    def do_rebase(self, args: str):
        """>>> git rebase {args}"""
        self.git.rebase(args)

    def do_reflog(self, args: str):
        """>>> git reflog {args}"""
        self.git.reflog(args)

    def do_remote(self, args: str):
        """>>> git remote {args}"""
        self.git.remote(args)

    def do_repack(self, args: str):
        """>>> git repack {args}"""
        self.git.repack(args)

    def do_replace(self, args: str):
        """>>> git replace {args}"""
        self.git.replace(args)

    def do_request_pull(self, args: str):
        """>>> git request_pull {args}"""
        self.git.request_pull(args)

    def do_rerere(self, args: str):
        """>>> git rerere {args}"""
        self.git.rerere(args)

    def do_reset(self, args: str):
        """>>> git reset {args}"""
        self.git.reset(args)

    def do_restore(self, args: str):
        """>>> git restore {args}"""
        self.git.restore(args)

    def do_revert(self, args: str):
        """>>> git revert {args}"""
        self.git.revert(args)

    def do_rm(self, args: str):
        """>>> git rm {args}"""
        self.git.rm(args)

    def do_scalar(self, args: str):
        """>>> git scalar {args}"""
        self.git.scalar(args)

    def do_shortlog(self, args: str):
        """>>> git shortlog {args}"""
        self.git.shortlog(args)

    def do_show(self, args: str):
        """>>> git show {args}"""
        self.git.show(args)

    def do_show_branch(self, args: str):
        """>>> git show_branch {args}"""
        self.git.show_branch(args)

    def do_sparse_checkout(self, args: str):
        """>>> git sparse_checkout {args}"""
        self.git.sparse_checkout(args)

    def do_stash(self, args: str):
        """>>> git stash {args}"""
        self.git.stash(args)

    def do_status(self, args: str):
        """>>> git status {args}"""
        self.git.status(args)

    def do_submodule(self, args: str):
        """>>> git submodule {args}"""
        self.git.submodule(args)

    def do_switch(self, args: str):
        """>>> git switch {args}"""
        self.git.switch(args)

    def do_tag(self, args: str):
        """>>> git tag {args}"""
        self.git.tag(args)

    def do_verify_commit(self, args: str):
        """>>> git verify_commit {args}"""
        self.git.verify_commit(args)

    def do_verify_tag(self, args: str):
        """>>> git verify_tag {args}"""
        self.git.verify_tag(args)

    def do_version(self, args: str):
        """>>> git version {args}"""
        self.git.version(args)

    def do_whatchanged(self, args: str):
        """>>> git whatchanged {args}"""
        self.git.whatchanged(args)

    def do_worktree(self, args: str):
        """>>> git worktree {args}"""
        self.git.worktree(args)

    # Seat |==================================Convenience==================================|

    def do_add_url(self, url: str):
        """Add remote origin url for repo and push repo.
        >>> git remote add origin {url}
        >>> git push -u origin main"""
        self.git.add_remote_url(url)
        self.git.push("-u origin main")

    @with_parser(parsers.add_files_parser)
    def do_amend(self, args: Namespace):
        """Stage files and add to previous commit."""
        self.git.amend(args.files)

    def do_branches(self, _: str):
        """Show local and remote branches.
        >>> git branch -vva"""
        self.git.list_branches()

    def do_commitall(self, message: str):
        """Stage and commit all modified and untracked files with this message.
        >>> git add .
        >>> git commit -m \"{message}\" """
        message = message.strip('"').replace('"', "'")
        self.git.add_all()
        self.git.commit(f'-m "{message}"')

    @with_parser(parsers.delete_branch_parser)
    def do_delete_branch(self, args: Namespace):
        """Delete branch."""
        self.git.delete_branch(args.branch, not args.remote)

    def do_delete_gh_repo(self, _: str):
        """Delete this repo from GitHub.

        GitHub CLI must be installed and configured.

        May require you to reauthorize and rerun command."""
        GitHub().delete_remote()

    def do_dob(self, _: str):
        """Date of this repo's first commit."""
        dob = self.git.dob
        elapsed = Timer.format_time((datetime.now() - dob).total_seconds())
        print(f"{dob:%m/%d/%Y}|{elapsed} ago")

    def do_ignore(self, patterns: str):
        """Add the list of patterns/file names to `.gitignore` and commit with the message `chore: add to gitignore`."""
        self.git.ignore(patterns.split())
        self.git.commit_files([".gitignore"], "chore: add to gitignore")

    @with_parser(parsers.add_files_parser)
    def do_initcommit(self, args: Namespace):
        """Stage and commit all files with message "Initial Commit"."""
        self.git.initcommit(args.files)

    def do_loggy(self, _: str):
        """>>> git --oneline --name-only --abbrev-commit --graph"""
        self.git.loggy()

    def do_make_private(self, _: str):
        """Make the GitHub remote for this repo private.

        This repo must exist and GitHub CLI must be installed and configured."""
        GitHub().make_private()

    def do_make_public(self, _: str):
        """Make the GitHub remote for this repo public.

        This repo must exist and GitHub CLI must be installed and configured."""
        GitHub().make_public()

    def do_merge_to(self, branch: str):
        """Merge the current branch into the provided branch after switching to the provided branch.

        If no branch name is given, "main" will be used."""
        self.git.merge_to(branch or "main")

    def do_new_branch(self, name: str):
        """Create and switch to a new branch with this `name`."""
        self.git.create_new_branch(name)

    @with_parser(parsers.new_remote_parser)
    def do_new_gh_remote(self, args: Namespace):
        """Create a remote GitHub repository for this repo.

        GitHub CLI must be installed and configured for this to work."""
        GitHub().create_remote_from_cwd(args.public)

    def do_new_repo(self, _: str):
        """Create a new git repo in this directory."""
        self.git.new_repo()

    def do_push_new(self, _: str):
        """Push current branch to origin with `-u` flag.
        >>> git push -u origin {this_branch}"""
        self.git.push_new_branch(self.git.current_branch)

    def do_undo(self, _: str):
        """Undo all uncommitted changes.
        >>> git checkout ."""
        self.git.undo()

    @with_parser(parsers.add_files_parser)
    def do_untrack(self, args: Namespace):
        """Untrack files matching provided path/pattern list.

        For each path/pattern, equivalent to:
        >>> git rm --cached {path}"""
        self.git.untrack(*args.files)

    @with_parser(parsers.rename_file_parser)
    def do_rename_file(self, args: Namespace):
        """Renames a file.
        After renaming the file, the renaming change is staged for commit."""
        self.git.rename_file(args.file, args.new_name)


def main():
    GitBetter().cmdloop()


if __name__ == "__main__":
    main()
