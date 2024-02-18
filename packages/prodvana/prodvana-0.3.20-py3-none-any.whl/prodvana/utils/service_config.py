import logging
from collections.abc import Set
from typing import NamedTuple

from prodvana.client import Client
from prodvana.proto.prodvana.desired_state import manager_pb2
from prodvana.proto.prodvana.service import service_manager_pb2


def get_target_image_tags_for_desired_state(
    client: Client, summary: manager_pb2.DesiredStateSummary
) -> Set[str]:
    class ServiceVersion(NamedTuple):
        application: str
        service: str
        version: str

    target_versions = set[ServiceVersion]()
    if summary.desired_state.HasField("service"):
        service = summary.desired_state.service
        for rc in service.release_channels:
            target_versions.add(
                ServiceVersion(
                    application=service.application,
                    service=service.service,
                    version=rc.versions[0].version,
                )
            )

    if summary.desired_state.HasField("service_group"):
        service_group = summary.desired_state.service_group
        for service in service_group.services:
            for rc in service.release_channels:
                target_versions.add(
                    ServiceVersion(
                        application=service.application,
                        service=service.service,
                        version=rc.versions[0].version,
                    )
                )

    images = set[str]()
    for version in target_versions:
        this_images = get_image_tags_from_service_version(
            client,
            application=version.application,
            service=version.service,
            version=version.version,
        )
        images.update(this_images)
    return images


def get_image_tags_from_service_version(
    client: Client, application: str, service: str, version: str
) -> Set[str]:
    logging.info(
        "Getting image tags for app=%s service=%s version=%s",
        application,
        service,
        version,
    )
    resp = client.service_manager.GetMaterializedConfig(
        service_manager_pb2.GetMaterializedConfigReq(
            application=application,
            service=service,
            version=version,
        )
    )

    images = set()
    for p in resp.compiled_service_instance_configs:
        for param_value in p.parameter_values:
            if param_value.docker_image_tag:
                images.add(param_value.docker_image_tag)
    return images
