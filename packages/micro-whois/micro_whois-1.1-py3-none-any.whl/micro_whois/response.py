from typing import NamedTuple

WhoisResponse = NamedTuple("WhoisResponse",
                           [
	                           ("date_created", str),
	                           ("country", str),
	                           ("state", str),
	                           ("organization", str),
	                           ("admin_org", str),
	                           ("admin_state", str),
	                           ("admin_country", str),
	                           ("nameservers", list[str]),
                           ])
