from __future__ import annotations
from .test_vars import QueueTestVars, EXPERIMENT_ID

VALID_PASSWORD = 'valid'
VALID_USERNAME = 'user'
VALID_ACCESS = 'valid_access'
VALID_REFRESH = 'valid_refresh'
VERSION = 'version_value'


class MockedAuthenticate:
    """Mock replacement for Authenticate"""
    def __init__(self, *args, **kwargs):
        self.status_code = None
        self.access_token = None
        self.refresh_token = None
        self.mocked_authenticate(*args, **kwargs)

    def json(self):
        return {
            'access': self.access_token,
            'refresh': self.refresh_token
        }
    
    def mocked_authenticate(self, *args, **kwargs):
        """authentication function to check credential validity """
        data = kwargs.get('data')
        email = data.get('email')
        password = data.get('password')
        if email != VALID_USERNAME or password != VALID_PASSWORD:
            self.status_code = 400
            return self
        self.status_code = 200
        self.access_token = VALID_ACCESS
        self.refresh_token = VALID_REFRESH
        return self


class MockedRefresh:
    """Mock class to handle token refreshing"""
    def __init__(self, *args, **kwargs):
        self.access_token = None
        self.refresh_token = None
        self.status_code = None
        self.mocked_refresh(*args, **kwargs)

    def mocked_refresh(self, *args, **kwargs):
        """Replace tokens with valid values"""
        data = kwargs.get('data')
        refresh = data.get('refresh')
        if refresh == VALID_REFRESH:
            self.access_token = VALID_ACCESS
            self.refresh_token = VALID_REFRESH
            self.status_code = 200
        else:
            self.status_code = 400

    def json(self):
        return {
            'access': self.access_token,
            'refresh': self.refresh_token
        }


class MockedVersion:
    """Mocking class to replace the get version API route"""
    def __init__(self, *args, **kwargs):
        self.status_code = None
        self.ok = False
        self.text = None
        self.mocked_version(*args, **kwargs)

    def mocked_version(self, *args, **kwargs):
        """Check tokens and return a verion string"""
        access = extract_token_from_header(kwargs)
        if access == VALID_ACCESS:
            self.status_code = 200
            self.ok = True
            return VERSION
        else:
            self.status_code = 401
            self.text = 'error'

    @staticmethod
    def close():
        pass


class MockedEmulator:
    """Mocking class to replace the emulator"""
    def __init__(self, *args, **kwargs):
        self.status_code = None
        self.text = None
        self.allowed_extensions = {'txt', 'qasm'}
        self.ok = False
        self.text = None
        self.mocked_emulator(*args, **kwargs)

    def mocked_emulator(self, *args, **kwargs):
        """Check files and return a response consistent with emulator api route"""
        file = kwargs['files']['file']
        filename = file.raw.name
        if self.allowed_file(filename):
            self.status_code = 200
            self.ok = True
        else:
            self.status_code = 400
            self.text = 'error'
        self.text = '[[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]\n'

    def allowed_file(self, filename):
        """Check file is as expected"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    @staticmethod
    def close():
        pass


class MockedQueue:
    """Replacing the status-queue API route"""
    def __init__(self, *args, **kwargs):
        self.status_code = None
        self.queue = None
        self.ok = False
        self.text = None
        self.mocked_queue(*args, **kwargs)

    @staticmethod
    def parse_path(path: str):
        """Get path arguments from a url"""
        short_url = path.split("?", 1)[1]
        split_args = short_url.split('&')
        arguments = {}
        for item in split_args:
            key, val = item.split('=')
            arguments[key] = int(val)
        return arguments

    def mocked_queue(self, *args, **kwargs):
        """Generate a mocked queue of experiments"""
        arguments = self.parse_path(args[0])
        full_queue = {
            0: {'experiment_id': QueueTestVars.experiment_id0, 'status': 'PENDING', 'timestamp': 1686057785.409567},
            1: {'experiment_id': QueueTestVars.experiment_id1, 'status': 'COMPLETED', 'timestamp': 1686057785.441656},
            2: {'experiment_id': QueueTestVars.experiment_id2, 'status': 'COMPLETED', 'timestamp': 1686057785.456754},
            3: {'experiment_id': QueueTestVars.experiment_id3, 'status': 'COMPLETED', 'timestamp': 1686057786.456754},
            4: {'experiment_id': QueueTestVars.experiment_id4, 'status': 'COMPLETED', 'timestamp': 1686057787.456754}
        }
        self.remove_out_of_range_indices(full_queue, arguments)
        self.queue = full_queue
        self.status_code = 200
        self.ok = True

    def json(self):
        return self.queue

    @staticmethod
    def remove_out_of_range_indices(queue: dict, arguments: dict):
        """Use path arguments to filter out of range indices from a queue"""
        bad_indices = []
        if 'first' in arguments.keys() and 'last' in arguments.keys():
            for index in queue.keys():
                if index < int(arguments['first']):
                    bad_indices.append(index)
                if index > int(arguments['last']):
                    bad_indices.append(index)
            for index in bad_indices:
                del queue[index]

    @staticmethod
    def close():
        pass


class MockedStatus:
    """Top level class for get status mocking"""
    def __init__(self, *args, **kwargs):
        self.status_code = None
        self.ok = False
        self.text = None

    @staticmethod
    def close():
        pass


class MockedPendingStatus(MockedStatus):
    """Class to return a pending status"""
    def __init__(self, *args, **kwargs):
        super().__init__()

    def get_status(self):
        self.ok = True
        return {
            'experiment_id': EXPERIMENT_ID,
            'status': 'PENDING',
            'timestamp': 1686143323.307925
        }

    def json(self):
        return self.get_status()


class MockedCompleteStatus(MockedStatus):
    """Class to return a complete status"""
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.json = self.get_status()

    def get_status(self):
        self.ok = True
        return {
            'experiment_id': EXPERIMENT_ID,
            'status': 'Complete',
            'timestamp': 1686143323.307925
        }


class MockedResults:
    """Mocking class to return a results json object"""
    def __init__(self):
        self.json = {'0': 0.75, '1': 0.25}
        self.status_code = None

    def close(self):
        pass


def extract_token_from_header(headers: dict[dict[str]]):
    """Get auth token from an HTTP header"""
    bearer = headers.get('headers').get('Authorization')
    return bearer.replace('Bearer ', '')
