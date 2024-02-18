# pylint: disable=too-many-instance-attributes
"""Python script to Validate, Register and analyze impact of DAPIs with a DAPI Server."""

import json
import os

from typing import Dict, List, Optional
from dataclasses import dataclass

import click
from click import ClickException

import requests

from opendapi.scripts.common import (
    get_all_opendapi_files,
    run_git_command,
    save_dapi_suggestions,
    DAPIRequests,
    DAPIServerConfig,
    DAPIServerResponse,
    OpenDAPIFileContents,
)


@dataclass
class ChangeTriggerEvent:
    """Change trigger event, e.g. from Github Actions"""

    event_type: str
    before_change_sha: str
    after_change_sha: str
    repo_api_url: str
    repo_html_url: str
    repo_owner: str
    git_ref: str = None
    pull_request_number: Optional[int] = None

    @property
    def is_pull_request_event(self) -> bool:
        """Check if the event is a pull request event"""
        return self.event_type == "pull_request"

    @property
    def is_push_event(self) -> bool:
        """Check if the event is a push event"""
        return self.event_type == "push"


class DAPIServerAdapter:
    """Adapter to interact with the DAPI Server."""

    def __init__(
        self,
        repo_root_dir: str,
        dapi_server_config: DAPIServerConfig,
        trigger_event: ChangeTriggerEvent,
    ) -> None:
        """Initialize the adapter."""
        self.dapi_server_config = dapi_server_config
        self.trigger_event = trigger_event
        self.repo_root_dir = repo_root_dir
        self.all_files: OpenDAPIFileContents = get_all_opendapi_files(repo_root_dir)

        self.changed_files: OpenDAPIFileContents = self.get_changed_opendapi_files(
            self.trigger_event.before_change_sha, self.trigger_event.after_change_sha
        )

        self.dapi_requests = DAPIRequests(
            dapi_server_config=dapi_server_config,
            all_files=self.all_files,
            changed_files=self.changed_files,
            error_msg_handler=self.display_markdown_summary,
            error_exception_cls=ClickException,
        )

    def display_markdown_summary(self, message: str):
        """Set the message to be displayed on the DAPI Server."""
        if "GITHUB_STEP_SUMMARY" in os.environ:
            with open(
                os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8"
            ) as file_ptr:
                print(f"{message}\n\n", file=file_ptr)
        print(message)

    def _run_git_command(self, command_split: List[str]) -> str:
        """Run a git command."""
        # pylint: disable=R0801
        try:
            return run_git_command(self.repo_root_dir, command_split)
        except Exception as exc:
            raise ClickException(f"git command {command_split}: {exc}") from exc

    def git_diff_filenames(
        self, before_change_sha: str, after_change_sha: str
    ) -> List[str]:
        """Get the list of files changed between two commits."""
        files = self._run_git_command(
            ["git", "diff", "--name-only", before_change_sha, after_change_sha]
        )
        return [filename for filename in files.decode("utf-8").split("\n") if filename]

    def get_changed_opendapi_files(
        self, before_change_sha: str, after_change_sha: str
    ) -> OpenDAPIFileContents:
        """Get files changed between two commits."""

        changed_files = self.git_diff_filenames(before_change_sha, after_change_sha)

        # pylint: disable=R0801
        result: Dict[str, Dict[str, Dict]] = {}

        for result_key, files in self.all_files.contents_as_dict().items():
            result[result_key] = {}
            for filename, file_contents in files.items():
                for changed_file in changed_files:
                    if filename.endswith(changed_file):
                        result[result_key][filename] = file_contents
        return OpenDAPIFileContents(**result, root_dir=self.repo_root_dir)

    def ask_github(self, api_path: str, json_payload: str, is_post: bool) -> Dict:
        """Make API calls to github"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "User-Agent": "opendapi.org",
        }
        if is_post:
            response = requests.post(
                f"{self.trigger_event.repo_api_url}/{api_path}",
                headers=headers,
                json=json_payload,
                timeout=30,
            )
        else:
            response = requests.get(
                f"{self.trigger_event.repo_api_url}/{api_path}",
                params=json_payload,
                headers=headers,
                timeout=30,
            )
        # Error on any status code other than 201 (created) or 422 (PR already exists)
        if response.status_code > 400 and response.status_code != 422:
            raise ClickException(
                "Something went wrong! "
                f"API failure with {response.status_code} for creating a "
                f"pull request at {self.trigger_event.repo_api_url}/{api_path}. "
                f"Response: {response.text}"
            )

        return response.json()

    def create_or_update_pull_request(
        self, title: str, body: str, base: str, head: str
    ) -> int:
        """Create or update a pull request on Github."""

        # Check if a pull request already exists for this branch using list pull requests
        pull_requests = self.ask_github(
            "pulls",
            {
                "head": f"{self.trigger_event.repo_owner}:{head}",
                "base": base,
                "state": "open",
            },
            is_post=False,
        )

        if not pull_requests:
            # Create a new pull request for autoupdate_branch_name
            # to the base branch if one doesn't exist
            response_json = self.ask_github(
                "pulls",
                {"title": title, "body": body, "head": head, "base": base},
                is_post=True,
            )
            suggestions_pr_number = response_json.get("number")
        else:
            suggestions_pr_number = pull_requests[0].get("number")

        return suggestions_pr_number

    def add_pull_request_comment(self, message):
        """Add a comment to the pull request."""
        self.ask_github(
            f"issues/{self.trigger_event.pull_request_number}/comments",
            {"body": message},
            is_post=True,
        )

    def create_suggestions_pull_request(
        self, server_response: DAPIServerResponse, message: str
    ) -> Optional[int]:
        """Add suggestions as a commit."""
        suggestions = server_response.suggestions or {}
        server_name = server_response.server_meta.name

        # Set git config
        self._run_git_command(
            [
                "git",
                "config",
                "--global",
                "user.email",
                server_response.server_meta.github_user_email,
            ]
        )
        self._run_git_command(
            [
                "git",
                "config",
                "--global",
                "user.name",
                server_response.server_meta.github_user_name,
            ]
        )

        # Get current branch name
        current_branch_name = (
            self._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .decode("utf-8")
            .strip()
        )

        # Identify an unique branch name for this Pull request
        autoupdate_branch_name = (
            f"{server_name}-opendapi-autoupdate"
            f"/{self.trigger_event.pull_request_number}"
        )

        # Checkout a branch for this Pull request to make the changes if one doesn't exist
        # if it does exist, checkout the branch and reset it to the latest commit
        self._run_git_command(["git", "checkout", "-B", autoupdate_branch_name])

        # Reset the branch to the latest commit on the Pull request
        self._run_git_command(
            ["git", "reset", "--hard", self.trigger_event.after_change_sha]
        )

        save_dapi_suggestions(self.repo_root_dir, suggestions)

        # Add all files to the commit
        self._run_git_command(["git", "add", "."])

        # Check if there are any changes to commit
        git_status = self._run_git_command(["git", "status", "--porcelain"])

        if not git_status:
            return None

        # Commit the changes
        self._run_git_command(["git", "commit", "-m", message])

        # Push the changes
        self._run_git_command(
            ["git", "push", "-f", "origin", f"HEAD:refs/heads/{autoupdate_branch_name}"]
        )

        body = "## "
        if server_response.server_meta.logo_url:
            body += (
                f'<img src="{server_response.server_meta.logo_url}" '
                'width="30" valign="middle"/> '
            )
        body += f"{server_response.server_meta.name} AI\n"

        body += (
            f"We identified data model changes in #{self.trigger_event.pull_request_number} "
            "and generated updated data documentation for you.\n\n "
            "Please review and merge into your working branch if this looks good.\n\n"
        )

        suggestions_pr_number = self.create_or_update_pull_request(
            title=(
                f"{server_name} data documentation updates "
                f"for #{self.trigger_event.pull_request_number}"
            ),
            body=body,
            base=current_branch_name,
            head=autoupdate_branch_name,
        )

        # Reset by checking out the original branch
        self._run_git_command(["git", "checkout", current_branch_name])

        return suggestions_pr_number

    def add_action_summary(self, resp: DAPIServerResponse):
        """Summarize the output of a request to the DAPI Server."""
        if resp.error:
            self.display_markdown_summary("There were errors")

        self.display_markdown_summary(resp.markdown or resp.text)

        display_json = {
            "errors": resp.errors,
            "suggestions": resp.suggestions,
            "info": resp.info,
        }
        self.display_markdown_summary(
            f"```json\n{json.dumps(display_json, indent=2)}\n```"
        )

    def should_register(self) -> bool:
        """Check if we should register with the DAPI Server."""
        if (
            self.dapi_server_config.register_on_merge_to_mainline
            and self.trigger_event.is_push_event
            and self.trigger_event.git_ref
            == f"refs/heads/{self.dapi_server_config.mainline_branch_name}"
        ):
            return True
        self.display_markdown_summary(
            "Registration skipped because the conditions weren't met"
        )
        return False

    def run(self):
        """Run the action."""
        # Handle no OpenDAPI files or no changes to OpenDAPI files
        if self.all_files.is_empty or self.changed_files.is_empty:
            self.display_markdown_summary(
                "No OpenDAPI files or changes found. "
                "Check out https://opendapi.org to get started."
            )
            return

        validate_resp = self.dapi_requests.validate()
        self.add_action_summary(validate_resp)

        # Create Pull request commit with suggestions
        if self.dapi_server_config.suggest_changes:
            suggestions_pr_number = self.create_suggestions_pull_request(
                validate_resp, "OpenDAPI suggestions"
            )
        else:
            suggestions_pr_number = None

        if self.should_register():
            register_resp = self.dapi_requests.register(
                self.trigger_event.after_change_sha,
                self.trigger_event.repo_html_url,
            )
            self.add_action_summary(register_resp)

        # pylint: disable=R0801
        impact_resp = self.dapi_requests.analyze_impact()
        self.add_action_summary(impact_resp)

        if self.dapi_server_config.display_dapi_stats:
            stats_resp = self.dapi_requests.retrieve_stats()
            self.add_action_summary(stats_resp)

        # Construct and add summary response as a Pull request comment
        if self.trigger_event.is_pull_request_event:
            # Title
            pr_comment_md = "## "
            pr_comment_md += f'<a href="{validate_resp.server_meta.url}">'
            if validate_resp.server_meta.logo_url:
                pr_comment_md += (
                    f'<img src="{validate_resp.server_meta.logo_url}"'
                    ' width="30" valign="middle"/>  '
                )
            pr_comment_md += (
                f"{validate_resp.server_meta.name} Data Documentation AI</a>\n\n"
            )

            # Suggestions
            if suggestions_pr_number:
                pr_comment_md += (
                    "### :heart: Great looking PR! Review your data model changes\n\n"
                )
                pr_comment_md += (
                    "We noticed some data model changes and "
                    "generated updated data documentation for you. "
                    "We have some suggestions for you. "
                    f"Please review #{suggestions_pr_number} and merge into this Pull Request.\n\n"
                )
                pr_comment_md += (
                    f'<a href="{self.trigger_event.repo_html_url}/pull/{suggestions_pr_number}">'
                    f'<img src="{validate_resp.server_meta.suggestions_cta_url}" width="140"/>'
                    "</a>"
                    "\n\n<hr>\n\n"
                )

            # Validation Response
            if validate_resp.markdown:
                pr_comment_md += validate_resp.markdown
                pr_comment_md += "\n\n<hr>\n\n"

            # No registration response for Pull requests

            # Impact Response
            if impact_resp.markdown:
                pr_comment_md += impact_resp.markdown

            # Stats Response
            if self.dapi_server_config.display_dapi_stats:
                pr_comment_md += "\n\n<hr>\n\n"
                if stats_resp.markdown:
                    pr_comment_md += stats_resp.markdown

            self.add_pull_request_comment(pr_comment_md)


@click.command()
@click.option(
    "--github-event-name",
    type=click.Choice(["push", "pull_request"], case_sensitive=True),
    envvar="GITHUB_EVENT_NAME",
    show_envvar=True,
)
@click.option("--github-workspace", envvar="GITHUB_WORKSPACE", show_envvar=True)
@click.option("--github-step-summary", envvar="GITHUB_STEP_SUMMARY", show_envvar=True)
@click.option(
    "--github-event-path",
    type=click.File("rb"),
    envvar="GITHUB_EVENT_PATH",
    show_envvar=True,
)
@click.option("--github-token", envvar="GITHUB_TOKEN", show_envvar=True)
@click.option("--dapi-server-host", envvar="DAPI_SERVER_HOST", show_envvar=True)
@click.option("--dapi-server-api-key", envvar="DAPI_SERVER_API_KEY", show_envvar=True)
@click.option(
    "--mainline-branch", default="main", envvar="MAINLINE_BRANCH_NAME", show_envvar=True
)
@click.option(
    "--register-on-merge-to-mainline",
    is_flag=True,
    default=True,
    envvar="REGISTER_ON_MERGE_TO_MAINLINE",
    show_envvar=True,
)
@click.option(
    "--suggest-changes",
    is_flag=True,
    default=True,
    envvar="SUGGEST_CHANGES",
    show_envvar=True,
)
def dapi_ci(
    github_event_name: str,
    github_workspace: str,
    github_step_summary: str,
    github_event_path: str,
    github_token: str,
    dapi_server_host: str,
    dapi_server_api_key: str,
    mainline_branch: str,
    register_on_merge_to_mainline: bool,
    suggest_changes: bool,
):  # pylint: disable=too-many-arguments,too-many-locals
    """Github Action handler CLI script for DAPI validation"""

    if not github_event_path:
        raise ClickException("Event path not specified")

    try:
        github_event = json.load(github_event_path)
    except json.JSONDecodeError as exc:
        raise ClickException(
            f"Unable to load event json file {github_event_path.name}: {exc}"
        ) from exc

    # Rebuild github context from environment variables
    gh_context: dict = {
        "event_name": github_event_name,
        "root_dir": github_workspace,
        "step_summary_path": github_step_summary,
        "event_path": github_event_path,
        "token": github_token,
        "event": github_event,
    }

    change_trigger_event = ChangeTriggerEvent(
        event_type=gh_context["event_name"],
        repo_api_url=gh_context["event"]["repository"]["url"],
        repo_html_url=gh_context["event"]["repository"]["html_url"],
        repo_owner=gh_context["event"]["repository"]["owner"]["login"],
        before_change_sha=gh_context["event"]["before"]
        if gh_context["event_name"] == "push"
        else gh_context["event"]["pull_request"]["base"]["sha"],
        after_change_sha=gh_context["event"]["after"]
        if gh_context["event_name"] == "push"
        else gh_context["event"]["pull_request"]["head"]["sha"],
        git_ref=gh_context["event"]["ref"]
        if gh_context["event_name"] == "push"
        else gh_context["event"]["pull_request"]["head"]["ref"],
        pull_request_number=gh_context["event"]["pull_request"]["number"]
        if gh_context["event_name"] == "pull_request"
        else None,
    )

    # We will suggest changes only if it is a pull request event handler
    suggest_changes = not change_trigger_event.is_pull_request_event

    dapi_server_config = DAPIServerConfig(
        server_host=dapi_server_host,
        api_key=dapi_server_api_key,
        mainline_branch_name=mainline_branch,
        register_on_merge_to_mainline=register_on_merge_to_mainline,
        suggest_changes=suggest_changes,
    )

    dapi_server_adapter = DAPIServerAdapter(
        repo_root_dir=gh_context["root_dir"],
        dapi_server_config=dapi_server_config,
        trigger_event=change_trigger_event,
    )

    dapi_server_adapter.display_markdown_summary("# OpenDAPI CI")
    dapi_server_adapter.display_markdown_summary(
        "Here we will validate, register, and analyze the impact of changes to OpenDAPI files."
    )
    dapi_server_adapter.run()


if __name__ == "__main__":
    dapi_ci()  # pylint: disable=no-value-for-parameter  # pragma: no cover
