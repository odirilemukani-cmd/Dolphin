from http.server import BaseHTTPRequestHandler
import json

from _viper import (
    authenticated,
    STATE,
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


        command = str(
            data.get("command", "")
        ).lower().strip()


        # START
        if command == "start":

            STATE.running = True

            STATE.last_action = "START"

            STATE.last_message = "Viper started"


        # STOP
        elif command == "stop":

            STATE.running = False

            STATE.last_action = "STOP"

            STATE.last_message = "Viper stopped"


        # PAPER MODE
        elif command == "paper":

            STATE.mode = "paper"

            STATE.last_action = "PAPER"

            STATE.last_message = (
                "Paper mode selected"
            )


        # LIVE MODE
        elif command == "live":

            STATE.mode = "live"

            STATE.last_action = "LIVE"

            STATE.last_message = (
                "LIVE mode selected. "
                "Broker execution is required."
            )


        # CONFIGURE
        elif command == "configure":

            symbol = data.get("symbol")

            timeframe = data.get("timeframe")

            lot = data.get("lot")


            if symbol:

                STATE.symbol = str(
                    symbol
                ).upper()


            if timeframe:

                STATE.timeframe = str(
                    timeframe
                ).upper()


            if lot is not None:

                try:

                    new_lot = float(lot)

                    if new_lot <= 0:

                        raise ValueError

                    STATE.lot = new_lot

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


            STATE.last_action = "CONFIGURE"

            STATE.last_message = (
                "Configuration updated"
            )


        # UNKNOWN COMMAND
        else:

            self.send_json(
                400,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message": "Unknown command"
                }
            )

            return


        # Successful response
        self.send_json(
            200,
            {
                "bot": "Viper",
                "status": "updated",
                "state": json_safe_state()
            }
        )
