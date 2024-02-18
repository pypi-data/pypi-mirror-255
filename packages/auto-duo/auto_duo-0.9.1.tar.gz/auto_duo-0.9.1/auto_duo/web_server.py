from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
from _thread import start_new_thread
from threading import Lock
from time import sleep
from .main import activate, agree_forever
from .data import html_file as html

html = html.encode('utf-8')


class DuoServer:
    def create_request(self):
        class Request(BaseHTTPRequestHandler):
            def do_GET(self):
                path = self.path
                if (path in ['/', '/index.html']):
                    self.send_response(200)
                    self.send_header('Content-Length', len(html))
                    self.end_headers()
                    self.wfile.write(html)
                    return
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'404 Not Found')
                return

            def do_POST(self_):  # need to use the outer self
                response = {
                    'status': 0,
                    'data': '',
                    'error': ''
                }
                path = self_.path
                if (path != '/qr_submit'):
                    self_.send_response(404)
                    response['status'] = -1
                    response['error'] = 'Invalid url'
                    resp = json.dumps(response).encode('utf-8')
                    self_.send_header('Content-Length', len(resp))
                    self_.end_headers()
                    self_.wfile.write(resp)
                    return
                try:
                    data = self_.rfile.read(int(self_.headers['Content-Length'])).decode('utf-8')
                    data = json.loads(data)
                    qr_code = data['data']
                    _check = qr_code.split('-')
                    assert (len(_check) == 2 and len(_check[0]) == 20 and len(_check[1]) == 38)
                except:
                    self_.send_response(400)
                    response['status'] = -1
                    response['error'] = 'Invalid request'
                    resp = json.dumps(response).encode('utf-8')
                    self_.send_header('Content-Length', len(resp))
                    self_.end_headers()
                    self_.wfile.write(resp)
                    return
                status, result = activate(qr_code)
                if (status):
                    self.add_async(result)
                    start_new_thread(agree_forever, (result,))
                    self_.send_response(200)
                    response['status'] = 0
                    response['data'] = "Success"
                    resp = json.dumps(response).encode('utf-8')
                    self_.send_header('Content-Length', len(resp))
                    self_.end_headers()
                    self_.wfile.write(resp)
                    return
                result = result.lower()
                resp_text = "Failed"
                if (result.find('unknown') >= 0):
                    resp_text = "Invalid QR code, please check whether it has expired"
                response['status'] = -1
                response['error'] = resp_text
                self_.send_response(400)
                resp = json.dumps(response).encode('utf-8')
                self_.send_header('Content-Length', len(resp))
                self_.end_headers()
                self_.wfile.write(resp)
                return
        return Request

    def __init__(self, file_path: str, port: int):
        self.file_path = file_path
        self.json = []
        self.port = port
        self.lock = Lock()
        self.Request = self.create_request()
        file_exist = True
        try:
            f = open(file_path, 'r')
        except:
            file_exist = False
        if (file_exist):
            data = f.read()
            self.json = json.loads(data)
            f.close()
        else:
            self.json = []
        # ensure that we have write permission
        f = open(file_path, 'w')
        f.write(json.dumps(self.json, ensure_ascii=False))
        f.close()
        for a in self.json:
            start_new_thread(agree_forever, (a,))

    def __save(self):
        with self.lock:
            f = open(self.file_path, 'w')
            f.write(json.dumps(self.json, ensure_ascii=False))
            f.close()

    def __add(self, data_dict: str):
        with self.lock:
            self.json.append(data_dict)
        self.save_async()

    def save_async(self):
        start_new_thread(self.__save, ())

    def add_async(self, data_dict: str):
        start_new_thread(self.__add, (data_dict,))

    def start_async(self):
        server = ThreadingHTTPServer(('0.0.0.0', self.port), self.Request)
        start_new_thread(server.serve_forever, ())
        print(f'[*] Listening on 0.0.0.0:{self.port}')


def start_server(file_path: str, port: int):
    duo_server = DuoServer(file_path, port)
    duo_server.start_async()
    while True:
        sleep(10)
