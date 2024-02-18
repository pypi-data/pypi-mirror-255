from unittest.mock import MagicMock, patch

from takeoff_sdk import Takeoff, TakeoffEnvSetting


def test_takeoff_initialization():
    model_name = "test_model"
    device = "cpu"
    takeoff = Takeoff(model_name=model_name, device=device)

    assert takeoff.model_name == model_name
    assert takeoff.device == device
    assert isinstance(takeoff.takeoff_config, TakeoffEnvSetting)
    assert takeoff.models == []
    assert takeoff.consumer_groups == {}
    assert takeoff.server_url is None
    assert takeoff.management_url is None
    assert takeoff.container is None


def test_takeoff_from_config():
    config = TakeoffEnvSetting(model_name="test_model", device="cpu")
    takeoff = Takeoff.from_config(config)

    assert takeoff.model_name == config.model_name
    assert takeoff.device == config.device


@patch("takeoff_sdk.sdk.takeoff.start_takeoff", return_value=(8000, 8001, MagicMock()))
@patch("takeoff_sdk.sdk.takeoff.is_takeoff_loading", side_effect=[True, True, False])
def test_takeoff_start(mock_is_loading, mock_start_takeoff):
    takeoff = Takeoff(model_name="test_model", device="cpu")

    # Assuming readers() method returns some mock data
    mock_readers = {"group1": [{"model_name": "model1"}]}
    takeoff.readers = MagicMock(return_value=mock_readers)

    takeoff.start()

    assert takeoff.server_url == "http://localhost:8000"
    assert takeoff.management_url == "http://localhost:8001"
    assert "model1" in takeoff.consumer_groups
    assert "model1" in takeoff.models
    mock_start_takeoff.assert_called_once_with(takeoff.takeoff_config)
    assert mock_is_loading.call_count == 3
