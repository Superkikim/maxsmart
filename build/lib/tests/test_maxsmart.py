import unittest
from unittest.mock import patch
from maxsmart.maxsmart import MaxSmart

class TestMaxSmart(unittest.TestCase):

    @patch('maxsmart.maxsmart.requests.get')
    def test_turn_on(self, mock_get):
        # Arrange
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'status': 'ok'}
        maxsmart = MaxSmart('192.168.1.1', 'test_sn')

        # Act
        response = maxsmart.turn_on(1)

        # Assert
        mock_get.assert_called_once()
        self.assertEqual(response, {'status': 'ok'})

    @patch('maxsmart.maxsmart.requests.get')
    def test_turn_off(self, mock_get):
        # Arrange
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'status': 'ok'}
        maxsmart = MaxSmart('192.168.1.1', 'test_sn')

        # Act
        response = maxsmart.turn_off(1)

        # Assert
        mock_get.assert_called_once()
        self.assertEqual(response, {'status': 'ok'})

    @patch('maxsmart.maxsmart.requests.get')
    def test_check_state(self, mock_get):
        # Arrange
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': {'switch': [0, 1, 0, 1, 0, 1]}}
        maxsmart = MaxSmart('192.168.1.1', 'test_sn')

        # Act
        response = maxsmart.check_state()

        # Assert
        mock_get.assert_called_once()
        self.assertEqual(response, [0, 1, 0, 1, 0, 1])

    # Continue with other methods...

if __name__ == '__main__':
    unittest.main()
