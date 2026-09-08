from typing import Annotated, Literal

from pydantic import Field

from .common import ContractModel, JsonValue, NodeId, SourceRef, UtcDateTime

type NodeType = Literal[
    "application",
    "agent",
    "model",
    "tool",
    "mcp_server",
    "api",
    "database",
    "secret",
    "identity",
    "certificate",
    "crypto_algorithm",
    "external_service",
    "dataset",
]


class NodeBase(ContractModel):
    id: NodeId
    type: NodeType
    name: str
    source: SourceRef | None = None
    tags: set[str] = Field(default_factory=set)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class Application(NodeBase):
    type: Literal["application"] = "application"
    frameworks: list[str] = Field(default_factory=list)
    entrypoints: list[str] = Field(default_factory=list)
    runtime: str | None = None
    deployment: str | None = None


class Agent(NodeBase):
    type: Literal["agent"] = "agent"
    framework: str | None = None
    instructions_source: SourceRef | None = None
    model_ids: list[NodeId] = Field(default_factory=list)
    tool_ids: list[NodeId] = Field(default_factory=list)
    memory_enabled: bool = False
    delegation_enabled: bool = False


class Model(NodeBase):
    type: Literal["model"] = "model"
    provider: str
    model_name: str
    endpoint: str | None = None
    local: bool = False
    capabilities: set[str] = Field(default_factory=set)


class Tool(NodeBase):
    type: Literal["tool"] = "tool"
    description: str | None = None
    input_schema: dict[str, JsonValue] = Field(default_factory=dict)
    side_effects: bool = False
    permissions: set[str] = Field(default_factory=set)
    server_id: NodeId | None = None


class MCPServer(NodeBase):
    type: Literal["mcp_server"] = "mcp_server"
    transport: str
    command: str | None = None
    url: str | None = None
    auth_method: str | None = None
    tool_ids: list[NodeId] = Field(default_factory=list)


class API(NodeBase):
    type: Literal["api"] = "api"
    base_url: str | None = None
    protocol: str
    auth_method: str | None = None
    operations: list[str] = Field(default_factory=list)
    external: bool = False


class Database(NodeBase):
    type: Literal["database"] = "database"
    engine: str
    host: str | None = None
    database: str | None = None
    encrypted: bool | None = None
    credential_id: NodeId | None = None


class Secret(NodeBase):
    type: Literal["secret"] = "secret"
    kind: str
    location: str
    exposed_value: bool = False
    environment_name: str | None = None


class Identity(NodeBase):
    type: Literal["identity"] = "identity"
    kind: str
    principal: str | None = None
    provider: str | None = None
    scopes: set[str] = Field(default_factory=set)
    privileged: bool = False


class Certificate(NodeBase):
    type: Literal["certificate"] = "certificate"
    subject: str | None = None
    issuer: str | None = None
    serial_number: str | None = None
    not_before: UtcDateTime | None = None
    not_after: UtcDateTime | None = None
    signature_algorithm: str | None = None
    public_key_algorithm: str | None = None
    public_key_bits: int | None = Field(default=None, ge=1)
    file_path: str | None = None


class CryptoAlgorithm(NodeBase):
    type: Literal["crypto_algorithm"] = "crypto_algorithm"
    algorithm: str
    purpose: str
    key_size_bits: int | None = Field(default=None, ge=1)
    quantum_status: Literal["safe", "hybrid", "vulnerable", "unknown"]
    implementation: str | None = None


class ExternalService(NodeBase):
    type: Literal["external_service"] = "external_service"
    service_type: str
    host: str | None = None
    provider: str | None = None
    auth_method: str | None = None
    data_classes: set[str] = Field(default_factory=set)


class Dataset(NodeBase):
    type: Literal["dataset"] = "dataset"
    format: str | None = None
    location: str | None = None
    sensitivity: Literal[
        "public", "internal", "confidential", "restricted", "unknown"
    ] = "unknown"
    vectorized: bool = False


type Node = Annotated[
    Application
    | Agent
    | Model
    | Tool
    | MCPServer
    | API
    | Database
    | Secret
    | Identity
    | Certificate
    | CryptoAlgorithm
    | ExternalService
    | Dataset,
    Field(discriminator="type"),
]
