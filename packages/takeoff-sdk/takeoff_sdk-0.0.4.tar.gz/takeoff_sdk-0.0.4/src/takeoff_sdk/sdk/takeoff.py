"""Takeoff Object SDK"""
# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import time

import requests
from loguru import logger

from .schema import TakeoffEnvSetting
from .utils import is_takeoff_loading, start_takeoff, is_docker_logs_error

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                                       Takeoff                                                        #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #


class Takeoff:
    def __init__(self, model_name, device, **kwargs):
        self.model_name = model_name
        self.device = device

        self.models = []
        self.consumer_groups = {}
        self.server_url = None
        self.management_url = None
        self.container = None

        self.takeoff_config = TakeoffEnvSetting(model_name=model_name, device=device, **kwargs)

    def cleanup(self):
        if self.container:
            self.container.remove(force=True)

    @classmethod
    def from_config(cls, takeoff_config: TakeoffEnvSetting):
        takeoff_args = takeoff_config.model_dump()
        return cls(**takeoff_args)

    def start(self):
        """Start the Takeoff server and add the model to the primary consumer group"""

        logger.info("Starting Takeoff server...")
        self.takeoff_port, self.management_port, self.container = start_takeoff(self.takeoff_config)

        self.server_url = f"http://localhost:{self.takeoff_port}"
        self.management_url = f"http://localhost:{self.management_port}"
        logger.info(f"Takeoff server running at: {self.server_url}")
        logger.info(f"Takeoff management server running at: {self.management_url}")

        for _ in range(100):  # Some models take a while to download
            if not is_takeoff_loading(self.server_url):
                break

            traceback = is_docker_logs_error(self.container)

            if traceback is not None:
                logger.error("Takeoff server failed to start. Error in docker logs. Cleaning up...")
                self.cleanup()
                raise Exception(
                    "Takeoff server failed to start due to error in docker logs. See below for details. \n" + traceback
                )
            logger.info("building...")
            time.sleep(3)
        else:
            raise Exception("Takeoff server build timed out")

        logger.info("server ready!")

        readers = self.readers()
        for group, details in readers.items():
            model_name = details[0]["model_name"]  # Assume one model for each group for now
            self.consumer_groups[model_name] = group
            self.models.append(model_name)

    def add_model(self, model_name: str, backend: str, device: str, consumer_group: str = "primary"):
        """Spawn a new reader for the given model and add it to the given consumer group

        Args:
            model_name (str): model name
            backend (str): backend
            device (str): device
            consumer_group (str, optional): consumer group. Defaults to "primary".
        """
        response = requests.post(
            self.management_url + "/reader",
            json={"model_name": model_name, "device": device, "backend": backend, "consumer_group": consumer_group},
        )
        assert response.ok
        self.models.append(model_name)
        self.consumer_groups[model_name] = consumer_group
        logger.info(f"Added model {model_name} to consumer group {consumer_group}")

    def readers(self):
        response = requests.get(self.management_url + "/reader_groups")
        return response.json()
