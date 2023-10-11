#!/usr/bin/python3


# TO-DO
# whenever the given input file is modified and saved, it should trigger an event
# Plus, when user reloads the page after modification, it does not reaechout to watchdog event
# event set is not good, as it allows only one set


import argparse
import yaml
import json
import http.server
import socketserver
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

yamlfile = None
json_data = None
httpd = None
file_monitoring_event = threading.Event()
http_server_event = threading.Event()

def yaml_json():
    global json_data

    if not os.path.exists(yamlfile) or yamlfile is None:
        print("[ERROR] File does not exist ...")
        exit(404)

    try:
        with open(yamlfile, 'r') as file:
            yaml_data = yaml.safe_load(file)
            json_data = json.dumps(yaml_data, indent=4)

    except Exception as e:
        print("[ERROR] Exception occurred, please take a look ...")
        print(e)

class YamlFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.event = threading.Event()

    def on_modified(self, event):
        if event.src_path == yamlfile:
            yaml_json()
            if not self.event.is_set():  # Check if the event hasn't been set (file modified) before
                print("[INFO] Reload the page to reflect the changes ...")
                self.event.set()  # Set the event to indicate that the message has been printed
            

def start_file_monitoring():
    observer = Observer()
    observer.schedule(YamlFileHandler(), path=os.path.dirname(yamlfile), recursive=False)
    observer.start()
    try:
        while not file_monitoring_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        yaml_json()
        self.wfile.write(json_data.encode())

def start_http_server(port):
    global httpd
    with socketserver.TCPServer(("", port), MyHandler) as httpd:
        http_server_event.set()
        print(f"[SERVER] Serving at http://localhost:{port}")
        httpd.serve_forever()

def main():
    global yamlfile
    parser = argparse.ArgumentParser(description="Threat Modeling as Code")
    parser.add_argument("file", help="yaml/yml file")
    parser.add_argument("-p", "--port", help="Specify the custom port to run. Default port is 9000", default=9000, type=int)
    args = parser.parse_args()

    yamlfile = args.file
    yaml_json()

    http_server_thread = threading.Thread(target=start_http_server, args=(args.port,))
    file_monitoring_thread = threading.Thread(target=start_file_monitoring)

    http_server_thread.start()
    file_monitoring_thread.start()

    try:
        while not http_server_event.is_set():
            time.sleep(1)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Exiting] Cleaning up and exiting ...")
        file_monitoring_event.set()
        if httpd:
            httpd.shutdown()
            httpd.server_close()
        http_server_thread.join()
        file_monitoring_thread.join()

if __name__ == "__main__":
    main()
