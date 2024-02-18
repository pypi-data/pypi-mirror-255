"""
This module contains the data model for the Takeoff SDK. This is used to parse the environment variables
"""
# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, validator

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                               Configuration Data Model                                               #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #

__all__ = ["TakeoffEnvSetting"]


class TakeoffEnvSetting(BaseModel):
    """
    This class contains the data model for the Takeoff SDK. This setting is used to set the environment variables
    """

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    # ------------------------------------- model configuration -------------------------------------- #

    # NOTE: these are expected to be set by the user
    model_name: str = Field(..., env="TAKEOFF_MODEL_NAME")
    device: str = Field(..., env="TAKEOFF_DEVICE")

    backend: Optional[str] = Field(None, env="TAKEOFF_BACKEND")

    max_batch_size: int = Field(8, env="TAKEOFF_MAX_BATCH_SIZE")
    batch_duration_millis: int = Field(100, env="TAKEOFF_BATCH_DURATION_MILLIS")
    access_token: Optional[str] = Field(None, env="TAKEOFF_ACCESS_TOKEN")
    cuda_visible_devices: Optional[str] = Field(None, env="TAKEOFF_CUDA_VISIBLE_DEVICES")

    refill_threshold: float = Field(0.5, env="TAKEOFF_REILL_THRESHOLD")
    disable_continuous_generation: bool = Field(False, env="TAKEOFF_DISABLE_CONTINUOUS_GENERATION")
    consumer_group: str = Field("primary", env="TAKEOFF_CONSUMER_GROUP")

    redis_host: str = Field("localhost", env="TAKEOFF_REDIS_HOST")
    redis_port: int = Field(6379, env="TAKEOFF_REDIS_PORT")

    heartbeat_wait_interval: int = Field(10, env="TAKEOFF_HEARTBEAT_WAIT_INTERVAL")

    # JF Config
    nvlink_unavailable: int = Field(0, env="TAKEOFF_NVLINK_UNAVAILABLE")

    tensor_parallel: int = Field(1, env="TAKEOFF_TENSOR_PARALLEL")
    disable_cuda_graph: int = Field(0, env="TAKEOFF_DISABLE_CUDA_GRAPH")
    quant_type: str = Field("auto", env="TAKEOFF_QUANT_TYPE")  # auto, awq
    max_seq_len: int = Field(128, env="TAKEOFF_MAX_SEQUENCE_LENGTH")
    disable_static: int = Field(0, env="TAKEOFF_DISABLE_STATIC")

    export_traces: bool = Field(False, env="TAKEOFF_EXPORT_TRACES")
    traces_host: str = Field("http://localhost:4317", env="TAKEOFF_TRACES_HOST")
    metrics_target: str = Field("redis", env="TAKEOFF_METRICS_TARGET")

    metrics_log_level: str = Field("INFO", env="TAKEOFF_METRICS_LOG_LEVEL")

    is_echo: bool = Field(False, env="TAKEOFF_ECHO")

    log_level: str = Field("INFO", env="TAKEOFF_LOG_LEVEL")
    rust_log_level: str = Field("INFO", env="RUST_LOG")

    run_name: str = Field("takeoff_default", env="TAKEOFF_RUN_NAME")

    license_key: Optional[str] = Field(None, env="LICENSE_KEY")

    @validator("device")
    def validate_device(cls, v):
        if v not in ["cpu", "cuda"]:
            raise ValueError("device must be either cpu or cuda")
        return v

    def settings_to_env_vars(self) -> Dict[str, str]:
        env_var_mapping = {}
        for field_name, model_field in self.__dict__.items():
            field_info = self.model_fields[field_name]
            default_value = field_info.default

            # Only add to env_var_mapping if the current value is different from the default value
            if model_field != default_value:
                if field_info.json_schema_extra is not None and "env" in field_info.json_schema_extra:
                    env_var_name = field_info.json_schema_extra["env"]

                    # Check if the value is of type bool and convert to lowercase string
                    value = model_field
                    if isinstance(value, bool):
                        value = str(value).lower()

                    env_var_mapping[env_var_name] = value

        return env_var_mapping
