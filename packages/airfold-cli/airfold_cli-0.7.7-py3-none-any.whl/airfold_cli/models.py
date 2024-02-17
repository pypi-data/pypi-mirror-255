from datetime import datetime
from enum import Enum
from typing import List, Optional

import humanize
from pydantic import BaseModel, Field


class Project(BaseModel, frozen=True):
    id: str
    name: str


class Organization(BaseModel):
    id: str
    name: str

    class Config:
        allow_population_by_field_name = True


class Permission(BaseModel):
    Effect: str
    Action: str
    Resource: str


class UserPermissions(BaseModel):
    org_id: str = Field(..., alias="orgId")
    user_perms: list[Permission] = Field(..., alias="userPerms")
    roles: list[str]

    class Config:
        allow_population_by_field_name = True


class UserProfile(BaseModel):
    id: str
    fname: str
    lname: str
    email: str
    avatar: Optional[str] = None
    full_name: str = Field(..., alias="fullName")
    organizations: List[Organization]
    permissions: List[UserPermissions]

    class Config:
        allow_population_by_field_name = True


class ProjectProfile(BaseModel):
    project_id: str = Field(..., alias="projectId")
    org_id: str = Field(..., alias="orgId")
    permissions: List[Permission]

    class Config:
        allow_population_by_field_name = True


class Config(BaseModel, frozen=True):
    endpoint: str
    org_id: str
    proj_id: str
    key: str


class OutputDataFormat(str, Enum):
    JSON = "json"
    NDJSON = "ndjson"

    def __str__(self):
        return self.value


Plan = list[dict]


class NamedParam(BaseModel):
    name: str
    value: str


class SchemaFormat(str, Enum):
    YAML = "yaml"
    JSON = "json"

    def __str__(self):
        return self.value


class PipeInfoStatus(str, Enum):
    PUBLISHED = "published"
    DRAFT = "draft"
    MATERIALIZED = "materialized"

    def __str__(self):
        return self.value


class Info(BaseModel):
    name: str
    created: datetime
    updated: datetime

    def dict(self, **kwargs):
        humanize_args: bool = kwargs.pop("humanize", False)
        output = super().dict(**kwargs)
        for k, v in output.items():
            if isinstance(v, datetime):
                output[k] = humanize.naturaltime(datetime.now() - v) if humanize_args else v.isoformat()
            if k.find("bytes") != -1:
                output[k] = humanize.naturalsize(v) if humanize_args else v
        return output


class PipeInfo(Info):
    status: PipeInfoStatus


class SourceInfo(Info):
    rows: int
    bytes: int
    errors: int
