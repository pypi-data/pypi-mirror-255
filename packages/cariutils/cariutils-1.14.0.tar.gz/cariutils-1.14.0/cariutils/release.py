"""
#
# Utility to create a new Github release
#
# Copyright(c) 2018, Carium, Inc. All rights reserved.
#
"""

import difflib
import importlib
import logging
import os
import re
import shlex
import tempfile
from argparse import ArgumentParser
from typing import Any, cast, Dict, List, Optional

import requests
from bumpversion.cli import main as bumpversion_main
from git.cmd import Git
from git.remote import PushInfo
from git.repo.base import Repo
from github import Github, Repository, UnknownObjectException
from github.PullRequest import PullRequest

from cariutils import itertools as it
from cariutils.cli import Cli, Command


cicd_author = shlex.quote("Carium CICD <devops+git@carium.com>")
security_gh_login = "dependabot[bot]"  # autobots rollout!
log = logging.getLogger(__name__)


class JiraRef:
    def __init__(self, issue: str):
        self.issue = issue  # short form ie DEV-1234

    @property
    def url(self) -> str:
        return f"https://carium.atlassian.net/browse/{self.issue}"

    @property
    def markdown_link(self) -> str:
        return f"[{self.issue}]({self.url})"


class ReleaseUtil:

    RELEASE_TYPE_MAP = {
        "#major#": 2,
        "#minor#": 1,
        "#patch#": 0,
    }
    REVERSE_RELEASE_MAP = {v: k.strip("#") for k, v in RELEASE_TYPE_MAP.items()}
    # JIRA ticket has to match exactly DEV/SOL followed by 1-6 digit numbers
    re_jira_ticket = re.compile(r"((DEV|SOL)-(?!\d{7,})\d{1,6})")
    re_release_type = re.compile(r"#[a-z]{5}#")

    @classmethod
    def bump_version(cls, module: str, version: str, release_type: str, *extra_args) -> None:
        """
        setup.cfg should contain bumpversion section with the current_version attribute, and
        bumpversion:files for each file with a version field.

        e.g.
        ```
        [bumpversion]
        current_version = 1.3.4

        [bumpversion:file:cariutils/__init__.py]
        ```

        See bumpversion documentation for more details.  https://github.com/peritus/bumpversion
        """
        if os.path.exists("setup.cfg"):
            args = [release_type]
        elif os.path.exists(".bumpversion.cfg"):
            args = [release_type]
        else:
            # temporary until setup.py is deprecated in each repo
            args = [
                "--current-version",
                version,
                release_type,
                "setup.py",
                "{}/__init__.py".format(module),
            ]
        bumpversion_main(args + list(extra_args))

    def __init__(self, token, module):
        self.token = token
        self.module = module

    def get_github(self, repo: Optional[str] = None) -> Repository:  # pyre-ignore[11]
        return Github(self.token).get_repo(repo or self.get_module().__github_repo__)

    def get_module(self):
        return importlib.import_module(self.module)

    @classmethod
    def get_commits_since_tag(cls, git_repo: Repo, tag: str) -> List[Dict[str, Any]]:
        """Return all commits since the given tag"""
        _git = cast(Git, git_repo.git)
        lines = _git.log(f"{tag}..HEAD").split("\n")
        commits = []
        commit_d = {}
        for line in lines:
            line = line.strip()
            if line.startswith("commit"):
                commit_d = {
                    "id": line.split("commit ", 1)[1],
                    "merge": False,
                    "pull-request": None,
                    "text": [],
                }
                commits.append(commit_d)
            elif line.startswith("Author:"):
                commit_d["author"] = line.split("Author:", 1)[1].strip()
            elif line.startswith("Date:"):
                commit_d["date"] = line.split("Date:", 1)[1].strip()
            elif line.startswith("Merge:"):
                commit_d["merge"] = True
            else:
                if line != "":
                    if line.startswith("Merge pull request"):
                        commit_d["pull-request"] = int(line.split("Merge pull request", 1)[1].split()[0][1:])
                    commit_d["text"].append(line)

        return commits

    def get_latest_prs(self) -> List[PullRequest]:
        github_repo = self.get_github()

        # Get the commit-tag from the last release
        # The commit should be the second from the last. The first one points to the release tag.
        try:
            last_release = github_repo.get_latest_release()
        except UnknownObjectException:
            print("Either the repo does not exist or there is no initial release -- please make one!")
            print(f"Try `release run --initial {self.module}`")
            raise

        git_repo = Repo(".")
        cast(Git, git_repo.git).fetch()

        # Get all merge commits since last-tag
        pulls = [
            github_repo.get_pull(each["pull-request"])
            for each in self.get_commits_since_tag(git_repo, last_release.tag_name)
            if each["pull-request"] is not None
        ]

        # Only consider pulls into main -- prevents pulls into other pulls from breaking versioning
        return [pull for pull in pulls if pull.base.ref == github_repo.default_branch]

    @classmethod
    def get_change_logs(cls, pr: PullRequest) -> List[str]:
        """Return the CHANGE_LOGS from the given PR"""
        lines = list(
            it.dropwhile(
                lambda line: line.lower().strip() != "# changelog",
                iter(pr.body.splitlines()),
            )
        )[1:]

        if len(lines) == 0 and pr.user.login == security_gh_login:
            # Github automated security PRs don't follow our #changelog requirements
            # So we construct one for it.
            version_bump_info_lines = [line for line in pr.body.splitlines() if "bumps" in line.strip().lower()]
            lines = [
                "- Automated dependency upgrade due to security advisory (thanks Github!)",
                f"- {version_bump_info_lines[0]}" if len(version_bump_info_lines) > 0 else "",
            ]

        return lines

    @classmethod
    def get_jira_tickets(cls, pr: PullRequest) -> List[JiraRef]:
        """Find JIRA patterns within # Changelog section"""
        lines = cls.get_change_logs(pr)
        if (len(lines) > 0) and ("thanks Github" in lines[0]):
            return [JiraRef("AUTOBOT")]

        return [JiraRef(t) for t in sorted({each[0] for line in lines for each in cls.re_jira_ticket.findall(line)})]

    @classmethod
    def get_release_type(cls, pr: PullRequest) -> int:
        for line in pr.body.splitlines():
            tag = cls.re_release_type.search(line.lower())
            if tag is None:
                continue
            tag = tag.group(0)
            if tag in cls.RELEASE_TYPE_MAP:
                return cls.RELEASE_TYPE_MAP[tag]

        # Automated security updates from Github always get #patch# since
        # they don't change any user-facing features
        if pr.user.login == security_gh_login:
            return cls.RELEASE_TYPE_MAP["#patch#"]

        raise ValueError("PR {} has no release type information".format(pr.number))


class PropagateCmd(Command):

    name = "propagate-version"

    @classmethod
    def init_args(cls, subparser: ArgumentParser) -> None:
        subparser.add_argument("--repository", required=True)
        subparser.add_argument("--image", required=True)
        subparser.add_argument("module")

    def execute(self) -> int:
        """Push the current version to the canonical kubernetes definition repository"""
        rel = ReleaseUtil(self.args.token, self.args.module)
        module = rel.get_module()
        new_version = module.__version__
        deployment_name = getattr(module, "__deployment_name__", self.args.module)

        image = f"{self.args.repository}/{self.args.image}"

        image_pattern = rf"{re.escape(image)}:\d+\.\d+\.\d+(-[\w\d\.]+)?(\s|$)"
        new_image = f"{image}:{new_version}"

        with tempfile.TemporaryDirectory() as dir:
            github = github_remote(self.args.token, "carium-inc/deployments")
            repo = Repo.clone_from(github, dir)

            short_file = f"cicd/{deployment_name}.yaml"
            k8s_deployment_file = f"{dir}/{short_file}"

            with open(k8s_deployment_file) as f:
                old_text = f.read()

            new_text = re.sub(image_pattern, rf"{new_image}\2", old_text)

            if new_text == old_text:
                print("I cant find any changes to make! Did you actually update the version?")
                return 1

            from_to = f"{github}/{short_file}".replace(self.args.token, "token")

            diff = difflib.unified_diff(
                a=old_text.splitlines(True),
                b=new_text.splitlines(True),
                fromfile=from_to,
                tofile=from_to,
            )
            print("".join(diff))

            with open(k8s_deployment_file, "w") as f:
                f.write(new_text)

            repo.index.add([k8s_deployment_file])

            message = f"Update {self.args.image} to {new_version}\n"
            repo.git.commit(all=True, message=message, author=cicd_author)

            print("Pushing...")
            info = repo.remotes["origin"].push()[0]
            print(info.summary)

            PI = PushInfo
            if info.flags & (PI.ERROR | PI.REMOTE_FAILURE | PI.REJECTED | PI.REMOTE_REJECTED):  # pyre-ignore[16]
                return 1

            # send slack message to #ci here using `message` text
            slack_url = os.environ.get("SLACK_URL")
            if slack_url:
                requests.post(url=slack_url, data={"text": message})
            else:
                # EP: Enforce coverage to pass
                pass

        return 0


class RunCmd(Command):

    name = "run"

    @classmethod
    def init_args(cls, subparser: ArgumentParser) -> None:
        subparser.add_argument("module")
        subparser.add_argument("--initial", default=False, action="store_true")

    def _initial_release(self) -> int:
        rel = ReleaseUtil(self.args.token, self.args.module)
        github_repo = rel.get_github()
        has_release = True
        try:
            github_repo.get_latest_release()
        except UnknownObjectException:
            has_release = False
        if has_release:
            print("--initial only valid for creating the very first release")
            return 1

        version = rel.get_module().__version__
        release_title = f"{version}: Initial Release"
        github_repo.create_git_release(
            tag=version,
            name=release_title,
            message="\n".join(
                [
                    "# Changelogs",
                    "",
                    "* Initial release",
                    f"  * Created with cariutils `release run --initial {self.args.module}`",
                    "",
                ]
            ),
        )
        return 0

    def execute(self) -> int:
        if self.args.initial:
            return self._initial_release()

        rel = ReleaseUtil(self.args.token, self.args.module)
        try:
            new_prs = rel.get_latest_prs()
        except UnknownObjectException:
            return 1

        if len(new_prs) == 0:
            print("No new PRs found. Exiting...")
            return 1

        release_type = ReleaseUtil.REVERSE_RELEASE_MAP[max(rel.get_release_type(pr) for pr in new_prs)]
        rel.bump_version(self.args.module, rel.get_module().__version__, release_type)

        # Re-read new version
        importlib.reload(rel.get_module())
        new_version = rel.get_module().__version__

        # Provenance information to make it easy to jump around while debugging
        pr_details = []
        for pull in new_prs:
            pr_details.append(f"Pr: {pull.html_url}")
            pr_details.append(f"Pr-Author: @{pull.user.login}")
            for ticket in ReleaseUtil.get_jira_tickets(pull):
                pr_details.append(f"Jira: {ticket.markdown_link}")

            pr_details.append("")

        # Update master
        repo = Repo(".")
        repo.commit()
        git = cast(Git, Repo(".").git)
        git.commit(
            all=True,
            message="Upgrade version to {new_version}\n\n[ci skip]\n\n{provenance}".format(
                new_version=new_version,
                provenance="\n".join(pr_details),
            ),
            author=cicd_author,
        )

        # We don't want to have to ship a private keypair to CircleCI -- we already have a github token!
        # But the default branch we are on has only has RO access :(
        # But the github token has write access :)
        # So we fudge the remote a little bit to factor in the github token
        remote_name = f"remote-versionbump-{new_version}"
        repo.create_remote(
            remote_name,
            github_remote(self.args.token, rel.get_module().__github_repo__),
        )
        git.push(remote_name, "master")
        repo.delete_remote(remote_name)  # pyre-fixme[6]

        # Create github release
        change_logs = list(it.chain(*[rel.get_change_logs(pr) for pr in new_prs]))
        github_repo = rel.get_github()
        release_title = "{}: {}".format(new_version, " / ".join(pull.title for pull in new_prs))[:255]
        github_repo.create_git_release(
            tag=new_version,
            name=release_title,
            message="\r\n".join(
                [
                    *pr_details,
                    "# CHANGELOGS",
                    *change_logs,
                    "",
                ]
            ),
        )

        return 0


class ReleaseTypeCmd(Command):

    name = "get-release-type"

    @classmethod
    def init_args(cls, subparser: ArgumentParser) -> None:
        subparser.add_argument("module")

    def execute(self) -> int:
        rel = ReleaseUtil(self.args.token, self.args.module)
        new_prs = rel.get_latest_prs()
        if len(new_prs) == 0:
            print("No new PR found")
            return 1

        release_type = max(rel.get_release_type(pr) for pr in new_prs)
        print(ReleaseUtil.REVERSE_RELEASE_MAP[release_type])
        return 0


class GetPrCmd(Command):

    name = "get-latest-prs"

    @classmethod
    def init_args(cls, subparser: ArgumentParser) -> None:
        subparser.add_argument("module")
        subparser.add_argument("--logs", action="store_true", default=False)

    def execute(self) -> int:
        rel = ReleaseUtil(self.args.token, self.args.module)
        new_prs = rel.get_latest_prs()
        for pr in new_prs:
            print("{}: {}".format(pr.number, pr.title))
            if self.args.logs:
                for line in rel.get_change_logs(pr):
                    print("  {}".format(line))

        return 0


class CheckPrMessage(Command):

    name = "check-pr"
    CIRCLE_ENV = "CIRCLE_PULL_REQUEST"

    def execute(self) -> int:
        if self.CIRCLE_ENV not in os.environ:
            print("This doesnt look like a PR! CIRCLE_PULL_REQUEST would have been set!")
            return 0  # <finger to forehead> can't complain about message formatting if there is no message

        pr_url = os.environ[self.CIRCLE_ENV]
        repo, pr_number = re.findall(r"github.com/(.+?)/pull/(\d+)", pr_url)[0]

        rel = ReleaseUtil(self.args.token, None)
        github = rel.get_github(repo=repo)
        pr = github.get_pull(int(pr_number))

        # Verify has versioning info
        try:
            change_level = ReleaseUtil.get_release_type(pr)
            print(f"This appears to be a {ReleaseUtil.REVERSE_RELEASE_MAP[change_level]} change.")
        except ValueError as exc:
            print(str(exc))
            return 1

        # And has changelog info
        changelog = "\r\n".join(ReleaseUtil.get_change_logs(pr))
        if changelog.strip() == "":
            print("Did you forget to add a `# changelog` section?")
            return 1

        print("The changelog appears to be:")
        print("-" * 25)
        print(changelog)
        print("-" * 25)

        # And has tickets
        tickets = ReleaseUtil.get_jira_tickets(pr)
        if len(tickets) == 0:
            print("Did you forget to add the JIRA tickets on the changelog section?")
            return 1

        print("Tickets:")
        print("\n".join([ticket.issue for ticket in tickets]))

        return 0


class Release(Cli):
    commands = (
        "CheckPrMessage",
        "GetPrCmd",
        "PropagateCmd",
        "ReleaseTypeCmd",
        "RunCmd",
    )

    @classmethod
    def get_default_token(cls) -> str:
        # CircleCI has a secret env var set with the token we'll be using
        # But a human will have one set in their git config
        privileged = os.environ.get("RELEASE_GITHUB_TOKEN")  # special, privileged
        default_circle = os.environ.get("GITHUB_ACCESS_TOKEN")  # non-privileged default

        params = {"global": True, "with_exceptions": False}
        return privileged or default_circle or cast(Git, Repo().git).config("github.token", **params)

    @classmethod
    def init_args(cls, parser: ArgumentParser) -> None:
        parser.add_argument("--token", default=cls.get_default_token())


def github_remote(token: str, repo: str) -> str:
    return f"https://{token}@github.com/{repo}.git"


if __name__ == "__main__":  # pragma: no cover
    Release.main()
