# *** Public Channels ***
CHANNEL_RECENT_TRADES = "recentTrades"
CHANNEL_ORDER_BOOK = "orderBook"
CHANNEL_USER_TRADE = "userTrade"
CHANNEL_USER_ORDER = "userOrder"

# *** Private Channels ***
# To be implemented

# General keys
TRADE_ID = "trade_id"
ACCOUNT_ID = "account_id"
ORDER_ID = "order_id"
INSTRUMENT_ID = "instrument_id"
SYMBOL = "symbol"
RATE = "rate"
PRICE = "price"
QUANTITY = "quantity"
ACC_FILL_SIZE = "acc_fill_size"
SIDE = "side"
LEND = "lend"
BORROW = "borrow"
UPDATE_TIME = "update_time"
RATES_TYPE = "rates_type"
FLOATING = "floating"
FIXED_RATE = "fixed_rate"
MARKET_ORDER = "market_order"
LIMIT_ORDER = "limit_order"
# *** market data / marketInfo channel ***

# only for floating rate market - SPOT
LAST_INDEX_RATE_UPDATE_TIME = "index_rate_update_time"
BORROW_RATE_INDEX = "borrow_rate_index"
LEND_RATE_INDEX = "lend_rate_index"

# only for fixed rate market
MARKET_MID_RATE = "mid_rate"

# *** orderbook channel ***
BIDS = "bids"
ASKS = "asks"

# *** public trades ***
TRADE_TIME = "trade_time"

# *** Order ***
ORDER_TYPE = "order_type"
CLIENT_ORDER_ID = "client_order_id"
MARKET_TYPE = "market_type"
CREATE_TIME = "create_time"
ORDER_STATUS = "order_status"
ORDER_STATUS_TYPE = {
    1: "on_book",
    10: "done",
    11: "manually_cancelled",
    12: "auto_cancelled",
    13: "partially_filled"
}
