from pathlib import Path

from lattence.discovery import discover_infrastructure, inventory_project


def test_discovers_deployment_infrastructure_and_ci_files(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
    (tmp_path / "cluster.yaml").write_text(
        "apiVersion: apps/v1\nkind: Deployment\n", encoding="utf-8"
    )
    (tmp_path / "main.tf").write_text(
        'resource "local_file" "example" {}\n', encoding="utf-8"
    )
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "checks.yml").write_text("jobs: {}\n", encoding="utf-8")

    result = discover_infrastructure(tmp_path, inventory_project(tmp_path).files)

    assert {item.deployment for item in result.applications} == {
        "container",
        "kubernetes",
    }
    assert {item.service_type for item in result.services} == {
        "continuous-integration",
        "infrastructure",
    }
    assert all(item.source is not None for item in result.applications)
    assert all(item.source is not None for item in result.services)


def test_plain_yaml_is_not_a_cluster_workload(tmp_path: Path) -> None:
    (tmp_path / "config.yml").write_text("name: fixture\n", encoding="utf-8")

    result = discover_infrastructure(tmp_path, inventory_project(tmp_path).files)

    assert result.applications == ()
    assert result.services == ()
