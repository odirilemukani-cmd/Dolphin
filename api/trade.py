from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            data = json.loads(body) if body else {}

            symbol = data.get("symbol", "XAUUSD")
            action = data.get("action", "").upper()
            lot = float(data.get("lot", 0.01))

            if action not in ["BUY", "SELL"]:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                self.wfile.write(json.dumps({
                    "bot": "Dolphin",
                    "status": "error",
                    "message": "Action must be BUY or SELL"
                }).encode())

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

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps(response).encode()
            )

        except Exception as error:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps({
                "bot": "Dolphin",
                "status": "error",
                "message": str(error)
            }).encode())
