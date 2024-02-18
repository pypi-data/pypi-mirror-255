import logging
import time
import traceback
from datetime import date, timedelta
from typing import List
from uuid import uuid4
from warnings import warn

import requests
from requests.exceptions import JSONDecodeError
from urllib3.exceptions import ProtocolError

import infinity.rest_client.constants as constants
from infinity.login.infinity_login import LoginClient
from infinity.rest_client.client_exceptions import *
from infinity.utils import generate_query_url, get_default_logger


class RestClient:
    """
    The main REST API client class

    With this client class you can connect to, and communicate with, the Infinity exchange,
    to request market data, send orders and receive execution information etc.
    """

    def __init__(self, rest_url: str, login: LoginClient = None, user_agent: str = None,
                 verify_tls: bool = True, logger: logging.Logger = None):
        """
        Initializes the instance of the client class.

        Args:
          rest_url (str): REST URL; exchange base url
          login (LoginClient): login to use private REST API
          user_agent (str): You can explicitly set the user agent here. (Default is None.) If no user_agent is
          specified, then internally the following user_agent is used:
          Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0
          Safari/537.36
          verify_tls (bool): Whether to use TLS (Transport Layer Security) when making API requests to the Infinity
          Exchange. This should usually be set to True, which is the default value, so shouldn't need to be explicitly
          specified. (Default is True.)
          logger (logging.Logger): Your choice of logger. (Default is None.)
        """
        self._user_agent = user_agent
        self._verify_tls = verify_tls
        self._logger = logger

        self._inf_login = login
        self._access_token = None

        self._order_id_map = {}

        if logger is None:
            self._logger = get_default_logger()

        if self._user_agent is None:
            self._user_agent = ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                                "Chrome/72.0.3626.119 Safari/537.36")

        self._API_BASE_URL = rest_url

        self._public_session = self._init_public_session()

        if self._inf_login:
            self._logger.info("Initializing HTTP session for Infinity REST Private...")
            if self._inf_login.is_login_success():
                self._logger.info("Infinity REST Private session is created")
                self._account_id = self.get_account_id()
            else:
                self._logger.warning("cannot login, please check login details")

    def _handle_response(self, response: requests.Response, is_private: bool) -> dict | Exception:
        """
        Handle response from Infinity's REST APIs

        This handles the response from Infinity's REST APIs before returning to the user. If the response is successful,
        the data portion (if available) of the response is returned, otherwise the whole response. If the response
        is not successful a relevant error is raised. The response returned is in the json format.

        Args:
            response: The response from a call to an Infinity REST API (typically done through our public functions in
            this python file).
            is_private (bool): Whether the response is from a private API call or not.

        Returns:
            response: The data portion (in json format) of the Infinity REST API response if available; the entire
                response (in json format) otherwise.

        """
        key = "private" if is_private else "public"
        try:
            if not str(response.status_code).startswith("2"):
                trace_msg = traceback.format_exc()
                error_message = (f" - {key} request to Infinity Exchange failed, " +
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
            response = self._parse_orders(response=res)
            return response
        except (ProtocolError, requests.exceptions.ConnectionError) as e:
            self._logger.error(f"{key} REST session fail to send request due to connection error={e}")
            raise e
        except (ValueError, JSONDecodeError) as e:
            self._logger.error(f"Error occurs when handling REST {key} response = {response.text}", exc_info=e)
            raise e
        except Exception as e:
            self._logger.error(f"Unknown error occurs when handling REST {key} response = {response.text}", exc_info=e)
            raise e

    def _send_request(self, is_private: bool, method: str, **kwargs) -> dict | Exception:
        key = "private" if is_private else "public"
        try:
            headers = {"Content-Type": "application/json", "User-Agent": self._user_agent}
            if is_private:
                current_session = self._inf_login.private_session
                while self._inf_login.is_re_logging_in() or self._inf_login.is_refreshing_token():
                    time.sleep(0.001)
                headers.update({"Authorization": "Bearer " + self._inf_login.get_access_token()})
            else:
                current_session = self._public_session
            call = getattr(current_session, method)
            response = call(**kwargs, headers=headers)
            return self._handle_response(response=response, is_private=is_private)
        except Exception as e:
            self._logger.error(f"{key} REST session fail to send request", exc_info=e)
            raise e

    @staticmethod
    def _replace_placeholder_with_value(url: str, placeholder_constant: str, value: str):
        """
        Replace URL placeholder with actual value.

        This helper function replaces a placeholder in a URL with the desired actual value.

        Args:
            url (str): URL string.
            placeholder_constant (str): Original value in the string.
            value (str): New value to replace the original value in the string.

        Returns:
            str: The URL with the placeholder replaced with the desired value.

        """

        return url.replace(placeholder_constant, value)

    # *** Authentication ***
    def login_success(self) -> bool:
        """
        Check if login was successful.

        Returns:
            bool: True if login succeeded, False otherwise.
        """
        return self._inf_login.is_login_success()

    def _init_public_session(self):
        """
        Initialize the public API session.

        Creates a Requests Session for making unauthenticated
        API calls to public endpoints.

        Configures the session with the base URL, TLS verification,
        and user agent as needed.

        Returns:
            requests.Session: The configured public session.
        """
        self._logger.info("Initializing HTTP session for Infinity REST Public...")
        session = requests.Session()
        session.verify = self._verify_tls
        self._logger.info("Infinity REST Public session is created.")
        return session

    def _close_session(self):
        """
        Close the private API session.

        Closes the Requests Session used for authenticated
        API calls. Should be called when done using the
        private APIs.
        """
        if self._inf_login.is_login_success():
            self._logger.debug("Closing private session...")
            self._inf_login.close_session()
        self._logger.debug("Closing public session...")
        self._public_session.close()
        self._logger.debug("HTTP session closed.")

    # *** Funding ***

    def deposit(self, limit: int = 20, start_block_id: int | None = None) -> dict:
        """
        Deposit assets to the user's account.

        Args:
            limit (int): the number of user deposit requests
            start_block_id (int): the block id of user deposit request

        Returns:
            dict: The API response containing details of the deposit.
        """
        url = self._API_BASE_URL + constants.PRIVATE_DEPOSIT_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_LIMIT: limit}

        if start_block_id is not None:
            dict_query_params.update({constants.QUERY_KEY_START_BLOCK_ID: start_block_id})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_withdraw_status(self, request_ids: list[int]) -> dict:
        """
        Get fund withdrawal request status (for given list of request IDs).

        Args:
           request_ids (list): List of Fund Withdrawal Request IDs, e.g. ["123", "456"]

        Returns:
           dict: Dictionary containing the status of the fund withdrawal requests, with the following structure:

           {
               "success": true,
               "data": {
                   "requests": [{...}]
               }
           }
        """
        if len(request_ids) == 0:
            self._logger.error("get_withdraw_status request_ids cannot be empty.")
            return {}
        url = self._API_BASE_URL + constants.PRIVATE_GET_WITHDRAW_STATUS_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_REQUEST_IDS: request_ids}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_withdraws(self, limit: int = 20, start_id: int | None = None) -> dict:
        """
        Gets data of fund withdrawals.

        Args:
            start_id (int): Fund Withdrawal Request ID as reference starting point, optional
            limit (int): Limit of Fund withdrawals to be returned, optional

        Returns:
            response: dict of fund withdrawals

            {
               "success": true,
               "data": {
                   "requests": [{...}]
               }
           }

        """

        url = self._API_BASE_URL + constants.PRIVATE_GET_WITHDRAWS_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_LIMIT: limit}
        if start_id is not None:
            dict_query_params.update({constants.QUERY_KEY_START_ID: start_id})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def withdraw(self, token_id: int, quantity: float, chain_id: int = 1) -> dict:
        """
        Withdraw funds from the exchange.

        Args:
          token_id (int): The ID of the token to withdraw.
          quantity (float): The quantity of tokens to withdraw.
          chain_id (int, optional): The chain ID. Defaults to 1.

        Returns:
          dict: The API response containing details of the withdrawal.
        """

        url = self._API_BASE_URL + constants.PRIVATE_WITHDRAW_ENDPOINT
        data = {
            constants.QUERY_KEY_TOKEN_ID: token_id,
            constants.QUERY_KEY_QUANTITY: quantity,
            constants.QUERY_KEY_CHAIN_ID: chain_id
        }
        return self._send_request(is_private=True, method="post", url=url, json=data)

    def get_blockchain_info(self, blockchain_id: int) -> dict:
        """
        Get blockchain details for a given blockchain id.

        This gets the blockchain details for a given, Infinity designated, blockchain id. At the time of writing, the
        Infinity exchange only supports one blockchain, Ethereum, which has a blockchain id value of 1.

        Args:
            blockchain_id: The Infinity exchange id for a particular blockchain. At the time of writing, only a value of
            1, for Ethereum, is supported.

        Returns:
            response: Session response from requesting blockchain details. For example:

            {'blockChain': {'name': 'Ethereum',
                'processedBlockNum': 15402679,
                'processedBlockHash': '0x4e99a2a28a0963a8bde5960e06071d8880c0ebb09353981b47322294af227834'}}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_BLOCKCHAIN_INFO_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_BLOCKCHAIN_ID: blockchain_id})
        return self._send_request(is_private=False, method="get", url=url)

    # *** Markets ***

    def get_market_mtms(self, account_id: int | None = None) -> dict:
        """
        Get user's fixed positions marked to market by account id.

        This gets the user's fixed positions, marked to market, for a given account id.
        If no account id is specified, then the user's trading account is used.

        Args:
          account_id (int): Account ID (Default is None.)

        Returns:
          response (dict): Session response from requesting the user's marked to market fixed positions for a given
          account id. For example:
          {
            "mtm": [
                {
                    "accountId": 202,
                    "marketId": 1,
                    "instrumentId": "ETH-SPOT",
                    "tokenId": 1,
                    "mtm": "-282.981195038"
                },
                {
                    "accountId": 202,
                    "marketId": 12006,
                    "instrumentId": "ETH-2023-12-01",
                    "tokenId": 1,
                    "mtm": "-42.970918771015334",
                    "maturityDate": 1701417600000
                },...]
        }
        """
        if account_id is None:
            account_id = self._account_id

        url = self._API_BASE_URL + constants.PRIVATE_GET_MARKET_MTMS_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_ACCOUNT_ID: account_id})
        return self._send_request(is_private=True, method="get", url=url)

    def get_market_summaries(self, token_id: int, fixed_rate_instrument_ids: list[str] | None = None,
                             min_bid_ask_size: int | None = None) -> dict:
        """
        Get orderbook summary by token id.

        This gets the current orderbook summary for a given token id. The floating rate is always provided. If
        any fixed_rate_instrument_ids are specified, they will also be included; otherwise *all* fixed rate markets will
        be included alongside the floating rate. If min_bid_ask_size is specified then only the best bid or ask
        order level containing at least this amount will be returned.

        In addition to the same information provided by the function get_current_best_bid_ask_by_token_id() this
        function also returns summary position, DV01 and carry values, as well as position (for both fixed and
        floating), carry (floating only) and PV01 & DV01 (fixed only) values for each market.

        Args:
            token_id (int): Token ID
            fixed_rate_instrument_ids (list[str]): List of fixed rate instrument ID. (Default value is None.)
            min_bid_ask_size (int): Minimum bid ask size. (Default value is 0.)

        Returns:
            response: Session response from requesting the orderbook summary for a given token id. For example:

            {
                "summary": {
                    "position": "-1663900.499",
                    "dv01": "-37.06615241628705619",
                    "carry": "-109412.515206378184334876"
                },
                "ir": {
                    "marketId": 1,
                    "instrumentId": "ETH-SPOT",
                    "bid": "0.0184",
                    "bidQuantity": "42.3415",
                    "bidStepSize": "2",
                    "ask": "0.0194",
                    "askQuantity": "62.6592",
                    "askStepSize": "2",
                    "position": "-702938.5559",
                    "carry": "-12934.06942856"
                },
                "fr": [
                    {
                        "marketId": 11986,
                        "instrumentId": "ETH-2023-11-28",
                        "name": "ETH-1D",
                        "daysToMaturity": 1,
                        "bid": "0",
                        "bidQuantity": "0",
                        "bidStepSize": "2",
                        "ask": "0",
                        "askQuantity": "0",
                        "askStepSize": "2",
                        "position": "0",
                        "pv01Series": "0.000000273957",
                        "dv01": "0"
                    },...]
            }

        """
        url = self._API_BASE_URL + constants.PRIVATE_GET_MARKET_SUMMARIES_ENDPOINT
        if min_bid_ask_size is None:
            min_bid_ask_size = 2

        dict_query_params = {
            constants.QUERY_KEY_TOKEN_ID: token_id,
            constants.QUERY_KEY_MIN_BID_N_ASK_SIZE: min_bid_ask_size
        }

        if fixed_rate_instrument_ids is not None:
            dict_query_params.update({constants.QUERY_KEY_LIST_FIXED_RATE_INSTRUMENT_IDS: fixed_rate_instrument_ids})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_all_markets(self) -> dict:
        """
        Retrieves all markets from the REST API.

        Returns:
            A list of market objects, where each object contains the following attributes:
            - instrument_id: The unique identifier of the market.
            - market_name: The name of the market.
            - market_type: The type of the market (e.g., stocks, cryptocurrencies).
            - market_status: The current status of the market (e.g., open, closed).

        Raises:
            APIException: If there is an error while making the API request.

        Example:
            {
                "markets": [
                    {
                        "marketId": 1,
                        "tokenId": 1,
                        "quantityStep": "0.0001",
                        "minQuantity": "0.0001",
                        "maxQuantity": "100000",
                        "rateStep": "0.0001",
                        "category": 1,
                        "takerFeeRate": "0.0001",
                        "makerFeeRate": "0.001",
                        "interestFeeRate": "0.0513",
                        "enable": "True",
                        "borrowPriceIndex": "1.0436041980657",
                        "lendPriceIndex": "1.0433127067136",
                        "priceIndexDate": 1701057900000,
                        "rate": "0.0184",
                        "updateDate": 1701057901000,
                        "direction": "False",
                        "actualRate": "0.0184",
                        "name": "ETH SPOT",
                        "instrumentId": "ETH-SPOT",
                        "high24": "0",
                        "low24": "0",
                        "volume24": "0",
                        "rate24": "0",
                        "totalValue": "0",
                        "deposits": 133893,
                        "borrows": 11534,
                        "subscriptions": "790668.72898"
                    },...
                ]
            }

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_ALL_MARKETS_ENDPOINT
        return self._send_request(is_private=False, method="get", url=url)

    def get_all_order_buckets(self, instrument_ids: list[str]) -> dict:
        """
        Get orders (floating and fixed) in rate buckets for a given token ID and list of fixed rate instrument IDs

        Args:
            instrument_ids (list<str>): List of instrument ids

        Returns:
            dict of rate buckets, grouped by instrument id. For example:
            {
                "rateBuckets": [
                    {
                        "marketId": 11991,
                        "instrumentId": "ETH-2023-11-28",
                        "rate": "0.0349",
                        "quantity": "1.8744",
                        "side": "True"
                    },...
                ]
            }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_ALL_ORDER_BUCKETS_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_INSTRUMENT_IDS: instrument_ids}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_bba(self, token_id: int, fixed_rate_instrument_ids: list[str] | None = None,
                min_bid_ask_size: int = 0) -> dict:
        """
        Get current best bid & ask by token id.

        This gets the current best bid and ask rates for a given token id. The floating rate is always provided. If
        any fixed_rate_instrument_ids are specified, they will also be included; otherwise *all* fixed rate markets will
        be included alongside the floating rate. If min_bid_ask_size is specified then only the best bid or ask
        order level containing at least this amount will be returned.

        Args:
            token_id (int): Token ID
            fixed_rate_instrument_ids (list[str]): List of fixed rate instrument id. (Default value is None.)
            min_bid_ask_size (int): Minimum bid ask size. (Default value is 0.)

        Returns:
            response: Session response from requesting the current best bid and ask rates for a given token id.
            For example:
            {
                "ir": {
                    "marketId": 1,
                    "instrumentId": "ETH-SPOT",
                    "bid": "0.0184",
                    "bidQuantity": "42.3415",
                    "bidStepSize": "0",
                    "ask": "0.0194",
                    "askQuantity": "62.6592",
                    "askStepSize": "0"
                },
                "fr": [
                    {
                        "marketId": 11986,
                        "instrumentId": "ETH-2023-11-27",
                        "name": "ETH-FIXED",
                        "daysToMaturity": 1,
                        "bid": "0",
                        "bidQuantity": "0",
                        "bidStepSize": "0",
                        "ask": "0",
                        "askQuantity": "0",
                        "askStepSize": "0"
                    }
                ]
            }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_BBA_ENDPOINT

        dict_query_params = {
            constants.QUERY_KEY_TOKEN_ID: token_id,
            constants.QUERY_KEY_MIN_BID_N_ASK_SIZE: min_bid_ask_size
        }

        if fixed_rate_instrument_ids is not None:
            dict_query_params.update({constants.QUERY_KEY_LIST_FIXED_RATE_INSTRUMENT_IDS: fixed_rate_instrument_ids})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_all_fixed_details(self, token_id: int | None = None) -> dict:
        """
        Get all/active fixed rate markets by token id

        This gets the active fixed rate markets for a given token id. At the time of writing (although subject to change
        prior to our rollout to MainNet), available token id values are:
                Token id 1 = ETH
                Token id 2 = USDT
                Token id 3 = USDC
                Token id 4 = DAI
                Token id 5 = WBTC

            Tip:
                - Use the function get_token_details() to get a full list of valid token ids.
                - To see which token ids have active markets, use get_floating_rate_market_details().
                - Or visit our developer portal to see the latest set of available token ids.

        Args:
            token_id (int): Token ID

        Returns: response: Session response from requesting active fixed rate markets for a given token. For example:
        {
            "markets": [
                {
                    "marketId": 11986,
                    "tokenId": 1,
                    "instrumentId": "ETH-2023-11-27",
                    "name": "ETH-FIXED",
                    "quantityStep": "0.0001",
                    "minQuantity": "0.0001",
                    "maxQuantity": "100000",
                    "rateStep": "0.0001",
                    "enable": "True",
                    "direction": "False",
                    "daysToMaturity": 1,
                    "updateDate": 1701060305000,
                    "maturityDate": 1701072000000
                },...
            ]
        }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_ALL_FIXED_DETAILS_ENDPOINT
        dict_query_params = {}
        if token_id is not None:
            dict_query_params.update({constants.QUERY_KEY_TOKEN_ID: token_id})
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_all_floating_details(self) -> dict:
        """
        Get floating rate market details.

        This gets both market and token related details for the floating rate markets supported on Infinity exchange.

        Returns: response: Session response from requesting floating rate market details. For example:
        {
            "markets": [
                {
                    "marketId": 1,
                    "tokenId": 1,
                    "quantityStep": "0.0001",
                    "minQuantity": "0.0001",
                    "maxQuantity": "100000",
                    "rateStep": "0.0001",
                    "category": 1,
                    "takerFeeRate": "0.0001",
                    "makerFeeRate": "0.001",
                    "interestFeeRate": "0.0513",
                    "enable": "True",
                    "borrowPriceIndex": "1.0436055811517",
                    "lendPriceIndex": "1.0433140746",
                    "priceIndexDate": 1701060180000,
                    "rate": "0.0184",
                    "updateDate": 1701060181000,
                    "direction": "False",
                    "actualRate": "0.0184",
                    "name": "ETH SPOT",
                    "instrumentId": "ETH-SPOT",
                    "high24": "0",
                    "low24": "0",
                    "volume24": "0",
                    "rate24": "0",
                    "totalValue": "0",
                    "deposits": 133893,
                    "borrows": 11534,
                    "subscriptions": "790668.72898"
                },...]
        }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_ALL_FLOATING_DETAILS_ENDPOINT
        return self._send_request(is_private=False, method="get", url=url)

    def get_fixed_details(self, instrument_id: str) -> dict:
        """
        Get fixed rate market details by instrument id.

        This gets fixed rate market details for a given (fixed rate) instrument id.

        For fixed markets, use the function get_active_fixed_rate_markets_by_token_id() to find currently active
        market ids.

        Args:
            instrument_id (str): Instrument id of the fixed rate market.

        Returns: response: Session response from requesting details for a given fixed rate market. For example:
        {
            "market": {
                "marketId": 11986,
                "tokenId": 1,
                "instrumentId": "ETH-2023-11-27",
                "name": "ETH-FIXED",
                "quantityStep": "0.0001",
                "minQuantity": "0.0001",
                "maxQuantity": "100000",
                "rateStep": "0.0001",
                "enable": "True",
                "direction": "False",
                "daysToMaturity": 1,
                "updateDate": 1701060305000,
                "high24": "0",
                "low24": "0",
                "volume24": "0",
                "rate24": "0",
                "totalValue": "0",
                "maturityDate": 1701072000000
            }
        }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FIXED_DETAILS_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_INSTRUMENT_ID: instrument_id}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_fixed_fees(self, instrument_id: str, order_qty: float) -> dict:
        """
        Get fixed rate transaction fee estimate by instrument id and quantity.

        This returns an estimate provided by the Infinity exchange for a fixed rate transaction for a given instrument id
        based on a given order size.

        Args:
            instrument_id (str): Instrument id of the fixed rate market.
            order_qty (float): Order Quantity

        Returns:
            response: Session response from requesting a fixed rate transaction fee estimate for a given instrument id and
            quantity. For example:

            {'estimatedTrxFee': '0.001'}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FIXED_FEES_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_INSTRUMENT_ID: instrument_id,
                                                             constants.QUERY_KEY_ORDER_QTY: order_qty})
        return self._send_request(is_private=False, method="get", url=url)

    def get_fixed_history(self, instrument_id: str, start: str | None = None, end: str | None = None,
                          interval_minutes: int | None = None) -> dict:
        """
        Get fixed rate market history by instrument id.

        This returns the fixed rate market history for a given instrument id between the specified start and end datetimes,
        bucketed by the specified interval size (in minutes).

        Args:
            instrument_id (str): instrument id of the fixed rate market
            start (str): Start Date (of the form yyyymmdd) or Start Datetime
            end (str): End Date (of the form yyyymmdd) or End Datetime
            interval_minutes: Interval size in minutes for bucketing the returned data. If the interval size is more
            than one day, then it needs to be a multiple of one day; if it is less than one day, then it needs to be
            a multiple of 15 minutes.

        Returns:
            {'date': 20221022,
            'open': '0',
            'close': '0',
            'high': '0',
            'low': '0',
            'volume': '0',
            'totalValue': '309278.7355',
            'lendDepth': 344,
            'borrowDepth': 214}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FIXED_HISTORY_ENDPOINT

        dict_query_params = {constants.INSTRUMENT_ID: instrument_id}

        today = date.today()
        if start is None:
            start = today - timedelta(days=365)  # Default - 1 year ago
        if end is None:
            end = today + timedelta(days=1)  # Default - tomorrow
        if interval_minutes is None:
            interval_minutes = 24 * 60  # Daily

        interval_milliseconds = interval_minutes * 60 * 1000

        dict_query_params.update({constants.QUERY_KEY_START: start.strftime('%Y%m%d')})
        dict_query_params.update({constants.QUERY_KEY_END: end.strftime('%Y%m%d')})
        dict_query_params.update({constants.QUERY_KEY_INTERVAL: interval_milliseconds})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_fixed_orderbook(self, instrument_id: str, limit: int = 10) -> dict:
        """
        Get fixed rate orderbook details by instrument id.

        This gets the fixed rate orderbook details for a given (fixed rate) instrument id.

        For fixed markets, use the function get_active_fixed_rate_markets_by_token_id() to find currently active
        instrument ids.

        Args:
            instrument_id (str): instrument id of the fixed rate market
            limit (int): Limit the number of bids and asks returned. Default is 10.

        Returns:
            response: Session response from requesting orderbook details for a given fixed rate market. For example:

            {'bids': [{'rate': '0.0501', 'quantity': '7.0712'},
                {'rate': '0.0491', 'quantity': '2.548'},
                {'rate': '0.0484', 'quantity': '3.6413'},
                {'rate': '0.0476', 'quantity': '4.0714'},
                {'rate': '0.0473', 'quantity': '3.4771'},
                {'rate': '0.0468', 'quantity': '3.7143'},
                {'rate': '0.0467', 'quantity': '6.4285'},
                {'rate': '0.0461', 'quantity': '2.1954'},
                {'rate': '0.0459', 'quantity': '3.4785'},
                {'rate': '0.0452', 'quantity': '5.809'}],
                'asks': [{'rate': '0.0567', 'quantity': '2.0793'},
                {'rate': '0.0565', 'quantity': '3.0973'},
                {'rate': '0.0559', 'quantity': '2.5663'},
                {'rate': '0.0557', 'quantity': '3.6502'},
                {'rate': '0.0556', 'quantity': '3.3638'},
                {'rate': '0.0553', 'quantity': '2.87'},
                {'rate': '0.0552', 'quantity': '2.4223'},
                {'rate': '0.0549', 'quantity': '3.2074'},
                {'rate': '0.0548', 'quantity': '3.2421'},
                {'rate': '0.0546', 'quantity': '2.5734'}]}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FIXED_ORDERBOOK_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_INSTRUMENT_ID: instrument_id,
                             constants.QUERY_KEY_LIMIT: limit}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_fixed_rate(self, instrument_id: str) -> dict:
        """
        Get latest fixed rate market info by instrument id.

        This gets the latest fixed rate market info a given instrument id.

        Args:
            instrument_id (str): instrument id of the fixed rate market

        Returns:
            response: Session response from requesting the latest fixed rate market info a given instrument id.
            For example:
            {
                "marketInfo": {
                    "marketId": 11986,
                    "instrumentId": "ETH-2023-11-27",
                    "direction": "False",
                    "updateDate": 1701052205000
                }
            }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FIXED_RATE_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_INSTRUMENT_ID: instrument_id}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_fixed_trades(self, instrument_id: str, limit: int = 20) -> dict:
        """
        Get recent fixed rate transactions by instrument id.

        This gets the most recent fixed rate transactions for a given instrument id.

        Args:
            instrument_id (str): instrument id of the fixed rate market.
            limit (int): Maximum number of transactions to return. (Default is 20.)

        Returns:
            response: Session response from requesting recent fixed rate transactions for a give market. For example:

            {'trxs': [{'side': False,
                'rate': '0.0501',
                'quantity': '3.697',
                'date': 1689833397180},
                {'side': False,
                'rate': '0.0493',
                'quantity': '3.9288',
                'date': 1689833043675},
                {'side': True,
                'rate': '0.0487',
                'quantity': '2.651',
                'date': 1689832827936},
                {'side': False,
                'rate': '0.0478',
                'quantity': '3.8613',
                'date': 1689832426057},
                {'side': False,
                'rate': '0.0339',
                'quantity': '3.0605',
                'date': 1689799385952}]}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FIXED_TRADES_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_INSTRUMENT_ID: instrument_id,
                             constants.QUERY_KEY_LIMIT: limit}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_floating_details(self, instrument_id: str) -> dict:
        """
        Get floating rate market details for a given instrument id.

        This gets market details for a given floating rate market.

        Args:
            instrument_id (str): instrument id of the floating rate market.

        Returns: response: Session response from requesting the floating rate market details for a given instrument id.
        For example:
        {
            "market": {
                "marketId": 1,
                "tokenId": 1,
                "quantityStep": "0.0001",
                "minQuantity": "0.0001",
                "maxQuantity": "100000",
                "rateStep": "0.0001",
                "category": 1,
                "takerFeeRate": "0.0001",
                "makerFeeRate": "0.001",
                "interestFeeRate": "0.0513",
                "enable": "True",
                "borrowPriceIndex": "1.0436063454907",
                "lendPriceIndex": "1.0433148305391",
                "priceIndexDate": 1701061440000,
                "rate": "0.0184",
                "updateDate": 1701061441000,
                "direction": "False",
                "actualRate": "0.0184",
                "name": "ETH SPOT",
                "instrumentId": "ETH-SPOT",
                "high24": "0",
                "low24": "0",
                "volume24": "0",
                "rate24": "0",
                "totalValue": "0"
            }
        }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FLOATING_DETAILS_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_INSTRUMENT_ID: instrument_id}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_floating_history(self, instrument_id: str, start: str | None = None, end: str | None = None,
                             interval_minutes: int | None = None) -> dict:
        """
        Get floating rate market history by instrument id

        This returns the floating rate market history for a given market id between the specified start and end
        datetimes, bucketed by the specified interval size (in minutes).

        Args:
            instrument_id (str): instrument id of the floating rate market.
            start (str): Start Date (of the form yyyymmdd) or Start Datetime
            end (str): End Date (of the form yyyymmdd) or End Datetime
            interval_minutes: Interval size in minutes for bucketing the returned data. If the interval size is more
            than one day, then it needs to be a multiple of one day; if it is less than one day, then it needs to be
            a multiple of 15 minutes.

        Returns:
            {
                "open": "0",
                "close": "0",
                "high": "0",
                "low": "0",
                "volume": "0"
            }

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FLOATING_HISTORY_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_INSTRUMENT_ID: instrument_id}

        today = date.today()
        if start is None:
            start = today - timedelta(days=365)  # Default - 1 year ago
        if end is None:
            end = today + timedelta(days=1)  # Default - tomorrow
        if interval_minutes is None:
            interval_minutes = 24 * 60  # Daily

        interval_milliseconds = interval_minutes * 60 * 1000

        dict_query_params.update({constants.QUERY_KEY_START: start.strftime('%Y%m%d')})
        dict_query_params.update({constants.QUERY_KEY_END: end.strftime('%Y%m%d')})
        dict_query_params.update({constants.QUERY_KEY_INTERVAL: interval_milliseconds})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_floating_orderbook(self, instrument_id: str, limit: int = 10) -> dict:
        """
        Get floating rate orderbook details by instrument id.

        This gets the first 10 levels of the order book for a given instrument id.

        Args:
            instrument_id (str): instrument id of the floating rate market.
            limit (int): Maximum number of orders to return

        Returns:
            response: Session response from requesting floating rate orderbook details for a given instrument id. For
                example:

            {'bids': [{'rate': '0.0216', 'quantity': '6.6675'},
                {'rate': '0.0215', 'quantity': '62.6472'},
                {'rate': '0.0214', 'quantity': '62.6472'},
                {'rate': '0.0213', 'quantity': '65.7989'},
                {'rate': '0.0212', 'quantity': '64.5349'},
                {'rate': '0.0211', 'quantity': '62.647'},
                {'rate': '0.021', 'quantity': '62.6471'},
                {'rate': '0.0209', 'quantity': '62.6471'},
                {'rate': '0.0208', 'quantity': '63.617'},
                {'rate': '0.0207', 'quantity': '63.8282'}],
                'asks': [{'rate': '0.0242', 'quantity': '118.8663'},
                {'rate': '0.0241', 'quantity': '118.8662'},
                {'rate': '0.024', 'quantity': '118.8663'},
                {'rate': '0.0239', 'quantity': '118.8663'},
                {'rate': '0.0238', 'quantity': '118.8664'},
                {'rate': '0.0237', 'quantity': '118.8662'},
                {'rate': '0.0236', 'quantity': '118.8662'},
                {'rate': '0.0235', 'quantity': '118.8664'},
                {'rate': '0.0234', 'quantity': '118.8662'},
                {'rate': '0.0233', 'quantity': '118.8664'}]}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FLOATING_ORDERBOOK_ENDPOINT
        dict_query_params = {
            constants.QUERY_KEY_INSTRUMENT_ID: instrument_id,
            constants.QUERY_KEY_LIMIT: limit
        }

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_floating_rate(self, instrument_id: str) -> dict:
        """
        Get market info by instrument id.

        This gets key market information for a given instrument id, specifically the borrow and lend price indices, as well
        as creation date and latest (daily) update date.

        Args:
            instrument_id (str): instrument id of the floating rate market.

        Returns:
            response: Session response from requesting market info for a given instrument id. For example:

            {
                "marketInfo": {
                    "marketId": 1,
                    "instrumentId": "ETH-SPOT",
                    "rate": "0.0184",
                    "direction": "False",
                    "borrowPriceIndex": "1.0436093664524",
                    "lendPriceIndex": "1.0433178183012",
                    "priceIndexDate": 1701066420000,
                    "updateDate": 1701066421032
                }
            }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FLOATING_RATE_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_INSTRUMENT_ID: instrument_id})
        return self._send_request(is_private=False, method="get", url=url)

    def get_floating_trades(self, instrument_id: str, limit: int = 20) -> dict:
        """
        Get recent floating rate transactions by instrument id.

        This gets the recent floating rate transactions for a given instrument id. If not limit is specified, then 20
        transactions are returned. The maximum number of transactions that can be returned is 100.

        Args:
            instrument_id (str): instrument id of the floating rate market.
            limit (int): Maximum number of transactions. (Default value is 20. Maximum value is 100.)

        Returns:
            response: Session response from requesting the user's recent floating rate transactions. For example:
            {
                "trxs": [
                    {
                        "tradeId": 85296286,
                        "side": "False",
                        "rate": "0.0184",
                        "quantity": "0.0008",
                        "date": 1701055737221
                    },
                    {
                        "tradeId": 85296285,
                        "side": "False",
                        "rate": "0.0184",
                        "quantity": "0.0018",
                        "date": 1701055737221
                    },...]
            }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_FLOATING_TRADES_ENDPOINT
        dict_query_params = {constants.INSTRUMENT_ID: instrument_id,
                             constants.QUERY_KEY_LIMIT: limit}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_historical_mid(self, token_id: int | None = None,
                           fixed_rate_instrument_ids: list[str] | None = None) -> dict:
        """
        Get historical mid rates.

        This gets both the current last & mid rate, and the last & mid rate from 24 hours ago, as well as the last and
        mid rate deltas. If token id is specified, only values for this token will be provided; otherwise values
        for *all* tokens will be provided. If any fixed_rate_instrument_ids are specified, they will also be included;
        otherwise *all* fixed rate markets will be included alongside the floating rate.

        Args:
            token_id (int): Token ID (Default value is None.)
            fixed_rate_instrument_ids (list): List of fixed rate instrument ids. (Default value is None.)

        Returns:
            response: Session response from requesting historical mid rates. For example:
            {
                "1": [ // token Id
                    {
                        "marketId": 1,
                        "instrumentId": "ETH-SPOT",
                        "tokenId": 1,
                        "rate": "0.022",
                        "midRate": "0.022",
                        "volume24": "50756",
                        "rate24": "0.0184",
                        "midRate24": "0.0184",
                        "aaveLendRate": "0.00998329795579504129",
                        "aaveBorrowRate": "0.03104622531939249144",
                        "rateDelta24": "0.0036",
                        "midRateDelta24": "0.0036"
                    },
                    {
                        "marketId": 11996,
                        "instrumentId": "ETH-2023-11-29",
                        "tokenId": 1,
                        "daysToMaturity": 2,
                        "rate": "0.0409",
                        "midRate": "0.0388",
                        "volume24": "26755",
                        "rate24": "0",
                        "midRate24": "0",
                        "rateDelta24": "0.0409",
                        "midRateDelta24": "0.0388",
                        "maturityDate": 1701216000000
                    }
                ]
            }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_24H_SNAPSHOT_ENDPOINT

        dict_query_params = {}

        if token_id is not None:
            dict_query_params.update({constants.QUERY_KEY_TOKEN_ID: token_id})

        if fixed_rate_instrument_ids is not None:
            dict_query_params.update({constants.QUERY_KEY_LIST_FIXED_RATE_INSTRUMENT_IDS: fixed_rate_instrument_ids})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_historical_rates(self, token_id: int, fixed_rate_instrument_ids: list[str] | None = None,
                             days_to_include: int = 365) -> dict:
        """
        Get historical rate details by token id.

        This gets the historical floating & fixed rates for a given token id.

        Args:
            token_id (int): Token ID
            fixed_rate_instrument_ids (list): List of fixed rate instrument IDs. (Default value is None.)
            days_to_include (int): Number of days to include. (Default value is 365.)

        Returns:
            response: Session response from requesting historical floating & fixed rates for a given token id.
            For example:
            {
                "floating": [
                    {
                        "date": 1700524800000,
                        "open": "0.0198",
                        "close": "0.1051",
                        "high": "0.15",
                        "low": "0.0197",
                        "volume": "189069",
                        "totalValue": "0",
                        "usdValue": "1934.89760794",
                        "lendDepth": 52686,
                        "borrowDepth": 1667446467,
                        "numDaysAgo": 7,
                        "instrumentId": "ETH-SPOT",
                        "tokenId": 1
                    }
                ],
                "fixed": {
                    "1": [ // dayToMaturity
                        {
                            "date": 1700524800000,
                            "open": "0",
                            "close": "0",
                            "high": "0",
                            "low": "0",
                            "volume": "0",
                            "totalValue": "0",
                            "usdValue": "2084.15",
                            "lendDepth": 0,
                            "borrowDepth": 0,
                            "numDaysAgo": 7,
                            "daysToMaturity": 1,
                            "instrumentId": "ETH-2023-11-28"
                        }
                    ]
                }
            }

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_HISTORICAL_RATES_ENDPOINT

        dict_query_params = {
            constants.QUERY_KEY_TOKEN_ID: token_id,
            constants.QUERY_KEY_DAYS_TO_INCLUDE: days_to_include
        }

        if fixed_rate_instrument_ids is not None:
            dict_query_params.update({constants.QUERY_KEY_LIST_FIXED_RATE_INSTRUMENT_IDS: fixed_rate_instrument_ids})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_historical_total_value(self, limit: int = 365) -> dict:
        """
        Get historical total USD value.

        This gets the user's total USD value of their positions on the Infinity exchange going back a certain number of
        days. If no days are specified, then 365 days are returned.

        Args:
            limit (int): the number of days of history to be returned. (Default is 365.)

        Returns:
            response: Session response from requesting the user's historical total USD value. For example:

            {'data': [{'date': 1689811200000, 'totalValue': '1892106745.70250482'},
                {'date': 1689724800000, 'totalValue': '1897966236.82078836'},
                {'date': 1689638400000, 'totalValue': '1896161074.26784196'},
                {'date': 1689552000000, 'totalValue': '1913045756.64165925'},
                {'date': 1689465600000, 'totalValue': '1904193743.92327572'}]}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_HISTORICAL_TOTAL_VALUE_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_LIMIT: limit})
        return self._send_request(is_private=False, method="get", url=url)

    def get_historical_yield_curve(self, token_id: int, days_to_include: int = 30) -> dict:
        """
        Get fixed rate historical yield curve by token id.

        This gets the fixed rate historical yield curve for a given token id, and for a certain number of days back.

        Args:
            token_id (int): Token ID
            days_to_include (int): Number of days of historical data to return. (Default is 30.)

        Returns:
            response: Session response from requesting the fixed rate historical yield curve for a given token id.
            For example:
            {
                "historicalCurve": {
                    "2023-11-27": [
                        {
                            "marketId": 1,
                            "instrumentId": "ETH-SPOT",
                            "rate": "0.0184",
                            "label": "Float",
                            "xpos": 0
                        },
                        {
                            "marketId": 11986,
                            "instrumentId": "ETH-2023-11-27",
                            "rate": "0.0211166666668",
                            "label": "1D",
                            "xpos": 1
                        },
                        {
                            "marketId": 11991,
                            "instrumentId": "ETH-2023-11-28",
                            "rate": "0.0211250000002",
                            "label": "2D",
                            "xpos": 2
                        },
                        {
                            "marketId": 12006,
                            "instrumentId": "ETH-2023-12-01",
                            "rate": "0.02115",
                            "label": "1W",
                            "xpos": 3
                        },
                        {
                            "marketId": 12041,
                            "instrumentId": "ETH-2023-12-08",
                            "rate": "0.0375",
                            "label": "2W",
                            "xpos": 4
                        },
                        {
                            "marketId": 12076,
                            "instrumentId": "ETH-2023-12-15",
                            "rate": "0.0371833333329",
                            "label": "3W",
                            "xpos": 5
                        },
                        {
                            "marketId": 12146,
                            "instrumentId": "ETH-2023-12-29",
                            "rate": "0.03655",
                            "label": "1M",
                            "xpos": 6
                        },
                        {
                            "marketId": 12286,
                            "instrumentId": "ETH-2024-01-26",
                            "rate": "0.0402",
                            "label": "2M",
                            "xpos": 7
                        },
                        {
                            "marketId": 12430,
                            "instrumentId": "ETH-2024-02-23",
                            "rate": "0.0406000000004",
                            "label": "3M",
                            "xpos": 8
                        },
                        {
                            "marketId": 12146,
                            "instrumentId": "ETH-2023-12-29",
                            "rate": "0.03655",
                            "label": "1Q",
                            "xpos": 9
                        },
                        {
                            "marketId": 12608,
                            "instrumentId": "ETH-2024-03-29",
                            "rate": "0.0411",
                            "label": "2Q",
                            "xpos": 10
                        },
                        {
                            "marketId": 15172,
                            "instrumentId": "ETH-2024-06-28",
                            "rate": "0.04295",
                            "label": "3Q",
                            "xpos": 11
                        },
                        {
                            "marketId": 15632,
                            "instrumentId": "ETH-2024-09-27",
                            "rate": "0.04445",
                            "label": "4Q",
                            "xpos": 12
                        }
                    ]
                }
            }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_HISTORICAL_YIELD_CURVE_ENDPOINT
        url = generate_query_url(
            url=url, dict_query_params={constants.QUERY_KEY_TOKEN_ID: token_id,
                                        constants.QUERY_KEY_DAYS_TO_INCLUDE: days_to_include})
        return self._send_request(is_private=False, method="get", url=url)

    def get_yield_curve(self, token_id: int, is_ull_yield_curve: bool = False) -> dict:
        """
        Get interpolated yield curve by token id.

        This gets the interpolated yield cure for a given token id. Interpolation is provided for each daily datapoint
        for an entire year, i.e. for today (i.e. daysToMaturity=0) and 364 days thereafter (i.e. up to
        daysToMaturity=364), making a total of 365 interpolated, daily data points.
        At the time of writing (although subject to change prior to our rollout to MainNet), available token id
        values are:
                Token id 1 = ETH
                Token id 2 = USDT
                Token id 3 = USDC
                Token id 4 = DAI
                Token id 5 = WBTC

            Tip:
                - Use the function get_token_details() to get a full list of valid token ids.
                - To see which token ids have active markets, use get_floating_rate_market_details().
                - Or visit our developer portal to see the latest set of available token ids.

        Args:
            token_id (int): Token ID
            is_ull_yield_curve (bool): Whether to return the ULL yield curve. Defaults to False.

        Returns:
            response: Session response from requesting the interpolated yield curve for a given token. For example:
            {
                "interpolatedRates": [
                    {
                        "marketId": 1,
                        "instrumentId": "ETH-SPOT",
                        "tokenId": 1,
                        "interpolatedPx": "0.0208",
                        "daysToMaturity": 0,
                        "enable": "True"
                    },
                    {
                        "marketId": 11991,
                        "instrumentId": "ETH-2023-11-28",
                        "tokenId": 1,
                        "interpolatedPx": "0.0335",
                        "daysToMaturity": 1,
                        "enable": "True",
                        "maturityDate": 1701158400000
                    }
                ]
            }
        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_YIELD_CURVE_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_TOKEN_ID: token_id,
                                                             constants.QUERY_KEY_FULL_YIELD_CURVE: is_ull_yield_curve})
        return self._send_request(is_private=False, method="get", url=url)

    # *** Tokens ***

    def get_token_mtms(self, account_id: int | None = None) -> dict:
        """
        Get user's aggregate total marked to market value for each token by account id.

        This gets the user's aggregate marked to market (MTM) value for each token for a given account id. For the
        avoidance of doubt, each token aggregate MTM value combines the MTM value the floating rate position and
        the MTM values for all fixed rate positions. If no account id is specified, then the user's trading
        account is used.

        Args:
            account_id (int): Account ID  (Default is None.)

        Returns:
            response: Session response from requesting the user's aggregated marked to market values for each token for
            a given account id. Note that the MTM value is in terms of number of tokens (not in USD). For example:
            {
                "mtm": [
                    {
                        "accountId": 202,
                        "tokenId": 1,
                        "mtm": "-18060.175696994414"
                    },
                    {
                        "accountId": 202,
                        "tokenId": 2,
                        "mtm": "-228.02030598304393"
                    },
                    {
                        "accountId": 202,
                        "tokenId": 3,
                        "mtm": "-188.4635786372907"
                    },
                    {
                        "accountId": 202,
                        "tokenId": 4,
                        "mtm": "-234.866262672426"
                    },
                    {
                        "accountId": 202,
                        "tokenId": 5,
                        "mtm": "-13.988802440773487"
                    }
                ]
            }
        """
        if account_id is None:
            account_id = self._account_id

        url = self._API_BASE_URL + constants.PRIVATE_GET_TOKEN_MTMS_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_ACCOUNT_ID: account_id})
        return self._send_request(is_private=True, method="get", url=url)

    def get_token_details(self, token_id: int) -> dict:
        """
        Get token details for given token id.

        This gets the token details for a given token id. At the time of writing (although subject to change prior to
        our rollout to MainNet), available token id values are:
                Token id 1 = ETH
                Token id 2 = USDT
                Token id 3 = USDC
                Token id 4 = DAI
                Token id 5 = WBTC

            Tip:
                - Use the function get_token_details() to get a full list of valid token ids.
                - To see which token ids have active markets, use get_floating_rate_market_details().
                - Or visit our developer portal to see the latest set of available token ids.
        Args:
            token_id (int): Token ID

        Returns:
            response: Session response from requesting token details for a given token. For example:

            {'token': {'tokenId': 1,
                'code': 'ETH',
                'name': 'Ethereum',
                'tokenType': 1,
                'valueType': 1,
                'tokenValuationProtocol': 0,
                'tokenAddress': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
                'decimals': 18,
                'nativeToken': True,
                'withdrawFee': '0.01',
                'price': '1897.26698853'}}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_TOKEN_DETAILS_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_TOKEN_ID: token_id}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=False, method="get", url=url)

    def get_tokens(self) -> dict:
        """
        Get token details.

        This gets all token details.

        Returns:
            response: Session response from requesting all token details. For example:

            {'tokens': [{'tokenId': 0,
                'code': 'WETH',
                'name': 'Wrapped ETH',
                'tokenType': 1,
                'valueType': 1,
                'tokenValuationProtocol': 0,
                'tokenAddress': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
                'decimals': 18,
                'nativeToken': False,
                'withdrawFee': '0.01',
                'price': '1955.63'},
                {'tokenId': 1,
                'code': 'ETH',
                'name': 'Ethereum',
                'tokenType': 1,
                'valueType': 1,
                'tokenValuationProtocol': 0,
                'tokenAddress': '0x0000000000000000000000000000000000000000',
                'decimals': 18,
                'nativeToken': True,
                'withdrawFee': '0.01',
                'price': '1898.21728251'},
                {'tokenId': 2,
                'code': 'USDT',
                'name': 'USDT',
                'tokenType': 1,
                'valueType': 2,
                'tokenValuationProtocol': 0,
                'tokenAddress': '0xdac17f958d2ee523a2206206994597c13d831ec7',
                'decimals': 6,
                'nativeToken': False,
                'withdrawFee': '5',
                'price': '1.00006526'}...]}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_TOKENS_ENDPOINT
        return self._send_request(is_private=False, method="get", url=url)

    def get_underlying_tokens(self, token_ids: List[int]) -> dict:
        """
        Get token details for given list of token ids.

        This gets the token details for a given list of token ids.

            Tip:
                - Use the function get_token_details() to get a full list of valid token ids.
                - Or visit our developer portal to see the latest set of available token ids.
        Args:
            token_ids ([int]): List of Token IDs

        Returns:
            response: Session response from requesting token details for a given token. For example:

        {'tokens': [{'tokenId': 1,
                'code': 'ETH',
                'name': 'Ethereum',
                'tokenType': 1,
                'valueType': 1,
                'tokenValuationProtocol': 0,
                'tokenAddress': '0x0000000000000000000000000000000000000000',
                'decimals': 18,
                'nativeToken': True,
                'withdrawFee': '0.01',
                'price': '1844.05'},
            {'tokenId': 6,
                'code': 'aUSDT',
                'name': 'Aave interest bearing USDT',
                'tokenType': 1,
                'valueType': 2,
                'tokenValuationProtocol': 1,
                'tokenAddress': '0x3ed3b47dd13ec9a98b44e6204a523e766b225811',
                'decimals': 6,
                'nativeToken': False,
                'withdrawFee': '0',
                'price': '1.117670517515475',
                'underlyingAssets': [{'underlyingTokenId': 2,
                    'underlyingTokenIndex': '1.118940515'}]}]}

        """
        url = self._API_BASE_URL + constants.PUBLIC_GET_UNDERLYING_TOKENS_ENDPOINT

        data = []
        for token_id in token_ids:
            data.append({
                'tokenId': token_id,
                'quantity': 1
            })

        return self._send_request(is_private=False, method="post", url=url, json=data)

    # *** Trading  ***

    @staticmethod
    def _check_valid_order_quantity(order_quantity: float) -> bool:
        """
        Check if order quantity is valid.

        This checks if the order quantity is provided. At the time of writing, the explicit check done is whether the
            order quantity is greater than zero. If this check fails, an InvalidOrderQtyError is raised.

        Args:
            order_quantity (float): Order quantity.

        Returns:
            bool: True if the order quantity is valid.

        """
        if order_quantity <= 0:
            raise InvalidOrderQtyError(assigned_order_quantity=order_quantity,
                                       message="Invalid order quantity provided when creating an order. " +
                                               "Please provide a valid order quantity greater than 0.")

        return True

    @staticmethod
    def _check_valid_order_type(order_type: int, rate: float) -> bool:
        """
        Check if an order type is valid.

        This checks if an order type is valid. At the time of writing, the explicit checks done are whether the order is
            a limit or market order, and whether a rate is provided for a limit order. If either of these checks fail,
            an InvalidOrderTypeError is raised.

        Args:
            order_type (int): Order type. (Expected values are 1 for market order, or 2 for limit order.)
            rate (float):

        Returns:
            bool: True if the order type is valid.

        """
        if order_type not in [constants.ORDER_TYPE_LIMIT, constants.ORDER_TYPE_MARKET]:
            raise InvalidOrderTypeError(assigned_order_type=order_type,
                                        message="Invalid order type provided when creating an order. "
                                                + "Please provide a valid order type.")
        if order_type == constants.ORDER_TYPE_LIMIT and rate is None:
            raise InvalidOrderTypeError(assigned_order_type=order_type,
                                        message="Invalid order type and rate value combination for LIMIT order type." +
                                                f" {order_type=}, {rate=}. Please provide a valid combination.")
        return True

    def _parse_orders(self, response: dict) -> dict:
        """
        Parse order response

        Args:
            response (dict): raw response

        Returns:
            parsed order (dict)
        """
        if response.get("order", None) is not None:
            order = response["order"]
            response["order"] = self._process_order_fields(order=order)
        elif response.get("orders", None) is not None:
            orders = response["orders"]
            parsed = []
            for order in orders:
                parsed.append(self._process_order_fields(order=order))
            response["orders"] = parsed
        return response

    def _process_order_fields(self, order: dict) -> dict:
        """
        Save order ID to client order ID in self._order_id_map translate order data to readable format

        Args:
            order (dict): order message

        Returns:
             parsed order (dict)
        """
        order_id = order.get(constants.QUERY_KEY_ORDER_ID, None)
        client_order_id = order.get(constants.CLIENT_ORDER_ID, None)
        if order and client_order_id is not None:
            self._order_id_map[order_id] = client_order_id
        status_code = order.get(constants.STATUS, None)
        if status_code is not None:
            order[constants.STATUS] = constants.ORDER_STATUS_TYPE[status_code]
        return order

    @staticmethod
    def generate_client_order_id() -> str:
        """
        Generate a custom client order id.

        This generates a random, customer client order id of the form of an 8-character hexadecimal value. This generator
            provides 16^8 (i.e. over 4 billion) different unique combinations, suggesting the odds of generate two identical
            values in a short time frame is extremely low.

        Returns:
            A random 8-character hexadecimal value. For example:

            1234abcd

        """
        return uuid4().hex[:8]

    def get_client_order_id_from_order_id(self, order_id: str) -> str | None:
        """
        When order is created, add created order ID with its client order ID into order ID map.
        This function is to pass order ID as key to find client Order ID in order ID map.

        Args:
            order_id(str): created order ID

        Returns:
             client order ID (str)
        """
        return self._order_id_map[order_id]

    def aggregate_orders_by_rate(self, float_rate_instrument_id: str | None = None,
                                 fixed_rate_instrument_ids: list[str] | None = None,
                                 account_id: int | None = None) -> dict:
        """
        Get user's orders in rate buckets.

        This gets the user's orders in rate buckets for the given floating rate and fixed rate markets. If no account ID
        is specified, then the user's trading account is used.

        Args:
            float_rate_instrument_id (str): Floating rate instrument ID.
            fixed_rate_instrument_ids (list[str]): List of fixed rate instrument IDs.
            account_id (int): Account ID (Default is None.)

        Returns:
            response: Session response from requesting the user's orders in rate buckets. For example:
            {
                "ir": [
                    {
                        "marketId": 1,
                        "instrumentId": "ETH-SPOT",
                        "rate": "0.0143",
                        "quantity": "2.7022",
                        "side": "True"
                    },
                    {
                        "marketId": 1,
                        "instrumentId": "ETH-SPOT",
                        "rate": "0.0151",
                        "quantity": "2.7065",
                        "side": "True"
                    }
                ],
                "fr": [
                    {
                        "marketId": 11991,
                        "instrumentId": "ETH-2023-11-28",
                        "rate": "0.05",
                        "quantity": "0.01",
                        "side": "False"
                    }
                ]
            }

        """
        url = self._API_BASE_URL + constants.PRIVATE_AGGREGATE_ORDERS_BY_RATE_ENDPOINT
        dict_query_params = {}
        if float_rate_instrument_id is not None:
            dict_query_params[constants.QUERY_KEY_FLOATING_RATE_INSTRUMENT_ID] = float_rate_instrument_id
        if fixed_rate_instrument_ids is not None and len(fixed_rate_instrument_ids) > 0:
            dict_query_params[constants.QUERY_KEY_LIST_FIXED_RATE_INSTRUMENT_IDS] = fixed_rate_instrument_ids

        if len(dict_query_params) == 0:
            self._logger.error("API [aggregate_orders_by_rate] need to given a floating rate market ID " +
                               "or a list of fixed rate market ID, or both")
            return {}

        if account_id is not None:
            dict_query_params[constants.QUERY_KEY_ACCOUNT_ID] = account_id

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def batch_cancel_orders(self, instrument_id: str, account_id: int | None = None,
                            client_order_ids: list[str] | None = None, order_ids: list[int] | None = None) -> dict:
        """
        Batch cancel multiple orders.

        This method allows you to cancel multiple orders in a single API call.
        You need to provide a list of order IDs to cancel.

        Args:
            instrument_id (str): Instrument ID.
            account_id (int): Account ID. (optional)
            order_ids (List[int]): A list of exchange order IDs to cancel. (optional if client_order_ids is specified)
            client_order_ids (List[str]): A list of client order IDs to cancel. (optional if order_ids is specified)


        Returns:
            dict: A dictionary containing the response from the Infinity REST API.

        Raises:
            Exception: If an error occurs while sending the API request or handling the response.
        """
        if account_id is None:
            account_id = self._account_id
        dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: account_id,
                             constants.QUERY_KEY_INSTRUMENT_ID: instrument_id}
        url = self._API_BASE_URL + constants.PRIVATE_BATCH_CANCEL_ORDERS_ENDPOINT
        url = generate_query_url(url=url, dict_query_params=dict_query_params)

        if client_order_ids is not None and order_ids is not None:
            raise InputParameterError("Please only specify client_order_ids or order_ids, not both.")
        elif client_order_ids is None and order_ids is None:
            raise InputParameterError("Please specify either client_order_ids or order_ids.")
        else:
            json = {}
            if client_order_ids is not None:
                json = {constants.CLIENT_ORDER_IDS: client_order_ids}
            elif order_ids is not None:
                json = {constants.ORDER_IDS: order_ids}
            return self._send_request(is_private=True, method="post", url=url, json=json)

    def cancel_order(self, instrument_id: str, account_id: int | None = None, order_id: int | None = None,
                     client_order_id: str | None = None) -> dict:
        """
        Cancel an order by order id or client order id.

        This cancels an order as specified by its Infinity Exchange order id or client order id.

        Args:
            instrument_id (str): Market instrument ID.
            order_id (int): Exchange order ID (required if client order ID is not provided)
            client_order_id (str): Client order ID (required if Infinity Exchange order ID is not provided)
            account_id (int): account ID (Optional)

        Returns:
            response: Session response from attempting to cancel an order. Note a success boolean and empty
                data dictionary are returned only. For example:

            {}

        """
        url = self._API_BASE_URL + constants.PRIVATE_CANCEL_ORDER_ENDPOINT
        if account_id is None:
            account_id = self.account_id
        params = {
            constants.QUERY_KEY_ACCOUNT_ID: account_id,
            constants.QUERY_KEY_INSTRUMENT_ID: instrument_id
        }
        if order_id is None and client_order_id is None:
            raise InputParameterError("Please specify either order_id or client_order_id.")
        if order_id is not None:
            params.update({constants.QUERY_KEY_ORDER_ID: order_id})
        elif client_order_id is not None:
            params.update({constants.CLIENT_ORDER_ID: client_order_id})

        url = generate_query_url(url=url, dict_query_params=params)
        return self._send_request(is_private=True, method="post", url=url)

    def create_fixed_order(self, instrument_id: str, order_type: int, side: int, quantity: float,
                           client_order_id: str, rate: float | None = None, passive: int = 0) -> dict:
        """
        Create fixed rate order.

        This sends a fixed rate order to the Infinity exchange.

        Args:
            instrument_id (str): Market instrument ID.
            order_type (int): Order type (1 for market order, or 2 for limit order).
            side (int): Side (0 for lend order, or 1 for borrow order).
            quantity (float): Order quantity.
            client_order_id (str): User-defined custom string. This string must consist of only digits and letters
                (uppercase or lowercase), with a length of 1-8 characters.
            rate (float): Order rate. To send a market order do not include parameter. If this parameter is included
                when order_type is set to 1 for a market order, then the order will be sent as a maximum slippage market
                order. (Default value is None.)
            passive (int): Whether an order is passive (a value of 1) or active (a value of 0, or ignored). A passive
                order will be automatically cancelled if, when placed, it would lift any existing orders in the order
                book. An active order has no such restriction, and will be executed immediately if it lifts any existing
                orders. The ability to specify that an order is passive is useful for market markers wanting to ensure
                their limit orders are adding liquidity to an order book, rather than taking orders away. (Default value
                is 0.)

        Returns:
            response: Session response from attempting to place a fixed rate order. For example:

            {
                "order": {
                    "orderId": 272684374,
                    "marketId": 11991,
                    "instrumentId": "ETH-2023-11-28",
                    "accountId": 202,
                    "side": "False",
                    "orderType": 2,
                    "quantity": "0.01",
                    "fulfilled": "0",
                    "rate": "0.05",
                    "status": "on_book",
                    "clientOrderId": "7eb31378",
                    "passive": "False",
                    "orderDate": 1701071692221,
                    "source": 1
                }
            }
        """
        self._check_valid_order_type(order_type=order_type, rate=rate)
        self._check_valid_order_quantity(order_quantity=quantity)

        url = self._API_BASE_URL + constants.PRIVATE_CREATE_FIXED_ORDER_ENDPOINT

        body = {
            constants.INSTRUMENT_ID: instrument_id,
            constants.ACCOUNT_ID: self._account_id,
            constants.SIDE: side,
            constants.ORDER_TYPE: order_type,
            constants.QUANTITY: str(quantity),
            constants.CLIENT_ORDER_ID: str(client_order_id),
            constants.PASSIVE: passive
        }

        if rate is not None:
            body.update({constants.RATE: str(rate)})

        return self._send_request(is_private=True, method="post", url=url, json=body)

    def create_floating_order(self, instrument_id: str, order_type: int, side: int, quantity: float,
                              client_order_id: str, rate: float | None = None, passive: int = 0) -> dict:
        """
        Create floating rate order.

        This sends a floating rate order to the Infinity exchange.

        Args:
            instrument_id (str): instrument ID.
            order_type (int): Order type. (1 for market order, or 2 for limit order.)
            side (int): Side, (0 for lend order, or 1 for borrow order.)
            quantity (float): Order quantity.
            client_order_id (str): User-defined custom string. This string must consist of only digits and letters
                (uppercase or lowercase), with a length of 1-8 characters.
            rate (float): Order rate. To send a market order do not include parameter. If this parameter is included
                when order_type is set to 1 for a market order, then the order will be sent as a maximum slippage market
                order. (Default value is None.)
            passive (int): Whether an order is passive (a value of 1) or active (a value of 0, or ignored). A passive
                order will be automatically cancelled if, when placed, it would lift any existing orders in the order
                book. An active order has no such restriction, and will be executed immediately if it lifts any existing
                orders. The ability to specify that an order is passive is useful for market markers wanting to ensure
                their limit orders are adding liquidity to an order book, rather than taking orders away. (Default value
                is 0.)

        Returns:
            response: Session response from attempting to place a floating rate order. For example:

            {
                "order": {
                    "orderId": 105241907,
                    "marketId": 1,
                    "instrumentId": "ETH-SPOT",
                    "accountId": 202,
                    "side": "False",
                    "orderType": 2,
                    "quantity": "0.01",
                    "fulfilled": "0",
                    "rate": "0.5",
                    "status": "on_book",
                    "clientOrderId": "51afa3eb",
                    "passive": "False",
                    "orderDate": 1701071497306,
                    "source": 1
                }
            }
        """
        self._check_valid_order_type(order_type=order_type, rate=rate)
        self._check_valid_order_quantity(order_quantity=quantity)

        url = self._API_BASE_URL + constants.PRIVATE_CREATE_FLOATING_ORDER_ENDPOINT

        body = {
            constants.INSTRUMENT_ID: instrument_id,
            constants.ACCOUNT_ID: self._account_id,
            constants.SIDE: side,
            constants.ORDER_TYPE: order_type,
            constants.QUANTITY: str(quantity),
            constants.CLIENT_ORDER_ID: str(client_order_id),
            constants.PASSIVE: passive
        }

        if rate is not None:
            body.update({constants.RATE: str(rate)})
        return self._send_request(is_private=True, method="post", url=url, json=body)

    def get_fixed_orders(self, instrument_id: str | None = None, account_id: int | None = None,
                         pending_only: bool | None = None, done_only: bool | None = None,
                         start_id: int | None = None, limit: int = 10) -> dict:
        """
        Get a user's fixed rate orders.

        This gets the user's most recent fixed rate orders for their default trading account, ordered by order id. Fixed
        rate orders can be retrieved for a given fixed rate market instrument id, or if not specified for all fixed rate market
        ids. It can retrieve all orders, only pending orders, or only done orders. The order start ID and the
        maximum number of orders retrieved can optionally be set. If start ID is not set, then orders starting from
        the earliest order will be returned; if the maximum number of orders is not set, then a maximum of 10 orders
        will be returned.

        Args:
            instrument_id (str): instrument id of fixed rate market. (Default value is None.)
            account_id (int): account id. (Default value is None.)
            pending_only (bool): Include pending orders (True) or not (None). (Default value is None.)
            done_only (bool): Include completed orders (True) or not (None). (Default value is None.)
            start_id (int): Starting order ID. (Default value is None.)
            limit (int): Maximum number of orders. (Default value is 10.)

        Returns:
            response: Session response from attempting to list a user's fixed rate orders. For example:

        {
            "orders": [
                {
                    "orderId": 272684374,
                    "marketId": 11991,
                    "instrumentId": "ETH-2023-11-28",
                    "accountId": 202,
                    "side": "False",
                    "orderType": 2,
                    "quantity": "0.01",
                    "fulfilled": "0",
                    "rate": "0.05",
                    "status": "manually_cancelled",
                    "clientOrderId": "7eb31378",
                    "passive": "False",
                    "orderDate": 1701071692221,
                    "source": 1,
                    "updateDate": 1701071806691,
                    "daysToMaturity": 1,
                    "maturityDate": 1701158400000
                },...]
        }
        """
        url = self._API_BASE_URL + constants.PRIVATE_GET_FIXED_ORDERS_ENDPOINT
        if account_id is None:
            account_id = self._account_id
        dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: account_id}

        if pending_only:
            dict_query_params[constants.QUERY_KEY_PENDING] = pending_only
        if done_only:
            dict_query_params[constants.QUERY_KEY_DONE] = done_only

        if instrument_id is not None:
            dict_query_params.update({constants.QUERY_KEY_INSTRUMENT_ID: instrument_id})

        if start_id is not None:
            dict_query_params.update({constants.QUERY_KEY_START_ID: start_id})

        if limit is not None:
            dict_query_params.update({constants.QUERY_KEY_LIMIT: limit})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_floating_orders(self, instrument_id: str | None = None, account_id: int | None = None,
                            pending_only: bool | None = None, done_only: bool | None = None,
                            start_id: int | None = None, limit: int = 10) -> dict:
        """
        Get a user's floating rate orders.

        This gets the user's most recent floating rate orders for their default trading account, ordered by order id.
        Floating rate orders can be retrieved for a given floating rate instrument id, or if not specified for all
        floating rate instrument ids. It can retrieve all orders, only pending orders, or only done orders. The order
        start ID and the maximum number of orders retrieved can optionally be set. If start ID is not set, then
        orders starting from the earliest order will be returned; if the maximum number of orders is not set, then a
        maximum of 10 orders will be returned.

        Args:
            instrument_id (str): instrument id of the floating market. (Default value is None.)
            account_id (int): account id. (Default value is None.)
            pending_only (bool): get pending orders only (True) or not (None). (Default value is None.)
            done_only (bool): get completed orders only (True) or not (None). (Default value is None.)
            start_id (int): Starting order ID. (Default value is None.)
            limit (int): Maximum number of orders. (Default value is 10.)

        Returns:
            response: Session response from attempting to list a user's floating rate orders. For example:

            {
                "orders": [
                    {
                        "orderId": 105241907,
                        "marketId": 1,
                        "instrumentId": "ETH-SPOT",
                        "accountId": 202,
                        "side": "False",
                        "orderType": 2,
                        "quantity": "0.01",
                        "fulfilled": "0",
                        "rate": "0.5",
                        "status": "manually_cancelled",
                        "clientOrderId": "51afa3eb",
                        "passive": "False",
                        "orderDate": 1701071497306,
                        "source": 1,
                        "updateDate": 1701071841660
                    },...]
            }
        """
        url = self._API_BASE_URL + constants.PRIVATE_GET_FLOATING_ORDERS_ENDPOINT
        if account_id is None:
            account_id = self._account_id
        dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: account_id}
        if pending_only:
            dict_query_params[constants.QUERY_KEY_PENDING] = pending_only
        if done_only:
            dict_query_params[constants.QUERY_KEY_DONE] = done_only

        if instrument_id is not None:
            dict_query_params.update({constants.QUERY_KEY_INSTRUMENT_ID: instrument_id})

        if start_id is not None:
            dict_query_params.update({constants.QUERY_KEY_START_ID: start_id})

        if limit is not None:
            dict_query_params.update({constants.QUERY_KEY_LIMIT: limit})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_floating_positions(self, instrument_id: str | None = None, account_id: int | None = None) -> dict:
        """
        Get user's current floating rate positions for a given instrument id.

        This gets the user's current floating rate positions for a given instrument id and account id. If no account id is
        specified, then the user's trading account is used.

        Args:
            instrument_id (str): instrument id of the floating market.
            account_id (int): Account ID (Default is None.)

        Returns: response: Session response from requesting the user's current floating rate positions for a given
        instrument id. For example:

            {
                "positions": [
                    {
                        "accountId": 202,
                        "marketId": 1,
                        "instrumentId": "ETH-SPOT",
                        "priceIndex": "1.0431946135629",
                        "quantity": "-702938.5559",
                        "updateDate": 1701055737000
                    }
                ]
            }
        """
        url = self._API_BASE_URL + constants.PRIVATE_GET_FLOATING_POSITIONS_ENDPOINT
        if account_id is None:
            account_id = self._account_id
        dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: account_id}
        if instrument_id is not None:
            dict_query_params.update({constants.QUERY_KEY_INSTRUMENT_ID: instrument_id})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_private_floating_trades(self, account_id: int | None = None, instrument_id: str | None = None,
                                    start_trx_id: int | None = None, limit: int = 20) -> dict:
        """
        Get user's floating rate transactions by account id.

        This gets the user's floating rate transactions for a given account id. If no account id is specified, then the
        user's trading account is used. If no instrument id is specified, then all floating rate markets are returned.
        If start transaction id is specified then only transactions from that id are returned;
        otherwise transactions from the first transaction are returned.
        If limit is not specified, then 20 transactions will be returned.
        Note that irrespective of the value of limit, not more than 100 transactions will be returned.

        Args:
            account_id (int): Account ID. (Default is None.)
            instrument_id (str): instrument id of the floating rate market. (Default is all floating rate markets.)
            start_trx_id (int): Start Transaction ID. (Default is None.)
            limit (int): Maximum number of transactions to return. (Default is 20. Maximum is 100.)

        Returns:
            response: Session response from requesting the user's floating rate transactions. For example:
            {
                "trxs": [
                    {
                        "trxId": 146763412,
                        "marketId": 1,
                        "instrumentId": "ETH-SPOT",
                        "order_type": 1, // limit or market
                        "order_side": False, // borrow or lend
                        "order_rate": "0.0334",
                        "trade_rate": "0.0334",
                        "order_quantity": "0.0001",
                        "trade_quantity": "0.0001",
                        "orderId": 276866883,
                        "clientOrderId": "24eer32"
                        "date": 1701229683449
                    }
                ]
            }
        """
        if account_id is None:
            account_id = self._account_id

        url = self._API_BASE_URL + constants.PRIVATE_GET_FLOATING_TRADES_ENDPOINT

        dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: account_id}

        if instrument_id is not None:
            dict_query_params[constants.QUERY_KEY_INSTRUMENT_ID] = instrument_id
        if start_trx_id is not None:
            dict_query_params[constants.QUERY_KEY_START_ID] = start_trx_id
        dict_query_params[constants.QUERY_KEY_LIMIT] = limit

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_private_fixed_trades(self, account_id: int | None = None, instrument_id: str | None = None,
                                 start_trx_id: int | None = None, limit: int = 20) -> dict:
        """
        Get user's fixed rate transactions by account id.

        This gets the user's fixed rate transactions for a given account id. If no account id is specified, then the
            user's trading account is used. If no instrument id is specified, then all fixed rate markets are returned.
            If start transaction id is specified then only transactions from that id are returned;
            otherwise transactions from the first transaction are returned.
            If limit is not specified, then 20 transactions will be returned.
            Note that irrespective of the value of limit, not more than 100 transactions will be returned.

        Args:
            account_id (int): Account ID. (Default is None.)
            instrument_id (str): instrument id of the fixed rate market. (Default is all fixed rate markets.)
            start_trx_id (int): Start Transaction ID. (Default is None.)
            limit (int): Maximum number of transactions to return. (Default is 20. Maximum is 100.)

        Returns:
            response: Session response from requesting the user's fixed rate transactions. For example:
            {
                "trxs": [
                    {
                        "trxId": 146763412,
                        "marketId": 12001,
                        "instrumentId": "ETH-2023-11-30",
                        "order_type": 1, // limit or market
                        "order_side": False, // borrow or lend
                        "order_rate": "0.0334",
                        "trade_rate": "0.0334",
                        "order_quantity": "0.0001",
                        "trade_quantity": "0.0001",
                        "orderId": 276866883,
                        "clientOrderId": "24eer32"
                        "date": 1701229683449
                    }
                ]
            }
        """
        if account_id is None:
            account_id = self._account_id

        url = self._API_BASE_URL + constants.PRIVATE_GET_FIXED_TRADES_ENDPOINT

        dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: account_id}

        if instrument_id is not None:
            dict_query_params[constants.QUERY_KEY_INSTRUMENT_ID] = instrument_id
        if start_trx_id is not None:
            dict_query_params[constants.QUERY_KEY_START_ID] = start_trx_id
        dict_query_params[constants.QUERY_KEY_LIMIT] = limit

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_positions(self, account_id: int | None = None) -> dict:
        """
        Get all user positions by user account id

        Args:
            account_id(int): account id (optional)

        Returns:
            response: Session response from requesting user positions by account id. For example:
            {
                "success": "True",
                "data": {
                    "accountPositions": [
                        {
                            "accountId": 122,
                            "tokenId": 1,
                            "instrumentId": "ETH-SPOT",
                            "price": "123",
                            "quantity": "123",
                            "accruedInterest": "424",
                            "netPositions": "456",
                            "mtm": "0",
                            "pv": "456",
                            "dv01": "0",
                            "rollOverHour": 8
                        },
                        {
                            "accountId": 122,
                            "tokenId": 1,
                            "instrumentId": "ETH-2024-09-27",
                            "rate": "0.123",
                            "price": "123.00",
                            "quantity": "-123.7171",
                            "accruedInterest": "0",
                            "netPositions": "-123.7171",
                            "mtm": "0.473806606",
                            "pv": "-0.243293394",
                            "dv01": "0.83533694",
                            "rollOverHour": 8,
                            "maturityDate": 1727424000000
                        }
                    ]
                }
            }
        """
        if account_id is None:
            account_id = self.account_id
        url = self._API_BASE_URL + constants.PRIVATE_GET_ALL_POSITIONS_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_ACCOUNT_ID: account_id})
        return self._send_request(is_private=True, method="get", url=url)

    def get_positions_and_dv01(self, account_id: int | None = None) -> dict:
        warn('get_positions_and_dv01(/private/get_positions_and_dv01) will be deprecated', DeprecationWarning,
             stacklevel=2)
        """ Get user's fixed rate positions and DV01.

        This gets the user's fixed rate positions and DV01 value for a given account id. If no account id is specified,
        then the user's trading account is used.

        Args:
            account_id (int): Account ID  (Optional)

        Returns:
            response: Session response from requesting the user's fixed rate positions and DV01. For example:
            {
                "posDv01": [
                    {
                        "marketId": 1,
                        "instrumentId": "ETH-SPOT",
                        "tokenId": 1,
                        "position": "-702938.5559",
                        "accountId": "202"
                    },
                    {
                        "marketId": 12041,
                        "instrumentId": "ETH-2023-12-08",
                        "tokenId": 1,
                        "position": "-8129.6739",
                        "dv01": "0.02448790048474353",
                        "accountId": "202",
                        "maturityDate": 1702022400000
                    },...
                ]
            }
        """
        if account_id is None:
            account_id = self._account_id

        url = self._API_BASE_URL + constants.PRIVATE_GET_POSITIONS_AND_DV01_ENDPOINT
        url = generate_query_url(url=url, dict_query_params={constants.QUERY_KEY_ACCOUNT_ID: account_id})
        return self._send_request(is_private=True, method="get", url=url)

    # *** User  ***

    def get_user_info(self) -> dict:
        """
        Get user's information

        This gets user's base information.

        Returns:
            response: Session response from requesting the user's fixed rate positions and DV01. For example:

        {
            "user": {
                "userId": 57,
                "address": "0x5ef1b2c02f5e40c0ff667612c5d7effb0e7df963",
                "userType": 1,
                "accounts": [
                    {
                        "accountId": 201,
                        "type": 1
                    },
                    {
                        "accountId": 202,
                        "type": 2
                    }
                ]
            }
        }

        """
        url = self._API_BASE_URL + constants.PRIVATE_GET_USER_INFO_ENDPOINT
        return self._send_request(is_private=True, method="get", url=url)

    # *** Account ***

    @property
    def account_id(self) -> int:
        """
        Return the user's account id.

        This returns the id assigned by the Infinity exchange for the user's Infinity trading account.
        (This is NOT a user's onchain blockchain account ID.)

        Returns:
           int: The user's Infinity account ID.
        """
        return self._account_id

    def get_account_id(self, account_type: int = 2) -> int:
        """
        Get account ID for logged-in user.

       Args:
           account_type (int, optional): Type of account to get ID for. Default is 2.

       Returns:
           int: The account ID for the logged-in user.
       """
        res = self.get_accounts()
        for account in res["accounts"]:
            if account["type"] == account_type:
                return account["accountId"]
        self._logger.error(f"cannot find {account_type=}")

    def get_all_account_tx(self, transaction_type: int | None = None, start_id: int | None = None,
                           limit: int = 20) -> dict:
        """
        Get all account txs.

        This method returns the user's account transactions based on the set filters.

        Args:
            transaction_type (int): e.g. 5
            start_id (int): e.g. 507810925, for filtering purpose
            limit (int): e.g. 20, 20 by default

        Returns:
            response: Session response from attempting to get user's account transactions. For example:
            {
                "trxs": [
                    {
                        "trxId": 742551183,
                        "accountId": 202,
                        "tokenId": 1,
                        "type": 5,
                        "quantity": "-43.83697037",
                        "balance": "1757611.203652645",
                        "createDate": 1701072022000
                    },
                    {
                        "trxId": 742551182,
                        "accountId": 202,
                        "tokenId": 1,
                        "type": 5,
                        "quantity": "0.407328846",
                        "balance": "1757655.040623015",
                        "createDate": 1701072022000
                    },...
                ]
            }

        """
        url = self._API_BASE_URL + constants.PRIVATE_GET_ALL_ACCOUNT_TX_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_LIMIT: limit}
        if transaction_type is not None:
            dict_query_params.update({constants.QUERY_KEY_TYPE: transaction_type})
        if start_id is not None:
            dict_query_params.update({constants.QUERY_KEY_START_ID: start_id})
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_max_borrow(self, account_id: int | None = None) -> dict:
        """
        Get user's maximum borrow by account ID.

        Args:
           account_id (int): Account ID to get max borrow for

        Returns:
           response (dict): API response containing max borrow info for the account. For example:

            {
                "accountTokenPositions": [
                    {
                        "accountId": 202,
                        "tokenId": 1,
                        "price": "2048.623648",
                        "netAssetValue": "75804.224363624",
                        "cash": "1757611.203652645",
                        "cashAvailable": "1741771.339552645",
                        "interest": "-5111.518933788",
                        "netPositions": "-1664183.038731983",
                        "mtm": "-17623.940557038",
                        "pv": "-1681806.979289021",
                        "netTransfers": "0",
                        "maxWithdraw": "1512754.459379676",
                        "totalTransfers": "-100"
                    },...
                ]
            }
        """
        url = self._API_BASE_URL + constants.PRIVATE_GET_MAX_BORROW_ENDPOINT

        if account_id is None:
            dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: self._account_id}
        else:
            dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: account_id}

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_account_info(self, account_id: int | None = None) -> dict:
        """
        Get user details for the default trading accounts

        This provided detailed information about the user's default trading account at Infinity exchange,
        including quantity of tokens in that account.
        Args:
            account_id (int): Account ID to get info for. If not provided, will use the user's default trading account.

        Returns:
            response: Session response from attempting to list details all of a user's default trading account.
            For example:
            {
                "account": {
                    "accountId": 202,
                    "userId": 57,
                    "type": 2,
                    "name": "Trading",
                    "status": 1,
                    "healthScore": 5686.08303,
                    "asset": 2757194984.6983743,
                    "assetLtv": 2213971121.2718234,
                    "liability": 389362.999307264,
                    "ratesMargin": 0.03867397,
                    "ltvType": 1,
                    "updateDate": 1693214293000,
                    "tokens": [
                        {
                            "accountId": 202,
                            "tokenId": 1,
                            "quantity": "1757611.203652645",
                            "lockedQuantity": "15839.8641",
                            "code": "ETH",
                            "tokenType": 1,
                            "valueType": 1,
                            "tokenValuationProtocol": 0,
                            "availableQuantity": "1741771.339552645"
                        }
                    ]
                }
            }
        """
        if account_id is None:
            account_id = self._account_id
        url = self._API_BASE_URL + constants.PRIVATE_GET_ACCOUNT_INFO_ENDPOINT
        dict_query_params = {constants.QUERY_KEY_ACCOUNT_ID: account_id}
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_account_tx(self, limit: int = 20, account_id: int | None = None, transaction_type: str | None = None,
                       start_id: int | None = None) -> dict:
        """
        Get account transactions.

       Args:
           account_id (int, optional): Account ID to get transactions for. If not provided, will use the user's default trading account.
           limit (int, optional): Number of transactions to return. Default is 20.
           transaction_type (str, optional): Filter by transaction type.
           start_id (int, optional): Start ID for pagination.

       Returns:
           dict: API response containing list of account transactions. For example:
           {
                "trxs": [
                    {
                        "trxId": 742551183,
                        "accountId": 202,
                        "tokenId": 1,
                        "type": 5,
                        "quantity": "-43.83697037",
                        "balance": "1757611.203652645",
                        "createDate": 1701072022000
                    },...
                ]
            }
       """
        url = self._API_BASE_URL + constants.PRIVATE_GET_ACCOUNT_TX_ENDPOINT
        if account_id is None:
            account_id = self._account_id
        dict_query_params = {
            constants.QUERY_KEY_ACCOUNT_ID: account_id,
            constants.QUERY_KEY_LIMIT: limit
        }
        if transaction_type is not None:
            dict_query_params.update({constants.QUERY_KEY_TYPE: transaction_type})
        if start_id is not None:
            dict_query_params.update({constants.QUERY_KEY_START_ID: start_id})

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="get", url=url)

    def get_accounts(self) -> dict:
        """
        Get the user's accounts

        This lists the user's current and trading accounts at Infinity exchange, along with available
        quantity of tokens in those accounts.

        Returns:
            response: Session response from attempting to list all of a user's accounts. For example:
            {
                "accounts": [
                    {
                        "accountId": 201,
                        "userId": 57,
                        "type": 1,
                        "name": "Current",
                        "status": 1,
                        "healthScore": 10000,
                        "asset": 0,
                        "assetLtv": 0,
                        "liability": 0,
                        "ratesMargin": 0,
                        "ltvType": 1,
                        "updateDate": 1686791547000,
                        "tokens": [
                            {
                                "accountId": 201,
                                "tokenId": 1,
                                "quantity": "100",
                                "lockedQuantity": "0",
                                "code": "ETH",
                                "tokenType": 1,
                                "valueType": 1,
                                "tokenValuationProtocol": 0,
                                "availableQuantity": "100"
                            }
                        ]
                    },...
                ]
            }

        """

        url = self._API_BASE_URL + constants.PRIVATE_GET_ACCOUNTS_ENDPOINT
        return self._send_request(is_private=True, method="get", url=url)

    def transfer_floating_position(self, from_account_id: int, to_account_id: int, instrument_id: str,
                                   quantity: float) -> dict:
        """
        Transfer position between accounts.

       Args:
           from_account_id (int): Account ID to transfer position from
           to_account_id (int): Account ID to transfer position to
           instrument_id (str): instrument ID of market for position being transferred
           quantity (float): Quantity of position to transfer

       Returns:
           response (dict): API response from position transfer attempt
       """

        url = self._API_BASE_URL + constants.PRIVATE_TRANSFER_FLOATING_POSITION_ENDPOINT
        dict_query_params = {
            constants.QUERY_KEY_FROM_ACCOUNT_ID: from_account_id,
            constants.QUERY_KEY_TO_ACCOUNT_ID: to_account_id,
            constants.QUERY_KEY_INSTRUMENT_ID: instrument_id,
            constants.QUERY_KEY_QUANTITY: quantity
        }

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="post", url=url)

    def transfer_token(self, from_account_id: int, to_account_id: int, token_id: int, quantity: float) -> dict:
        """
        Transfer token between accounts.

           Args:
               from_account_id (int): Account ID to transfer tokens from
               to_account_id (int): Account ID to transfer tokens to
               token_id (int): ID of token to transfer
               quantity (float): Quantity of tokens to transfer

           Returns:
               response (dict): API response from token transfer attempt
        """
        url = self._API_BASE_URL + constants.PRIVATE_TRANSFER_TOKEN_ENDPOINT
        dict_query_params = {
            constants.QUERY_KEY_FROM_ACCOUNT_ID: from_account_id,
            constants.QUERY_KEY_TO_ACCOUNT_ID: to_account_id,
            constants.QUERY_KEY_TOKEN_ID: token_id,
            constants.QUERY_KEY_QUANTITY: quantity
        }

        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="post", url=url)

    def update_account_name(self, account_id: int, new_name: str) -> dict:
        """
        Renaming of user account.

        Renames the value of the 'name' field to new_name.

        Args:
            account_id (int): e.g. 128
            new_name (str): e.g. 'NewName'

        Returns:
            response: Session response from account renaming attempt. For example:

        {
        "account": {
            "accountId": 128,
            "userId": 31,
            "type": 2,
            "name": "NewName",
            "status": 1,
            "healthScore": 10000.0,
            "asset": 2.757222438174139E14,
            "assetLtv": 2.2139931492951125E14,
            "liability": 4.8861696117990464E7,
            "ratesMargin": 444.856525596,
            "ltvType": 1,
            "updateDate": 1697450536000
            }
        }

        """
        url = self._API_BASE_URL + constants.PRIVATE_UPDATE_ACCOUNT_NAME_ENDPOINT
        dict_query_params = {
            constants.QUERY_KEY_ACCOUNT_ID: account_id,
            constants.QUERY_KEY_NAME: new_name
        }
        url = generate_query_url(url=url, dict_query_params=dict_query_params)
        return self._send_request(is_private=True, method="post", url=url)
