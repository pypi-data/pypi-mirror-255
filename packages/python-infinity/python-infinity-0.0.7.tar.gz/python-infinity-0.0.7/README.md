# python-infinity

This is a Python3 connector for Infinity exchange's REST APIs and WebSocket.

Please note that the python-infinity package is an <b>unofficial</b> project and should be used at your own risk.
It is <b>NOT</b> affiliated with the Infinity exchange and does <b>NOT</b> provide financial or investment advice.

## Table of Contents

- <b>[Overview](#overview)</b>
- <b>[Features](#features)</b>
- <b>[Documentation](#documentation)</b>
- <b>[Quick Start](#quick-start)</b>
- <b>[Example Usage](#example-usage)</b>
- <b>[Disclaimer](#disclaimer)</b>
- <b>[Contact](#contact)</b>

## Overview
The <code>python-infinity</code> package is a Python3 connector that allows you to interact with the Infinity Exchange.
The package utilizes threads to handle concurrent execution of REST API requests and WebSocket subscriptions.
This allows for efficient handling of multiple requests and real-time data streams without blocking the main execution thread.

The connector provides a <b>REST client</b> that allows you to make requests to all the available REST API endpoints of the Infinity exchange.
You can perform actions such as retrieving user information, and more.
It also includes a <b>WebSocket client</b> that enables you to subscribe to real-time data streams from the Infinity exchange.
You can subscribe to channels like orderbook data, user order data etc.

To access private endpoints and perform actions on behalf of a user, the package includes a <b>LoginClient</b> class.
This class handles the login process and manages the authentication using a <b>JWT access token</b>.
You can create an instance of the LoginClient class and pass it to the REST or WebSocket client for private session usage.



This project is undergoing active development, ensuring that new changes to the Infinity API will
be promptly integrated.

For feedback or suggestions, please reach out via one of the contact methods specified in <b>[Contact](#contact)</b>.

## Features
<ol style="line-height:180%" type="1">
<li>REST API Handling</li>
<li>WebSocket Handling</li>
<li>Login Client</li>
<li>Thread-based Execution</li>
<li>Exception Handling and Reconnection</li></ol>


| Release Version | Changelog                                    |
|-----------------|----------------------------------------------|
| `0.0.7`         | Stable release for testnet (**recommended**) |


## Documentation
For more detailed information, please refer to the [Infinity Exchange Docs](https://developers.infinity.exchange/#change-log).

## Quick Start

### Prerequisites
<code>python-infinity</code> is tested on python version: `3.11` to `3.11.6`.
Earlier or Later versions of Python might work, but they have not been thoroughly tested and could potentially conflict with the external web3 library.

<code>python-infinity</code> utilizes web3, threading, websocket-client and requests for its methods, alongside other
built-in modules.
As the package utilizes the web3 library, we suggest to use version `>=6.0.0` here.

### Installation
To get started with the <code>python-infinity</code> package, you can install it manually or via <b>PyPI</b> with <code>pip</code>:

```commandline
pip install python-infinity
```
### Known Issues
#### The <code>getargspec</code> Error (web3 version <= 5.31.4)

If you are using web3 version `<=5.31.4` You may encounter the following error: <code>ImportError: cannot import name 'getargspec' from 'inspect'</code>

This error message is the result of a slight conflict between the various package versions we need.

We will continue to look for a more permanent solution to this. But for the time being, please do the following quick fix to resolve this issue.

You can update web3 version: <code>>=6.0.0</code>

Or apply fix on <code>expressions.py</code>
<ol style="line-height:180%" type="1">
<li>Find <code>.../site-packages/parsimonious/expressions.py</code> and double-click <code>expressions.py</code> to open it</li>
<li>Inside <code>expressions.py</code> file, change <code>inspect import getargspec</code> to <code>inspect import getfullargspec</code></li>
<li>Error should be resolved, please run the code again</li></ol>

## Example Usage
To be able to interact with private endpoints, an ethereum EOA account (wallet address) and the corresponding private
key is <b>required</b>.
We suggest to not include those information in your source code directly but alternatively store them in environment
variables.
Again, please note that the python-infinity package is an <b>unofficial</b> project and should be used at your own risk.

<b>JWT access token</b> handling is managed in this package for authentication. For interacting with private endpoints and private websocket, a login is
required on the Infinity exchange side.
If you are planning to interact with any private endpoints, please create an instance of the LoginClient class and parse
it into the corresponding client (RestClient or WebSocketClient).
If you want to only interact with public endpoints and public websocket, the login step <code>2. Create an instance of the LoginClient
class</code> can be skipped.

### 1. Import the required modules

```python
# Infinity Exchange Login client
from infinity.login import LoginClient
# Infinity Exchange REST client
from infinity.rest_client import RestClient
# Infinity Exchange Websocket client
from infinity.websocket_client import WebSocketClient
```

### 2. Create an instance of the LoginClient class (Optional)
The login process will be carried out in the initializer of the LoginClient class.
If you only interact with public session, this part can be skipped.
Please refer to the documentation for information on how to use other parameters.

```python
from infinity.login import LoginClient as InfinityLogin

infinity_login = InfinityLogin(rest_url="Infinity Exchange REST URL",
                               chain_id="Chain ID",
                               account_address=account_address,  # user wallet address
                               private_key=private_key)  # user private key
```

### 3. REST / WEBSOCKET client

#### 3.1 REST client

Create a REST client instance, parse the infinity_login instance from <code>2. Create an instance of the LoginClient
class</code> for private endpoint usage.
Please refer to the documentation for information on how to use other parameters.
```python
from infinity.rest_client import RestClient as InfinityRestClient
# =============================================================================
# For public REST
# =============================================================================
infinity_public_rest = InfinityRestClient(rest_url="Infinity Exchange REST URL")
# =============================================================================
# For public and private REST
# =============================================================================
infinity_rest = InfinityRestClient(rest_url="Infinity Exchange REST URL",
                                   login=infinity_login)  # Infinity Exchange Login Client
```

Usage example:

```python
# Public endpoint method example
market_info_floating_rate = infinity_rest.get_floating_rate(instrument_id="ETH-SPOT")

# Private endpoint method example
user_info = infinity_rest.get_user_info()
```

#### 3.2 WEBSOCKET client
Create a WEBSOCKET client instance, parse the infinity_login instance from <code>2. Create an instance of the
LoginClient class</code> for private channel usage.

Please refer to the documentation for information on how to use other parameters.

```python
from infinity.websocket_client import WebSocketClient as InfinityWebsocketClient

# =============================================================================
# For public WEBSOCKET channel
# =============================================================================
infinity_public_ws = InfinityWebsocketClient(ws_url="Infinity Exchange Websocket URL",
                                             auto_reconnect_retries=3)  # default is 0 which would disable reconnection retries
infinity_public_ws.run_all()
infinity_public_ws.disconnect_all_ws_connection()  # disconnect all the websocket connection
# =============================================================================
# For private and public WEBSOCKET channel
# =============================================================================
infinity_ws = InfinityWebsocketClient(ws_url="Infinity Exchange Websocket URL",
                                      login=infinity_login,  # Infinity Exchange Login Client
                                      auto_reconnect_retries=3)
infinity_ws.run_all()

infinity_ws.disconnect_all_ws_connection()  # disconnect all the websocket connection
```

Usage example - channel subscription / unsubscription:

```python
# =============================================================================
# For public WEBSOCKET channel, e.g. orderbook data, recent trades
# =============================================================================

# Subscribing - recent trades
infinity_ws.subscribe_public_trades(instrument_id="USDC-SPOT")

# Unsubscribing - recent trades
infinity_ws.unsubscribe_public_trades(instrument_id="USDC-SPOT")

# Subscribing - orderbook data
infinity_ws.subscribe_orderbook(instrument_id="WBTC-2023-12-29")

# Unsubscribing - orderbook data
infinity_ws.unsubscribe_orderbook(instrument_id="WBTC-2023-12-29")

# =============================================================================
# For private WEBSOCKET channel, e.g. user order data, user trade data
# =============================================================================

# Subscribing - user order data
infinity_ws.subscribe_user_order(instrument_id="USDC-2023-11-03")

# Unsubscribing - user order data
infinity_ws.unsubscribe_user_order(instrument_id="USDC-2023-11-03")

# Subscribing - user trade data
infinity_ws.subscribe_user_trade(instrument_id="DAI-SPOT")

# Unsubscribing - user trade data
infinity_ws.unsubscribe_user_trade(instrument_id="DAI-SPOT")
```

Usage example - callbacks for extracting relevant data

```python
while True:
    # =============================================================================
    # For public WEBSOCKET channel, e.g. orderbook data, recent trades
    # =============================================================================
    public_trade = infinity_ws.get_received_data(channel="recentTrades")
    orderbook = infinity_ws.get_received_data(channel="orderBook")

    # =============================================================================
    # For private WEBSOCKET channel, e.g. user order data, user trade data
    # =============================================================================

    user_order = infinity_ws.get_received_data(channel="userOrder")
    user_trade = infinity_ws.get_received_data(channel="userTrade")
```
Infinity Websocket package also provides functions to be overridden for processing websocket data stream.
```python
def process_orderbook_data(self, orderbook: dict) -> None:
    pass # please refer to websocket client's process_orderbook_data
def process_public_trade(self, public_trade: dict) -> None:
    pass # please refer to websocket client's process_public_trade
def process_user_order(self, user_order: dict) -> None:
    pass # please refer to websocket client's process_user_order
def process_user_trade(self, user_trade: dict) -> None:
    pass # please refer to websocket client's process_user_trade
```

## Error Codes

Infinity Exchange uses the following error codes:

| Error code | Description                    |
|------------|--------------------------------|
| 1          | Success                        |
| 2          | Permission Denied              |
| 9          | Unexpected Error               |
| 1000       | Pemission Denied               |
| 1001       | Validation Error               |
| 1002       | Operation Failed               |
| 9999       | Unexpected Error               |
| 10000      | Invalid Wallet (Deposit)       |
| 10001      | Invalid Token (Deposit)        |
| 10010      | Invalid Wallet (Withdraw)      |
| 10011      | Invalid Token (Withdraw)       |
| 10012      | Not Enough Funds to Withdraw   |
| 10020      | Not Enough Tokens To Liquidate |
| 10021      | No Liquidation Steps Found     |
| 10022      | Liquidation Swap Failed        |

Order API error codes table

| Error code | Description                   |
|------------|-------------------------------|
| 102        | INVALID_ACCOUNT               |
| 104        | TIMEOUT                       |
| 107        | MINIMUM_QUANTITY_NOT_REACH    |
| 108        | NO_ORDER                      |
| 109        | ORDER_DONE_OR_CANCELLED       |
| 110        | TRADE_SERVER_PARSE            |
| 111        | TRADE_SERVER_ORDER_BOOK_ERROR |
| 112        | TRADE_SERVER_DB               |
| 113        | TRADE_SERVER_DB_CONNECTION    |
| 114        | MARKET_EXPIRED                |
| 115        | RATE_TRANSACTION_ERROR        |
| 120        | QUANTITY_STEP_NOT_MATCH       |
| 121        | NO_TWAP                       |
| 122        | INVALID_DEDUPLICATE_STRING    |
| 191        | ORDER_AUTO_CANCELLED          |
| 192        | ORDER_MANUALLY_CANCELLED      |

## Orders

### Order Sides

| Boolean   | Side   |
|-----------|--------|
| 0 (False) | Lend   |
| 1 (True)  | Borrow |

### Order Status Codes

| Status Code | Status                    | Description                           |
|-------------|---------------------------|---------------------------------------|
| 0           | STATUS_PENDING            | Pending (i.e. Not yet sent to market) |
| 1           | STATUS_ONBOOK             | On Book (i.e. Live order in market)   |
| 10          | STATUS_DONE               | Done (i.e. Fully executed)            |
| 11          | STATUS_MANUALLY_CANCELLED | Manually cancelled                    |
| 12          | STATUS_AUTO_CANCELLED     | Auto cancelled                        |
| 13          | STATUS_PARTIALLY_FILLED   | Partially Filled                      |
| 14          | STATUS_EXPIRED            | Market expired                        |
| 99          | STATUS_ERROR              | Error                                 |

### Order Types

| Type Code | Meaning      |
|-----------|--------------|
| 1         | Market Order |
| 2         | Limit Order  |

## Response Codes

| Code | Description                               |
|------|-------------------------------------------|
| 200  | OK                                        |
| 403  | Forbidden                                 |
| 500  | Internal Server Error or Invalid Response |
| 503  | Service Unavailable                       |

## Token IDs

| Code | Name        | Token ID | Quantity Step | Minimum Quantity | Rate Step |
|------|-------------|----------|---------------|------------------|-----------|
| ETH  | ETH         | 1        | 0.00001       | 0.001            | 0.0001    |
| USDT | USDT        | 2        | 0.01          | 1                | 0.0001    |
| USDC | USDC        | 3        | 0.01          | 1                | 0.0001    |
| DAI  | DAI         | 4        | 0.01          | 1                | 0.0001    |
| WBTC | Wrapped BTC | 5        | 0.000001      | 0.0001           | 0.0001    |

## Token Valuation Protocols

| Code | Protocol                   |
|------|----------------------------|
| 0    | No protocol / Not relevant |
| 1    | Aave                       |
| 2    | Uniswap                    |
| 3    | Compound                   |
| 4    | Curve                      |

## Transaction Types

| Code | Meaning                        |
|------|--------------------------------|
| 1    | Borrow                         |
| 2    | Lend                           |
| 3    | Repay                          |
| 4    | Unlend                         |
| 5    | Interest                       |
| 6    | Transfer In (Between Wallets)  |
| 7    | Transfer Out (Between Wallets) |
| 8    | External Transfer In           |
| 9    | External Transfer Out          |
| 10   | Trade                          |
| 11   | System Airdrop                 |
| 12   | LP Fee                         |
| 13   | Swap Secondary Token           |
| 14   | Withdrawal Fee                 |
| 15   | Transaction Fee                |
| 16   | LP Setup In                    |
| 17   | LP Setup Out                   |
| 18   | LP Unwind In                   |
| 19   | LP Unwind Out                  |
| 20   | Liquidation Unlend             |

## Disclaimer

This is an unofficial Python project (the "Package") and made available for informational purpose only and does not
constitute financial, investment or trading advice.
You acknowledge and agree to comply with the Terms of service at https://www.infinity.exchange/terms-conditions. If you
do not agree, please do not use this package.
Any unauthorised use of the Package is strictly prohibited.

## Contact

For support, suggestions or feedback please reach out to us via the following email address <code>pydevbuzz@gmail.com</code>