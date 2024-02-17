import unittest
from unittest.mock import patch

from seeqc_client import Client, Experiment
from .mocked_routes import VALID_PASSWORD, VALID_USERNAME, VALID_ACCESS, VALID_REFRESH, MockedAuthenticate, \
    MockedRefresh, MockedVersion, MockedEmulator, MockedQueue, MockedPendingStatus
from seeqc_client.tests.test_vars import QueueTestVars, EXPERIMENT_ID


class BaseCase(unittest.TestCase):
    """
    CLI Tests
    """
    def setUp(self):
        """Setup tests"""
        self.credentials = {'email': VALID_USERNAME, 'password': VALID_PASSWORD}
        self.client = Client()

    def tearDown(self) -> None:
        self.client.auth.access_token = None
        self.client.auth.refresh_token = None
    
    @patch('requests.post', MockedAuthenticate)
    def test_valid_authenticate(self):
        """Test that a client successfully authenticates given the correct credentials"""
        self.client.auth.authenticate(self.credentials)
        self.assertEqual(self.client.auth.access_token, VALID_ACCESS)
        self.assertEqual(self.client.auth.refresh_token, VALID_REFRESH)

    @patch('requests.post', MockedAuthenticate)
    def test_invalid_authenticate(self):
        """Test a client fails to authenticate with bad credentials"""
        self.client.auth.authenticate({'email': 'invalid', 'password': 'invalid'})
        self.assertEqual(self.client.auth.access_token, None)
        self.assertEqual(self.client.auth.refresh_token, None)

    @patch('requests.post', MockedRefresh)
    def test_valid_refresh(self):
        """Test that tokens can be refreshed given a valid refresh token"""
        self.client.auth.refresh_token = VALID_REFRESH
        self.client.auth.refresh()
        self.assertEqual(self.client.auth.access_token, VALID_ACCESS)

    @patch('requests.post', MockedRefresh)
    def test_invalid_refresh(self):
        """Test refresh fails with an invalid token"""
        self.client.auth.refresh_token = 'invalid'
        self.client.auth.refresh()
        self.assertEqual(self.client.auth.access_token, None)

    def test_get_version_valid(self):
        """Test that a successful request can be made to the resource server"""
        with patch('requests.post', MockedAuthenticate):
            self.client.auth.authenticate(self.credentials)
        with patch('requests.get', MockedVersion):
            response = self.client._get_version_request()
        self.assertEqual(response.status_code, 200)

    @patch('requests.post', MockedRefresh)
    def test_get_version_invalid_access_and_refresh(self):
        """Test that an unsuccessful request can be made to the resource server"""
        self.client.auth.access_token = 'invalid'
        self.client.auth.construct_header()
        with patch('requests.get', MockedVersion):
            response = self.client._get_version_request()
        self.assertEqual(response.status_code, 401)

    def test_post_good_emulator_request(self):
        """Test that a successful request can be made to an emulator backend"""
        with patch('requests.post', MockedEmulator):
            response = self.client._run_emulator_request('seeqc_client/tests/test.qasm', 10)
        self.assertEqual(response.status_code, 200)

    def test_post_bad_emulator_request(self):
        """Test that a successful request can be made to an emulator backend"""
        with patch('requests.post', MockedEmulator):
            response = self.client._run_emulator_request('seeqc_client/tests/bad_extension.qasm2', 10)
            self.assertEqual(response.status_code, 400)

    def test_get_experiments(self):
        """Check experiment queue get"""
        with patch('requests.get', MockedQueue):
            data = self.client.get_experiments()
        self.assertEqual(data[0]['experiment_id'], QueueTestVars.experiment_id0)
        self.assertEqual(len(data), 5)

    def test_get_experiments_private(self):
        """Check experiment queue get private method"""
        with patch('requests.get', MockedQueue):
            response = self.client._run_queue_request(start_index=0, end_index=20)
        self.assertEqual(response.status_code, 200)
        data = response.queue
        self.assertEqual(data[0]['experiment_id'], QueueTestVars.experiment_id0)
        self.assertEqual(len(data.keys()), 5)

    def test_get_experiments_short(self):
        """Check experiment queue with shortened queue"""
        with patch('requests.get', MockedQueue):
            response = self.client._run_queue_request(start_index=1, end_index=3)
        self.assertEqual(response.status_code, 200)
        data = response.queue
        self.assertEqual(data[1]['experiment_id'], QueueTestVars.experiment_id1)
        self.assertFalse(QueueTestVars.experiment_id4 in data.keys())
        self.assertFalse(QueueTestVars.experiment_id0 in data.keys())
        self.assertEqual(len(data.keys()), 3)

    def test_get_experiments_too_long(self):
        """Test experiment queue fails when too many experiments requested"""
        with self.assertRaises(AssertionError):
            self.client.get_experiments(start_index=0, end_index=Client().max_queue_length+1)

    def test_get_experiments_bad_range(self):
        """Test experiment queue fails when indices are given in wrong order"""
        with self.assertRaises(AssertionError):
            self.client.get_experiments(start_index=10, end_index=0)

    def test_pending_get_status(self):
        """Test that when an experiment is found to be pending that the results are not fetched"""
        experiment = Experiment(uid=EXPERIMENT_ID, get_results=False)
        with patch('requests.get', MockedPendingStatus), \
             patch('seeqc_client.Experiment._get_status') as mock_results:
            status = experiment._get_status()
            mock_results.assert_called_once()
            self.assertIsNotNone(status)

    def test_get_results(self):
        """Test that a results request is made as expected"""
        experiment = Experiment(uid=EXPERIMENT_ID, get_results=False)
        with patch('seeqc_client.Experiment._get_results_request') as mocked:
            experiment._get_results()
            mocked.assert_called_once()

    @patch('getpass.getpass')
    @patch('seeqc_client.Client._get_username')
    def test_initialise(self, mock_user, mock_getpass):
        """Test that a user can initialise the client"""
        mock_getpass.return_value = VALID_PASSWORD
        mock_user.return_value = VALID_USERNAME
        with patch('seeqc_client.authorisation.Authorisation.authenticate') as mocked:
            self.client.initialise()
            mocked.assert_called_once_with(credentials=self.credentials)
        mock_user.reset_mock()
        mock_getpass.reset_mock()

    def test_cancel(self):
        experiment = Experiment(uid=EXPERIMENT_ID, get_results=False)
        with patch('seeqc_client.Experiment._post_cancel_request') as mock_cancel:
            experiment.cancel()
            mock_cancel.assert_called_once()

    def test_format_result(self):
        """Get experiment status response"""
        result = '[[0],[1],[0]]\n'
        formatted = self.client._format_emulator_result(result)
        self.assertEqual(formatted, [[0], [1], [0]])
