import re
from typing import Any
from typing import Dict


async def get_appended_prefix(
    hub,
    ctx,
    data: dict = None,
) -> Dict[str, Any]:
    if data:
        if isinstance(data, dict):
            for k, v in data.items():
                if k and isinstance(v, (dict, list)):
                    await hub.tool.avilb.utils.get_appended_prefix(ctx, data=v)
                if ("_ref" in k and isinstance(v, str)) and (
                    ("name=" not in v) and ("/api" not in v)
                ):
                    obj_prefix = k.split("_ref")[0]
                    if re.search("_", obj_prefix):
                        obj_prefix = obj_prefix.replace("_", "")
                    DIFF_ENDPOINTS = {
                        "vrf": "vrfcontext",
                        "botpolicy": "botdetectionpolicy",
                    }
                    if obj_prefix in DIFF_ENDPOINTS.keys():
                        obj_prefix = DIFF_ENDPOINTS[obj_prefix]
                    new_value = await hub.tool.avilb.session.append_prefix(
                        ctx, obj_prefix=obj_prefix, value=v
                    )
                    data.update({k: new_value})
                if "_ref" in k and isinstance(v, list):
                    new_value_list = []
                    for index in range(len(data[k])):
                        if ("name=" not in data[k][index]) and (
                            "/api" not in data[k][index]
                        ):
                            obj_prefix = k.split("_refs")[0]
                            new_value = await hub.tool.avilb.session.append_prefix(
                                ctx, obj_prefix=obj_prefix, value=data[k][index]
                            )
                            new_value_list.append(new_value)
                    if len(new_value_list) != 0:
                        data.update({k: new_value_list})
        elif isinstance(data, list):
            for item in data:
                await hub.tool.avilb.utils.get_appended_prefix(ctx, data=item)
    return data
