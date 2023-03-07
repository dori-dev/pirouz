import http.server
import socketserver


handler = http.server.SimpleHTTPRequestHandler
server_address = ('localhost', 8000)

with socketserver.TCPServer(server_address, handler) as http:
    url = "http://{}:{}/".format(*http.server_address)
    print(f"HTTP server is running on {url}")
    http.serve_forever()
