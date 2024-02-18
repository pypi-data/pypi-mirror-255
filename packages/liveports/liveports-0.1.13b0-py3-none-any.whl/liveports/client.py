import socket
import signal
import time
import brotli
import tempfile
import zlib
from urllib.parse import urlparse
import urllib.request as requester
from collections import deque
import os
import gzip
import sys
import ssl
import json
import threading
import http.server
import http.client
import urllib
import socketserver
import fcntl
from .blaster_utils import run_shell, CommandLineNamedArgs, CommandLineArgs, \
	DummyObject, nsplit

__version__ = "0.1.13b"

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

socketserver.ThreadingTCPServer.allow_reuse_address = True

# Process command line arguments
try:
	SOURCE = CommandLineNamedArgs.get("source", "")  # given domain

	# If request logging enabled, we will use a proxy server to log request/response
	LOCAL_PROXY_PORT = int(CommandLineNamedArgs.get("proxyPort", 4060))
	LOG_VIEWER_PORT = int(CommandLineNamedArgs.get("logViewerPort") or (LOCAL_PROXY_PORT + 1))
	DEBUG_LOG_LEVEL = int(CommandLineNamedArgs.get("logLevel") or 0)
	# target
	TARGET_HOST = "localhost"
	if(target_host := CommandLineNamedArgs.get("target")):
		TARGET_PROTOCOL = urlparse(target_host).scheme or "http"
		TARGET_PORT = urlparse(target_host).port or (80 if TARGET_PROTOCOL == "http" else 443)
		TARGET_HOST = urlparse(target_host).hostname or "localhost"
	else:
		TARGET_PORT = int(CommandLineNamedArgs.get("targetPort") or CommandLineArgs[-1])
		TARGET_PROTOCOL = (
			CommandLineNamedArgs.get("targetProtocol")
			or (CommandLineArgs[1] if len(CommandLineArgs) > 1 else "http")
		).lower()

	NO_PROXY = bool(CommandLineNamedArgs.get("noproxy", False)) and TARGET_HOST == "localhost"  # only when target host is localhost
except Exception:
	print('''
Invalid Arguments. Usage Examples:
- liveports http 3000
- liveports https 8000
- liveports https 8000 --source="https://yourdomain.com"
- liveports https 8000 --source="https://yourdomain.com" --noproxy  # for no mediating logging
- liveports --target="https://localhost:3000" --source="https://yourdomain.com"
- liveports --target="https://example.com" --source="https://yourdomain.com"
''')
	sys.exit(1)

if(TARGET_PROTOCOL not in ["http", "https"]):
	print("Invalid protocol: must be one of http/https", TARGET_PROTOCOL)
	sys.exit(1)


class Client:
	is_running = True
	is_stopped = False
	proxy_server = None
	log_viewer_server = None
	ssh_proc = DummyObject()

	@staticmethod
	def _stop(sig, frame):
		Client.is_running = False
		Client.is_stopped = True
		if(proc := getattr(Client.ssh_proc, "proc", None)):
			os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
			Client.ssh_proc.proc = None
			print("\nClosing.. please wait..")

	@classmethod
	def start_proxy_server(cls):
		cls.proxy_server = proxy_server = socketserver.ThreadingTCPServer(("", LOCAL_PROXY_PORT), ProxyHandler)
		proxy_server.timeout = 5
		while(Client.is_running):
			proxy_server.handle_request()
		cls.proxy_server.server_close()
		cls.proxy_server = None

	@classmethod
	def start_log_viewer(cls):
		cls.log_viewer_server = log_viewer_server = socketserver.ThreadingTCPServer(("", LOG_VIEWER_PORT), LogViewer)
		log_viewer_server.timeout = 5
		while(Client.is_running):
			log_viewer_server.handle_request()
		cls.log_viewer_server.server_close()
		cls.log_viewer_server = None

	@staticmethod
	def ssh_reverse_proxy(server_hostname, server_port, password):
		echo_password_file = os.path.join(tempfile.gettempdir(), "liveports_echo_pass")
		open(echo_password_file, "w").write(f"#!/bin/bash\necho \"{password}\"\n")
		run_shell(f"chmod +x {echo_password_file}", shell=True)
		proxy_port = TARGET_PORT if NO_PROXY else LOCAL_PROXY_PORT
		run_shell(
			f"ssh -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -NR {server_port}:localhost:{proxy_port} proxyuser@{server_hostname}",
			shell=True,
			env={"SSH_ASKPASS": echo_password_file, "DISPLAY": "xxx"},
			state=Client.ssh_proc,
			preexec_fn=os.setsid,
			fail=False
		)
		Client.is_running = False


# handle sigint
signal.signal(signal.SIGINT, Client._stop)


# LOG VIEWER
class LogViewer(http.server.SimpleHTTPRequestHandler):
	logs = deque()

	def log_message(self, format, *args):
		pass

	def do_GET(self):
		url = urllib.parse.urlparse(self.path)
		req_path = url.path
		resp = b''
		self.send_response(200)
		params = (url.query and urllib.parse.parse_qs(url.query))
		if(params and (since := params.get("since", [0])[0])):
			since = int(since)
			self.send_header("Content-Type", "application/json")
			ret = []
			for i in range(len(LogViewer.logs) - 1, -1, -1):
				if(LogViewer.logs[i]["timestamp"] <= since or len(ret) >= 100):
					break
				ret.append(LogViewer.logs[i])
			ret.reverse()
			resp = json.dumps(ret).encode()
		else:
			resp = open(
				os.path.join(os.path.dirname(__file__), "logviewer.html"),
				"rb"
			).read()
			self.send_header("Content-Type", "text/html")

		# 1. SEND ERROR RESONSE
		self.send_header("Content-Length", str(len(resp)))
		self.end_headers()
		# 5. SEND BODY
		self.wfile.write(resp)

	@staticmethod
	def find_in_memory_view(data: memoryview, pattern):
		pattern_len = len(pattern)
		for i in range(len(data) - pattern_len + 1):
			if(data[i:i + pattern_len] == pattern):
				return i
		return -1

	@classmethod
	def process_http_data(cls, data: bytearray):
		data = memoryview(data)
		ret = []
		while(data):
			headers_end = LogViewer.find_in_memory_view(data, b"\r\n\r\n")
			if(headers_end == -1):
				DEBUG_LOG_LEVEL > 1 and print("could not find end of headers")
				return ret
			headers, data = data[:headers_end], data[headers_end + 4:]

			status_line, *headers = headers.tobytes().decode("utf-8").split("\r\n")
			headers_map = {}
			for header in headers:
				k, v = nsplit(header, ":", 1)
				headers_map[k.lower().strip()] = v.lower().strip()
			body = bytearray()
			if(headers_map.get("transfer-encoding", "") == "chunked"):
				data_len = len(data)
				offset = 0
				while offset < data_len:
					# Find the end of the chunk size line
					chunk_size_end_offset = LogViewer.find_in_memory_view(data[offset:], b"\r\n")
					if(chunk_size_end_offset == -1):
						DEBUG_LOG_LEVEL > 1 and print("could not find end of chunk size")
						return ret
					chunk_size_end = offset + chunk_size_end_offset
					chunk_size_line = data[offset:chunk_size_end].tobytes().decode('utf-8')
					chunk_size = int(chunk_size_line, 16)

					# Calculate the start and end positions of the chunk data
					chunk_data_start = chunk_size_end + 2
					chunk_data_end = chunk_data_start + chunk_size
					body.extend(data[chunk_data_start:chunk_data_end])
					# Move the offset to the start of the next chunk
					offset = chunk_data_end + 2
					if(chunk_size == 0):
						break
				data = data[offset:]  # next http transaction
			else:
				content_length = int(headers_map.get("content-length", "0")) or len(data)
				body.extend(data[:content_length])
				data = data[content_length:]  # next http transaction

			# store it for log viewer
			body_str = ""
			content_type = headers_map.get("content-type", "").split(";")[0]
			content_encoding = headers_map.get("content-encoding", "")
			if(
				content_type.endswith("json")
				or content_type.endswith("www-form-urlencoded")
				or content_type.endswith("xml")
				or content_type.endswith("html")
			):
				try:
					if(content_encoding == "gzip"):
						body = gzip.decompress(body)
					elif(content_encoding == "deflate"):
						body = zlib.decompress(body)
					elif(content_encoding == "br"):
						body = brotli.decompress(body)
					elif(content_encoding):
						body = f"Unknown content encoding: {content_encoding}".encode('utf-8')

					body_str = body.decode("utf-8")
				except Exception as ex:
					body_str = f"Could not decode body: {ex}"

			elif(body):
				body_str = f"{content_type}: {len(body)} bytes"

			ret.append({"status_line": status_line, "headers": headers_map, "body": body_str})
		return ret

	@classmethod
	def process_wire_log(cls, req_data: bytearray, resp_data: bytearray):
		# very basic log processing
		now = int(time.time())
		for req, resp in zip(cls.process_http_data(req_data), cls.process_http_data(resp_data)):
			cls.logs.append({"request": req, "response": resp, "timestamp": now})
			# LOGGING TO CONSOLE
			method, path, *args = nsplit(req["status_line"], " ", 2)
			_, resp_status = nsplit(resp["status_line"], " ", 1)
			print(f"{method} {path} - {resp_status}")

		while(cls.logs and cls.logs[0]["timestamp"] < now - 5 * 60):  # keep logs for 5 minutes
			cls.logs.popleft()


# PROXY SERVER
class ProxyHandler(socketserver.BaseRequestHandler):
	is_running = True

	def handle(self):
		# Connect to the destination server
		self.request.settimeout(5)
		req_data = bytearray()
		resp_data = bytearray()
		target_sock = None
		try:
			target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# Wrap the destination socket with SSL
			if(TARGET_PROTOCOL == "https"):
				target_sock = ssl_context.wrap_socket(target_sock)

			target_sock.settimeout(5)
			target_sock.connect((TARGET_HOST, TARGET_PORT))

			thread = threading.Thread(target=self.forward_data, args=(self.request, target_sock, req_data))
			thread.start()

			self.forward_data(target_sock, self.request, resp_data)
			# Wait for the threads to complete
			thread.join()
		except Exception as ex:
			DEBUG_LOG_LEVEL > 1 and print("exception processing req: ", str(ex))
		finally:
			# Close the connections
			self.request.close()
			target_sock and target_sock.close()

		LogViewer.process_wire_log(req_data, resp_data)

	def forward_data(self, source, target, buf):
		while self.is_running and Client.is_running:
			try:
				data = source.recv(4096)
			except TimeoutError:
				continue
			if not data:
				self.is_running = False
				break
			buf.extend(data)
			target.sendall(data)
		target.shutdown(socket.SHUT_WR)


SERVER_CACHED_RESP_FILE = os.path.join(os.path.dirname(__file__), "liveports.json")
LOCK_FILE = os.path.join(tempfile.gettempdir(), f"liveports_{SOURCE}.lock")


def get_config():
	if(
		os.path.isfile(SERVER_CACHED_RESP_FILE)
		and (contents := open(SERVER_CACHED_RESP_FILE).read().strip())
	):
		try:
			return json.loads(contents)
		except Exception as ex:
			DEBUG_LOG_LEVEL > 2 and print("could not load config file", str(ex))
	return {}


def save_config(config):
	cache = get_config()
	prev_source_config = cache.get(SOURCE) or {}
	prev_source_config.update(config)
	cache[SOURCE] = prev_source_config
	open(SERVER_CACHED_RESP_FILE, "w").write(json.dumps(cache))


def main():
	print(f"v{__version__}")
	while(not Client.is_stopped):

		lock = open(LOCK_FILE, "w")
		try:
			fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

			prev_resp = get_config().get(SOURCE) or {}
			server_hostname = prev_resp.get("server_hostname")
			if(not server_hostname or CommandLineNamedArgs.get("force")):
				server_hostname = "ports.live"
			server_hostnames_tried = set()
			while(server_hostname not in server_hostnames_tried):
				try:
					resp = json.loads(
						requester.urlopen(
							requester.Request(
								url="https://" + server_hostname + "/api/register",
								data=json.dumps({
									"protocol": TARGET_PROTOCOL if NO_PROXY else "http",
									"target": TARGET_HOST + (f":{TARGET_PORT}" if TARGET_PORT not in (80, 443) else ""),
									"source": SOURCE,
									"api_key": CommandLineNamedArgs.get("api_key", prev_resp.get("api_key"))
								}).encode("utf-8"),
							)
						).read().decode("utf-8")
					)
				except Exception as ex:
					print(
						f"Sorry there was an error connecting to the server. {str(ex)}\n\n Please try again in a moment or add \"--force\" to force new hostname"
					)
					sys.exit(1)

				if(redirect_to := resp.get("redirect")):
					server_hostname = redirect_to
					server_hostnames_tried.add(server_hostname)
				else:
					break

			# update the previously cached data and cache it
			save_config(resp)

			if(hints := resp.get("hints")):
				for k, v in hints.items():
					print(v)

				if(hints.get("wait_retry")):
					print("Reconnecting...")
					time.sleep(5)
					continue

			if(resp.get("errors")):
				for k, v in resp["errors"].items():
					print(v)
				sys.exit(1)

			Client.is_running = True
			server_threads = []
			if(not NO_PROXY):
				# START LOGVIEWER SERVER
				log_viewer_server = threading.Thread(target=Client.start_log_viewer)
				log_viewer_server.start()
				server_threads.append(log_viewer_server)
				print(f'Log viewer: http://localhost:{LOG_VIEWER_PORT}')

				# START PROXYSERVER
				proxy_server = threading.Thread(target=Client.start_proxy_server)
				proxy_server.start()
				server_threads.append(proxy_server)

			print(f'Your public hostname is: https://{resp["public_hostname"]}')
			print("-------")
			# START SSH REVERSE PROXY
			Client.ssh_reverse_proxy(resp["server_hostname"], resp["server_port"], resp["password"])

			for _thread in server_threads:
				_thread.join()

		except IOError:
			print("Sorry! process may be running already")
			sys.exit(1)
		except Exception as ex:
			print("Sorry!", str(ex))
			sys.exit(1)
		finally:
			fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


if __name__ == '__main__':
	main()
