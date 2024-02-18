import pytest
from teia_sdk import PluginClient
from teia_sdk.utils import ppjson
from teia_sdk.plugins.schemas import FCallModelSettings, ChatMLMessage


class TestPluginsClient:
    @pytest.fixture
    def client(self):
        return PluginClient()

    def test_aveilable(self, client: PluginClient):
        assert len(client.available_plugins().keys()) > 3

    def test_select_and_run_plugin(self, client: PluginClient):
        response = client.select_and_run_plugin(
            model_settings=FCallModelSettings(model="gpt-3.5-turbo-0613"),
            messages=[ChatMLMessage(role="user", content="Who is Simion Petrov?")],
            plugin_names=["internal_search"],
        )
        assert "Simion Petrov" in response["plugin_infos"][0]["params"]["query"]
        assert response["plugin_infos"][0]["name"] == "internal_search"

    def test_select_plugin(self, client: PluginClient):
        response = client.run_selector(
            model_settings=FCallModelSettings(model="gpt-3.5-turbo-0613"),
            messages=[ChatMLMessage(role="user", content="Who is Simion Petrov?")],
            plugin_names=["internal_search"],
        )
        ppjson(response)
        assert "Simion Petrov" in response["arguments"]["query"]
        assert response["plugin"] == "internal_search"

    def test_run_plugin(self, client: PluginClient):
        plugin_calls = [
            {
                "plugin": "internal_search",
                "method": "internal_search",
                "arguments": {"query": "Who is Monica Pastor?"},
            }
        ]
        response = client.run_plugins(plugin_calls=plugin_calls)
        assert "Monica Pastor" in response["plugin_infos"][0]["params"]["query"]
        assert response["plugin_infos"][0]["name"] == "internal_search"
