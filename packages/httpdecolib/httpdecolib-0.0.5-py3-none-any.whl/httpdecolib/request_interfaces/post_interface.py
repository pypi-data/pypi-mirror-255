from .default_interface import default_request_interface
import json

class post_interface(default_request_interface):
	def _parse_data(self):
		self.data = self.handler.rfile.read(int(self.headers["Content-Length"]))
	def jsonize(self):
		splitdata = self.data.split(b"\n", 1)
		if len(splitdata) == 1:
			self.json = json.loads(splitdata[0])
			self.data = None
		else:
			self.json = json.loads(splitdata[0])
			self.data = splitdata[1]
