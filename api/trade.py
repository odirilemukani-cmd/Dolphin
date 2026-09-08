from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(
            json.dumps(data).encode("utf-8")
        )

    def do_POST(self):

        # Check API key
        api_key = self.headers.get("X-Dolphin-Key")
        correct_key = os.environ.get("DOLPHIN_API_KEY")

        if not correct_key or api_key != correct_key:
            self.send_json(401, {
                "bot": "Dolphin",
                "status": "error",
                "message": "Unauthorized"
            })
            return

        try:
            length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(length)

            data = json.loads(body) if body else {}

            symbol = data.get("symbol", "XAUUSD")
            action = data.get("action", "").upper()
            lot = float(data.get("lot", 0.01))

            if action not in ["BUY", "SELL"]:
                self.send_json(400, {
                    "bot": "Dolphin",
                    "status": "error",
                    "message": "Action must be BUY or SELL"
                })
                return

            if lot <= 0:
                self.send_json(400, {
                    "bot": "Dolphin",
                    "status": "error",
                    "message": "Lot must be greater than 0"
                })
                return

            response = {
                "bot": "Dolphin",
                "status": "paper_trade_received",
                "mode": "paper",
                "symbol": symbol,
                "action": action,
                "lot": lot,
                "message": "Paper trade accepted. No real trade was placed."
            }

            self.send_json(200, response)

        except Exception as error:

            self.send_json(400, {
                "bot": "Dolphin",
                "status": "error",
                "message": str(error)
            })
