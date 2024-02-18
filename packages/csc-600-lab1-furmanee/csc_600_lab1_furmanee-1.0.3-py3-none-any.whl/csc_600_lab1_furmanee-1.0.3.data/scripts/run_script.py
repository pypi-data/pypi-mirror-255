#!python

from src.main import MyHandler

port = 8000

with HTTPServer(('localhost', port), MyHandler) as server:
    print(f"Serving on port {port}")
    # Start the server
    server.serve_forever()

do_GET()