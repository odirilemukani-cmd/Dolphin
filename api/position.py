from http.server import BaseHTTPRequestHandler
import json

from _viper import (
    authenticated,
    trailing_stop
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


        # Required position data
        required = [
            "side",
            "entry",
            "current",
            "stop_loss",
            "symbol"
        ]


        missing = [
            field
            for field in required
            if field not in data
        ]


        if missing:

            self.send_json(
                400,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message":
                        "Missing position fields",
                    "missing": missing
                }
            )

            return


        # Calculate trailing stop
        try:

            new_stop = trailing_stop(

                data["side"],

                float(data["entry"]),

                float(data["current"]),

                float(data["stop_loss"]),

                data["symbol"]

            )

        except Exception:

            self.send_json(
                400,
                {
                    "bot": "Viper",
                    "status": "error",
                    "message":
                        "Invalid position values"
                }
            )

            return


        # Return result
        self.send_json(
            200,
            {
                "bot": "Viper",

                "status":
                    "trailing_calculated",

                "symbol":
                    data["symbol"],

                "side":
                    data["side"],

                "old_stop":
                    data["stop_loss"],

                "new_stop":
                    new_stop
            }
        )
