"""Top level module for handling API requests"""
import ast
import getpass
import json
import pprint
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional
from typing import Union
from _pickle import UnpicklingError

import numpy.typing as npt
import requests
from numpy import load
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import HTTPException

from .authorisation import Authorisation
from .plotting import plot

CHASSIS_NAME = 'virtual'
DEFAULT_QUEUE_LENGTH = 10

class Client:
    """Client class for handling API requests"""
    auth: Authorisation = Authorisation(url=None)

    def __init__(self, url=None):
        self.max_queue_length = 50
        if url is not None:
            self.auth.update_urls(url)

    def initialise(self, token_path: Union[Path, str] = None):
        """Create an authenticated session"""
        if token_path is None:
            credentials = self._get_credentials()
            self.auth.authenticate(credentials=credentials)
        else:
            self.auth.authenticate(refresh_token_path=token_path)

    def gen_token(self, token_path: Union[Path, str], credentials: dict = None):
        """Generate an authentication token at a given path"""
        if credentials is None:
            credentials = self._get_credentials()
        self.auth.gen_refresh_token(credentials, token_path)

    def run_emulator(self, qasm_path: Union[Path, str], num_shots: int=10):
        """Request for a qasm input to be run on an emulator node"""
        emulated = self._run_emulator_request(qasm_path, num_shots)
        self._raise_if_http_error(emulated)
        return self._format_emulator_result(emulated.text)

    def get_experiments(self, start_index: int = 0, end_index: int = DEFAULT_QUEUE_LENGTH):
        """Get previous experiments. Index represents how far back to look."""
        assert end_index > start_index, 'end index must be > start index'
        assert (end_index - start_index) <= self.max_queue_length, 'Please specify a range of experiments less than 50'
        return self._get_experiments(start_index=start_index, end_index=end_index)

    @staticmethod
    def get_experiment(uid: str):
        """Generate an experiment object using an existing experiment ID"""
        return Experiment(uid=uid)

    def create_experiment(self, upload: Union[Path, str]):
        """Create a new experiment from either a qasm string or a path pointing to a string"""
        self._check_file_extension(upload)
        return Experiment(circuit_filepath=upload)

    def _get_credentials(self):
        username = self._get_username()
        password = self._get_password()
        print('\nAuthenticating with authorisation server')
        return {'email': username, 'password': password}

    @staticmethod
    def _get_username():
        return input('Input your email address\n')

    @staticmethod
    def _get_password():
        return getpass.getpass('Input your password\n')

    @staticmethod
    def _raise_if_http_error(response):
        """Check if the request failed and if so raise the error"""
        if not response.ok:
            raise HTTPException(response.text)
        return False

    def _get_version_request(self):
        """Get version api call response"""

        @self.auth.request_handler
        def wrapped_get_version(url: str, headers: dict):
            """Get the version of the resource API"""
            response = requests.get(f"{url}/version",
                                    headers=headers)
            return response

        return wrapped_get_version()

    def _get_version(self):
        """Get API version. Simple way to test valid connectivity"""
        response = self._get_version_request()
        self._raise_if_http_error(response)
        return response.text

    def _run_emulator_request(self, qasm_path: Union[Path, str], num_shots: int):
        @self.auth.request_handler
        def wrapped_run_emulator(url: str, headers: dict):
            """Get the response from a qasm string upload to the emulator"""
            with open(qasm_path, 'rb') as file:
                files = {'file': file}
                data = {'shots': num_shots}
                response = requests.post(f"{url}/api/v1/emulator",
                                         headers=headers,
                                         data=data,
                                         files=files)
            return response

        return wrapped_run_emulator()

    @staticmethod
    def _format_emulator_result(result):
        return ast.literal_eval(result)


    def _run_queue_request(self, start_index, end_index):
        @self.auth.request_handler
        def wrapped_run_queue(url: str, headers: dict, first: int = start_index, last: int = end_index):
            """Get the response from a request for user experiments queue"""
            response = requests.get(f"{url}/api/v1/user-experiments?first={first}&last={last}",
                                    headers=headers)
            return response

        return wrapped_run_queue()

    def _get_experiments(self, start_index: int, end_index: int) -> dict:
        """Get user queue of experiments"""
        response = self._run_queue_request(start_index=start_index, end_index=end_index)
        self._raise_if_http_error(response)
        queue = self._format_experiment_list(response.json())
        pprint.pprint(queue)
        return queue

    @staticmethod
    def format_timestamps(experiments: dict):
        for experiment in experiments:
            experiment['timestamp'] = datetime.fromtimestamp(experiment['timestamp']).strftime('%c')
        return experiments

    def _format_experiment_list(self, queue: dict):
        output = []
        for index in queue.keys():
            output.append(queue[index])
        output = self.format_timestamps(output)
        return output

    @staticmethod
    def _check_file_extension(file: str):
        if '.qasm' not in file:
            raise NotImplementedError('Currently only .qasm files are accepted.')


class Experiment(Client):
    """
    Represents user experiments. Used to create remote jobs and retrieve results or statuses of existing ones
    """
    def __init__(self, circuit_filepath: Union[Path, str] = None, uid: str = None, get_results=True):
        super().__init__()
        assert circuit_filepath is not None or uid is not None, \
            'Please specify either the id of a previous experiment or a custom circuit file to create a new one'
        self.response = None
        self.results = None
        self.circuit_filepath = circuit_filepath
        self.uid = uid
        self.status = None
        if uid is not None and get_results:
            self._get_results()

    def run(self):
        """Run an experiment"""
        assert self.uid is None, 'Experiment has already been triggered'
        self._run_experiment()
        print('\n Sending request to server')
        print('\n Experiment queued')

    def _run_experiment(self):
        response = self._post_run_request()
        self._raise_if_http_error(response)
        self.uid = response.text

    def _process_circuit_file(self):
        """Process a circuit file for a custom circuit upload"""
        with open(self.circuit_filepath, 'rb') as f:
            file_data = BytesIO(f.read())
        file_data.seek(0)
        return FileStorage(file_data, filename='file')

    def _post_run_request(self, chassis: str = CHASSIS_NAME, routine: str = 'custom', routine_args: dict = None):
        """Get experiment status response"""
        payload = {'chassis': chassis, 'routine': routine, 'routine_args': routine_args}
        json_data = json.dumps(payload)

        @self.auth.request_handler
        def wrapped_run_request(url: str, headers: dict):
            """Get the status of an experiment"""
            headers['json_data'] = json_data
            with open(self.circuit_filepath, 'rb') as file:
                files = {'file': file}
                response = requests.post(f'{url}/api/v1/run-routine',
                                         files=files,
                                         headers=headers)
            return response

        return wrapped_run_request()

    def get_status(self, get_results: bool = True):
        """Return the status of an experiment and populate the status attribute"""
        if self.status != 'COMPLETE':
            self.status = self._get_status()
            print(f'Status is: {self.status}')
            if self.status == 'COMPLETE' and get_results:
                print('Retrieving results')
                self._get_results()
            return
        print(f'Status is: {self.status}')
        return

    def _get_status_request(self, experiment_id: str):
        """Get experiment status response"""

        @self.auth.request_handler
        def wrapped_get_status(url: str, headers: dict):
            """Get the status of an experiment"""
            response = requests.get(f"{url}/api/v1/status/{experiment_id}",
                                    headers=headers)
            return response

        return wrapped_get_status()

    def _get_status(self):
        """Get experiment status"""
        assert self.uid is not None, 'Experiment has not yet been initialised. No valid ID found'
        response = self._get_status_request(self.uid)
        self._raise_if_http_error(response)
        self.response = response
        data = response.json()
        return data['status']

    def get_register(self):
        """Return the quantum register"""
        response = self._get_register()
        self._raise_if_http_error(response)
        return self.try_array_deserialisation(response.content)

    def _get_results_request(self):
        """Get experiment status response"""

        @self.auth.request_handler
        def wrapped_get_results(url: str, headers: dict):
            """Get the status of an experiment"""
            response = self._get_results_call(url, headers)
            return response

        return wrapped_get_results()

    def _get_register(self):
        @self.auth.request_handler
        def wrapped_get_register(url: str, headers: dict):
            """Get the status of an experiment"""
            headers['full_results'] = 'True'
            response = self._get_results_call(url, headers)
            return response

        return wrapped_get_register()

    def _get_results_call(self, url, headers):
        return requests.get(f"{url}/api/v1/result-distribution/{self.uid}",
                            headers=headers)

    def _get_results(self):
        """Retrieve routine results"""
        response = self._get_results_request()
        self._raise_if_http_error(response)
        self.results = response.json()

    def show_results(self):
        """Print the state populations of the measurement"""
        pprint.pprint(self.results)

    def plot(self):
        """Plot the routine results as a histogram"""
        assert self.results is not None, 'Results must be retrieved before they can be plotted'
        plot(self.results)

    def cancel(self):
        """Cancel an experiment that has not yet started running, or completed"""
        response = self._post_cancel_request()
        self._raise_if_http_error(response)
        if response.ok:
            print('Job successfully cancelled')

    def _post_cancel_request(self):
        """Get experiment status response"""
        @self.auth.request_handler
        def wrapped_post_cancel(url: str, headers: dict):
            """Get the status of an experiment"""
            response = requests.post(f"{url}/api/v1/cancel/{self.uid}",
                                     headers=headers)
            return response
        return wrapped_post_cancel()

    def try_array_deserialisation(self, data: bytes) -> Optional[npt.NDArray]:
        """Deserialise an array and construct a response in case of failure"""
        try:
            return self.deserialise_array(data)
        except (TypeError, UnpicklingError, EOFError) as ex:
            print('Results file parsing failed with: ')
            print(ex)
            return None

    @staticmethod
    def deserialise_array(array: bytes):
        """Deserialise a numpy array from bytes"""
        load_bytes = BytesIO(array)
        return load(load_bytes, allow_pickle=True)
