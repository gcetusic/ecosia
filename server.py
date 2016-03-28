# -*- coding: utf-8 -*-

import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 8000


class EcosiaHttpRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()

        lang = self.headers.get('accept-language')
        self.wfile.write(str.encode('<html>\n'))
        self.wfile.write(str.encode('  <head>\n'))
        self.wfile.write(str.encode('    <title>Ecosian Response</title>\n'))
        self.wfile.write(str.encode('  </head>\n'))
        self.wfile.write(str.encode('  <body>\n'))
        self.wfile.write(str.encode(
            '    <p>Your language is: {}</p>\n'.format(lang)))
        self.wfile.write(str.encode(
            '    <p>You sent a: {}</p>\n'.format(self.command)))
        self.wfile.write(str.encode('  </body>\n'))
        self.wfile.write(str.encode('</html>\n'))

    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_len)
        post_vars = parse_qs(body.decode('utf-8')).get('postVar')

        if not post_vars:
            self.send_error(405, 'Missing POST parameter (postVar).')
            return
        for post_var in post_vars:
            post_var_value = ' '.join(post_vars)

        self._set_headers()
        lang = self.headers.get('accept-language')
        self.wfile.write(str.encode('<html>\n'))
        self.wfile.write(str.encode('  <head>\n'))
        self.wfile.write(str.encode('    <title>Ecosian Response</title>\n'))
        self.wfile.write(str.encode('  </head>\n'))
        self.wfile.write(str.encode('  <body>\n'))
        self.wfile.write(str.encode(
            '    <p>Your language is: {}</p>\n'.format(lang)))
        self.wfile.write(str.encode(
            '    <p>You sent a: {}</p>\n'.format(self.command)))
        self.wfile.write(str.encode(
            '    <p>Your POST variable value: {}</p>\n'.format(post_var_value)))
        self.wfile.write(str.encode('  </body>\n'))
        self.wfile.write(str.encode('</html>\n'))

    def handle_one_request(self):
        # overriding for 405 instead of 501 errors
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            if not self.path == "/":
                self.send_error(
                    404, "The requested resource could not be found (%r)" %
                    self.path)
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(405, "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            method()
            self.wfile.flush()
        except socket.timeout as e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return


def generate_server(
        server_class=HTTPServer, handler_class=EcosiaHttpRequestHandler,
        address='', port=8000):
    httpd = server_class((address, port), handler_class)
    return httpd

if __name__ == '__main__':
    try:
        from sys import argv

        if len(argv) == 2:
            SERVER_PORT = int(argv[1])

        httpd = generate_server(address=SERVER_ADDRESS, port=SERVER_PORT)

        print('Started HTTP server on {0}:{1}'.format(
            SERVER_ADDRESS, SERVER_PORT))
        httpd.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        httpd.socket.close()
