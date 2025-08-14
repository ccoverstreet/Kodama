#!/usr/bin/env python
# Kodama Python Backend
# The credit goes to Rui Santos * Sara Santos of Random Nerd Tutorials
# for most of the code framework. This project consists mostly of gluing these 
# separate pieces together.

# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-mjpeg-streaming-web-server-picamera2/

# Mostly copied from https://picamera.readthedocs.io/en/release-1.13/recipes2.html
# Run this script, then point a web browser at http:<this-ip-address>:7123
# Note: needs simplejpeg to be installed (pip3 install simplejpeg).

# IO + networking

import io
import logging
import socketserver
from http import server
from threading import Condition, Lock
from websockets.asyncio.server import Server

# Camera

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# TODO: ove this into it's own file in the future0
PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

STREAM_VIEWER_COUNT = 0
STREAM_VIEWER_LOCK = Lock()


def clamp(val, lower, upper):
    return min(max(val, lower))

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        global STREAM_VIEWER_LOCK
        global STREAM_VIEWER_COUNT
        global OUTPUT

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
            STREAM_VIEWER_LOCK.acquire()
            if STREAM_VIEWER_COUNT == 0:
                try: 
                    logging.warning("First viewer, starting PiCamera 2 recording")
                    picam2.start_recording(JpegEncoder(), FileOutput(OUTPUT))
                except:
                    STREAM_VIEWER_LOCK.release()

            STREAM_VIEWER_COUNT += 1
            logging.warning(f"Adding viewer, currently {STREAM_VIEWER_COUNT} viewers")

            STREAM_VIEWER_LOCK.release()


            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with OUTPUT.condition:
                        OUTPUT.condition.wait()
                        frame = OUTPUT.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                STREAM_VIEWER_LOCK.acquire()
                STREAM_VIEWER_COUNT -= 1
                logging.warning(f"Removing viewer. Currently {STREAM_VIEWER_COUNT} viewers")

                if STREAM_VIEWER_COUNT == 0:
                    logging.warning("No viewers currently. Stopping PiCamera2 recording")
                    picam2.stop_recording()

                STREAM_VIEWER_LOCK.release()

                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))

        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1080, 480)}))
OUTPUT = StreamingOutput()
#picam2.start_recording(JpegEncoder(), FileOutput(OUTPUT))

try:
    address = ('', 30303)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
