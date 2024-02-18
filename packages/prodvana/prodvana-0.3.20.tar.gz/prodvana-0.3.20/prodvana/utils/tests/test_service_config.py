import mock

from prodvana.client import Client
from prodvana.proto.prodvana.common_config import parameters_pb2, program_pb2
from prodvana.proto.prodvana.desired_state import manager_pb2
from prodvana.proto.prodvana.desired_state.model import desired_state_pb2
from prodvana.proto.prodvana.service import (
    service_config_pb2,
    service_manager_pb2,
    service_manager_pb2_grpc,
)
from prodvana.utils.service_config import get_target_image_tags_for_desired_state


def test_get_target_commits_with_image_urls() -> None:
    def fake_get_service_config(
        req: service_manager_pb2.GetMaterializedConfigReq,
    ) -> service_manager_pb2.GetMaterializedConfigResp:
        return service_manager_pb2.GetMaterializedConfigResp(
            compiled_service_instance_configs=[
                service_config_pb2.CompiledServiceInstanceConfig(
                    parameter_values=[
                        parameters_pb2.ParameterValue(
                            docker_image_tag={
                                "pvn-service-1": "1",
                                "pvn-service-2": "2",
                            }[req.version],
                        ),
                    ],
                    parameters=[
                        parameters_pb2.ParameterDefinition(
                            docker_image=parameters_pb2.DockerImageParameterDefinition(
                                default_tag="foo",
                                image_registry_info=program_pb2.ImageRegistryInfo(
                                    container_registry="registry",
                                    image_repository="repo",
                                ),
                            ),
                        ),
                    ],
                ),
            ]
        )

    client = mock.Mock(spec=Client)
    client.service_manager = mock.Mock(spec=service_manager_pb2_grpc.ServiceManagerStub)
    client.service_manager.GetMaterializedConfig = mock.Mock()
    client.service_manager.GetMaterializedConfig.side_effect = fake_get_service_config

    images = get_target_image_tags_for_desired_state(
        client,
        manager_pb2.DesiredStateSummary(
            desired_state=desired_state_pb2.State(
                service=desired_state_pb2.ServiceState(
                    release_channels=[
                        desired_state_pb2.ServiceInstanceState(
                            versions=[
                                desired_state_pb2.Version(
                                    version="pvn-service-1",
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        ),
    )
    assert images == set(["1"])

    images = get_target_image_tags_for_desired_state(
        client,
        manager_pb2.DesiredStateSummary(
            desired_state=desired_state_pb2.State(
                service=desired_state_pb2.ServiceState(
                    release_channels=[
                        desired_state_pb2.ServiceInstanceState(
                            release_channel="staging",
                            versions=[
                                desired_state_pb2.Version(
                                    version="pvn-service-2",
                                ),
                            ],
                        ),
                        desired_state_pb2.ServiceInstanceState(
                            release_channel="production",
                            versions=[
                                desired_state_pb2.Version(
                                    version="pvn-service-1",
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        ),
    )
    assert images == set(
        [
            "2",
            "1",
        ]
    )
