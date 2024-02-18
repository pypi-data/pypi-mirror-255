import os
from typing import Callable

from prodvana.client import Client
from prodvana.proto.prodvana.desired_state.manager_pb2 import GetDesiredStateReq
from prodvana.proto.prodvana.service.service_config_pb2 import (
    CompiledServiceInstanceConfig,
)
from prodvana.proto.prodvana.service.service_manager_pb2 import (
    GetMaterializedConfigReq,
    GetServiceInstanceReq,
)


class InjectedVariables:
    PVN_APPLICATION = "PVN_APPLICATION"
    PVN_RELEASE_CHANNEL = "PVN_RELEASE_CHANNEL"
    PVN_SERVICE = "PVN_SERVICE"
    PVN_DESIRED_STATE_ID = "PVN_DESIRED_STATE_ID"


def must_get_env(key: str, msg: str) -> str:
    val = os.getenv(key)
    assert val, f"{key} not set. {msg}"
    return val


def service_config_protection(
    client: Client, check: Callable[[CompiledServiceInstanceConfig], None]
) -> None:
    """
    A protection that is meant to run at the service or convergence level.
    `check` is a function that should throw an exception if there is something wrong with the service configuration.
    At the service level, check is called with the current service configuration.
    At the convergence level, check is called with the incoming service configuration.
    """
    app = must_get_env(
        InjectedVariables.PVN_APPLICATION,
        "Only service-instance-level protections are supported",
    )
    rc = must_get_env(
        InjectedVariables.PVN_RELEASE_CHANNEL,
        "Only service-instance-level protections are supported",
    )
    svc = must_get_env(
        InjectedVariables.PVN_SERVICE,
        "Only service-instance-level protections are supported",
    )
    root_ds_id = os.getenv(InjectedVariables.PVN_DESIRED_STATE_ID)
    if root_ds_id:
        # convergence level
        ds_resp = client.desired_state_manager.GetDesiredState(
            GetDesiredStateReq(
                desired_state_id=root_ds_id,
            )
        )
        assert ds_resp.compiled_desired_state.service, "Desired State is not a Service"
        assert ds_resp.compiled_desired_state.service.application == app, (
            f"Desired State is for application {ds_resp.compiled_desired_state.service.application}, "
            f"but protection is for {app}"
        )
        assert ds_resp.compiled_desired_state.service.service == svc, (
            f"Desired State is for service {ds_resp.compiled_desired_state.service.service}, "
            f"but protection is for {svc}"
        )
        for inst in ds_resp.compiled_desired_state.service.release_channels:
            if inst.release_channel == rc:
                version = inst.versions[0].version
                cfg_resp = client.service_manager.GetMaterializedConfig(
                    GetMaterializedConfigReq(
                        application=app,
                        service=svc,
                        version=version,
                    )
                )
                for inst_cfg in cfg_resp.compiled_service_instance_configs:
                    if inst_cfg.release_channel == rc:
                        check(inst_cfg)
                        return
                assert (
                    False
                ), f"Could not find service instance cfg for {app}/{rc}/{svc} at version {version}"
        assert False, f"Could not find service instance {app}/{rc}/{svc}"

    # service-instance level
    inst_resp = client.service_manager.GetServiceInstance(
        GetServiceInstanceReq(
            application=app,
            release_channel=rc,
            service=svc,
        )
    )
    check(inst_resp.service_instance.config)
