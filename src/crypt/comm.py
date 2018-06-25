#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   crypt/comm.py
#
########################################################################################################################
#    Author: Vikas Munshi <vikas.munshi@gmail.com>
#    Version 0.0.1: 2018.05.24
#
#    source: https://github.com/vikasmunshi/python-scripts/tree/master/src/
#    set-up: bash <(curl -s https://github.com/vikasmunshi/python-scripts/tree/master/src/setup.sh)
#
########################################################################################################################
#    MIT License
#
#    Copyright (c) 2018 Vikas Munshi
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the 'Software'), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
########################################################################################################################

from http.client import HTTPConnection, HTTPException, HTTPSConnection
from http.server import BaseHTTPRequestHandler, HTTPStatus
from json import dumps, loads
from socket import getfqdn, timeout
from socketserver import ThreadingTCPServer
from threading import Thread
from urllib.parse import parse_qs, unquote, urlencode

try:
    from . import __version__
except ImportError:
    __version__ = '0.0.1'


class RemoteObj(object):
    def __init__(self, methods: dict):
        for method, implementation in methods.items():
            setattr(self, method, implementation)

    def http_get(self, args: list, params: dict, headers: dict) -> dict:
        if not args:
            args = ['info']
        return getattr(self, args[0])(args, params)

    def info(self, *args, **kwargs) -> dict:
        return {'doc': 'documentation'}

    getters = []
    putters = []


class Store(dict):
    def http_get(self, args: list, params: dict, headers: dict) -> dict:
        key = '.'.join(args) if args else 'info'
        return {key: super().get(key)}

    def http_put(self, args: list, params: dict, headers: dict) -> dict:
        if args:
            key = '.'.join(args)
            if key not in self:
                value = params.get('value')
                self[key] = value
            return {key: self[key]}

    getters = []
    putters = []


class RequestHandler(BaseHTTPRequestHandler):
    server_version = 'CryptHTTP/' + __version__
    default_request_version = 'HTTP/0.9'
    protocol_version = 'HTTP/1.1'
    http_headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/json', 'Connection': 'keep-alive'}

    def handle_one_request(self) -> None:
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return
            try:
                req_path, _, req_query = self.path.partition('?')
                req_path = [str(x) for x in unquote(req_path).split('/') if x] if req_path else []
                req_query = {k: v[0] for (k, v) in parse_qs(req_query, True, False).items()} if req_query else {}
                req_body = self.rfile.read(int(self.headers.get('content-length', 0))).decode()
                req_body = loads(req_body) if req_body else {}
                req_params = dict(req_query, **req_body)
                req_headers = dict(self.headers)
            except (AttributeError, IndexError, TypeError) as e:
                self.log_error('bad request\n%r', e)
                self.send_error(HTTPStatus.BAD_REQUEST)
                return
            if not req_path:
                req_path = ['info']
            try:
                obj = getattr(self.server, req_path[0])
            except AttributeError:
                self.log_error('%s not implemented', req_path[0])
                self.send_error(HTTPStatus.NOT_IMPLEMENTED, req_path[0])
                return
            try:
                func = getattr(obj, 'http_' + self.command.lower())
            except AttributeError:
                self.log_error('%s not implemented', self.command.lower())
                self.send_error(HTTPStatus.NOT_IMPLEMENTED, self.command.lower())
                return
            try:
                response = func(req_path[1:], req_params, req_headers)
            except AttributeError:
                self.log_error('%s not implemented', req_path[1])
                self.send_error(HTTPStatus.NOT_IMPLEMENTED, req_path[1])
                return
            try:
                response = dumps(response or {}).encode()
                len_message = len(response)
                self.send_response(HTTPStatus.OK)
                for k, v in self.http_headers.items():
                    self.send_header(k, v)
                self.send_header('Content-Length', len_message)
                self.end_headers()
                self.wfile.write(response)
                self.wfile.flush()
            except (IndexError, TypeError) as e:
                self.log_error('internal server error\n%r', e)
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
                return
        except timeout as e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return


class Server(ThreadingTCPServer):
    def __init__(self, ip: str, port: int):
        super().__init__(server_address=(ip, port), RequestHandlerClass=RequestHandler, bind_and_activate=True)
        self.allow_reuse_address = True
        self.server_name = getfqdn(self.server_address[0])
        self.server_port = self.server_address[1]
        self.cmd = RemoteObj(methods={'stop': self.stop, 'info': self.info})

    def add_method(self, name: str, obj: RemoteObj) -> None:
        setattr(self, name, obj)

    def add_store(self, name: str, store: Store) -> None:
        setattr(self, name, store)

    def start(self) -> None:
        thread = Thread(target=self.serve_forever)
        thread.daemon = False
        thread.start()
        print('Server listening on {}:{}'.format(*self.server_address))

    def stop(self, *args, **kwargs) -> dict:
        self.shutdown()
        return {'status': 'shutdown'}

    def info(self, *args, **kwargs) -> dict:
        return {'status': 'ok'}


class Client(object):
    http_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def __init__(self, ip: str, port: int, timeout: int = 2):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def __enter__(self):
        self.conn = HTTPConnection(host=self.ip, port=self.port, timeout=self.timeout)
        self.conns = HTTPSConnection(host=self.ip, port=self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def get_response(self):
        response = self.conn.getresponse()
        if response.status == HTTPStatus.OK:
            if response.headers.get('content-type') == 'application/json':
                return loads(response.read())
            else:
                raise HTTPException('server returned non json response {}'.format(response.read()))
        else:
            raise HTTPException('server returned code {} {}'.format(response.status, response.reason))

    def get(self, path: str, query_params: dict = None) -> dict:
        self.conn.request(method='GET', url=path + (('?' + urlencode(query_params)) if query_params else ''))
        return self.get_response()

    def put(self, path: str, query_params: dict = None) -> dict:
        self.conn.request(method='PUT', url=path, body=dumps(query_params or {}), headers=self.http_headers)
        return self.get_response()

    def post(self, path: str, query_params: dict = None) -> dict:
        self.conn.request(method='POST', url=path, body=dumps(query_params or {}), headers=self.http_headers)
        return self.get_response()


if __name__ == '__main__':
    from sys import argv

    ip = '127.0.0.1'
    port = 50124
    args = argv[1:]
    if not args:
        with Client(ip, port) as c:
            print(c.get('/'))
    elif args[0] == 'start':
        s = Server(ip=ip, port=port)
        s.start()
    elif args[0] == 'stop':
        with Client(ip, port) as c:
            print(c.get('/cmd/shutdown'))
    elif args[0] == 'status':
        with Client(ip, port) as c:
            print(c.get('/cmd/status'))
    elif args[0] == 'test':
        with Server(ip=ip, port=port) as s:
            s.add_store('shares', Store())
            s.start()
            with Client(ip, port) as c:
                try:
                    c.put('/shares/a', {'value': {'x': 1, 'y': 1}})
                except Exception as e:
                    print(e)
                for x in ('/cmd/info', '/shares/', '/shares/a', '/cmd/xshutdown', '/cmd/stop'):
                    try:
                        print(c.get(x))
                    except Exception as e:
                        print(e)
            s.stop()
    else:
        with Client(ip, port) as c:
            print(c.get(args[0], {k: '' for k in args[1:]}))
