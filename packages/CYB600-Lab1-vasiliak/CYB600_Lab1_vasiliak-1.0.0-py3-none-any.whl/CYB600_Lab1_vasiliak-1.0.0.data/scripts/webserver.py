#!python
from src.main import HTTPRequestHandler, HTTPServer


def run(server_class=HTTPServer, handler_class=HTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()