import re
from dataclasses import dataclass
from pathlib import Path

from lattence.graph import Application, ExternalService, SourceRef

from .inventory import ProjectFile


@dataclass(frozen=True)
class InfrastructureDiscovery:
    applications: tuple[Application, ...]
    services: tuple[ExternalService, ...]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _application(path: str, name: str, deployment: str) -> Application:
    return Application(
        id=f"application:deployment:{_slug(path)}",
        name=name,
        source=SourceRef(path=path),
        entrypoints=[path],
        deployment=deployment,
    )


def _service(path: str, provider: str, service_type: str) -> ExternalService:
    return ExternalService(
        id=f"external_service:{service_type}:{_slug(path)}",
        name=f"{provider} {service_type}",
        source=SourceRef(path=path),
        service_type=service_type,
        provider=provider,
    )


def _is_kubernetes(path: str, source: str) -> bool:
    return Path(path).suffix.lower() in {".yaml", ".yml"} and bool(
        re.search(r"(?m)^apiVersion\s*:\s*[^\s]+", source)
        and re.search(
            r"(?m)^kind\s*:\s*(?:Deployment|StatefulSet|DaemonSet|Pod|Job)\s*$",
            source,
        )
    )


def discover_infrastructure(
    root: Path, files: tuple[ProjectFile, ...]
) -> InfrastructureDiscovery:
    applications: list[Application] = []
    services: list[ExternalService] = []
    for project_file in files:
        path = project_file.path
        name = Path(path).name
        try:
            source = (root / path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            source = ""

        if name == "Dockerfile" or name.startswith("Dockerfile."):
            applications.append(_application(path, "Container image", "container"))
        elif name in {
            "compose.yaml",
            "compose.yml",
            "docker-compose.yaml",
            "docker-compose.yml",
        }:
            applications.append(
                _application(path, "Container composition", "container")
            )
        elif _is_kubernetes(path, source):
            applications.append(_application(path, "Cluster workload", "kubernetes"))

        if Path(path).suffix.lower() == ".tf":
            services.append(_service(path, "terraform", "infrastructure"))
        if path.startswith(".github/workflows/") and Path(path).suffix.lower() in {
            ".yaml",
            ".yml",
        }:
            services.append(_service(path, "github-actions", "continuous-integration"))
        elif name == ".gitlab-ci.yml":
            services.append(_service(path, "gitlab-ci", "continuous-integration"))

    unique_applications = {item.id: item for item in applications}
    unique_services = {item.id: item for item in services}
    return InfrastructureDiscovery(
        tuple(unique_applications[key] for key in sorted(unique_applications)),
        tuple(unique_services[key] for key in sorted(unique_services)),
    )
