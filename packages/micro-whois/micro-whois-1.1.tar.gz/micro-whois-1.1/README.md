# micro-whois
Cross-platform whois client without dependencies in pure Python
## Features
- Automatic whois server detection
- No platform dependencies (such as unix whois binary)
- No external libraries used
## Installation
`pip install micro-whois`
## Usage
```python
from micro_whois import whois

result = whois("google.com")
for field, value in result.items():
	print(f"{field}: {value}")
```