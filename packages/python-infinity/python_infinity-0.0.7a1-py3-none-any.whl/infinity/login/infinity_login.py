import logging
import os
import threading
import traceback
import requests
from eth_account.messages import encode_structured_data
from requests import JSONDecodeError
from urllib3.exceptions import ProtocolError
from web3.auto import w3
from infinity.login import constants
from infinity.login.client_exceptions import *
from infinity.utils import RepeatTimer, get_default_logger, get_current_utc_timestamp


class LoginClient:
    """
    Client for handling Infinity login and authentication.

    Attributes:
        _login_success (bool): Whether login was successful or not
        _session (requests.Session): HTTP session
        _access_token (str): Access token from login
        _refresh_interval (int): Interval to refresh access token
        _re_login_interval (int): Interval to re-login

    """

    def __init__(self, rest_url: str, chain_id: str, account_address: str, private_key: str,
                 verify_tls: bool = True, refresh_interval: int = 3600, re_login_interval: int = 604800,
                 user_agent: str = None, logger: logging.Logger = None):
        """
        Initialize the LoginClient.

        Args:
            rest_url (str): Base URL for Infinity REST API
            chain_id (str): Chain ID
            account_address (str): Account address
            private_key (str): Private key
            verify_tls (bool, optional): Verify TLS certs. Defaults to True.
            refresh_interval (int, optional): Refresh interval in seconds.
                                              Refer to JWT access token expiring days (default: 3600 seconds = 1 hour)
            re_login_interval (int, optional): Re-login interval in seconds. (default: 604800 seconds = 7 days)
            user_agent (str, optional): User agent string. Defaults to None.
            logger (logging.Logger, optional): Logger. Defaults to None.

        """
        self._login_success = False
        self.__user_agent = user_agent
        self._logger = logger
        self._account_address = account_address
        self.__private_key = private_key
        self.__verify_tls = verify_tls

        self._session = None
        self._access_token = None
        self._last_refresh_timestamp = None
        self._refresh_interval = refresh_interval
        self._re_login_interval = re_login_interval
        self.__re_login_lock = threading.Lock()
        self.__refresh_lock = threading.Lock()
        self.__refresh_event = None
        self.__re_login_event = None

        if logger is None:
            self._logger = get_default_logger()

        if self.__user_agent is None:
            self.__user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/109.0.0.0 Safari/537.36")

        self._API_BASE_URL = rest_url
        self._chain_id = chain_id
        # public session for login
        self._session = self.init_session()
        self.do_login()

    def init_session(self) -> requests.Session:
        """
        Initialize an Infinity Login HTTP session.

        Creates and configures a requests Session object to be used for making
        API calls to the Infinity Login endpoints.

        Sets up the session with proper headers, TLS verification, and the
        user agent string.

        Returns:
            requests.Session: The configured HTTP session object.

        """
        self._logger.info("Initializing HTTP session for Infinity Login.")
        session = requests.Session()
        session.verify = self.__verify_tls
        return session

    def close_session(self) -> None:
        """
        Close the Infinity Login HTTP session.

        Closes the requests Session used for making API calls to Infinity Login.
        This should be called when done interacting with Infinity Login to free up resources.

        """
        self.__refresh_event.cancel()
        self.__re_login_event.cancel()
        if self.is_refreshing_token():
            self.__refresh_lock.release()
        if self.is_re_logging_in():
            self.__re_login_lock.release()
        self._session.close()
        self._logger.info("HTTP session closed for Infinity Login.")

    def __send_auth_request(self, method: str, **kwargs) -> dict | Exception:
        headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": self.__user_agent}
        if self._access_token is not None:
            headers["Authorization"] = f"Bearer {self._access_token}"
        call = getattr(self._session, method)
        response = call(**kwargs, headers=headers)
        return self._handle_response(response=response)

    def is_login_success(self) -> bool:
        """
        Check if login was successful.

        Returns:
            bool: True if login succeeded, False otherwise.

        """
        return self._login_success

    @property
    def account_address(self) -> str:
        """
        Return the user's account address.

        This returns the user's public blockchain address that is currently connected to the Infinity exchange.

        Returns:
            self._account_id: Account ID. For example:

                '0x0123456789abcdef0123456789abcdef01234567'

        """
        return self._account_address

    @property
    def private_session(self) -> requests.Session:
        return self._session

    # Login/ Logout

    def do_login(self) -> None:
        """
        Perform login and get access token.

        Sends login request using the given blockchain address and chain id.
        And saves access token if login succeeds.

        Raises:
            LoginError: If login failed.

        """
        start_t = get_current_utc_timestamp()
        if self.__private_key is None:
            self._logger.error("please provide private key. exit.")
            os._exit(1)
        nonce = None
        eip712_message = None
        signature = None
        # region get user login verify info
        try:
            body = {constants.ADDRESS: self._account_address, constants.CHAIN_ID: self._chain_id}
            url = self._API_BASE_URL + constants.LOGIN_ENDPOINT
            verify_info = self.__send_auth_request("post", url=url, data=body)
            nonce = verify_info.get("nonceHash", None)
            eip712_message = verify_info.get("eip712Message", None)
            if nonce is None or eip712_message is None:
                raise Exception
        except Exception as e:
            self._logger.fatal(f"Cannot get verify information to login, Error: {e}")
            os._exit(1)
        # endregion
        # region get user signature
        try:
            encoded_message = encode_structured_data(text=eip712_message)
            signed_message = w3.eth.account.sign_message(encoded_message, private_key=self.__private_key)
            signature = w3.to_hex(signed_message.signature)
        except Exception as e:
            self._logger.fatal(f"Fail to get login signature, Error:{e}")
            os._exit(1)
        # endregion
        # region sign in with user signature and get access token
        try:
            body = {constants.ADDRESS: self._account_address, constants.NONCE_HASH: nonce,
                    "signature": signature}
            url = self._API_BASE_URL + constants.VERIFY_LOGIN_ENDPOINT
            login_info = self.__send_auth_request("post", url=url, data=body)
            self._access_token = login_info.get("accessToken", {}).get("token", None)
            if self._access_token is None:
                self._logger.error("Fail to get access token when login")
                raise Exception
            self._last_refresh_timestamp = get_current_utc_timestamp()
            self._login_success = True
            time_spent = get_current_utc_timestamp() - start_t
            self._logger.info(f"User logged in, time spent = {time_spent} seconds.")
            self.after_login()
        except Exception as e:
            self._logger.error(f"Cannot get user login info.", exc_info=e)
            os._exit(1)
        # endregion

    def after_login(self) -> None:
        """
        Set up repeat timer for refresh access token event and re-login event
        """
        if self._login_success:
            if self.__refresh_event is None:
                self.__refresh_event = RepeatTimer(self._refresh_interval, self.refresh_access_token)
                self.__refresh_event.start()
            if self.__re_login_event is None:
                self.__re_login_event = RepeatTimer(self._re_login_interval, self.re_login)
                self.__re_login_event.start()

    def is_refreshing_token(self):
        """
        Check if access token refresh is in progress.

        Checks if another thread is currently refreshing the access token.

        Returns:
            bool: True if refresh in progress, False otherwise.

        """
        return self.__refresh_lock.locked()

    def is_re_logging_in(self):
        """
        Check if re-login is in progress.

        Checks if another thread is currently re-logging in to get a new access token.

        Returns:
            bool: True if re-login in progress, False otherwise.

        """
        return self.__re_login_lock.locked()

    def re_login(self) -> None:
        """
        Re-login to Infinity Exchange.

        Performs full login flow to re-login and retrieve a new access token.
        Saves new access token if re-login succeeds.

        Raises:
            LoginError: If re-login failed.

        """
        if self.is_re_logging_in():
            self._logger.debug("infinity login client is re-logging in, ignore duplicate re-login request.")
        else:
            self._logger.info("re-logging in...")
            with self.__re_login_lock:
                start_t = get_current_utc_timestamp()
                try:
                    self.__refresh_event.cancel()
                    self.__refresh_lock.release()
                    self.__refresh_event = None
                    self._login_success = False
                    self.do_login()
                except Exception as e:
                    self._logger.error("cannot re-login", exc_info=e)
                finally:
                    time_spent = get_current_utc_timestamp() - start_t
                    self._logger.debug(f"re-logged in, time spent = {time_spent} seconds")

    def get_access_token(self) -> str:
        """
        Get current access token.

        Returns:
            str: The access token string.

        """
        return self._access_token

    def get_last_refresh_timestamp(self) -> float:
        """
        Get last access token refresh utc timestamp. Login/re-login will update the timestamp as well.

        Returns:
            float: last access token refresh utc timestamp
        """
        return self._last_refresh_timestamp

    def get_refresh_interval(self) -> int:
        """
        Get the refresh interval for the access token.

        Returns:
            int: The refresh interval in seconds.

        """
        return self._refresh_interval

    @property
    def chain_id(self):
        """
        Get the chain ID.

        Returns:
            str: The chain ID.

        """
        return self._chain_id

    def refresh_access_token(self) -> None:
        """
        Refresh access token to extend expiration.

        Sends refresh token request to get new access token.
        Saves new token if refresh succeeds.

        Raises:
            RefreshError: If refresh request failed.

        """
        if self.is_re_logging_in():
            self._logger.info("re-logging in user, ignore access token refresh.")
        elif self.is_refreshing_token():
            self._logger.debug("access token is refreshing, ignore duplicate access token refresh request")
        elif self._access_token is None:
            self._logger.error(f"cannot find access token to refresh. Error: {traceback.format_exc()}")
        else:
            with self.__refresh_lock:
                start_t = get_current_utc_timestamp()
                try:
                    body = {constants.REFRESH_TOKEN: self._access_token}
                    url = self._API_BASE_URL + constants.REFRESH_ENDPOINT
                    refresh_info = self.__send_auth_request("post", url=url, data=body)
                    self._access_token = refresh_info.get("accessToken", {}).get("token", None)
                    if self._access_token is None:
                        self._logger.error("Fail to get refreshed access token")
                        raise Exception
                    self._last_refresh_timestamp = get_current_utc_timestamp()
                    time_spent = get_current_utc_timestamp() - start_t
                    self._logger.info(f"refreshed JWT token, time spent = {time_spent} seconds.")
                    self._login_success = True
                except Exception as e:
                    self._logger.error("cannot refresh access token in Infinity Login", exc_info=e)

    def _handle_response(self, response: requests.Response) -> dict | Exception:
        """
        Handle response from Infinity's REST APIs

        This handles the response from Infinity's REST APIs before returning to the user. If the response is successful,
        the data portion (if available) of the response is returned, otherwise the whole response. If the response
        is not successful a relevant error is raised. The response returned is in the json format.

        Args:
            response: The response from a call to an Infinity REST API (typically done through our public functions in
            this python file).

        Returns:
            response: The data portion (in json format) of the Infinity REST API response if available; the entire
                response (in json format) otherwise.

        """
        try:
            if not str(response.status_code).startswith("2"):
                trace_msg = traceback.format_exc()
                error_message = (" - request to Infinity Exchange failed, " +
                                 f"full response {response.text}, traceback: {trace_msg}")
                if str(response.status_code) == "400":
                    raise BadRequestError(response=response,
                                          message="Bad request error [400]" + error_message)
                elif str(response.status_code) == "401":
                    raise UnauthorizedError(response=response,
                                            message="Unauthorized error [401]" + error_message)
                elif str(response.status_code) == "403":
                    raise ForbiddenError(response=response,
                                         message="Forbidden error [403]" + error_message)
                elif str(response.status_code) == "500":
                    raise InternalServerError(response=response,
                                              message="Internal server error [500]" + error_message)
                elif str(response.status_code) == "503":
                    raise ServiceUnavailableError(response=response,
                                                  message="Service unavailable error [503]" + error_message)
                else:
                    raise UnknownError(response=response,
                                       message=f"Unknown error [{str(response.status_code)}]" + error_message)

            res = response.json()
            response_success = res.get("success", None)

            if response_success is not None:
                if response_success is False:
                    error_code = res["errorCode"]
                    error_msg_key = res["errorMsgKey"]
                    raise RequestErrorCodeError(response=response, error_code=error_code, error_msg_key=error_msg_key,
                                                message=f"Infinity request unsuccessful - Check the error code and "
                                                        f"error message key for details. {error_code=}, "
                                                        f"{error_msg_key=}.")

            # by default return full response, unless it has the "data" attribute, then this is returned
            if "data" in res:
                res = res["data"]
            return res
        except (ProtocolError, requests.exceptions.ConnectionError) as e:
            self._logger.error(f"Login session fail to send request due to connection issue, error = {e}")
            raise e
        except (ValueError, JSONDecodeError) as e:
            self._logger.error(f"Error occurs when handling login response = {response.text}", exc_info=e)
            raise e
        except Exception as e:
            self._logger.error(f"Unknown error occurs when handling login response = {response.text}", exc_info=e)
            raise e
