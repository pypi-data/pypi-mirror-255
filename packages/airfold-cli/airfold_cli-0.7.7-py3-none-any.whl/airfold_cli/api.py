import json
import os
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional, Union

import requests
import yaml
from airfold_common.format import ChFormat, Format
from airfold_common.models import FixResult, Issue
from airfold_common.project import ProjectFile, dump_yaml
from airfold_common.utils import uuid
from requests import JSONDecodeError, PreparedRequest, Response
from requests.auth import AuthBase
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)
from typing_extensions import Self

from airfold_cli.error import (
    APIError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    ProjectNotFoundError,
    UnauthorizedError,
)
from airfold_cli.models import (
    Config,
    OutputDataFormat,
    PipeInfo,
    PipeInfoStatus,
    Plan,
    ProjectProfile,
    SchemaFormat,
    SourceInfo,
    UserProfile,
)
from airfold_cli.utils import decode_short_uuid, load_config

AIRFOLD_API_URL = "https://api.airfold.co"

RETRY_TIMES = 3
WAIT_MIN_SECONDS = 0.5
WAIT_MAX_SECONDS = 5

ERRORS_TABLE = "_errors"


def api_retry(func):
    def wrapper(*args, **kwargs):
        return Retrying(
            retry=retry_if_exception_type(ConflictError),
            stop=stop_after_attempt(max_attempt_number=RETRY_TIMES),
            reraise=True,
            wait=wait_random_exponential(multiplier=1, min=WAIT_MIN_SECONDS, max=WAIT_MAX_SECONDS),
        )(func, *args, **kwargs)

    return wrapper


class BearerAuth(AuthBase):
    def __init__(self, token: str) -> None:
        self.token = token

    def __call__(self, req: PreparedRequest) -> PreparedRequest:
        req.headers["authorization"] = "Bearer " + self.token
        return req


class AirfoldApi:
    def __init__(self, api_key: str = "", endpoint: str = ""):
        self.auth: AuthBase = BearerAuth(api_key)
        self.endpoint: str = os.environ.get("AIRFOLD_API_URL", endpoint or AIRFOLD_API_URL)
        self._identity: Union[UserProfile, ProjectProfile] | None = None

    @classmethod
    def from_config(cls, _config: Config | None = None) -> Self:
        config: Config = _config or load_config()
        return cls(api_key=config.key, endpoint=config.endpoint)

    def _get_identity(self) -> Response:
        return requests.get(self.endpoint + "/v1/auth/identity", auth=self.auth)

    @api_retry
    def get_identity(self) -> Union[ProjectProfile, UserProfile]:
        res = self._get_identity()
        if res.ok:
            json_data = res.json()
            if json_data.get("user"):
                return UserProfile(**json_data.get("user"))
            else:
                return ProjectProfile(**json_data)

        raise self._resp_to_err(res)

    @property
    def identity(self) -> Union[ProjectProfile, UserProfile]:
        if not self._identity:
            self._identity = self.get_identity()
        return self._identity  # type: ignore

    def get_project_profile(self) -> ProjectProfile:
        if isinstance(self.identity, UserProfile):
            raise APIError("User-scoped API key used, please use workspace-scoped key")
        return self.identity

    def get_org_id(self) -> str:
        if isinstance(self.identity, UserProfile):
            return self.identity.organizations[0].id
        return self.identity.org_id

    @api_retry
    def list_projects(self, org_id: Optional[str] = None) -> Response:
        return requests.get(self.endpoint + f"/v1/{org_id or self.get_org_id()}/projects", auth=self.auth)

    @staticmethod
    def parse_error_response(res: Response) -> str:
        try:
            data: Dict = res.json()
            if data.get("error"):
                return data["error"]
            return res.reason
        except JSONDecodeError:
            pass
        if len(res.text) > 0 and res.status_code == 500:
            return res.text
        return res.reason

    def _resp_to_err(self, res: Response) -> APIError:
        desc = self.parse_error_response(res)
        if res.status_code == 401:
            return UnauthorizedError(desc)
        elif res.status_code == 403:
            return ForbiddenError(desc)
        elif res.status_code == 404:
            return ProjectNotFoundError(desc)
        elif res.status_code == 409:
            return ConflictError(desc)
        elif res.status_code >= 500:
            return InternalServerError(desc)
        return APIError(desc)

    def _push(
        self,
        data: str,
        dry_run: bool,
        force: bool,
    ) -> Response:
        url = self.endpoint + f"/v1/push"
        params = {"dry_run": dry_run, "force": force}
        headers = {"Content-Type": "application/yaml"}
        response = requests.post(url, data=data, params=params, headers=headers, auth=self.auth)

        return response

    @api_retry
    def push(
        self,
        data: str,
        dry_run: bool = False,
        force: bool = False,
    ) -> Plan:
        res = self._push(data, dry_run, force)
        if res.ok:
            return list(res.json())
        raise self._resp_to_err(res)

    def _pull(
        self,
    ) -> Response:
        return requests.get(self.endpoint + f"/v1/pull", auth=self.auth)

    @api_retry
    def pull(
        self,
    ) -> List[ProjectFile]:
        res = self._pull()
        if res.ok:
            return [ProjectFile(name=data["name"], data=data, pulled=True) for data in res.json()]  # type: ignore
        raise self._resp_to_err(res)

    def _graph(
        self,
    ) -> Response:
        return requests.get(self.endpoint + f"/v1/graph", auth=self.auth)

    @api_retry
    def graph(
        self,
    ) -> Dict:
        res = self._graph()
        if res.ok:
            return res.json()
        raise self._resp_to_err(res)

    def _pipe_delete(self, name: str, dry_run: bool, force: bool) -> Response:
        params = {"dry_run": dry_run, "force": force}
        return requests.delete(
            self.endpoint + f"/v1/pipes/{name}",
            params=params,
            auth=self.auth,
        )

    @api_retry
    def pipe_delete(self, name: str, dry_run: bool = False, force: bool = False) -> Plan:
        res = self._pipe_delete(name, dry_run, force)
        if res.ok:
            return list(res.json())
        raise self._resp_to_err(res)

    def _source_delete(self, name: str, dry_run: bool, force: bool) -> Response:
        params = {"dry_run": dry_run, "force": force}
        return requests.delete(
            self.endpoint + f"/v1/sources/{name}",
            params=params,
            auth=self.auth,
        )

    @api_retry
    def source_delete(self, name: str, dry_run: bool = False, force: bool = False) -> Plan:
        res = self._source_delete(name, dry_run, force)
        if res.ok:
            return list(res.json())
        raise self._resp_to_err(res)

    @staticmethod
    def _parse_data(res: Response, format: OutputDataFormat) -> List[Dict]:
        if format == OutputDataFormat.JSON:
            return [res.json()]

        ndjson_lines = res.text.split("\n")
        parsed_json = []
        for line in ndjson_lines:
            if line:
                json_object = json.loads(line)
                parsed_json.append(json_object)

        return parsed_json

    @staticmethod
    def _make_pipe_name_format(name: str, output_format: OutputDataFormat) -> str:
        return f"{name}.{output_format}"

    def _pipe_get_data(
        self, name: str, output_format: OutputDataFormat, params: Optional[dict[str, str]] = None
    ) -> Response:
        return requests.get(
            self.endpoint + f"/v1/pipes/{self._make_pipe_name_format(name, output_format)}",
            auth=self.auth,
            params=params,
        )

    @api_retry
    def pipe_get_data(
        self,
        name: str,
        output_format: OutputDataFormat = OutputDataFormat.NDJSON,
        params: Optional[dict[str, str]] = None,
    ) -> List[Dict]:
        res = self._pipe_get_data(name, output_format=output_format, params=params)
        if res.ok:
            return self._parse_data(res, output_format)
        raise self._resp_to_err(res)

    def _pipe_run(self, name: str, pipe_schema: dict[str, Any], output_format: OutputDataFormat) -> Response:
        headers = {"Content-Type": "application/yaml"}
        return requests.post(
            self.endpoint + f"/v1/run/{self._make_pipe_name_format(name, output_format)}",
            headers=headers,
            data=dump_yaml(pipe_schema),
            auth=self.auth,
        )

    @api_retry
    def pipe_run(
        self, name: str, pipe_schema: dict[str, Any], output_format: OutputDataFormat = OutputDataFormat.NDJSON
    ) -> List[Dict]:
        res = self._pipe_run(name, pipe_schema, output_format)
        if res.ok:
            return self._parse_data(res, output_format)
        raise self._resp_to_err(res)

    @api_retry
    def sql_run(self, query: str, output_format: OutputDataFormat = OutputDataFormat.NDJSON) -> List[Dict]:
        res = self._pipe_run(
            f"pipe_{uuid()}",
            {
                "nodes": [{"runner": {"sql": query}}],
            },
            output_format,
        )
        if res.ok:
            return self._parse_data(res, output_format)
        raise self._resp_to_err(res)

    def _get_storage_db_name(self) -> str:
        return f"s-{decode_short_uuid(self.get_project_profile().project_id)}"

    def list_pipes(self) -> List[PipeInfo]:
        files = self.pull()

        formatter: Format = ChFormat()
        pipes: list[ProjectFile] = list(filter(lambda f: formatter.is_pipe(f.data), files))
        if not pipes:
            return []

        event_types: list[str] = ["create", "update"]
        sql_template = dedent(
            """
            SELECT JSONExtractString(message, 'name') as name, type, min(timestamp) as earliest, max(timestamp) as latest FROM `{storage_db_name}`.`event`
                WHERE name in ({pipe_names}) AND type IN ('create', 'update') AND result='ok'
                GROUP BY name, type
                ORDER BY name, type LIMIT {max_results}
        """
        )
        events_data = self.sql_run(
            sql_template.format(
                max_results=len(pipes) * len(event_types),
                storage_db_name=self._get_storage_db_name(),
                pipe_names=", ".join([f"'{pipe.name}'" for pipe in pipes]),
            )
        )

        pipes_info: list[PipeInfo] = []
        for pipe in pipes:
            pipe_info_dict: dict = {"name": pipe.name}

            if pipe.data.get("publish"):
                pipe_info_dict["status"] = PipeInfoStatus.PUBLISHED
            elif pipe.data.get("to"):
                pipe_info_dict["status"] = PipeInfoStatus.MATERIALIZED
            else:
                pipe_info_dict["status"] = PipeInfoStatus.DRAFT

            pipe_events: list[dict] = list(filter(lambda e: e["name"] == pipe.name, events_data))
            if pipe_events:
                pipe_info_dict["created"] = min([e["earliest"] for e in pipe_events])
                pipe_info_dict["updated"] = max([e["latest"] for e in pipe_events])

            pipes_info.append(PipeInfo(**pipe_info_dict))

        return pipes_info

    def list_sources(self) -> List[SourceInfo]:
        files = self.pull()

        formatter: Format = ChFormat()
        sources: list[ProjectFile] = list(filter(lambda f: formatter.is_source(f.data), files))
        if not sources:
            return []

        metrics: dict[str, Any] = self.get_metrics(names=[f.name for f in sources])

        sources_info: list[SourceInfo] = []
        for source in sources:
            sm: Optional[dict] = metrics.get(source.name)
            if not sm:
                raise APIError(f"Failed to get metrics for source {source.name}")

            sources_info.append(
                SourceInfo(
                    **{
                        "name": source.name,
                        "created": sm.get("created", None),
                        "updated": sm.get("updated", None),
                        "rows": sm.get("rows", 0),
                        "bytes": sm.get("bytes_on_disk", 0),
                        "errors": sm.get("errors", 0),
                    }
                )
            )

        return sources_info

    def _rename(self, url_path: str, new_name: str, dry_run: bool, force: bool) -> Response:
        params: dict[str, bool | str] = {"new_name": new_name, "dry_run": dry_run, "force": force}
        return requests.post(
            self.endpoint + url_path,
            params=params,
            auth=self.auth,
        )

    @api_retry
    def rename_source(self, name: str, new_name: str, dry_run: bool = False, force: bool = False) -> Plan:
        res = self._rename(f"/v1/sources/{name}", new_name, dry_run, force)
        if res.ok:
            return list(res.json())
        raise self._resp_to_err(res)

    @api_retry
    def rename_pipe(self, name: str, new_name: str, dry_run: bool = False, force: bool = False) -> Plan:
        res = self._rename(f"/v1/pipes/{name}", new_name, dry_run, force)
        if res.ok:
            return list(res.json())
        raise self._resp_to_err(res)

    def _send_events(
        self,
        src_name: str,
        data: str,
    ) -> Response:
        url = self.endpoint + f"/v1/events/{src_name}"
        response = requests.post(url, data=data, auth=self.auth)

        return response

    def send_events(self, src_name: str, events: list[str]) -> str:
        ndjson = "\n".join(events)
        res = self._send_events(src_name, ndjson)
        if res.ok:
            return "ok"
        raise self._resp_to_err(res)

    def _doctor_run(self, checks: Optional[list[str]] = None, fix: bool = False) -> Response:
        params: dict[str, Any] = {"fix": fix}
        if checks:
            params["checks"] = ",".join(checks)
        return requests.post(self.endpoint + f"/v1/doctor", params=params, auth=self.auth)

    def _doctor_list_checks(self) -> Response:
        return requests.get(self.endpoint + f"/v1/doctor", auth=self.auth)

    @api_retry
    def doctor_run(self, checks: Optional[list[str]] = None, fix: bool = False) -> tuple[list[Issue], list[FixResult]]:
        res = self._doctor_run(checks, fix)
        if res.ok:
            json_data = res.json()
            fix_results: list[FixResult] = []
            issues: list[Issue] = []

            if fix:
                fix_results = [FixResult(**fix_result) for fix_result in json_data]
                issues = [fix_result.issue for fix_result in fix_results]
            else:
                issues = [Issue(**issue) for issue in json_data]
            return issues, fix_results
        raise self._resp_to_err(res)

    @api_retry
    def doctor_list_checks(self) -> list[str]:
        res = self._doctor_list_checks()
        if res.ok:
            return res.json()
        raise self._resp_to_err(res)

    @staticmethod
    def _schema_format_to_mime_type(schema_format: SchemaFormat) -> str:
        if schema_format == SchemaFormat.YAML:
            return "application/yaml"
        elif schema_format == SchemaFormat.JSON:
            return "application/json"

    def _infer_schema(self, data: str, schema_format: SchemaFormat) -> Response:
        url = self.endpoint + f"/v1/schemas"
        headers = {
            "Content-Type": "application/x-ndjson",
            "Accept": self._schema_format_to_mime_type(schema_format),
        }
        response = requests.post(
            url,
            data=data,
            headers=headers,
            auth=self.auth,
        )

        return response

    @api_retry
    def infer_schema(self, events: list[str], schema_format: SchemaFormat = SchemaFormat.YAML) -> dict[str, Any]:
        ndjson = "\n".join(events)
        res = self._infer_schema(ndjson, schema_format)
        if res.ok:
            if schema_format == SchemaFormat.JSON:
                return res.json()
            else:
                return yaml.safe_load(res.text)

        raise self._resp_to_err(res)

    def _get_metrics(
        self,
        names: Optional[list[str]],
        from_dt: Optional[datetime],
        to_dt: Optional[datetime],
        interval_s: Optional[int],
    ) -> Response:
        params: dict[str, Any] = {}
        if names:
            params["name"] = names
        if from_dt:
            params["from_dt"] = from_dt.isoformat()
        if to_dt:
            params["to_dt"] = to_dt.isoformat()
        if interval_s:
            params["interval_s"] = interval_s

        return requests.get(self.endpoint + f"/v1/metrics", params=params, auth=self.auth)

    @api_retry
    def get_metrics(
        self,
        names: Optional[list[str]] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        interval_s: Optional[int] = None,
    ) -> dict[str, Any]:
        res = self._get_metrics(names, from_dt, to_dt, interval_s)
        if res.ok:
            return res.json()
        raise self._resp_to_err(res)
