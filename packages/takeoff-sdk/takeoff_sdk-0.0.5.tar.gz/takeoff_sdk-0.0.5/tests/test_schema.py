import pytest
from pydantic import ValidationError
from takeoff_sdk import TakeoffEnvSetting


def test_data_model_with_default_values():
    # Test with default values
    settings = TakeoffEnvSetting(model_name="default_model", device="cpu")
    assert settings.model_name == "default_model"
    assert settings.device == "cpu"
    assert settings.backend is None
    assert settings.max_batch_size == 8
    assert settings.batch_duration_millis == 100
    assert settings.access_token is None
    assert settings.cuda_visible_devices is None
    assert not settings.disable_continuous_generation
    assert settings.consumer_group == "primary"
    assert settings.redis_host == "localhost"
    assert settings.redis_port == 6379
    assert settings.heartbeat_wait_interval == 10
    assert settings.nvlink_unavailable == 0
    assert settings.tensor_parallel == 1
    assert settings.disable_cuda_graph == 0
    assert settings.quant_type == "auto"
    assert settings.max_seq_len == 128
    assert settings.disable_static == 0
    assert not settings.export_traces
    assert settings.traces_host == "http://localhost:4317"
    assert settings.metrics_target == "redis"
    assert settings.metrics_log_level == "INFO"
    assert not settings.is_echo
    assert settings.log_level == "INFO"
    assert settings.rust_log_level == "INFO"
    assert settings.run_name == "takeoff_default"
    assert settings.license_key is None


def test_settings_to_env_vars_with_custom_values():
    # Test with custom values
    settings = TakeoffEnvSetting(model_name="custom_model", device="cpu", max_batch_size=16)
    env_vars = settings.settings_to_env_vars()
    expected_vars = {"TAKEOFF_MODEL_NAME": "custom_model", "TAKEOFF_DEVICE": "cpu", "TAKEOFF_MAX_BATCH_SIZE": 16}
    assert env_vars == expected_vars


def test_settings_to_env_vars_with_bool_values():
    # Test with bool values, it shoud be converted to lower case string
    settings = TakeoffEnvSetting(model_name="custom_model", device="cpu", disable_continuous_generation=True)
    env_vars = settings.settings_to_env_vars()
    expected_vars = {
        "TAKEOFF_MODEL_NAME": "custom_model",
        "TAKEOFF_DEVICE": "cpu",
        "TAKEOFF_DISABLE_CONTINUOUS_GENERATION": "true",
    }
    assert env_vars == expected_vars


def test_validate_device():
    # Valid devices should not raise an error
    valid_devices = ["cpu", "cuda"]
    for device in valid_devices:
        settings = TakeoffEnvSetting(model_name="test_model", device=device)
        assert settings.device == device

    # Invalid device should raise an error
    with pytest.raises(ValueError) as e:
        TakeoffEnvSetting(model_name="test_model", device="invalid_device")
    assert "device must be either cpu or cuda" in str(e.value)


def test_invalid_attribute():
    # Attempting to create an instance with an undefined attribute should raise an error
    with pytest.raises(ValidationError):
        TakeoffEnvSetting(model_name="test_model", device="cpu", undefined_attribute="value")
