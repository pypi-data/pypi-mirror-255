from unittest import mock
import pytest
from unittest.mock import MagicMock, patch
from my_functions_beatzaplenty.resize_linode_instance import main

class TestMainFunction:

    @patch('my_functions_beatzaplenty.resize_linode_instance.linode_api.LinodeClient')
    @patch('my_functions_beatzaplenty.resize_linode_instance.linode.wait_for_completion')
    @patch('my_functions_beatzaplenty.resize_linode_instance.linode.wait_for_instance_state')
    @patch('my_functions_beatzaplenty.resize_linode_instance.threading.Thread')
    def test_main(self, mock_thread, mock_wait_for_completion, mock_wait_for_instance_state, mock_LinodeClient):
        # Set up environment variables
        monkeypatch = MagicMock()
        monkeypatch.setenv('LINODE_API_KEY', '49701e88c9484fdb67b1a86ebb8048837a72d15dd4921c91c77920f9397e2a5d')

        # Set up configuration
        config = MagicMock()
        config.get.return_value = 'docker'
        config.get.linode_name = 'docker'
        
        # Set up Linode instances to simulate the scenario where the Linode with label 'docker' is not found
        mock_linode_instances = []

        # Mock Linode API client and instance
        mock_linode_instance = MagicMock()
        mock_linode_instance.id = 53627498
        mock_linode_instance.label = 'docker'
        mock_linode_instance.type.id = 'g6-nanode-1'

        mock_api_client = MagicMock()
        mock_api_client.linode.instances.return_value = [mock_linode_instance]
        mock_LinodeClient.return_value = mock_api_client

        # Mock linode.polling.event_poller_create
        mock_event_poller = MagicMock()
        mock_api_client.polling.event_poller_create.return_value = mock_event_poller

        main(config, arg_direction="--down", arg_monitor=True)

         # Assert that Linode API client is called with the correct parameters
        mock_LinodeClient.assert_called_once_with('49701e88c9484fdb67b1a86ebb8048837a72d15dd4921c91c77920f9397e2a5d')
#        expected_call = call(linode_api.Instance.label == 'docker')
        mock_api_client.linode.instances.assert_called_once_with(mock.ANY)

        # Assert that linode.polling.event_poller_create is called
        mock_api_client.polling.event_poller_create.assert_called_once_with('linode', 'linode_resize', entity_id=mock_linode_instance.id)

        # Assert that threading.Thread is called with the correct target
        mock_thread.assert_called_once_with(target=mock_event_poller.wait_for_next_event_finished, daemon=True)

        # Assert that linode.wait_for_completion is called before linode.wait_for_instance_state
        mock_wait_for_completion.assert_called_once()
        mock_wait_for_instance_state.assert_called_once()

if __name__ == '__main__':
    pytest.main()
