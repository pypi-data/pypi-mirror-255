from __future__ import absolute_import


import aia
import json
import logging
import oauthlib
import os
import re
import requests
import time
import yaml

from oauthlib.oauth2 import BackendApplicationClient
from typing import List, Dict
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth


class AoaClient(object):
    DEFAULT_TOKEN_CACHE_FILE_PATH = os.path.join(os.path.expanduser("~/.aoa"), ".token")
    DEFAULT_CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~/.aoa"), "config.yaml")

    def __init__(self, **kwargs):
        """

        Parameters:
           project_id (str): project id(uuid)
           ssl_verify (bool): enable or disable TLS cert validation
           aoa_url (str): aoa api endpoint

           auth_mode (str): device_code|client_credentials|bearer

           If using auth_mode=bearer
           auth_bearer (str): the raw bearer token

           If using auth_mode=client_credentials
           auth_client_id (str): oauth2 client id
           auth_client_secret (str): oauth2 client secret
           auth_token_url (str): oauth2 token endpoint

           if using auth_mode=device_code
           auth_client_id (str): oauth2 client id
           auth_client_secret (str): oauth2 client secret
           auth_token_url (str): oauth2 token endpoint
           auth_device_auth_url (str): oauth2 device code endpoint
        """
        self.logger = logging.getLogger(__name__)

        self.project_id = kwargs.get("project_id")
        self.ssl_verify = True
        self.aoa_url = None

        self.auth_mode = None

        self.__client_id = None
        self.__client_secret = None
        self.__token_url = None
        self.__device_auth_url = None
        self.__bearer_token = None

        self.__parse_aoa_config(**kwargs)

        if self.auth_mode == "device_code":
            try:
                self.__create_oauth_session_device_code()
            except oauthlib.oauth2.rfc6749.errors.InvalidGrantError as ge:
                if ge.description in ["Token is not active", "Session not active"]:
                    logging.warning(ge.description + "\nRetrying one more time\n")

                    if os.path.exists(AoaClient.DEFAULT_TOKEN_CACHE_FILE_PATH):
                        os.remove(AoaClient.DEFAULT_TOKEN_CACHE_FILE_PATH)

                    self.__create_oauth_session_device_code()
                else:
                    raise ge
            except oauthlib.oauth2.rfc6749.errors.InvalidTokenError as ge:
                logging.warning(ge.description + "\nRetrying one more time\n")

                if os.path.exists(AoaClient.DEFAULT_TOKEN_CACHE_FILE_PATH):
                    os.remove(AoaClient.DEFAULT_TOKEN_CACHE_FILE_PATH)

                self.__create_oauth_session_device_code()

        elif self.auth_mode == "client_credentials":
            self.__create_oauth_session_client_credentials()

        elif self.auth_mode == "bearer":
            self.__create_oauth_session_bearer()

        elif self.auth_mode is None:
            raise Exception("ModelOps endpoint not configured. " +
                            "Try (re)copy the CLI configuration from ModelOps UI -> Session Details -> CLI Config.")

        else:
            raise Exception(f"Auth mode: {self.auth_mode} not supported.")

    def __parse_aoa_config(self, **kwargs):
        if "config_file" in kwargs:
            self.__parse_yaml(kwargs['config_file'])
        else:
            if os.path.isfile(self.DEFAULT_CONFIG_FILE_PATH):
                self.__parse_yaml(self.DEFAULT_CONFIG_FILE_PATH)

        self.__parse_env_variables()
        self.__parse_kwargs(**kwargs)

    def __parse_yaml(self, yaml_path: str):
        with open(yaml_path, "r") as handle:
            conf = yaml.safe_load(handle)
        self.__parse_kwargs(**conf)

    def __parse_kwargs(self, **kwargs):
        self.aoa_url = kwargs.get("aoa_url", self.aoa_url)
        self.ssl_verify = kwargs.get("ssl_verify", self.ssl_verify)
        self.auth_mode = kwargs.get("auth_mode", self.auth_mode)

        self.__check_legacy_mode()

        if self.auth_mode == "device_code":
            self.__client_id = kwargs.get("auth_client_id", self.__client_id)
            self.__client_secret = kwargs.get("auth_client_secret", self.__client_secret)
            self.__token_url = kwargs.get("auth_token_url", self.__token_url)
            self.__device_auth_url = kwargs.get("auth_device_auth_url", self.__device_auth_url)

        elif self.auth_mode == "client_credentials":
            self.__client_id = kwargs.get("auth_client_id", self.__client_id)
            self.__client_secret = kwargs.get("auth_client_secret", self.__client_secret)
            self.__token_url = kwargs.get("auth_token_url", self.__token_url)

        elif self.auth_mode == "bearer":
            self.__bearer_token = kwargs.get("auth_bearer", self.__bearer_token)

        if "verify_connection" in kwargs:
            self.verify_aoa_connection = kwargs["verify_connection"]

    def __parse_env_variables(self):
        self.aoa_url = os.environ.get("AOA_URL", self.aoa_url)
        self.ssl_verify = os.environ.get("AOA_SSL_VERIFY", str(self.ssl_verify)).lower() == "true"
        self.auth_mode = os.environ.get("AOA_API_AUTH_MODE", self.auth_mode)

        self.__check_legacy_mode()

        if self.auth_mode == "device_code":
            self.__client_id = os.environ.get("AOA_API_AUTH_CLIENT_ID", self.__client_id)
            self.__client_secret = os.environ.get("AOA_API_AUTH_CLIENT_SECRET", self.__client_secret)
            self.__token_url = os.environ.get("AOA_API_AUTH_TOKEN_URL", self.__token_url)
            self.__device_auth_url = os.environ.get("AOA_API_AUTH_DEVICE_AUTH_URL", self.__device_auth_url)

        elif self.auth_mode == "client_credentials":
            self.__client_id = os.environ.get("AOA_API_AUTH_CLIENT_ID", self.__client_id)
            self.__client_secret = os.environ.get("AOA_API_AUTH_CLIENT_SECRET", self.__client_secret)
            self.__token_url = os.environ.get("AOA_API_AUTH_TOKEN_URL", self.__token_url)

        elif self.auth_mode == "bearer":
            self.__bearer_token = os.environ.get("AOA_API_AUTH_BEARER_TOKEN", self.__bearer_token)

    def __check_legacy_mode(self):
        if self.auth_mode == "oauth-cc":
            self.auth_mode = "client_credentials"
        elif self.auth_mode == "oauth":
            self.auth_mode = "device_code"

    def __validate_url(self):
        if not self.aoa_url:
            raise ValueError("ModelOps endpoint not configured. "
                             "Try (re)copy the CLI configuration from ModelOps UI -> Session Details -> CLI Config.")

    def set_project_id(self, project_id: str):
        """
        set project id

        Parameters:
           project_id (str): project id(uuid)
        """
        self.project_id = project_id

    def get_current_project(self):
        """
        get project id

        Return:
           project_id (str): project id(uuid)
        """
        return self.project_id

    def select_header_accept(self, accepts: List[str]):
        """
        converts list of header into a string

        Return:
            (str): request header
        """
        if not accepts:
            return

        accepts = [x.lower() for x in accepts]
        return ', '.join(accepts)

    def get_request(self, path, header_params: Dict[str, str], query_params: Dict[str, str]):
        """
        wrapper for get request

        Parameters:
           path (str): url
           header_params (dict): header parameters
           query_params (dict): query parameters

        Returns:
            dict for resources, str for errors, None for 404
        Raise:
            raises HTTPError in case of error status code other than 404
        """

        self.__validate_url()

        resp = self.session.get(
            url=self.__strip_url(self.aoa_url) + path,
            headers=header_params,
            params=query_params
        )

        if resp.status_code == 404:
            return None

        return self.__validate_and_extract_body(resp)

    def post_request(self, path, header_params: Dict[str, str], query_params: Dict[str, str], body: Dict[str, str]):
        """
        wrapper for post request

        Parameters:
           path (str): url
           header_params (dict): header parameters
           query_params (dict): query parameters
           body (dict): request body

        Returns:
            dict for resources, str for errors
        Raise:
            raises HTTPError in case of error status code
        """

        self.__validate_url()

        resp = self.session.post(
            url=self.__strip_url(self.aoa_url) + path,
            headers=header_params,
            params=query_params,
            data=json.dumps(body)
        )

        return self.__validate_and_extract_body(resp)

    def put_request(self, path, header_params: Dict[str, str], query_params: Dict[str, str], body: Dict[str, str]):
        """
        wrapper for put request

        Parameters:
           path (str): url
           header_params (dict): header parameters
           query_params (dict): query parameters
           body (dict): request body

        Returns:
            dict for resources, str for errors
        Raise:
            raises HTTPError in case of error status code
        """

        self.__validate_url()

        resp = self.session.put(
            url=self.__strip_url(self.aoa_url) + path,
            headers=header_params,
            params=query_params,
            data=json.dumps(body)
        )

        return self.__validate_and_extract_body(resp)

    def delete_request(self, path, header_params: Dict[str, str], query_params: Dict[str, str], body: Dict[str, str]):
        """
        wrapper for delete request
        Parameters:
           path (str): url
           header_params (dict): header parameters
           query_params (dict): query parameters
           body (dict): request body
        Returns:
            dict for resources, str for errors
        Raise:
            raises HTTPError in case of error status code
        """

        self.__validate_url()

        resp = self.session.delete(
            url=self.__strip_url(self.aoa_url) + path,
            headers=header_params,
            params=query_params,
            data=json.dumps(body)
        )

        return self.__validate_and_extract_body(resp)

    def __validate_and_extract_body(self, resp):
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if resp.text:
                raise requests.exceptions.HTTPError(f"Error Message: {resp.text}")
            else:
                raise err

        try:
            return resp.json()
        except ValueError:
            return resp.text

    def __strip_url(self, url):
        return url.rstrip('/')

    def __create_oauth_session_device_code(self):
        self.logger.debug("Configuring oauth with device_code grant")

        if self.__client_id is None or self.__token_url is None or self.__device_auth_url is None:
            raise Exception("Missing CLI configuration.\n" +
                            "Please (re)copy the CLI configuration from " +
                            "ModelOps UI -> Session Details -> CLI Config\n")

        token = None
        if os.path.exists(self.DEFAULT_TOKEN_CACHE_FILE_PATH):
            self.logger.debug(f"Loading cached token data from {self.DEFAULT_TOKEN_CACHE_FILE_PATH}")
            with open(self.DEFAULT_TOKEN_CACHE_FILE_PATH, "r") as f:
                token = json.load(f)

        if not token:
            self.session = requests.session()
            self.__set_session_tls()
            token = self.__get_device_code()

        if "refresh_token" in token:
            self.logger.debug(f"Token acquired successfully: {token}")

            session = OAuth2Session(client_id=self.__client_id)

            # don't chase certs/print warning for TLS if already done for __get_device_code
            if hasattr(self, "session"):
                session.verify = self.session.verify
                self.session = session
            else:
                self.session = session
                self.__set_session_tls()

            self.session.refresh_token(token_url=self.__token_url,
                                       refresh_token=token["refresh_token"],
                                       auth=HTTPBasicAuth(self.__client_id, self.__client_secret),
                                       verify=self.ssl_verify)

            with open(self.DEFAULT_TOKEN_CACHE_FILE_PATH, "w") as f:
                json.dump(token, f)

        else:
            raise Exception(f"Token does not contain access_token. Received {self.token}")

    def __create_oauth_session_client_credentials(self):
        self.logger.debug("Configuring oauth with client_credentials grant")

        if self.__client_id is None or self.__client_secret is None or self.__token_url is None:
            raise Exception("AOA_API_AUTH_CLIENT_ID, AOA_API_AUTH_CLIENT_SECRET, "
                            "AOA_API_AUTH_TOKEN_URL must be defined "
                            "with AOA_API_AUTH_MODE of 'client_credentials'")

        self.session = OAuth2Session(client=BackendApplicationClient(client_id=self.__client_id))
        self.__set_session_tls()
        self.session.fetch_token(token_url=self.__token_url,
                                 auth=HTTPBasicAuth(self.__client_id, self.__client_secret),
                                 verify=self.ssl_verify)

    def __create_oauth_session_bearer(self):
        self.session = requests.session()
        self.session.headers.update({"Authorization": self.__bearer_token})
        self.__set_session_tls()

    def __get_device_code(self):
        device_code_response = self.session.post(
            self.__device_auth_url,
            data={
                "client_id": self.__client_id,
                "scope": "openid profile"
            }
        )

        if device_code_response.status_code != 200:
            raise Exception(f"Error generating the device code. Received code {device_code_response.status_code}.")

        device_code_data = device_code_response.json()
        print("1. On your computer or mobile device navigate to: ", device_code_data['verification_uri_complete'])
        print("2. Enter the following code: ", device_code_data["user_code"])

        authenticated = False
        while not authenticated:
            print("Waiting for device code to be authorized...")
            token_response = self.session.post(
                self.__token_url,
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code_data["device_code"],
                    "client_id": self.__client_id
                }
            )

            token_data = token_response.json()
            if token_response.status_code == 200:
                authenticated = True

            elif "error" in token_data:
                if token_data["error"] in ("authorization_pending", "slow_down"):
                    time.sleep(device_code_data['interval'])
                else:
                    raise Exception(token_data["error_description"])

            else:
                raise Exception(f"Bad response code {token_response.status_code}")

        return token_data

    def __set_session_tls(self):
        self.session.verify = self.ssl_verify
        if self.ssl_verify:
            self.__chase_tls_cert_chain()
        else:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning

            self.logger.warning("Certificate validation disabled. Adding certificate verification is strongly advised")
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def __chase_tls_cert_chain(self):
        if self.aoa_url.startswith("https") and not (
                "REQUESTS_CA_BUNDLE" in os.environ or "CURL_CA_BUNDLE" in os.environ):

            try:
                if re.search('http|https', self.aoa_url):
                    requests.get(f"{self.aoa_url}/admin/info")
                else:
                    raise Exception("Invalid AOA_URL")
            except requests.exceptions.SSLError:
                from aia import AIASession
                from tempfile import NamedTemporaryFile

                self.logger.debug("Attempting certificate chain chasing via aia")

                # unless, debug logging enabled,
                # change logging level for aia to warning as it prints debug at info level
                if logging.root.level > logging.DEBUG:
                    logging.getLogger("aia").setLevel(logging.WARNING)

                try:
                    aia_session = AIASession()

                    ca_data = aia_session.cadata_from_url(self.aoa_url)
                    with NamedTemporaryFile("w", delete=False) as pem_file:
                        pem_file.write(ca_data)
                        pem_file.flush()

                    self.session.verify = pem_file.name
                except aia.InvalidCAError:
                    raise Exception("Attempted to find trusted root certificate via AIA chasing but not found.\n"
                                    "Please configure REQUESTS_CA_BUNDLE or CURL_CA_BUNDLE.\n"
                                    "Alternatively, to ignore TLS validation (not advised), export AOA_SSL_VERIFY=false")
