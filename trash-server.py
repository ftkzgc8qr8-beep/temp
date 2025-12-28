import logging
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import shutil
import re
import json
import requests
import feedparser
import cgi

# =======================
# Logging Confirmation
# =======================
logger = logging.getLogger('server_logger')
logger.setLevel(logging.INFO)
#---Four Space Marker
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
#---Four Space Marker Check
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
ch.setFormatter(formatter)
logger.addHandler(ch)
#---Four Space Marker

# =======================
# HTTP Request Handler
# =======================
class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):

    # -------------------------
    # POST: File Upload
    # -------------------------
    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
#---Four Space Marker
            if ctype != 'multipart/form-data':
              self.send_response(400)
              self.end_headers()
              self.wfile.write(b'Invalid Content-Type')
              return
#---Four Space Marker
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ=self.headers,
                keep_blank_values=True
            )  
#----------- Twelve Space Marker
            if 'file' not in form:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'No file field found')
                return
#----------- Twelve Space Marker
            file_item = form['file']
            if not file_item.filename:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Empty filename')
                return
#----------- Twelve Space Marker
            filename = self.sanitize_filename(file_item.filename)
#----------- Twelve Space Marker            
            # Stage upload
            self.ensure_directory('uploads') # {^_^}LOOKFLAG=> USING upload(s)
            upload_path = os.path.join('uploads', filename)
#----------- Twelve Space Marker            
            with open(upload_path, 'wb') as f:
                f.write(file_item.file.read())
#----------- Twelve Space Marker
            # Route file based on prefix rules
            self.move_file(upload_path)
            
            logger.info(f'File uploaded and routed: {filename}')
#----------- Twelve Space Marker            
            # Success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
#----------- Twelve Space Marker -- HTML Section below --
            success_message = f"""
            <html>
            <head>
                <title>Upload Successful</title>
                <script>
                    function redirectToUpload() {{
                        window.location.href = '/upload';
                    }}
                </script>
            </head>
            <body style="text-align:center; background-color: black; color: green;">
                <h2>File Uploaded Successfully!</h2>
                <p>File: {filename}</p>
                <img src="/success.png" width="300"><br><br>
                <button onclick="redirectToUpload()"
                    style="font-size:18px; padding:10px; background-color:#34ac44;
                    color:white; border:none; border-radius:5px; cursor:pointer;">
                    ⬅ Upload Another File
                </button>
            </body>
            </html>
            """
