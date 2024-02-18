"""Utility functions for Takeoff SDK"""
# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import os
import re
import uuid
from pathlib import Path

import docker
import requests
from .schema import TakeoffEnvSetting


def start_container(
    image_name: str,
    container_name: str,
    ports: dict,
    volumes: list,
    environment_vars: dict,
    device_requests: list,
    shm_size: str,
):
    """Start a docker container.

    Args:
        image_name (str): image name with tag. example: "takeoff:cpu"
        container_name (str): container name
        ports (dict): port mapping. example: {"3000/tcp": None, "3001/tcp": None}
        volumes (list): volume mapping. example: [path1:path2]
        environment_vars (dict): environment variables. example: {"TAKEOFF_MAX_BATCH_SIZE": 1}
        device_requests (list): device requests. example: [docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])]
        shm_size (str): shm size. example: "4G"
    """
    client = docker.from_env()

    container = client.containers.run(
        image_name,
        detach=True,
        auto_remove=True,
        environment=environment_vars,
        name=container_name,
        device_requests=device_requests,
        volumes=volumes,
        ports=ports,
        shm_size=shm_size,
    )
    return container


def is_docker_logs_error(container):
    """Check the docker logs for errors

    Args:
        container (docker.models.containers.Container): docker container

    Returns:
        str: traceback if error, None if no error
    """

    # Stream logs from the container
    try:
        logs = container.logs().decode("utf-8")

        # Regular expression to match tracebacks
        traceback_pattern = r"Traceback \(most recent call last\):.*?(?=\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z|$)"
        tracebacks = re.findall(traceback_pattern, logs, re.DOTALL)

        if len(tracebacks) > 0:
            print("=====================================")
            print("Error while starting Takeoff server!")

            # print(f"Tracebacks: {tracebacks[0]}")
            return tracebacks[0]

    except Exception as e:
        print(f"Error while reading logs: {e}")
        return f"Error while reading logs: {e}"

    return None


def is_takeoff_loading(server_url: str) -> bool:
    """Check if the Takeoff server is loading

    Args:
        server_url (str): server url

    Returns:
        bool: True if the server is loading, False if it is ready
    """
    try:
        response = requests.get(server_url + "/healthz")
        return not response.ok
    except requests.exceptions.ConnectionError:
        return True


def start_takeoff(takeoff_config: TakeoffEnvSetting) -> tuple:
    """Start a Takeoff server using the given configuration

    Args:
        takeoff_config (TakeoffEnvSetting): Takeoff configuration

    Returns:
        tuple: (takeoff_port, management_port, container)
    """

    image = os.environ.get("TAKEOFF_IMAGE", "tytn/takeoff-pro:0.8.0-gpu")

    random_name = "takeoff_" + str(uuid.uuid4())[:8]
    volumes = [f"{Path.home()}/.iris_cache:/code/models"]
    device_requests = (
        [docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])] if takeoff_config.device == "cuda" else None
    )
    environtment_vars = takeoff_config.settings_to_env_vars()

    container = start_container(
        image_name=image,
        container_name=random_name,
        ports={"3000/tcp": None, "3001/tcp": None, "3003/tcp": None},
        volumes=volumes,
        environment_vars=environtment_vars,
        device_requests=device_requests,
        shm_size="4G",
    )

    container.reload()
    takeoff_port = container.ports["3000/tcp"][0]["HostPort"]
    management_port = container.ports["3001/tcp"][0]["HostPort"]
    openai_port = container.ports["3003/tcp"][0]["HostPort"]

    return takeoff_port, management_port, openai_port, container
