# pylint: disable=too-many-instance-attributes
"""Python script to Validate, Register and analyze impact of DAPIs with a DAPI Server."""

import os

from typing import Dict, List
from datetime import datetime

import click
from click import ClickException

from opendapi.scripts.common import (
    OpenDAPIFileContents,
    DAPIRequests,
    DAPIServerConfig,
    DAPIServerResponse,
    run_git_command,
    get_all_opendapi_files,
    save_dapi_suggestions,
)


class DAPILocalServerAdapter:
    """Adapter to interact with the DAPI Server."""

    def __init__(
        self,
        repo_root_dir: str,
        dapi_server_config: DAPIServerConfig,
        revalidate_all_files: bool = False,
        overwrite_uncommitted_changes: bool = False,
    ) -> None:
        """Initialize the adapter."""
        self.dapi_server_config = dapi_server_config
        self.repo_root_dir = repo_root_dir
        self.overwrite_uncommitted_changes = overwrite_uncommitted_changes

        # Get all the OpenDAPI files
        self.all_files: OpenDAPIFileContents = get_all_opendapi_files(repo_root_dir)

        # Get the files changes from main branch
        if revalidate_all_files:
            click.secho("Revalidating all files", fg="green")
            self.changed_files = self.all_files
        else:
            self.changed_files: OpenDAPIFileContents = self.get_changed_opendapi_files(
                self.dapi_server_config.mainline_branch_name
            )
            click.secho("Revalidating only changed files", fg="green")

        self.dapi_requests = DAPIRequests(
            dapi_server_config=dapi_server_config,
            all_files=self.all_files,
            changed_files=self.changed_files,
            error_msg_handler=None,
            error_exception_cls=RuntimeError,
        )

    def _run_git_command(self, command_split: List[str]) -> str:
        """Run a git command."""
        try:
            return run_git_command(self.repo_root_dir, command_split)
        except Exception as exc:
            raise ClickException(f"git command {command_split}: {exc}") from exc

    def git_diff_filenames(self, mainline_branch_name: str) -> List[str]:
        """Get the list of files changed between current and main branch"""
        files = self._run_git_command(
            ["git", "diff", "--name-only", mainline_branch_name]
        )
        return [filename for filename in files.decode("utf-8").split("\n") if filename]

    def get_changed_opendapi_files(
        self, mainline_branch_name: str
    ) -> OpenDAPIFileContents:
        """Get files changed between current and main branch"""

        changed_files = self.git_diff_filenames(mainline_branch_name)

        result: Dict[str, Dict[str, Dict]] = {}

        for result_key, files in self.all_files.contents_as_dict().items():
            result[result_key] = {}
            for filename, file_contents in files.items():
                for changed_file in changed_files:
                    if filename.endswith(changed_file):
                        result[result_key][filename] = file_contents
        return OpenDAPIFileContents(**result, root_dir=self.repo_root_dir)

    def update_opendapi_files(self, server_response: DAPIServerResponse):
        """Update opendapi files based on server suggestions"""
        suggestions = server_response.suggestions or {}
        server_name = server_response.server_meta.name

        click.secho(
            f"Updating dapi files based on {server_name} suggestions",
        )

        # Update files if content is different
        save_dapi_suggestions(self.repo_root_dir, suggestions)
        click.secho(f"Updated {len(suggestions)} files", fg="green")

    def add_action_summary(self, resp: DAPIServerResponse):
        """Summarize the output of a request to the DAPI Server."""
        if resp.error:
            click.secho("There were errors", fg="red")

        click.echo(resp.text)

    def run(self):
        """Run the action."""
        # Check that all the local files are committed, so that we can generate
        # changes on top of the latest commit. We do not want to overwrite the
        # developer's latest changes.

        if not self.overwrite_uncommitted_changes and self._run_git_command(
            ["git", "diff", "--name-only"]
        ):
            raise ClickException(
                "Uncommitted changes found. Please commit your changes.",
            )

        # Handle no OpenDAPI files or no changes to OpenDAPI files
        if self.all_files.is_empty or self.changed_files.is_empty:
            raise ClickException("No OpenDAPI files or changes found")

        click.secho(
            f"Validating {len(self.changed_files.dapis)} DAPI files in "
            f"batch size of {self.dapi_server_config.batch_size}"
        )
        if self.dapi_server_config.suggest_changes:
            click.secho("Will request DAPI server to suggest changes", fg="green")

        start = datetime.now()
        with click.progressbar(length=len(self.changed_files.dapis)) as progressbar:
            validate_resp = self.dapi_requests.validate(
                notify_function=progressbar.update
            )
        end = datetime.now()

        click.secho(f"Time taken {end - start}", fg="green")
        self.add_action_summary(validate_resp)

        # Create Pull request commit with suggestions
        if self.dapi_server_config.suggest_changes:
            self.update_opendapi_files(validate_resp)

        impact_resp = self.dapi_requests.analyze_impact()
        self.add_action_summary(impact_resp)

        if self.dapi_server_config.display_dapi_stats:
            stats_resp = self.dapi_requests.retrieve_stats()
            self.add_action_summary(stats_resp)


@click.command()
@click.option("--dapi-server-host", envvar="DAPI_SERVER_HOST", show_envvar=True)
@click.option("--dapi-server-api-key", envvar="DAPI_SERVER_API_KEY", show_envvar=True)
@click.option(
    "--repo-root-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=os.getcwd(),
    envvar="REPO_ROOT_DIR",
    show_envvar=True,
    help="The root directory of the repository",
)
@click.option(
    "--mainline-branch-name",
    default="main",
    envvar="MAINLINE_BRANCH_NAME",
    show_envvar=True,
    help="The name of the mainline branch to compare against",
)
@click.option(
    "--suggest-changes",
    is_flag=True,
    default=True,
    envvar="SUGGEST_CHANGES",
    show_envvar=True,
    help="Suggest changes to the DAPI files",
)
@click.option(
    "--batch-size",
    default=50,
    envvar="BATCH_SIZE",
    help="Batch size for validating dapi files",
    show_envvar=True,
)
@click.option(
    "--revalidate-all-files",
    is_flag=True,
    default=False,
    envvar="REVALIDATE_ALL_FILES",
    help="Revalidate all files, not just the ones that have changed",
    show_envvar=True,
)
@click.option(
    "--overwrite-uncommitted-changes",
    is_flag=True,
    default=False,
    envvar="OVERWRITE_UNCOMMITTED_CHANGES",
    help="Overwrite uncommitted DAPI files with server suggestions",
    show_envvar=True,
)
def dapi_local(
    dapi_server_host: str,
    dapi_server_api_key: str,
    repo_root_dir: str,
    mainline_branch_name: str,
    suggest_changes: bool,
    batch_size: int,
    revalidate_all_files: bool,
    overwrite_uncommitted_changes: bool,
):  # pylint: disable=too-many-arguments,too-many-locals
    """CLI script for DAPI validation"""

    dapi_server_config = DAPIServerConfig(
        server_host=dapi_server_host,
        api_key=dapi_server_api_key,
        mainline_branch_name=mainline_branch_name,
        suggest_changes=suggest_changes,
        batch_size=batch_size,
    )

    dapi_server_adapter = DAPILocalServerAdapter(
        repo_root_dir=repo_root_dir,
        dapi_server_config=dapi_server_config,
        revalidate_all_files=revalidate_all_files,
        overwrite_uncommitted_changes=overwrite_uncommitted_changes,
    )

    dapi_server_adapter.run()


if __name__ == "__main__":
    dapi_local()  # pylint: disable=no-value-for-parameter  # pragma: no cover
