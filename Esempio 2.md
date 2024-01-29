In this second example we will have 3 laptops, 2 servers and 1 lighthouse. We want all the laptops to be able to connect to one of the servers, the servers should be able to connect to each other but the laptops should not.

### Analisi del problema
##### What rules do we implements to block host from connecting to other host not in the same security domain?
1) block connection from leaving the node you are currently in:
	- Possible security fault? Can be modified? Can be impersonated? Can be added in a second moment?
2) block connection from outside hosts not part of the same group:
	- How do i know if an outside request is from a host with a group in common with me? I think it's possible, to be verified.
Check [[Nebula security domains#What about scalability?|scalability issues]].
##### What about scalability?
If two machines need to be able to connect to a third one but should not be able to connect to each other? 
	- I can use the difference in rules that allow connections in an out.


