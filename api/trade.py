from http.server import BaseHTTPRequestHandler
import json

from _viper import (
    authenticated,
    STATE,
    risk_allowed,
    register_trade,
    normalize_action,
    valid_side,
    generate_id
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


        # Risk check
        allowed, reason = risk_allowed()

        if not allowed:

            self.send_json(
                403,
                {
                    "bot": "Viper",
                    "status": "blocked",
                    "message": reason
                }
            )

            return


        # Get action
        action = normalize_action(
            data.get("action", "")
        )


        # Validate action
        if not valid_side(action):

            self.send_json(
                400,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message": "Invalid action"
                }
            )

            return


        symbol = str(
            data.get(
                "symbol",
                STATE.symbol
            )
        ).upper()


        timeframe = str(
            data.get(
                "timeframe",
                STATE.timeframe
            )
        ).upper()


        # Validate lot
        try:

            lot = float(
                data.get(
                    "lot",
                    STATE.lot
                )
            )

        except Exception:

            self.send_json(
                400,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message": "Invalid lot"
                }
            )

            return


        if lot <= 0:

            self.send_json(
                400,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message": "Lot must be greater than zero"
                }
            )

            return


        # Optional order prices
        entry = data.get("entry")

        stop_loss = data.get(
            "stop_loss"
        )


        # Generate order ID
        order_id = generate_id()


        # Register trade
        register_trade()


        mode = STATE.mode


        if mode == "paper":

            status = "paper_trade_accepted"

            execution = {

                "executed": False,

                "broker": "paper"

            }

            message = (
                "Paper trade recorded. "
                "No real money was used."
            )

        else:

            status = (
                "live_order_accepted_by_api"
            )

            execution = {

                "executed": False,

                "broker":
                    "broker_adapter_required"

            }

            message = (
                "Order accepted by Viper API. "
                "A connected broker adapter "
                "must execute it."
            )


        # Response
        self.send_json(
            200,
            {

                "bot": "Viper",

                "status": status,

                "mode": mode,

                "order": {

                    "id": order_id,

                    "symbol": symbol,

                    "timeframe": timeframe,

                    "action": action,

                    "lot": lot,

                    "entry": entry,

                    "stop_loss": stop_loss

                },

                "execution": execution,

                "message": message

            }
        )
