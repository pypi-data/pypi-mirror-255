from typing import Optional, List

from pydantic import BaseModel, TypeAdapter


class GAM(BaseModel):
    network_id: int


class XANDR(BaseModel):
    member_id: int
    aws_region: str


class ActivationChannels(BaseModel):
    gam: Optional[GAM] = None
    xandr: Optional[XANDR] = None


class Features(BaseModel):
    sso_data: bool = False
    enterprise: bool = False


class Taxonomies(BaseModel):
    name: str
    score: float


class ContentProvider(BaseModel):
    name: str
    section_prefixes: List[str]
    source_system: str | None = None
    content_id_extraction_query: str | None = None
    hardcoded_taxonomies: List[Taxonomies] | None = None


class TenantConfig(BaseModel):
    name: str
    activation_channels: ActivationChannels
    features: Features
    kropka_tenants: List[str]
    content_providers: List[ContentProvider]


def get_json_schema():
    adapter = TypeAdapter(List[TenantConfig])
    return adapter.json_schema()
