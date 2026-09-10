import os
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


# ============================================================
# VIPER 🐍 CORE
# ============================================================

BOT_NAME = "Viper"

MODE = os.getenv("VIPER_MODE", "paper").lower()
DEFAULT_SYMBOL = os.getenv("VIPER_SYMBOL", "XAUUSD")
DEFAULT_TIMEFRAME = os.getenv("VIPER_TIMEFRAME", "M5")

DEFAULT_LOT = float(os.getenv("VIPER_LOT", "0.01"))

ACTIVATION_PIPS = float(
    os.getenv("VIPER_ACTIVATION_PIPS", "2.0")
)

TRAILING_LOCK_PIPS = float(
    os.getenv("VIPER_TRAILING_LOCK_PIPS", "1.0")
)

MAX_TRADES = int(
    os.getenv("VIPER_MAX_TRADES", "1")
)

MAX_DAILY_LOSS = float(
    os.getenv("VIPER_MAX_DAILY_LOSS", "5.0")
)

API_KEY = os.getenv("VIPER_API_KEY", "")


# ============================================================
# VIPER STATE
# ============================================================

@dataclass
class ViperState:

    running: bool = False

    mode: str = MODE

    symbol: str = DEFAULT_SYMBOL

    timeframe: str = DEFAULT_TIMEFRAME

    lot: float = DEFAULT_LOT

    trades_today: int = 0

    daily_profit: float = 0.0

    last_signal_id: str = ""

    last_signal_time: float = 0.0

    last_action: str = ""

    last_message: str = ""

    created_at: float = time.time()


STATE = ViperState()


# ============================================================
# TIME
# ============================================================

def utc_now():

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticated(headers):

    if not API_KEY:
        return False

    supplied = headers.get(
        "X-Viper-Key",
        ""
    )

    return supplied == API_KEY


# ============================================================
# STATE OUTPUT
# ============================================================

def json_safe_state():

    data = asdict(STATE)

    data["bot"] = BOT_NAME

    data["server_time"] = utc_now()

    return data


# ============================================================
# DAILY RESET
# ============================================================

def reset_daily_if_needed():

    if STATE.trades_today < 0:
        STATE.trades_today = 0


# ============================================================
# RISK CONTROL
# ============================================================

def risk_allowed():

    reset_daily_if_needed()

    if not STATE.running:

        return False, "Viper is stopped"

    if STATE.trades_today >= MAX_TRADES:

        return False, "Maximum daily trade count reached"

    if STATE.daily_profit <= -abs(MAX_DAILY_LOSS):

        return False, "Maximum daily loss reached"

    return True, "Risk checks passed"


# ============================================================
# TRADE REGISTRATION
# ============================================================

def register_trade():

    STATE.trades_today += 1


def register_result(profit):

    STATE.daily_profit += float(
        profit
    )


# ============================================================
# UNIQUE ID
# ============================================================

def generate_id():

    return str(
        uuid.uuid4()
    )


# ============================================================
# PIP SIZE
# ============================================================

def pip_size(symbol):

    symbol = symbol.upper()

    if "JPY" in symbol:

        return 0.01

    if "XAU" in symbol or "GOLD" in symbol:

        return 0.01

    return 0.0001


# ============================================================
# VALID ORDER SIDES
# ============================================================

def valid_side(side):

    return side.upper() in {
        "BUY",
        "SELL",
        "BUY_STOP",
        "SELL_STOP"
    }


def normalize_action(action):

    return str(
        action
    ).upper().strip()


# ============================================================
# FULL-BODY CANDLE DETECTION
# ============================================================

def full_body_signal(candle):

    required = [
        "open",
        "high",
        "low",
        "close"
    ]

    for field in required:

        if field not in candle:

            return None

    try:

        o = float(
            candle["open"]
        )

        h = float(
            candle["high"]
        )

        l = float(
            candle["low"]
        )

        c = float(
            candle["close"]
        )

    except Exception:

        return None


    if h < l:

        return None


    # Small floating-point tolerance
    tolerance = max(
        abs(o) * 0.000001,
        1e-9
    )


    # Bullish full-body candle
    bullish = (
        c > o
        and abs(l - o) <= tolerance
    )


    # Bearish full-body candle
    bearish = (
        c < o
        and abs(h - o) <= tolerance
    )


    if bullish:

        return {

            "action": "SELL_STOP",

            "entry": o,

            "stop_loss": h,

            "reason":
                "Bullish full-body candle"

        }


    if bearish:

        return {

            "action": "BUY_STOP",

            "entry": o,

            "stop_loss": l,

            "reason":
                "Bearish full-body candle"

        }


    return None


# ============================================================
# TRAILING STOP
# ============================================================

def trailing_stop(
    side,
    entry,
    current,
    old_stop,
    symbol
):

    size = pip_size(
        symbol
    )

    if size <= 0:

        return old_stop


    side = side.upper()

    entry = float(entry)

    current = float(current)

    old_stop = float(old_stop)


    # --------------------------------------------------------
    # BUY
    # --------------------------------------------------------

    if side == "BUY":

        profit_pips = (
            current - entry
        ) / size


        if profit_pips < ACTIVATION_PIPS:

            return old_stop


        candidate = (
            current
            - TRAILING_LOCK_PIPS * size
        )


        return max(
            old_stop,
            candidate
        )


    # --------------------------------------------------------
    # SELL
    # --------------------------------------------------------

    if side == "SELL":

        profit_pips = (
            entry - current
        ) / size


        if profit_pips < ACTIVATION_PIPS:

            return old_stop


        candidate = (
            current
            + TRAILING_LOCK_PIPS * size
        )


        return min(
            old_stop,
            candidate
        )


    return old_stop
