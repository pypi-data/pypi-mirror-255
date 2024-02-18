# Changelog

## v3.5.0 (2024-01-14)

#### New Features

* add `merge_to()` method
#### Others

* remove pytest from dependencies


## v3.4.0 (2024-01-05)

#### New Features

* add dob functionality
#### Refactorings

* loggy() includes commit date


## v3.3.0 (2023-10-29)

#### Refactorings

* commit files directly in commit_files so that other files added to the index aren't committed with them
#### Others

* add __version__


## v3.2.1 (2023-09-12)

#### Fixes

* add missing parameter to shell commands

## v3.2.0 (2023-09-11)

#### New Features

* add renaming function

## v3.1.0 (2023-08-22)

#### New Features

* add untrack method to gitbetter shell
## v3.0.0 (2023-08-19)

#### New Features

* add untrack() method
#### Refactorings

* BREAKING: Git class inherits from [`morbin.Morbin`](https://github.com/matt-manes/morbin) and all member functions previously having return type `str | int` now return a `morbin.Output` object

## v2.1.1 (2023-07-01)

#### Refactorings

* remove redundant shell command and parser
#### Others

* cleanup test directory


## v2.1.0 (2023-06-20)

#### Performance improvements

* do_ignore will commit the gitignore file after adding patterns
#### Refactorings

* sort class contents and remove unused import

## v2.0.1 (2023-06-18)

#### Fixes

* fix amend() calling wrong add function

## v2.0.0 (2023-06-13)

#### New Features

* help command shows built in git commands and convenience commands separately
* add commit_all()
* add ignore() to Git
* do_initcommit can take a list of files instead of only operating on all files
* add all core git commands to gitbetter shell
* initcommit() can accept a list of files
* add owner and repo name properties
* add all porcelain git commands
#### Fixes

* fix faulty import statement
* replace backslashes with forward slashes in add_files if there are any
#### Refactorings

* do_push_new() will use current_branch property instead of needing branch name supplied
* remove recursive options from shell parsers in favor of native wildcard usage
* remove quote check from do_commitall
* make origin_url a property
* move shell parsers to separate file
* change some convenience functions to use newly added core functions
* change execute method name to git
* update to revised Git functions
* remove owner and name params from github cli functions
#### Docs

* update readme
* update and improve docstrings
#### Others

* remove unused imports
* remove unused arg from do_delete_gh_repo
* add to ignore
* update ignores


## v1.4.0 (2023-06-01)

#### Refactorings

* no longer necessary to specify the -f/--files flag before listing files when using the add command
## v1.3.0 (2023-05-30)

#### New Features

* add current_branch property to Git class
#### Refactorings

* Git().branch() arg defaults to empty string


## v1.2.0 (2023-05-30)

#### New Features

* add context manager to turn stdout capture on then back off
#### Docs

* update readme


## v1.1.0 (2023-05-26)

#### Refactorings

* change tag function parameter default and doc string
## v1.0.0 (2023-05-21)

#### New Features

* all git functions can return stdout as a string
#### Fixes

* fix issue where git.add() would remove path separators
#### Refactorings

* git bindings are now contained in the `Git` class
* do_commit() doesn't assume arg string is a message
* make capture_stdout a class property
* update shell to use Git class
* move git functions into a class so dev can specify whether to capture stdout or not
#### Docs

* update readme


## v0.5.2 (2023-05-15)

#### Fixes

* fix create_remote_from_cwd function to properly add remote and push


## v0.5.1 (2023-05-13)

#### Fixes

* fix  create_remote_from_cwd() not setting remote to upstream


## v0.5.0 (2023-05-11)

#### New Features

* add create_remote_from_cwd()
#### Refactorings

* rename do_list_branches() to do_branches()
* do_new_gh_remote invokes create_remote_from_cwd so url no longer needs to be added manually after creating remote
#### Docs

* update readme
* update doc string


## v0.4.0 (2023-05-04)

#### New Features

* add status command


## v0.3.0 (2023-05-02)

#### Refactorings

* remove do_cmd as it's now covered by parent class's do_sys


## v0.2.0 (2023-05-02)

#### New Features

* override do_help to display unrecognized_command_behavior_status after standard help message
* add functionality to toggle unrecognized command behavior
* add default override to execute line as system command when unrecognized
* display current working directory in prompt
#### Fixes

* set requires-python to >=3.10
#### Refactorings

* remove cwd command
#### Docs

* update readme


## v0.1.1 (2023-04-30)

#### Fixes

* cast Pathier objects to strings in recurse_files()


## v0.1.0 (2023-04-30)

#### New Features

* add do_cmd() to excute shell commands without quitting gitbetter
* enclose 'message' in quotes if you forget them
#### Refactorings

* rename some functions
#### Docs

* update readme
* add future feature to list in readme


## v0.0.0 (2023-04-29)
