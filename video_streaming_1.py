# Web streaming example updated now again and again 2 final 2 very final
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from gpiozero import LEDBoard

PAGE="""\
<html>
<head>
<link rel="apple-touch-icon" sizes="57x57" href="http://192.168.4.1:8000/apple-icon-57x57.png">
<link rel="apple-touch-icon" sizes="60x60" href="http://192.168.4.1:8000/apple-icon-60x60.png">
<link rel="apple-touch-icon" sizes="72x72" href="http://192.168.4.1:8000/apple-icon-72x72.png">
<link rel="apple-touch-icon" sizes="76x76" href="http://192.168.4.1:8000/apple-icon-76x76.png">
<link rel="apple-touch-icon" sizes="114x114" href="http://192.168.4.1:8000/apple-icon-114x114.png">
<link rel="apple-touch-icon" sizes="120x120" href="http://192.168.4.1:8000/apple-icon-120x120.png">
<link rel="apple-touch-icon" sizes="144x144" href="http://192.168.4.1:8000/apple-icon-144x144.png">
<link rel="apple-touch-icon" sizes="152x152" href="http://192.168.4.1:8000/apple-icon-152x152.png">
<link rel="apple-touch-icon" sizes="180x180" href="http://192.168.4.1:8000/apple-icon-180x180.png">
<link rel="icon" type="image/png" sizes="192x192"  href="http://192.168.4.1:8000/android-icon-192x192.png">
<link rel="icon" type="image/png" sizes="32x32" href="http://192.168.4.1:8000/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="96x96" href="http://192.168.4.1:8000/favicon-96x96.png">
<link rel="icon" type="image/png" sizes="16x16" href="http://192.168.4.1:8000/favicon-16x16.png">
<link rel="manifest" href="http://192.168.4.1:8000/manifest.json">
<meta name="msapplication-TileColor" content="#ffffff">
<meta name="msapplication-TileImage" content="http://192.168.4.1:8000/ms-icon-144x144.png">
<meta name="theme-color" content="#ffffff">
<style>
img {
display: block;
margin-left: -450px;
margin-right: auto;
width: auto;
height: 75%;
overflow: hidden;
transform: rotate(90deg); /* W3C */
-webkit-transform: rotate(90deg); /* Safari & Chrome */
-moz-transform: rotate(90deg); /* Firefox */
-ms-transform: rotate(90deg); /* Internet Explorer */
-o-transform: rotate(90deg); /* Opera */
}
</style>
<title>CaringEye Safety Camera</title>
</head>
<body>

<center><img src="stream.mjpg"></center>
</body>
</html>
"""


# Activating LEDs at start of the camera. There is no On/Off, LEDs work the whole time
# led indicates the pin on GPIO that will power LEDs
# test
leds = LEDBoard(16, 20, 21)
leds.on()

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()

            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
       
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='1280x720', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    camera.rotation = 180
    camera.start_recording(output, format='mjpeg')
 
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()

    finally:
        camera.stop_recording()
