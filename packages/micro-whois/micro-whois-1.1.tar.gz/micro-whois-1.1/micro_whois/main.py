import socket

from micro_whois.response import WhoisResponse

PORT = 43


def direct_query(host: str, server='whois.iana.org') -> dict[str, str | list[str]]:
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
		key = k.strip().lower()
		value = v.strip()
		if key in ["name server", "nserver"]:
			if key not in result:
				result[key] = [value]
			else:
				result[key].append(value)
		else:
			result[key] = value

	return result


def whois(target: str):
	"""
	Requests whois data on hostname registrar's server
	:param target: Target hostname to get info about
	:return: Result dictionary
	"""
	top_level_response = direct_query(target)
	top_level_registrar = top_level_response["whois"]
	# print(f"Requesting {top_level_registrar}")
	result = direct_query(target, top_level_registrar)
	if "registrar whois server" in result:

		sub_level_registrar = result["registrar whois server"]
		# print(f'Extra request: {sub_level_registrar}')
		result = direct_query(target, sub_level_registrar)

	fields = {
		"date_created": result.get("creation date") or result.get("created"),
		"country": None,
		"state": result.get("registrant state/province"),
		"organization": None,
		"admin_org": result.get("admin organization"),
		"admin_state": result.get("admin state/province"),
		"admin_country": result.get("admin country"),
		"nameservers": result.get("name server") or result.get('nserver')
	}

	if "registrar" in result and result['registrar'] == 'RU-CENTER-RU':
		fields['country'] = "RU"
	else:
		fields['country'] = result["registrant country"]

	if 'org' in result:
		fields["organization"] = result['org']
	else:
		fields["organization"] = result["registrant organization"]

	typed_result = WhoisResponse(**fields)
	return typed_result
