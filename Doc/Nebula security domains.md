### Requisiti
Design and implement a proof of concept for "security domains" in a Nebula network. A security domain is a set of logically related resources that can communicate and subject to the following constraints:
· A resource can have multiple security domains
· The information related to the security domain must be present in the resource's digital certificate
· A resource can open a connection only toward another resource that share at least one security domain otherwise it is blocked by default

Specifications
· There must be a single configuration file where for each resource of the network are specified its security domains
· From this configuration files it must be possible to generate all the nebula certificates and nebula configuration files to implement the constraints of the security domain for the whole network
· Using the generated files, manually instantiate the network and verify the relevant connections

Resources
- [https://github.com/slackhq/nebula](https://github.com/slackhq/nebula)
- [https://medium.com/several-people-are-coding/introducing-nebula-the-open-source-global-overlay-network-from-slack-884110a5579](https://medium.com/several-people-are-coding/introducing-nebula-the-open-source-global-overlay-network-from-slack-884110a5579)
- [https://nebula.defined.net/docs/](https://nebula.defined.net/docs/)
- https://nebula.defined.net/docs/guides/quick-start/
- https://nebula.defined.net/docs/config/

### Analisi dei requisiti
##### security domains
A security domain is a set of logically related resources that can communicate and subject to the following constraints:
- A resource can have multiple security domains
- The information related to the security domain must be present in the resource's digital certificate
- A resource can open a connection only toward another resource that share at least one security domain otherwise it is blocked by default
##### resources
Any machine of the virtual network including both Host and Lighthouse, those includes servers, laptops, mobile phones and anything that can run the nebula software.
##### communicate
Being able to exchange message as if being part of the same sub-net
##### digital certificate
It's a the host certificate. From the official doc: "A host certificate contains the name, IP address, group membership, and a number of other details about a host. Individual hosts cannot modify their own certificate, because doing so will invalidate it. This allows us to trust that a host cannot impersonate another host within a Nebula network. Each host will have its own private key, which is used to validate the identity of that host when Nebula tunnels are created."

### Analisi del problema
##### Deployment of the files?
(not really part of the project)
##### Division in security domains?
I'll most likely use the group feature of nebula. Is it enough?
##### How to auto generate?
A simple script is enough? All need to be from a single setting file.
- Might as well use this file to generate all the info of the network and not just the security domains...
##### Security issues?
Is there a way to inject modification or other forms of attacks?
##### Can the lighthouse be part of a security domain?
Most likely not, the lighthouse should not have restrictions on who can communicate with him.
##### What rules do we implements to block host from connecting to other host not in the same security domain?
1) block connection from leaving the node you are currently in:
	- Possible security fault? Can be modified? Can be impersonated? Can be added in a second moment?
2) block connection from outside hosts not part of the same group:
	- How do i know if an outside request is from a host with a group in common with me? I think it's possible, to be verified.
Check [[Nebula security domains#What about scalability?|scalability issues]].
##### How easy it is to modify the network layout, rules and security domains?
it will be enough if it's not more complicated than the normal nebula host configuration method.
How mani hosts do i need to update for a single change? Changing an host requires change in the lighthouse as well?
##### What about scalability?
If two machines need to be able to connect to a third one but should not be able to connect to each other? 
	- I can use the difference in rules that allow connections in an out.
##### Nebula firewall rules priority?
If i set two rules, one allows any connection from a group and another block request from a specific host. If the host is part of the group i'd assume that the request are still blocked because a more specific rule has priority over a more general, is this the case?
And what if a laptop is in two groups with conflicting rules, which ore takes priority?

### Progettazione
##### Security domain
We implements a security domain as a specific kind of nebula group with defined rules that block any connections from host not part of the same group.
