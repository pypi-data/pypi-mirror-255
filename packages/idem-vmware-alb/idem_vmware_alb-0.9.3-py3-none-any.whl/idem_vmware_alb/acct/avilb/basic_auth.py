import re
import warnings
from typing import Any
from typing import Dict

from idem_vmware_alb.tool.avilb.apisession import ApiSession

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

BASE_URL = "/api"


async def gather(hub, profiles) -> Dict[str, Any]:
    """
    Generate token with basic auth

    Example:
    .. code-block:: yaml

        avilb:
          profile_name:
            username: "admin"
            password: "password"
            endpoint_url: 'https://10.65.11.14/'
            tenant: "admin"

    """

    sub_profiles = {}
    for (
        profile,
        ctx,
    ) in profiles.get("avilb", {}).items():
        endpoint_url = ctx.get("endpoint_url")

        if not re.search(BASE_URL, endpoint_url):
            endpoint_url = "".join((endpoint_url.rstrip("/"), BASE_URL))
        ctx["endpoint_url"] = endpoint_url
        # The plugin_version is hardcoded for now , but will change once the autogeneration sync gets done
        plugin_version = "30.2.1"
        # Create a session using APISession to fetch CSRFToken , sessionid to avoid basic authentication
        api = ApiSession.get_session(
            ctx.get("endpoint_url").rstrip("/api"),
            ctx.get("username"),
            ctx.get("password"),
            verify=False,
        )
        if api:
            login = await hub.tool.avilb.session.request(
                ctx,
                method="post",
                path="/login",
                data={"username": ctx.get("username"), "password": ctx.get("password")},
            )

            if login["status"] == 200:
                api_version = login["ret"]["version"]["Version"]
                if api_version > plugin_version:
                    api_version = plugin_version
            if api.cookies:
                sess = api.cookies["sessionid"]
                csrftoken = api.cookies["csrftoken"]
            sub_profiles[profile] = dict(
                endpoint_url=endpoint_url,
                headers={
                    "Referer": endpoint_url.rstrip("api"),
                    "X-Avi-Version": api_version,
                    "X-CSRFToken": csrftoken,
                    "Cookie": f"csrftoken={csrftoken};avi-sessionid={sess}; sessionid={sess}",
                },
            )
            ApiSession.reset_session(api)
    return sub_profiles
