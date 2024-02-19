from .default_interface import default_request_interface

class get_interface(default_request_interface):
	def _parse_data(self):
		self.json = {}
		if self.handler.path.count("?") > 0:
			end_of_path = self.handler.path.split("?")[-1]
			key_value_pairs = end_of_path.split("&")
			for key_value_pair in key_value_pairs:
				key, value = key_value_pair.split("=")
				self.json[key] = value
