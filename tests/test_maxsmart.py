import unittest
from unittest.mock import patch, MagicMock
from maxsmart import MaxSmart

class TestMaxSmart(unittest.TestCase):
    def setUp(self):
        self.ip = '127.0.0.1'
        self.sn = 'abc123'
        self.ms = MaxSmart(self.ip, self.sn)

    @patch('requests.get')
    def test_send_command(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(return_value={'data': 'mock_data'})
        mock_get.return_value = mock_resp

        result = self.ms._send_command('test_cmd', {'param1': 'value1'})
        self.assertEqual(result, {'data': 'mock_data'})

    @patch('maxsmart.MaxSmart._send_command')
    @patch('maxsmart.MaxSmart._verify_port_state')
    def test_turn_on(self, mock_verify_port_state, mock_send_command):
        self.ms.turn_on(3)
        mock_send_command.assert_called_once_with(200, {"sn": self.sn, "port": 3, "state": 1})
        mock_verify_port_state.assert_called_once_with(3, 1)

    @patch('maxsmart.MaxSmart._send_command')
    @patch('maxsmart.MaxSmart._verify_port_state')
    def test_turn_off(self, mock_verify_port_state, mock_send_command):
        self.ms.turn_off(3)
        mock_send_command.assert_called_once_with(200, {"sn": self.sn, "port": 3, "state": 0})
        mock_verify_port_state.assert_called_once_with(3, 0)

    @patch('maxsmart.MaxSmart._send_command')
    def test_check_state(self, mock_send_command):
        mock_send_command.return_value = {'data': {'switch': [1, 0, 0, 1, 1, 0]}}
        result = self.ms.check_state()
        self.assertEqual(result, [1, 0, 0, 1, 1, 0])

    @patch('maxsmart.MaxSmart.check_state')
    def test_check_port_state(self, mock_check_state):
        mock_check_state.return_value = [1, 0, 0, 1, 1, 0]
        result = self.ms.check_port_state(3)
        self.assertEqual(result, 0)

    @patch('maxsmart.MaxSmart._send_command')
    def test_get_hourly_data(self, mock_send_command):
        mock_send_command.return_value = {'data': {'watt': [10, 20, 30, 40, 50, 60]}}
        result = self.ms.get_hourly_data(4)
        self.assertEqual(result, 40)

    @patch('maxsmart.MaxSmart._send_command')
    def test_get_power_data(self, mock_send_command):
        mock_send_command.return_value = {'data': {'watt': [10, 20, 30, 40, 50, 60], 'amp': [1, 2, 3, 4, 5, 6]}}
        result = self.ms.get_power_data(4)
        self.assertEqual(result, {"watt": 40, "amp": 4})

if __name__ == '__main__':
    unittest.main()
