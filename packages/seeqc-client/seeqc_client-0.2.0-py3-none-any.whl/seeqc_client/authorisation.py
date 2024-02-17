from functools import wraps
from time import sleep
from pathlib import Path
from typing import Union

import requests


class Authorisation:
    """Authenticating with auth server"""

    def __init__(self, url=None):
        self.access_token = None
        self.refresh_token = None
        self.header = None
        self.urls = url
        if url is None:
            self.url = 'https://api.seeqc.cloud'

    def authenticate(self, credentials: dict = None, refresh_token_path: Union[Path, str] = None):
        """Exchange credentials for tokens"""
        response = self._auth_request_from_cred_or_token(credentials, refresh_token_path)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get('access')
            self.refresh_token = tokens.get('refresh')
            self.construct_header()
            print('\nAuthentication successful')
        else:
            print('Invalid credentials')
        return response.status_code

    def refresh(self) -> bool:
        """Refresh the access token and retry on failure"""
        retries = 3
        for _ in range(retries):
            is_refreshed = self.is_valid_refresh_attempt()
            if is_refreshed:
                return True
            else:
                sleep(0.5)
        print('Request could not be made')
        return False

    def is_valid_refresh_attempt(self) -> bool:
        """Refresh access token and return boolean indication success"""
        auth_url = self.url
        response = requests.post(auth_url + '/api/v1/refresh', data={'refresh': self.refresh_token})
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get('access')
            self.refresh_token = tokens.get('refresh')
            self.construct_header()
            return True
        return False

    def update_urls(self, url):
        self.url = url

    def construct_header(self):
        """Construct header in format for api gateway"""
        self.header = {"Authorization": f"Bearer {self.access_token}"}

    def request_handler(self, request_function: callable) -> callable:
        """Decorator function for API calls. Discovers API url when not specified and constructs auth header"""
        @wraps(request_function)
        def decorated_fn(*args, **kwargs):
            if 'url' not in kwargs:
                kwargs['url'] = self.url
            response = request_function(*args, **kwargs, headers=self.header)
            response.close()
            if response.status_code == 401:
                if self.refresh():
                    response = request_function(*args, **kwargs, headers=self.header)
                else:
                    print('Your authenticated session has expired and this client is unable to reauthenticate. '
                          'Please try reinstantiating the client.')
            return response
        return decorated_fn

    def gen_refresh_token(self, credentials: dict, refresh_token_path: Union[Path, str]):
        """Function used to generate a user token that can later be used for authentication"""
        auth_url = self.url
        response = requests.post(auth_url+'/api/v1/authenticate', data=credentials)
        if response.status_code == 200:
            print('\nAuthentication successful, retrieving refresh token')
            tokens = response.json()
            refresh_token = tokens.get('refresh')
            with open(refresh_token_path, 'w') as f:
                f.write(refresh_token)
        else:
            raise PermissionError('Invalid credentials')

    def _auth_request_from_cred_or_token(self, credentials: dict = None,
                                                refresh_token_path: Union[Path, str] = None):
        """Create and submit a post request to authenticate using either credentials or a token"""
        if (credentials is None) and (refresh_token_path is None):
            raise ValueError("Need to specify an authentication method: either credentials or refresh token")
        if (credentials is not None) and (refresh_token_path is not None):
            raise ValueError("Can't specify both credentials and a refresh token during authentication")
        auth_url = self.url
        response = None
        if credentials is not None:
            response = requests.post(auth_url+'/api/v1/authenticate', data=credentials)
        else:
            assert refresh_token_path is not None
            with open(refresh_token_path, 'r') as f:
                refresh_token_str = f.read()
                refresh_token_data = {'refresh': refresh_token_str}
                response = requests.post(auth_url+'/api/v1/refresh', data=refresh_token_data)
        return response
