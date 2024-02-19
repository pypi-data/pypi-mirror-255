# Library that is supposed to ease creation of http/https server
# Do not use this in any of your project. Its just a trash for school.

import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer

from .request_interfaces import get_interface, post_interface

class exceptions:
	class DecoratedFunctionCallException(Exception):
		pass
	class NoConditionException(Exception):
		pass
	class ConditionConflictException(Exception):
		pass


class _WebServerHandlerClass(BaseHTTPRequestHandler):
	parent = None # I am not certain should I set this or not. I think I should at least to be explicit about varaibles
	def do_GET(self):
		self.parent.on_request(get_interface(self), "get")
	def do_POST(self):
		self.parent.on_request(post_interface(self), "post")
	def log_message(*args, **kwargs):
		pass

class WebServer:
	get_functions_and_conditions_list = []
	post_functions_and_conditions_list = []
	handler = None
	def __init__(self, ip, port):
		self.handler = _WebServerHandlerClass
		self.handler.parent = self
		self.handler = HTTPServer((ip, port), self.handler)
		self.handler.parent = self
	def convert_to_ssl(self, certfile, keyfile):
		self.handler.socket = ssl.wrap_socket(self.handler.socket, certfile = certfile, keyfile = keyfile, server_side = True)
	def start(self):
		try:
			self.handler.serve_forever()
		except KeyboardInterrupt:
			self.handler.server_close()
	def _deco_condition_builder(self, paths):
		def check_function(WebHandler):
			return WebHandler.path in paths
		return check_function

	def get(self, paths = None, checker_function = None):
		def decorator(function):
			if not paths and not checker_function:
				raise NoConditionException(f"No conditions specified for the {function.__name__} function")
			elif paths and checker_function:
				raise ConditionConflictException(f"Two conditions conflict for the {function.__name__} function")
			def wrapped_function(*args, **kwargs):
				raise exceptions.DecoratedFunctionCallException("Functions decorated by WebServer are not supposed to be called.")
			self.get_functions_and_conditions_list.append((function, self._deco_condition_builder(paths) if paths else checker_function))
			return wrapped_function
		return decorator

	def post(self, paths = None, checker_function = None):
		def decorator(function):
			if not paths and not checker_function:
				raise NoConditionException(f"No conditions specified for the {function.__name__} function")
			elif paths and checker_function:
				raise ConditionConflictException(f"Two conditions conflict for the {function.__name__} function")
			def wrapped_function(*args, **kwargs):
				raise exceptions.DecoratedFunctionCallException("Functions decorated by WebServer are not supposed to be called.")
			self.post_functions_and_conditions_list.append((function, self._deco_condition_builder(paths) if paths else checker_function))
			return wrapped_function
		return decorator

	def on_request(self, interface, request_type):
		satisfied = False
		for function, condition in eval(f"self.{request_type}_functions_and_conditions_list"): #if eval is used it is the matter of time before it gets exploited. Surely it wouldnt be in that case...
			if condition(interface):
				function(interface)
				satisfied = True
		if not satisfied:
			interface.write("No function checher conditions were met")
			interface.header("Content-Type", "text/plain")
			interface.finish(404)
