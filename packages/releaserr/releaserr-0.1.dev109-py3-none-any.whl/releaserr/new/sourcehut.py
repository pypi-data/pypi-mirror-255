# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
Rough Sourcehut API wrapper to create projects
"""

from __future__ import annotations

from sourcehut.client import VISIBILITY, SrhtClient
from sourcehut.services import git, lists, todo

DEFAULT_BASEURL = "sr.ht"


class SourcehutProjectMaker:
    TODO_PREAMBLE = """\
This tracker allows comments on existing tickets but no new ones.
Please report new issues and request features on the mailing list.

"""
    LIST_PREAMBLE = """\
Mailing list for discussion, issue reporting, and patches related to the
[{0}](https://sr.ht/~gotmax23/{0}/) project.
For help sending patches to this list, please consult
[git-send-email.io](https://git-send-email.io).

"""

    def __init__(
        self,
        client: SrhtClient,
        name: str,
        visibility: VISIBILITY = VISIBILITY.PUBLIC,
        description: str | None = None,
    ) -> None:
        self.client = client
        self.name = name
        self.visibility = visibility
        self.description = description

        self.gitc = git.GitSrhtClient(self.client)
        self.todoc = todo.TodoSrhtClient(self.client)
        self.listc = lists.ListsSrhtClient(self.client)

    async def create_git(self) -> git.Repository:
        return await self.gitc.create_repository(
            self.name, visibility=self.visibility, description=self.description
        )

    async def create_todo(self) -> todo.Tracker:
        return await self.todoc.create_tracker(
            self.name,
            description=self.TODO_PREAMBLE + self.linktree,
            visibility=self.visibility,
        )

    async def _disable_new_todos(
        self, tracker_id: int | todo.TrackerRef
    ) -> todo.TrackerDefaultACL:
        return await self.todoc.update_tracker_acl(
            tracker_id,
            browse=True,
            comment=True,
            edit=False,
            submit=False,
            triage=False,
        )

    async def create_list(self) -> lists.MailingList:
        return await self.listc.create_list(
            self.name,
            description=self.LIST_PREAMBLE.format(self.name) + self.linktree,
            visibility=self.visibility,
        )

    @property
    def linktree(self) -> str:
        return f"""\
## {self.name}

{self.description or ""}

- [{self.name} project hub](https://sr.ht/~gotmax23/{self.name})
- [{self.name} git.sr.ht repo](https://git.sr.ht/~gotmax23/{self.name})
- [{self.name} mailing list][archives] ([~gotmax/{self.name}@lists.sr.ht][mailto])
- [{self.name} tracker](https://todo.sr.ht/~gotmax23/{self.name})

[archives]: https://lists.sr.ht/~gotmax23/{self.name}
[mailto]: mailto:~gotmax/{self.name}@lists.sr.ht
"""
