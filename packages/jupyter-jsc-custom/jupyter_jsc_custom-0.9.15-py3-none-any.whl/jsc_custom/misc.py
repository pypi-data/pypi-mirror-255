import asyncio
import copy
import logging
import os
import socket
import sys
import time

import yaml
from jsonformatter import JsonFormatter
from jupyterhub.app import app_log

logged_logger_name = os.environ.get("LOGGER_NAME", "JupyterHub")
logger_name = "JupyterHub"

_custom_config_cache = {}
_custom_config_last_update = 0
_custom_config_file = os.environ.get("CUSTOM_CONFIG_PATH")

_logging_cache = {}

log = logging.getLogger("JupyterHub")
background_tasks = []


def get_logging_config():
    global _logging_cache
    return _logging_cache


# Custom Config comes from a ConfigMap in Kubernetes
def get_custom_config():
    global _custom_config_cache
    global _custom_config_last_update
    global _logging_cache

    # Only update custom_config, if it has changed on disk
    try:
        last_change = os.path.getmtime(_custom_config_file)
        if last_change > _custom_config_last_update:
            app_log.debug("Load custom config file.")
            with open(_custom_config_file, "r") as f:
                ret = yaml.full_load(f)
            _custom_config_last_update = last_change
            _custom_config_cache = ret

            if _custom_config_cache.get("logging", {}) != _logging_cache:
                _logging_cache = _custom_config_cache.get("logging", {})
                app_log.debug("Update Logger")
                update_extra_handlers()

    except:
        app_log.exception("Could not load custom config file")
    else:
        return _custom_config_cache


def filter_custom_config_by_auth_state_keys():
    custom_config = get_custom_config()    
    custom_config_auth_state_keys = custom_config.get(
        "authStateKeys",
        [
            "services",
            "userModules",
            "announcement",
            "groups",
            "systems",
            "incidentCheck"
        ],
    )
    
    filtered_config = {}
    for key in custom_config_auth_state_keys:
        if key in custom_config.keys():
            filtered_config[key] = custom_config[key]
    return filtered_config


_reservations_cache = {}
_last_change_reservation = 0


def get_reservations():
    global _reservations_cache
    return _reservations_cache


async def update_reservations():
    # Update reservations every n seconds
    import copy
    import re
    from subprocess import check_output
    from subprocess import STDOUT

    global _reservations_cache
    global _last_change_reservation
    reservation_key = "/mnt/reservation_key/ssh-privatekey"
    regex_pattern = "([\\S]+)=([\\S]+)"

    while True:
        log.info("Run ReservationCheck")
        config = get_custom_config()
        reservation_timeout = config.get("reservationCheck", {}).get("timeout", 3)
        try:
            previous_dict = _reservations_cache.copy()
        except:
            previous_dict = {}
        output_dict = {}

        for system, infos in (
            config.get("reservationCheck", {}).get("systems", {}).items()
        ):
            if system not in output_dict.keys():
                output_dict[system] = []
            li = [
                "ssh",
                "-i",
                reservation_key,
                "-oLogLevel=ERROR",
                "-oStrictHostKeyChecking=no",
                "-oUserKnownHostsFile=/dev/null",
                "{}@{}".format(infos.get("user", "ljupyter"), infos.get("host", "")),
                "-T",
            ]

            def null_to_empty(key, value, infos):
                if key in infos.get(
                    "nullReplaceKeys", ["Accounts", "Users", "PartitionName"]
                ) and value == infos.get("nullString", "(null)"):
                    return ""
                return value

            try:
                log.debug(f"ReservationCheck - Run {' '.join(li)}")
                output = (
                    check_output(li, stderr=STDOUT, timeout=reservation_timeout)
                    .decode("utf8")
                    .rstrip()
                )
                system_list_n = output.split("\n\n")
                system_list = [x.replace("\n", "") for x in system_list_n]
            except:
                log.exception(
                    f"ReservationCheck - Could not check reservation for {system}. Use previous values."
                )
                if system in previous_dict.keys():
                    output_dict[system] = previous_dict[system]
            else:
                for reservation_string in system_list:
                    reservation_key_values_list = re.findall(
                        regex_pattern, reservation_string
                    )
                    reservation_key_values_dict = {
                        x[0]: null_to_empty(x[0], x[1], infos)
                        for x in reservation_key_values_list
                    }
                    if "ReservationName" in reservation_key_values_dict.keys():
                        output_dict[system].append(
                            copy.deepcopy(reservation_key_values_dict)
                        )

        _reservations_cache = output_dict
        sleep_timer = config.get("reservationCheck", {}).get("interval", 300)
        _last_change_reservation = time.time()
        await asyncio.sleep(sleep_timer)


background_tasks.append(asyncio.create_task(update_reservations()))

_incidents_cache = {}
_last_change_incidents = 0


def get_incidents():
    global _incidents_cache
    return _incidents_cache


async def update_incidents():
    # Update incidents every n seconds
    import shutil

    import requests
    from dateutil import parser

    global _incidents_cache
    global _last_change_incidents

    static_dir = "/mnt/shared-data/share/jupyterhub/static/images/footer"

    while True:
        log.info("Run IncidentCheck")

        def update_status_image(system, health):
            image_path = f"{static_dir}/systems/{system.lower()}.svg"
            # 0: Healthy, 10: Annotation, 20: Minor, 30: Medium, 40: Major, 50: Critical
            template_path = f"{static_dir}/templates/{health}.svg"
            try:
                log.debug(f"IncidentCheck - Copy {template_path} to {image_path}")
                shutil.copyfile(template_path, image_path)
            except:
                log.exception(
                    f"IncidentCheck - Could not copy {template_path} to {image_path}"
                )

        def filter_and_sort_incidents(incidents_list):
            def _sort(incidents):
                incidents.sort(
                    key=lambda x: x.get("incident_severity", 0), reverse=True
                )
                return incidents

            # FAIL > DEG > MAINT > ANNOT
            failures = [x for x in incidents_list if x.get("incident_type") == "FAIL"]
            if failures:
                return _sort(failures)
            degradations = [
                x for x in incidents_list if x.get("incident_type") == "DEG"
            ]
            if degradations:
                return _sort(degradations)
            maintenances = [
                x for x in incidents_list if x.get("incident_type") == "MAINT"
            ]
            if maintenances:
                return _sort(maintenances)
            # Do not return annotations as their short description is mostly unhelpful
            return []

        def get_info_msg(incidents_list):
            if len(incidents_list) > 1:
                log.warning(
                    "IncidentCheck - Multiple active incidents of the same type. Use the highest severity one."
                )
            incident = incidents_list[0]
            short_description = incident["short_description"]
            if short_description:
                description = short_description
            else:
                description = incident["description"]
            start_time = incident["start_time"]
            if incident["end_time"]:
                end_time = incident["end_time"]
            else:
                end_time = "unknown"
            info_msg = f"{start_time} - {end_time}:\n{description}"
            return info_msg

        def _update_incidents(system, svc, active_svc_incidents, incidents):
            if not incidents.get(system, {}):
                incidents[system] = {}

            # Service has active incidents
            if active_svc_incidents:
                log.debug(f"IncidentCheck - Found active incidents for {system}.")
                incidents[system]["incident"] = get_info_msg(active_svc_incidents)
            elif svc["next_maintenance"]:
                next_maintenance_incidents = [
                    x
                    for x in active_svc_incidents
                    if parser.parse(x["start_time"])
                    == parser.parse(svc["next_maintenance"])
                ]
                if len(next_maintenance_incidents) == 0:
                    raise Exception(
                        f"IncidentCheck - Could not find matching start time in incidents for maintenance for {system}."
                    )
                log.debug(
                    f"IncidentCheck - Found announced maintenance(s) for {system}."
                )
                incidents[system]["incident"] = get_info_msg(next_maintenance_incidents)
            else:
                incidents[system]["incident"] = ""

            # Set initial status image if no health status exists yet
            if "health" not in incidents.get(system):
                update_status_image(system, svc["health"])
            # Change status image if service has a new health status
            elif svc["health"] != incidents.get(system).get("health", 0):
                update_status_image(system, svc["health"])
            incidents.get(system)["health"] = svc["health"]

        config = get_custom_config().get("incidentCheck", {})
        sleep_timer = config.get("interval", 60)
        incidents = _incidents_cache.copy()

        api_url = config.get("url", "https://status.jsc.fz-juelich.de/api")
        timeout = config.get("timeout", 5)
        try:
            all_incidents_r = requests.get(f"{api_url}/incidents", timeout=timeout)
            all_incidents_r.raise_for_status()
            all_incidents = all_incidents_r.json()
            for name, id in config["services"].items():
                try:
                    svc_r = requests.get(f"{api_url}/services/{id}", timeout=timeout)
                    svc_r.raise_for_status()
                    svc = svc_r.json()
                    active_svc_incidents = [
                        x
                        for x in all_incidents
                        if int(id) in x.get("affected_services", [])
                        and not x.get("resolved", "")
                    ]
                    active_svc_incidents = filter_and_sort_incidents(
                        active_svc_incidents
                    )
                    _update_incidents(name, svc, active_svc_incidents, incidents)
                except:
                    log.exception(
                        f"IncidentCheck - Could not check for incidents for {name}"
                    )
        except:
            log.exception("IncidentCheck - Could not check for incidents")
        _incidents_cache = incidents
        _last_change_incidents = int(time.time())
        await asyncio.sleep(sleep_timer)


background_tasks.append(asyncio.create_task(update_incidents()))


async def create_ns(user):
    ns = dict(user=user)
    if user:
        auth_state = await user.get_auth_state()
        if "refresh_token" in auth_state.keys():
            del auth_state["refresh_token"]
        ns["auth_state"] = auth_state
    return ns


class ExtraFormatter(logging.Formatter):
    dummy = logging.LogRecord(None, None, None, None, None, None, None)
    ignored_extras = [
        "args",
        "asctime",
        "created",
        "exc_info",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    ]

    def format(self, record):
        extra_txt = ""
        for k, v in record.__dict__.items():
            if k not in self.dummy.__dict__ and k not in self.ignored_extras:
                extra_txt += " --- {}={}".format(k, v)
        message = super().format(record)
        return message + extra_txt


# Translate level to int
def get_level(level_str):
    if type(level_str) == int:
        return level_str
    elif level_str.upper() in logging._nameToLevel.keys():
        return logging._nameToLevel[level_str.upper()]
    elif level_str.upper() == "TRACE":
        return 5
    elif level_str.upper().startswith("DEACTIVATE"):
        return 99
    else:
        try:
            return int(level_str)
        except ValueError:
            pass
    raise NotImplementedError(f"{level_str} as level not supported.")


# supported classes
supported_handler_classes = {
    "stream": logging.StreamHandler,
    "file": logging.handlers.TimedRotatingFileHandler,
    "smtp": logging.handlers.SMTPHandler,
    "syslog": logging.handlers.SysLogHandler,
}

# supported formatters and their arguments
supported_formatter_classes = {"json": JsonFormatter, "simple": ExtraFormatter}
json_fmt = {
    "asctime": "asctime",
    "levelno": "levelno",
    "levelname": "levelname",
    "logger": logged_logger_name,
    "file": "pathname",
    "line": "lineno",
    "function": "funcName",
    "Message": "message",
}
simple_fmt = f"%(asctime)s logger={logged_logger_name} levelno=%(levelno)s levelname=%(levelname)s file=%(pathname)s line=%(lineno)d function=%(funcName)s : %(message)s"
supported_formatter_kwargs = {
    "json": {"fmt": json_fmt, "mix_extra": True},
    "simple": {"fmt": simple_fmt},
}


def update_extra_handlers():
    global _logging_cache
    logging_config = copy.deepcopy(_logging_cache)
    logger = logging.getLogger(logger_name)

    if logging.getLevelName(5) != "TRACE":
        # First call
        # Remove default StreamHandler
        if len(logger.handlers) > 0:
            logger.removeHandler(logger.handlers[0])

        # In trace will be sensitive information like tokens
        logging.addLevelName(5, "TRACE")

        def trace_func(self, message, *args, **kws):
            if self.isEnabledFor(5):
                # Yes, logger takes its '*args' as 'args'.
                self._log(5, message, args, **kws)

        logging.Logger.trace = trace_func
        logger.setLevel(5)

    logger_handlers = logger.handlers
    handler_names = [x.name for x in logger_handlers]

    for handler_name, handler_config in logging_config.items():
        if (not handler_config.get("enabled", False)) and handler_name in handler_names:
            # Handler was disabled, remove it
            logger.handlers = [x for x in logger_handlers if x.name != handler_name]
            logger.debug(f"Logging handler removed ({handler_name})")
        elif handler_config.get("enabled", False):
            # Recreate handlers which has changed their config
            configuration = copy.deepcopy(handler_config)

            # map some special values
            if handler_name == "stream":
                if configuration["stream"] == "ext://sys.stdout":
                    configuration["stream"] = sys.stdout
                elif configuration["stream"] == "ext://sys.stderr":
                    configuration["stream"] = sys.stderr
            elif handler_name == "syslog":
                if configuration["socktype"] == "ext://socket.SOCK_STREAM":
                    configuration["socktype"] = socket.SOCK_STREAM
                elif configuration["socktype"] == "ext://socket.SOCK_DGRAM":
                    configuration["socktype"] = socket.SOCK_DGRAM

            _ = configuration.pop("enabled")
            formatter_name = configuration.pop("formatter")
            level = get_level(configuration.pop("level"))
            none_keys = []
            for key, value in configuration.items():
                if value is None:
                    none_keys.append(key)
            for x in none_keys:
                _ = configuration.pop(x)

            # Create handler, formatter, and add it
            handler = supported_handler_classes[handler_name](**configuration)
            formatter = supported_formatter_classes[formatter_name](
                **supported_formatter_kwargs[formatter_name]
            )
            handler.name = handler_name
            handler.setLevel(level)
            handler.setFormatter(formatter)
            if handler_name in handler_names:
                # Remove previously added handler
                logger.handlers = [x for x in logger_handlers if x.name != handler_name]
            logger.addHandler(handler)

            if "filename" in configuration:
                # filename is already used in log.x(extra)
                configuration["file_name"] = configuration["filename"]
                del configuration["filename"]
            logger.debug(f"Logging handler added ({handler_name})", extra=configuration)
