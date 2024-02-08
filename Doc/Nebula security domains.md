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
Ogni nodo nel network deve avere:
- una coppia chiave certificato personale
- il certificato della CA (ma non la chiave)
- il file di config
- l'eseguibile di nebula (o nebula installato)
Needs to deploy on linux, Freebsd, windows, macOS, iOS, android.
##### Division in security domains?
I'll most likely use the group feature of nebula. Is it enough?
With the group feature i can define a group for each security domain and set the host to allow connections from thw same group(s). That's exactly what i need.
##### How to auto generate?
A simple script is enough? All need to be from a single setting file.
- Might as well use this file to generate all the info of the network and not just the security domains...
##### Security issues?
Is there a way to inject modification or other forms of attacks?
- Posso dare per scontato che il canale di trasferimento dei file sia sicuro?
- Posso sicuramente modificiare il file in un nodo manualmente...
- [x] domani provo a chiede al prof
##### Can the lighthouse be part of a security domain?
Most likely not, the lighthouse should not have restrictions on who can communicate with him.
But if i have multiple lighthouse i might...
The answer is still no but i can't block a user from putting a lighthouse in the config, maybe i should at least print some warning
##### What rules do we implements to block host from connecting to other host not in the same security domain?
1) block connection from leaving the node you are currently in:
	- Possible security fault? Can be modified? Can be impersonated? Can be added in a second moment?
	- In questo caso posso solo bloccare tutto quello che esce ad esclusione di bersagli appartenenti ad un gruppo, questo vuol dire che o fai parte di un qualche gruppo o nessuno ti parlerà mai.
1) block connection from outside hosts not part of the same group:
	- How do i know if an outside request is from a host with a group in common with me? Nebula takes care of that.
Check [[Nebula security domains#What about scalability?|scalability issues]].
##### How easy it is to modify the network layout, rules and security domains?
it will be enough if it's not more complicated than the normal nebula host configuration method.
How many hosts do i need to update for a single change? Changing an host requires change in the lighthouse as well? NO
See: https://www.defined.net/
Maybe regenerate only the files that would actually be changed?
It's cool but a bit too complicated while working with a simple config file. If i had a full application to menage all the networks it's would be a must.
##### What about scalability?
If two machines need to be able to connect to a third one but should not be able to connect to each other? 
	- I can use the difference in rules that allow connections in an out.
**PROBLEM CASE: Mistrustful Colleagues**
##### Nebula firewall rules priority?
If i set two rules, one allows any connection from a group and another block request from a specific host. If the host is part of the group i'd assume that the request are still blocked because a more specific rule has priority over a more general, is this the case?
And what if a laptop is in two groups with conflicting rules, which ore takes priority?
##### What if i have more than one lighthouse?
The config file must be defined as normally, it should not conflict with the project.
If i want lighthouse to have some restrictions? NO
##### Difference between group and groups
In nebula both "group" and "groups" can be defined, the difference is that "groups" are in AND logic and the rules apply only to hosts that have all the groups listed
##### Default deny 
Nebula uses a logic of default deny and add allow rules, there is no way of defining specific deny rules.
##### Formato del file di config
Un bel JSON non sarebbe male ma è la versione migliore? Molto probabilmente si
##### Problems with lighthouse as relay
*nebula traffic is peer-to-peer encrypted, and relays don't interfere with that. So, no relay can sniff plaintext packets.*

*Nebula's designed to drop untrusted traffic as quickly / efficiently as possible, so running a lighthouse as a relay doesn't add any extra DoS security risk there*

*in small networks, lighthouse as relay is what I would do  
in large networks, I would deploy dedicated relays close (in terms of network hops/capacity) to the peers the relay is serving, and I would not use the lighthouse as a relay*
##### Interesting possible flaw in security
*Nebula's initial handshake includes the certificate of the peer initiating the connection, and that initial handshake packet is unencrypted. To encrypt the initial handshake packet would require more round trips per handshake, or a pre-shared key, neither of which Nebula supports today.*
##### Formato del file di config?
1) scrivo una lista di security domains, in ogni domain definisco la lista di host che vi appartengono
2) scrivo una lista di host, in ogni host definisco la lista di security domain a cui appartiene
*As an aside, and I'm not sure how you're generating the config files, but YML is pretty programmatic, and JSON is a subset of YML. So you can also programmatically build up a JSON array and just use that for your config.toml. (Or use a library to write it as YML for readability.) Might be less error-prone than string templating if that's your current approach.*
Generare in automatico il file di config rimuoverebbe il problema (almeno in parte) di un file scritto male, questo implicherebbe avere un'applicazione per gestire la rete con gui e tutto quanto.
##### Does a host need the lighthouse?
*Lighthouses allow Nebula nodes to discover the routable IP addresses of other nodes (i.e. to locate each other.) If the Nebula nodes can't connect to a shared Lighthouse, the only other way they might know where to look is if you define a [static_host_map](https://nebula.defined.net/docs/config/static-host-map/) entry for each other.* 
Even if in very particular cases that could be remotely possible it's not a good practice and i don't think it should be implemented, it's better to add a local lighthouse if necessary. 



### Note
In the final doc add link to documentation and slack, they have been very useful and nice.