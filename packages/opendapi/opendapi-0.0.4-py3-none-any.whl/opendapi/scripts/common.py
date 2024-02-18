# pylint: disable=too-many-instance-attributes
"""Python script to Validate, Register and analyze impact of DAPIs with a DAPI Server."""

import itertools
import json
import os
import subprocess  # nosec: B404

from typing import Dict, List, Optional, Callable, Type, Any
from dataclasses import dataclass
from urllib.parse import urljoin
from deepmerge import always_merger
from ruamel.yaml import YAML

import requests

from opendapi.validators.teams import TeamsValidator
from opendapi.validators.dapi import DapiValidator
from opendapi.validators.datastores import DatastoresValidator
from opendapi.validators.purposes import PurposesValidator


def _chunks(data, size=1):
    iterator = iter(data)
    for _ in range(0, len(data), size):
        yield {k: data[k] for k in itertools.islice(iterator, size)}


@dataclass
class DAPIServerConfig:
    """Configuration for the DAPI Server."""

    server_host: str
    api_key: str
    mainline_branch_name: str
    register_on_merge_to_mainline: bool = True
    suggest_changes: bool = True
    display_dapi_stats: bool = False
    batch_size: int = 1


@dataclass
class DAPIServerMeta:
    """Metadata about the DAPI server"""

    name: str
    url: str
    github_user_name: str
    github_user_email: str
    logo_url: Optional[str] = None
    suggestions_cta_url: Optional[str] = None


@dataclass
class DAPIServerResponse:
    """DAPI server Response formatted"""

    status_code: int
    server_meta: DAPIServerMeta
    suggestions: Optional[Dict] = None
    info: Optional[Dict] = None
    errors: Optional[Dict] = None
    text: Optional[str] = None
    markdown: Optional[str] = None

    @property
    def error(self) -> bool:
        """Check if there is an error in the response."""
        return self.errors is not None and len(self.errors) > 0

    def merge(self, other: "DAPIServerResponse") -> "DAPIServerResponse":
        """Merge two responses."""

        def merge_text_fn(this_text, other_text):
            if not this_text or not other_text:
                return other_text or this_text

            return (
                "\n\n".join([this_text, other_text])
                if this_text != other_text
                else other_text
            )

        def merge_dict(this_dict, other_dict):
            if not this_dict or not other_dict:
                return other_dict or this_dict

            return always_merger.merge(this_dict, other_dict)

        return DAPIServerResponse(
            status_code=other.status_code or self.status_code,
            server_meta=other.server_meta or self.server_meta,
            errors=merge_dict(self.errors, other.errors),
            suggestions=merge_dict(self.suggestions, other.suggestions),
            info=merge_dict(self.info, other.info),
            text=merge_text_fn(self.text, other.text),
            markdown=merge_text_fn(self.markdown, other.markdown),
        )


@dataclass
class OpenDAPIFileContents:
    """Set of OpenDAPI files."""

    teams: Dict[str, Dict]
    dapis: Dict[str, Dict]
    datastores: Dict[str, Dict]
    purposes: Dict[str, Dict]
    root_dir: str

    def contents_as_dict(self):
        """Convert to a dictionary."""
        return {
            "teams": self.teams,
            "dapis": self.dapis,
            "datastores": self.datastores,
            "purposes": self.purposes,
        }

    @staticmethod
    def _prune_root_dir(location: str, root_dir: str):
        """Prune the root dir from the location."""
        return location[len(root_dir) + 1 :]

    def for_server(self):
        """Convert to a format ready for the DAPI Server."""
        result = {}
        for result_key, contents in self.contents_as_dict().items():
            result[result_key] = {
                self._prune_root_dir(location, self.root_dir): json_content
                for location, json_content in contents.items()
            }
        return result

    @property
    def is_empty(self):
        """Check if the contents are empty."""
        return len(self) == 0

    def __len__(self):
        length = 0
        for val in self.contents_as_dict().values():
            length += len(val)
        return length


def run_git_command(cwd: str, command_split: List[str]) -> str:
    """Run a git command."""
    try:
        return subprocess.check_output(
            command_split,
            cwd=cwd,
        )  # nosec
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"git command {command_split}: {exc}") from exc


def get_all_opendapi_files(repo_root_dir: str) -> OpenDAPIFileContents:
    """Get files from the DAPI Server."""

    result: Dict[str, Dict[str, Dict]] = {}
    for result_key, validator_cls in {
        "teams": TeamsValidator,
        "dapis": DapiValidator,
        "datastores": DatastoresValidator,
        "purposes": PurposesValidator,
    }.items():
        result[result_key] = validator_cls(
            repo_root_dir,
            enforce_existence=False,
            should_autoupdate=False,
        ).parsed_files
    return OpenDAPIFileContents(**result, root_dir=repo_root_dir)


def save_dapi_suggestions(repo_root_dir: str, suggestions: Dict[str, Any]) -> None:
    """Save the DAPI suggestions to the repo."""

    yaml = YAML()
    # Update files if content is different
    for filename, file_contents in suggestions.items():
        # write file_contents into file
        with open(
            os.path.join(repo_root_dir, filename), "w", encoding="utf-8"
        ) as file_ptr:
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                yaml.dump(file_contents, file_ptr)
            elif filename.endswith(".json"):
                json.dump(file_contents, file_ptr, indent=2)
            else:
                print(file_contents, file=file_ptr)


class DAPIRequests:
    """Class to handle requests to the DAPI Server."""

    def __init__(
        self,
        dapi_server_config: DAPIServerConfig,
        all_files: OpenDAPIFileContents,
        changed_files: OpenDAPIFileContents,
        error_msg_handler: Optional[Callable[[str], None]] = None,
        error_exception_cls: Optional[Type[Exception]] = None,
    ):  # pylint: disable=too-many-arguments
        self.dapi_server_config = dapi_server_config
        self.all_files = all_files
        self.changed_files = changed_files
        self.error_msg_handler = error_msg_handler
        self.error_exception_cls = error_exception_cls or Exception

    def ask_dapi_server(self, request_path: str, payload: dict) -> DAPIServerResponse:
        """Ask the DAPI Server for something."""
        headers = {
            "Content-Type": "application/json",
            "X-DAPI-Server-API-Key": self.dapi_server_config.api_key,
        }

        response = requests.post(
            urljoin(self.dapi_server_config.server_host, request_path),
            headers=headers,
            json=payload,
            timeout=60,
        )

        # Server responds with a detailed error on 400, so only error when status > 400
        if response.status_code > 400:
            msg = (
                f"Something went wrong! API failure with {response.status_code} "
                f"for {request_path}"
            )
            if self.error_msg_handler:
                self.error_msg_handler(msg)
            raise self.error_exception_cls(msg)

        message = response.json()

        server_meta = message.get("server_meta", {})

        return DAPIServerResponse(
            status_code=response.status_code,
            server_meta=DAPIServerMeta(
                name=server_meta.get("name", "DAPI Server"),
                url=server_meta.get("url", "https://opendapi.org"),
                github_user_name=server_meta.get("github_user_name", "github-actions"),
                github_user_email=server_meta.get(
                    "github_user_email", "github-actions@github.com"
                ),
                logo_url=server_meta.get("logo_url"),
                suggestions_cta_url=server_meta.get("suggestions_cta_url"),
            ),
            errors=message.get("errors"),
            suggestions=message.get("suggestions"),
            info=message.get("info"),
            markdown=message.get("md"),
            text=message.get("text"),
        )

    def validate(
        self,
        notify_function: Optional[Callable[[int], None]] = None,
    ) -> DAPIServerResponse:
        """Validate OpenDAPI files with the DAPI Server."""
        all_files = self.all_files.for_server()
        changed_files = self.changed_files.for_server()
        batch_size = self.dapi_server_config.batch_size

        # First, we validate the non-dapi files
        resp = self.ask_dapi_server(
            "/v1/registry/validate",
            {
                "dapis": {},  # don't send dapi files
                "teams": all_files["teams"],
                "datastores": all_files["datastores"],
                "purposes": all_files["purposes"],
                "suggest_changes": self.dapi_server_config.suggest_changes,
            },
        )

        # Then we validate the dapi files in batches
        for dapi_chunk in _chunks(changed_files["dapis"], batch_size):
            for dapi_loc in dapi_chunk:
                all_files["dapis"].pop(dapi_loc, None)

            this_resp = self.ask_dapi_server(
                "/v1/registry/validate",
                {
                    "dapis": dapi_chunk,
                    "teams": {},
                    "datastores": {},
                    "purposes": {},
                    # Suggestions are needed only when the DAPI was touched in this PR
                    "suggest_changes": self.dapi_server_config.suggest_changes,
                },
            )
            resp = resp.merge(this_resp)

            if notify_function is not None:
                notify_function(batch_size)

        # Finally, we validate the remaining files without suggestions
        if all_files["dapis"]:
            resp = resp.merge(
                self.ask_dapi_server(
                    "/v1/registry/validate",
                    {
                        "dapis": all_files["dapis"],
                        "teams": {},
                        "datastores": {},
                        "purposes": {},
                        "suggest_changes": False,
                    },
                )
            )

            if notify_function is not None:
                notify_function(batch_size)

        return resp

    def analyze_impact(self) -> DAPIServerResponse:
        """Analyze the impact of changes on the DAPI Server."""
        changed_files = self.changed_files.for_server()
        return self.ask_dapi_server(
            "/v1/registry/impact",
            {
                "dapis": changed_files["dapis"],
                "teams": changed_files["teams"],
                "datastores": changed_files["datastores"],
                "purposes": changed_files["purposes"],
            },
        )

    def retrieve_stats(self) -> DAPIServerResponse:
        """Retrieve stats from the DAPI Server."""
        changed_files = self.changed_files.for_server()
        return self.ask_dapi_server(
            "/v1/registry/stats",
            {
                "dapis": changed_files["dapis"],
                "teams": changed_files["teams"],
                "datastores": changed_files["datastores"],
                "purposes": changed_files["purposes"],
            },
        )

    def register(self, commit_hash: str, source: str) -> Optional[DAPIServerResponse]:
        """Register OpenDAPI files with the DAPI Server."""
        all_files = self.all_files.for_server()
        return self.ask_dapi_server(
            "/v1/registry/register",
            {
                "dapis": all_files["dapis"],
                "teams": all_files["teams"],
                "datastores": all_files["datastores"],
                "purposes": all_files["purposes"],
                "commit_hash": commit_hash,
                "source": source,
                "unregister_missing_from_source": True,
            },
        )
