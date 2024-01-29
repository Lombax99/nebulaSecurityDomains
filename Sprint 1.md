### Goal
In this sprint i'll try to generate manually an example of config files and Certificates for a simple case.
### Example
I want 5 machine, 3 laptops able to connect with each other, 1 server able to receive request from one of the laptops, and the lighthouse.
### Requisiti
Design and implement a proof of concept for "security domains" in a Nebula network. A security domain is a set of logically related resources that can communicate and subject to the following constraints:
· ==A resource can have multiple security domains==
· The ==information== related to the security domain must be present ==in the resource's digital certificate==
· A resource can open a connection only toward another resource that ==share at least one security domain== otherwise it is blocked by default
### Analisi del problema
##### Division in security domains?
I'll most likely use the group feature of nebula. Is it enough?
##### Security issues?
Is there a way to inject modification or other forms of attacks?
##### What rules do we implements to block host from connecting to other host not in the same security domain?
1) block connection from leaving the node you are currently in:
	- Possible security fault? Can be modified? Can be impersonated? Can be added in a second moment?
2) block connection from outside hosts not part of the same group:
	- How do i know if an outside request is from a host with a group in common with me? I think it's possible, to be verified.
Check [[Nebula security domains#What about scalability?|scalability issues]].
### Progettazione
In this case we need 2 security domains, one for the laptops and one for connecting to the server. One of the laptops will be part of both the security domains:
- LaptopSD:
	- laptop1
	- laptop2
	- laptop3
- ServerSD:
	- laptop1
	- server






