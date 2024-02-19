import socket

PORT = 43


def direct_query(host: str, server='whois.iana.org') -> dict[str, str]:
	"""
	Queries data directly on specified server
	:param host: Target hostname to get info about
	:param server: Whois server
	:return: Result dictionary
	"""
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((server, PORT))
		req = f"{host}\r\n".encode()
		s.sendall(req)
		data = ""
		chunk = s.recv(1024)
		while chunk:
			data += chunk.decode()
			chunk = s.recv(1024)

	result = {}
	for line in data.split('\n'):
		if not line or line[0] == '%':
			continue
		fi = line.find(':')
		k, v = line[:fi], line[fi + 1:]
		result[k.strip().lower()] = v.strip()
	return result


def whois(target: str) -> dict[str, str]:
	"""
	Requests whois data on hostname registrar's server
	:param target: Target hostname to get info about
	:return: Result dictionary
	"""
	top_level_response = direct_query(target)
	top_level_registrar = top_level_response['whois']

	result = direct_query(target, top_level_registrar)
	if "registrar whois server" in result:
		sub_level_registrar = result["registrar whois server"]
		result = direct_query(target, sub_level_registrar)
	return result
