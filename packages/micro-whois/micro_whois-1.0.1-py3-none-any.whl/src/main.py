import socket

PORT = 43


def direct_query(host: str, server='whois.iana.org'):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((server, PORT))
		req = f"{host}\r\n".encode()
		print(req)
		s.sendall(req)
		data = ""
		chunk = s.recv(1024)
		while chunk:
			data += chunk.decode()
			chunk = s.recv(1024)

	result = {}
	for line in data.split('\n'):
		if not line or line[0] == '%': continue
		fi = line.find(':')
		k, v = line[:fi], line[fi + 1:]
		result[k.strip().lower()] = v.strip()
	return result

def whois(target: str):
	top_who = direct_query(target)
	top_reg = top_who['whois']

	#top_reg="whois.verisign-grs.com"
	print(top_reg)
	r=direct_query(target, top_reg)
	if "registrar whois server" in r:
		sub_reg = r["registrar whois server"]
		r = direct_query(target, sub_reg)
	return r
