from http.server import BaseHTTPRequestHandler
import json
import time

from _viper import (
    authenticated,
    STATE,
    full_body_signal,
    generate_id,
    risk_allowed
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


    def do_POST(self):

        # Check Viper API key
        if not authenticated(self.headers):

            self.send_json(
                401,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message": "Unauthorized"
                }
            )

            return


        # Read request
        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            raw = self.rfile.read(length)

            data = json.loads(
                raw.decode("utf-8")
            )

        except Exception:

            self.send_json(
                400,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message": "Invalid JSON"
                }
            )

            return


        # Candle data
        candle = data.get("candle")

        if not isinstance(candle, dict):

            self.send_json(
                400,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message": "candle object required"
                }
            )

            return


        # Detect full-body candle
        signal = full_body_signal(candle)


        # No setup
        if signal is None:

            self.send_json(
                200,
                {
                    "bot": "Viper",
                    "status": "no_signal",
                    "message":
                        "No valid full-body candle detected"
                }
            )

            return


        # Risk check
        allowed, reason = risk_allowed()

        if not allowed:

            self.send_json(
                403,
                {
                    "bot": "Viper",
                    "status": "signal_blocked",
                    "signal": signal,
                    "message": reason
                }
            )

            return


        # Create signal ID
        signal_id = generate_id()


        STATE.last_signal_id = signal_id

        STATE.last_signal_time = time.time()

        STATE.last_action = signal["action"]

        STATE.last_message = signal["reason"]


        # Return signal
        self.send_json(
            200,
            {
                "bot": "Viper",

                "status":
                    "signal_detected",

                "signal_id":
                    signal_id,

                "symbol":
                    data.get(
                        "symbol",
                        STATE.symbol
                    ),

                "timeframe":
                    data.get(
                        "timeframe",
                        STATE.timeframe
                    ),

                "signal":
                    signal,

                "message":
                    "Viper detected a valid strategy setup."
            }
        )
