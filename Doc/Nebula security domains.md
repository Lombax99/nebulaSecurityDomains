### Requirements
Design and implement a proof of concept for "**security domains**" in a Nebula network. A **security domain** is a set of logically related **resources** that can **communicate** and subject to the following constraints:
- A resource can have multiple **security domains**
- The information related to the **security domain** must be present in the **resource's digital certificate**
- A **resource** can open a **connection** only toward another resource that share at least one **security domain** otherwise it is blocked by default

Specifications
- There must be a single configuration file where for each **resource** of the network are specified its **security domains**
- From this configuration files it must be possible to generate all the **nebula certificates** and nebula configuration files to implement the constraints of the **security domain** for the whole network
- Using the generated files, manually instantiate the network and verify the relevant connections

Resources
- [nebula github](https://github.com/slackhq/nebula)
- [medium: introducing nebula, the open source global overlay network](https://medium.com/several-people-are-coding/introducing-nebula-the-open-source-global-overlay-network-from-slack-884110a5579)
- [nebula doc](https://nebula.defined.net/docs/)
- [nebula quick start](https://nebula.defined.net/docs/guides/quick-start/)
- [nebula config reference](https://nebula.defined.net/docs/config/)
- [nebula official slack](https://join.slack.com/t/nebulaoss/shared_invite/enQtOTA5MDI4NDg3MTg4LTkwY2EwNTI4NzQyMzc0M2ZlODBjNWI3NTY1MzhiOThiMmZlZjVkMTI0NGY4YTMyNjUwMWEyNzNkZTJmYzQxOGU) (Big thanks alle persone del server per la loro disponibilità)

### Requirements analysis
##### Security Domains
A security domain is a set of logically related resources that can communicate and subject to the following constraints:
- A resource can have multiple security domains
- The information related to the security domain must be present in the resource's digital certificate
- A resource can open a connection only toward another resource that share at least one security domain otherwise it is blocked by default
From now i'll abbreviate Security Domains as **SecDom**.
##### Resources
Any machine of the virtual network including both Host and Lighthouse, those includes servers, laptops, mobile phones and anything that can run the nebula software.
##### Lighthouse
In Nebula, a lighthouse is a Nebula host that is responsible for keeping track of all of the other Nebula hosts, and helping them find each other within a Nebula network.
##### Hosts
A Nebula host is simply any single node in the network, e.g. a server, laptop, phone, tablet. The Certificate Authority is used to sign keys for each host added to a Nebula network. A host certificate contains the name, IP address, group membership, and a number of other details about a host. Individual hosts cannot modify their own certificate, because doing so will invalidate it. This allows us to trust that a host cannot impersonate another host within a Nebula network. Each host will have its own private key, which is used to validate the identity of that host when Nebula tunnels are created.
##### Communicate
Being able to exchange message as if being part of the same sub-net.
##### Digital Certificate
It's a the host certificate. From the official doc: "A host certificate contains the name, IP address, group membership, and a number of other details about a host. Individual hosts cannot modify their own certificate, because doing so will invalidate it. This allows us to trust that a host cannot impersonate another host within a Nebula network. Each host will have its own private key, which is used to validate the identity of that host when Nebula tunnels are created."

### Keypoints
##### Deployment dei file?
Each node in the network must have:
- a personal certificate key pair
- the CA's certificate (but not the key)
- the config file
- the nebula executable (or nebula installed)
Needs to deploy on linux, Freebsd, windows, macOS, iOS, android.
##### Division in security domains?
I'll most likely use the group feature of nebula. Is it enough?
With the nebula's group feature i can define a group for each security domain and set the host to allow connections from the same group(s). That's exactly what i need. Everything  else will need to be dropped.
##### Nebula firewall rules priority?
If i set two rules, one allows any connection from a group and another block request from a specific host. If the host is part of the group i'd assume that the request are still blocked because a more specific rule has priority over a more general, is this the case?
##### Can the lighthouse be part of a security domain?
Most likely not, the lighthouse should not have restrictions on who can communicate with him. But if i have multiple lighthouses i might.
##### Is it possible to have multiple lighthouses?
Yes nebula allows multiple lighthouses in the same network configuration. There are no particular configuration needed in a multi-lighthouse case scenario.
##### Usability, How easy it needs to be to modify the network layout, rules and security domains?
For the network layout it will be enough if it's not more complicated than the normal nebula host configuration method.
For SecDom related changes, changing the configuration file should apply all the changes to all the files ready to be deployed to the hosts.
A change in a single host should affects other host no more than it already does in a normally defined nebula network.
A good idea would be to regenerate only the files of hosts that would actually be changed.
While working with a simple file seems a bit too complex. It would require a full application to menage all the network and keep track of changes. ([Defined Networking's Managed Nebula](https://www.defined.net/) 👀)
##### What about scalability?
Nebula could be used for configuration of hundreds if not thousands of nodes. Scalability should be considered a possible critical point.
##### Config file format?
Most common format of configuration files that could be used in this case are JSON, YAML and TOML.
##### Security issues?
Is there a way to inject modification or other forms of attacks?
- Can I assume that the file transfer channel is secure?
- I can definitely modify the file in a node manually, should be saved in /etc folder to require at least sudo permission.
To be discussed with the commissioner

### Discussions with the commissioner
- Issues related to security of files generated both at deployment and at runtime on the various nodes in the network will not be addressed in the project
- Generation phase of initial configuration files (thus excluding rules derived from SecDoms) and subsequent deployment will not be addressed in the project

### Test Plan
During the test do communications will be simulated by simple ping (ICMP) to test the correct network configuration.
**Caution**: for implementations of the ICMP protocol once a node connects with a second it is possible that the latter will be able to create a new connection at a later time in the opposite direction even if the network configuration would not allow it.

### Test Bed
All tests will run on virtual machines generated through [Vagrant](https://developer.hashicorp.com/vagrant/tutorials/getting-started) running Ubuntu 12 operating system and virtualized with VirtualBox.
The machines will be configured to run on different subnets, an additional machine will act as a router and allow all others to connect to the vm lighthouse simulating the public internet.
VagrantFiles will be available in the Test section of the various sprints later.

### Division of work
The work will be broken down into sprints in a similar (but not the same) way as the SCRUM agile framework; the work on which these sprints will be based is unrelated to the framework and is described below:
- Sprint 1: Development of a first working version as proof-of-concept
	Testing: Simple case, 5 machines including 3 laptops in a common SecDom, 1 server capable of accepting requests from only one of the laptops (laptop1), and the lighthouse.
- Sprint 2: Analysis and advanced development of a deployable application.
	Test: More complex case, 6 machines including 3 laptops in one SecDom, 2 servers in a different SecDom, and the lighthouse. Two of the three laptops must be able to connect with only one of the servers.
	We are simulating a distributed server in a cluster of machines with one of them actin as gate for all the laptops.
- Sprint 3: Definition of edge cases and possible fixes.
	Test: [[Sprint 3 - Mistrustful colleagues#Boundary case - Mistrustful colleagues|Boundary case - Mistrustful colleagues]]


