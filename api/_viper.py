from http.server import BaseHTTPRequestHandler
import json

from _viper import (
    BOT_NAME,
    MODE,
    DEFAULT_SYMBOL,
    DEFAULT_TIMEFRAME,
    DEFAULT_LOT,
    ACTIVATION_PIPS,
    TRAILING_LOCK_PIPS,
    MAX_TRADES,
    MAX_DAILY_LOSS,
    json_safe_state
)


class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(
            json.dumps(data).encode("utf-8")
        )


    def do_GET(self):

        state = json_safe_state()

        self.send_json(
            200,
            {
                "bot": BOT_NAME,

                "status": "online",

                "running": state["running"],

                "mode": state["mode"],

                "symbol": state["symbol"],

                "timeframe": state["timeframe"],

                "lot": state["lot"],

                "strategy": {

                    "name": "Candle Flip",

                    "full_body_detection": True,

                    "opposite_stop": True

                },

                "protection": {

                    "activation_pips":
                        ACTIVATION_PIPS,

                    "trailing_lock_pips":
                        TRAILING_LOCK_PIPS,

                    "max_trades":
                        MAX_TRADES,

                    "max_daily_loss":
                        MAX_DAILY_LOSS

                },

                "state": state
            }
        )
