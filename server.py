#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse
from phonetics_api import phonetics_api

PORT = 8000

# 数据文件路径
PROGRESS_FILE = 'progress.json'
VOCABULARY_FILE = 'vocabulary.json'

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/save-progress':
            self.handle_save_progress()
        elif self.path == '/api/save-vocabulary':
            self.handle_save_vocabulary()
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == '/api/get-progress':
            self.handle_get_progress()
        elif self.path == '/api/get-vocabulary':
            self.handle_get_vocabulary()
        elif self.path.startswith('/api/phonetics/'):
            self.handle_get_phonetics()
        else:
            super().do_GET()

    def handle_save_progress(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_save_vocabulary(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            with open(VOCABULARY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_get_progress(self):
        try:
            if os.path.exists(PROGRESS_FILE):
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'currentIndex': 0, 'correctCount': 0, 'vocabulary': []}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_get_vocabulary(self):
        try:
            if os.path.exists(VOCABULARY_FILE):
                with open(VOCABULARY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_get_phonetics(self):
        """处理音标查询请求"""
        try:
            # 从URL中提取单词
            word = self.path.split('/api/phonetics/')[1]
            if '?' in word:
                word = word.split('?')[0]
            
            # 获取音标
            phonetic = phonetics_api.get_phonetics(word)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'word': word, 'phonetic': phonetic}, ensure_ascii=False).encode())
        except Exception as e:
            self.send_error(500, str(e))

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"服务器运行在 http://localhost:{PORT}")
        print("按 Ctrl+C 停止服务器")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止") 