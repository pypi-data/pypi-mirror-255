import copy
from re import sub

from dict_tools.data import NamespaceDict


def snake_case(s):
    return "_".join(
        sub(
            "([A-Z][a-z]+)", r" \1", sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()


def run(hub, ctx):
    # This customization is used to create an additional folder "alb" to have a 5 segment function reference call
    nsx_resources = [
        "Cloud",
        "VirtualService",
        "Pool",
        "HealthMonitor",
        "VsVip",
        "ApplicationProfile",
        "NetworkProfile",
        "ApplicationPersistenceProfile",
        "SSLProfile",
        "ServiceEngineGroup",
    ]
    updated_cloud_spec: NamespaceDict = copy.deepcopy(ctx.cloud_spec)
    for name, plugin in ctx.cloud_spec.get("plugins").items():
        new_plugin = updated_cloud_spec.get("plugins").pop(name)
        for k in nsx_resources:
            if k.lower() == name:
                new_name = snake_case(k)
                break
        new_resource_name = new_name
        applications = ["virtual_service", "vs_vip", "pool"]
        profiles = [
            "application_persistence_profile",
            "application_profile",
            "network_profile",
            "health_monitor",
        ]
        infrastructure = ["cloud", "service_engine_group"]
        if new_resource_name in applications:
            new_resource_name = "applications." + new_resource_name
        elif new_resource_name in profiles:
            new_resource_name = "profiles." + new_resource_name
        elif new_resource_name in infrastructure:
            new_resource_name = "infrastructure." + new_resource_name
        else:
            new_resource_name = "security." + new_resource_name
        for func_name, func_data in new_plugin.get("functions").items():
            func_data.get("hardcoded", {})["resource_name"] = new_resource_name

            if new_resource_name == "applications.vs_vip":
                for method in new_plugin.get("functions").keys():
                    params = new_plugin.get("functions").get(method).get("params")
                    if params != None and params.get("vip") != None:
                        params["vip"]["member"]["params"]["vip_id"].update(
                            {"required": False}
                        )
            for method in new_plugin.get("functions").keys():
                if method == "get":
                    params = new_plugin.get("functions").get(method).get("params")
                    if params != None and params.get("X-Avi-Tenant") != None:
                        params["tenant_ref"] = params.pop("X-Avi-Tenant")
        updated_cloud_spec["plugins"][new_resource_name] = new_plugin
    ctx.cloud_spec = updated_cloud_spec
