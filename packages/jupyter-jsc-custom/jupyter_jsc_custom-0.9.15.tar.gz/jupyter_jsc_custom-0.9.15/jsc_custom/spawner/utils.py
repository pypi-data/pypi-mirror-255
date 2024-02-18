import asyncio

from ..misc import get_custom_config

_general_spawn_event = asyncio.Event()
_user_spawner_events = {}


def get_general_spawn_event():
    global _general_spawn_event
    return _general_spawn_event


def get_user_spawner_events(user_id):
    global _user_spawner_events
    if user_id not in _user_spawner_events.keys():
        _user_spawner_events[user_id] = {
            "start": asyncio.Event(),
        }
    return _user_spawner_events[user_id]


def check_formdata_keys(data):
    keys = data.keys()
    custom_config = get_custom_config()
    systems_config = custom_config.get("systems")
    unicore_systems = []
    for system_name, sys_config in systems_config.items():
        backend_service = sys_config.get("backendService", "")
        if (
            custom_config.get("backendServices", {})
            .get(backend_service, {})
            .get("type", "")
            == "unicore"
        ):
            unicore_systems.append(system_name)
    required_keys = {"name", "profile", "system"}
    if data.get("system") in unicore_systems:
        required_keys = required_keys | {"account", "project", "partition"}
    allowed_keys = required_keys | {
        "image",
        "userdata_path",
        "flavor",
        "reservation",
        "nodes",
        "gpus",
        "runtime",
        "xserver",
        "userModules",
    }

    if not required_keys <= keys:
        raise KeyError(f"Keys must include {required_keys}, but got {keys}.")
    if not keys <= allowed_keys:
        raise KeyError(f"Got keys {keys}, but only {allowed_keys} are allowed.")


async def get_options_from_form(formdata):
    check_formdata_keys(formdata)

    custom_config = get_custom_config()
    systems_config = custom_config.get("systems")
    resources = custom_config.get("resources")

    def skip_resources(key, value):
        system = formdata.get("system")[0]
        partition = formdata.get("partition")[0]
        resource_keys = ["nodes", "gpus", "runtime"]
        if key in resource_keys:
            if partition in systems_config.get(system, {}).get(
                "interactivePartitions", []
            ):
                return True
            else:
                if key not in resources.get(system.upper()).get(partition).keys():
                    return True
        else:
            if value in ["undefined", "None"]:
                return True
        return False

    def runtime_update(key, value_list):
        if key == "resource_runtime":
            return int(value_list[0]) * 60
        return value_list[0]

    return {
        key: runtime_update(key, value)
        for key, value in formdata.items()
        if not skip_resources(key, value[0])
    }
