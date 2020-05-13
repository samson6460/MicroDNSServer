# MicroDNSServer
It's a micro DNS server library for MicroPython.It adopts the programming style of DNSServer library in ESP Arduino Core.

## Installation
Just upload DNSServer.py to your ESP board and you're done.

## Usage
To use DNSServer.py library, you should:

1. From DNSServer library import `DNSServer` class.

2. Call a `DNSServer` class.

3. By calling `start()` to start the server and assign the ip address to correspoding domain name.

4. Call `processNextRequest()` repeatly to process requests.

## Method reference

### start(dns_port, domain_name, resolvedIP)
- Start the server at specified port.
- Assign the ip address to correspoding domain name by setting `domain_name`、`resolvedIP` para.
- `domain_name`、`resolvedIP` para can be string if you only need one paired, otherwise they should be string list.
- If you need to redirect all domain name to one ip address, set `domain_name` as `'*'`.

### processNextRequest()
- Check for new request and pass the corresponding ip address to client.

### stop()
- Stop the DNS server.

## Attribute reference

### ttl
- You can set the ttl by change this attribute.

### errorReplyCode
- You can set the Rcode by change this attribute.
- From DNSServer library import `DNSReplyCode` class and you get can all Rcode.


