# Path Placeholders
PATH_PLACEHOLDER_TOKEN_ID = "{tokenId}"
PATH_PLACEHOLDER_ID = "{id}"
PATH_PLACEHOLDER_ACCOUNT_ID = "{accountId}"

# URl Query keys
QUERY_KEY_BLOCKCHAIN_ID = "blockChainId"
QUERY_KEY_TOKEN_ID = "tokenId"
QUERY_KEY_INSTRUMENT_ID = "instrumentId"
QUERY_KEY_ORDER_QTY = "orderQty"
QUERY_KEY_ONLY_ON_BOOK = "onlyOnbook"
QUERY_KEY_USER_ADDRESS = "userAddress"
QUERY_KEY_ORDER_ID = "orderId"
QUERY_KEY_START_ID = "startId"
QUERY_KEY_ASCENDING = "asc"
QUERY_KEY_LIMIT = "limit"
QUERY_KEY_START = "start"
QUERY_KEY_END = "end"
QUERY_KEY_INTERVAL = "interval"
QUERY_KEY_ACCOUNT_ID = "accountId"
QUERY_KEY_PENDING = "pending"
QUERY_KEY_DONE = "done"
QUERY_KEY_LAST_FLOATING_RATE_ORDER_ID = "lastRateOrderId"
QUERY_KEY_LAST_FIXED_RATE_ORDER_ID = "lastFixedRateOrderId"
QUERY_KEY_DAYS_TO_INCLUDE = "daysToInclude"
QUERY_KEY_FLOATING_RATE_INSTRUMENT_ID = "floatRateInstrumentId"
QUERY_KEY_LIST_FIXED_RATE_INSTRUMENT_IDS = "fixedRateInstrumentIds"
QUERY_KEY_MIN_BID_N_ASK_SIZE = "minBidNAskSize"
QUERY_KEY_TASK_ID = "taskID"
QUERY_KEY_INSTRUMENT_IDS = "instrumentIds"
QUERY_KEY_START_BLOCK_ID = "startBlockId"
QUERY_KEY_TYPE = "type"
QUERY_KEY_FROM_ACCOUNT_ID = "fromAccountId"
QUERY_KEY_TO_ACCOUNT_ID = "toAccountId"
QUERY_KEY_QUANTITY = "quantity"
QUERY_KEY_REQUEST_IDS = "requestIds"
QUERY_KEY_NAME = "name"
QUERY_KEY_CHAIN_ID = "chainId"
QUERY_KEY_FULL_YIELD_CURVE = "fullYieldCurve"

# Request Body fields
ADDRESS = "addr"
CHAIN_ID = "chainId"
CLIENT_ORDER_ID = "clientOrderId"
CLIENT_ORDER_IDS = "clientOrderIds"
INSTRUMENT_ID = "instrumentId"
NONCE_HASH = "nonceHash"
ORDER_IDS = "orderIds"
ORDER_TYPE = "orderType"
PASSIVE = "passive"
PRICE = "price"
RATE = "rate"
QUANTITY = "quantity"
REFRESH_TOKEN = "refreshToken"
SIDE = "side"
STATUS = "status"
ACCOUNT_ID = "accountId"

# Order status
ON_BOOK = "on_book"
DONE = "done"
MANUALLY_CANCELLED = "manually_cancelled"
AUTO_CANCELLED = "auto_cancelled"
PARTIALLY_FILLED = "partially_filled"
ORDER_STATUS_TYPE = {
    1: ON_BOOK,
    10: DONE,
    11: MANUALLY_CANCELLED,
    12: AUTO_CANCELLED,
    13: PARTIALLY_FILLED
}

# Order types
ORDER_TYPE_MARKET = 1
ORDER_TYPE_LIMIT = 2

# Order side
ORDER_SIDE_LEND = 0
ORDER_SIDE_BORROW = 1

# *** Funding ***
PRIVATE_DEPOSIT_ENDPOINT = "/private/deposit"
PRIVATE_GET_WITHDRAW_STATUS_ENDPOINT = "/private/get_withdraw_status"
PRIVATE_GET_WITHDRAWS_ENDPOINT = "/private/get_withdraws"
PRIVATE_WITHDRAW_ENDPOINT = "/private/withdraw"
PUBLIC_GET_BLOCKCHAIN_INFO_ENDPOINT = "/public/get_blockchain_info"

# *** Markets ***
PRIVATE_GET_MARKET_MTMS_ENDPOINT = "/private/get_market_mtms"
PRIVATE_GET_MARKET_SUMMARIES_ENDPOINT = "/private/get_market_summaries"
PUBLIC_GET_24H_SNAPSHOT_ENDPOINT = "/public/get_24h_snapshot"
PUBLIC_GET_ALL_FIXED_DETAILS_ENDPOINT = "/public/get_all_fixed_details"
PUBLIC_GET_ALL_FLOATING_DETAILS_ENDPOINT = "/public/get_all_floating_details"
PUBLIC_GET_ALL_MARKETS_ENDPOINT = "/public/get_all_markets"
PUBLIC_GET_ALL_ORDER_BUCKETS_ENDPOINT = "/public/get_all_order_buckets"
PUBLIC_GET_BBA_ENDPOINT = "/public/get_bba"
PUBLIC_GET_FIXED_DETAILS_ENDPOINT = "/public/get_fixed_details"
PUBLIC_GET_FIXED_FEES_ENDPOINT = "/public/get_fixed_fees"
PUBLIC_GET_FIXED_HISTORY_ENDPOINT = "/public/get_fixed_history"
PUBLIC_GET_FIXED_ORDERBOOK_ENDPOINT = "/public/get_fixed_orderbook"
PUBLIC_GET_FIXED_RATE_ENDPOINT = "/public/get_fixed_rate"
PUBLIC_GET_FIXED_TRADES_ENDPOINT = "/public/get_fixed_trades"
PUBLIC_GET_FLOATING_DETAILS_ENDPOINT = "/public/get_floating_details"
PUBLIC_GET_FLOATING_HISTORY_ENDPOINT = "/public/get_floating_history"
PUBLIC_GET_FLOATING_ORDERBOOK_ENDPOINT = "/public/get_floating_orderbook"
PUBLIC_GET_FLOATING_RATE_ENDPOINT = "/public/get_floating_rate"
PUBLIC_GET_FLOATING_TRADES_ENDPOINT = "/public/get_floating_trades"
PUBLIC_GET_HISTORICAL_TOTAL_VALUE_ENDPOINT = "/public/get_historical_total_value"
PUBLIC_GET_HISTORICAL_RATES_ENDPOINT = "/public/get_historical_rates"
PUBLIC_GET_HISTORICAL_YIELD_CURVE_ENDPOINT = "/public/get_historical_yield_curve"
PUBLIC_GET_YIELD_CURVE_ENDPOINT = "/public/get_yield_curve"

# *** Tokens ***
PRIVATE_GET_TOKEN_MTMS_ENDPOINT = "/private/get_token_mtms"
PUBLIC_GET_TOKEN_DETAILS_ENDPOINT = "/public/get_token_details"
PUBLIC_GET_TOKENS_ENDPOINT = "/public/get_tokens"
PUBLIC_GET_UNDERLYING_TOKENS_ENDPOINT = "/public/get_underlying_tokens"

# *** Trading ***
PRIVATE_AGGREGATE_ORDERS_BY_RATE_ENDPOINT = "/private/aggregate_orders_by_rate"
PRIVATE_BATCH_CANCEL_ORDERS_ENDPOINT = "/api/trade/cancel-batch-orders"
PRIVATE_CANCEL_ORDER_ENDPOINT = "/api/trade/cancel-order"
PRIVATE_CREATE_FIXED_ORDER_ENDPOINT = "/private/create_fixed_order"
PRIVATE_CREATE_FLOATING_ORDER_ENDPOINT = "/private/create_floating_order"
PRIVATE_GET_FIXED_ORDERS_ENDPOINT = "/private/get_fixed_orders"
PRIVATE_GET_FLOATING_ORDERS_ENDPOINT = "/private/get_floating_orders"
PRIVATE_GET_FLOATING_POSITIONS_ENDPOINT = "/private/get_floating_positions"
PRIVATE_GET_FLOATING_TRADES_ENDPOINT = "/private/get_floating_trades"
PRIVATE_GET_FIXED_TRADES_ENDPOINT = "/private/get_fixed_trades"
PRIVATE_GET_ALL_POSITIONS_ENDPOINT = "/private/get_all_positions"

# *** User ***
PRIVATE_GET_USER_INFO_ENDPOINT = "/private/get_user_info"

# *** Account ***
PRIVATE_GET_ALL_ACCOUNT_TX_ENDPOINT = "/private/get_all_account_tx"
PRIVATE_GET_MAX_BORROW_ENDPOINT = "/private/get_max_borrow"
PRIVATE_GET_ACCOUNT_INFO_ENDPOINT = "/private/get_account_info"
PRIVATE_GET_ACCOUNT_TX_ENDPOINT = "/private/get_account_tx"
PRIVATE_GET_ACCOUNTS_ENDPOINT = "/private/get_accounts"
PRIVATE_TRANSFER_FLOATING_POSITION_ENDPOINT = "/private/transfer_floating_position"
PRIVATE_TRANSFER_TOKEN_ENDPOINT = "/private/transfer_token"
PRIVATE_UPDATE_ACCOUNT_NAME_ENDPOINT = "/private/update_account_name"

# will be deprecated
PRIVATE_CANCEL_FIXED_ORDER_ENDPOINT = "/private/cancel_fixed_order"
PRIVATE_CANCEL_FLOATING_ORDER_ENDPOINT = "/private/cancel_floating_order"
PRIVATE_GET_POSITIONS_AND_DV01_ENDPOINT = "/private/get_positions_and_dv01"
