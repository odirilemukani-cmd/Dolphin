from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class DolphinHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            response = {
                "bot": "Dolphin",
                "status": "online"
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps(response).encode()
            )

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("0.0.0.0", 8000), DolphinHandler)

print("Dolphin server started on port 8000")

server.serve_forever()
