### Requisiti
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

### Analisi dei requisiti
##### Security Domains
A security domain is a set of logically related resources that can communicate and subject to the following constraints:
- A resource can have multiple security domains
- The information related to the security domain must be present in the resource's digital certificate
- A resource can open a connection only toward another resource that share at least one security domain otherwise it is blocked by default
From now i'll abbreviate Security Domains as **SecDom**.
##### Resources
Any machine of the virtual network including both Host and Lighthouse, those includes servers, laptops, mobile phones and anything that can run the nebula software.
##### Lighthouse
In Nebula, a lighthouse is a Nebula host that is responsible for keeping track of all of the other Nebula hosts, and helping them find each other within a Nebula network
##### Hosts
A Nebula host is simply any single node in the network, e.g. a server, laptop, phone, tablet. The Certificate Authority is used to sign keys for each host added to a Nebula network. A host certificate contains the name, IP address, group membership, and a number of other details about a host. Individual hosts cannot modify their own certificate, because doing so will invalidate it. This allows us to trust that a host cannot impersonate another host within a Nebula network. Each host will have its own private key, which is used to validate the identity of that host when Nebula tunnels are created.
##### Communicate
Being able to exchange message as if being part of the same sub-net
##### Digital Certificate
It's a the host certificate. From the official doc: "A host certificate contains the name, IP address, group membership, and a number of other details about a host. Individual hosts cannot modify their own certificate, because doing so will invalidate it. This allows us to trust that a host cannot impersonate another host within a Nebula network. Each host will have its own private key, which is used to validate the identity of that host when Nebula tunnels are created."

### Keypoints
##### Deployment dei file?
Ogni nodo nel network deve avere:
- una coppia chiave certificato personale
- il certificato della CA (ma non la chiave)
- il file di config
- l'eseguibile di nebula (o nebula installato)
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
While working with a simple file seems a bit too complex. It would require a full application to menage all the network and keep track of changes.
##### What about scalability?
Nebula could be used for configuration of hundreds if not thousands of nodes. Scalability should be considered a possible critical point.
##### Formato del file di config
Most common format of configuration files that could be used in this case are JSON, YAML and TOML.
##### Security issues?
Is there a way to inject modification or other forms of attacks?
- Posso dare per scontato che il canale di trasferimento dei file sia sicuro?
- Posso sicuramente modificiare il file in un nodo manualmente, should be saved in /etc folder to require at least sudo permission.
Da discutere con il committente

### Discussioni con il committente
- Problemi legati all  sicurezza dei file generati sia in fase di deployment sia in fase di esecuzione sui vari nodi della rete non sarà trattato nel progetto
- Fase di generazione dei file di configurazione iniziali (quindi escluse le regole derivanti dai SecDom) e successivo deployment non sarà trattato nel progetto

### Test Plan
Durante la fare di test verranno simulate le comunicazioni mediante semplice ping (ICMP) per testare la corretta configurazione della rete.
**Attenzione**: per implementazioni del protocollo ICMP una volta che un nodo si connette con un secondo è possibile che questo riesca a creare una nuova connessione in un secondo momento nella direzione opposta anche se la configurazione della rete non lo permetterebbe.

### Test Bed
Tutti i test verranno eseguiti su macchine virtuali generate tramite [Vagrant](https://developer.hashicorp.com/vagrant/tutorials/getting-started) con sistema operativo Ubuntu 12 e virtualizzate con VirtualBox.
Le macchine saranno configurate per girare su sottoreti diverse, un'ulteriore macchina farà da ruter e permettera a tutte le altre di collegarsi alla vm lighthouse simulando la rete internet pubblica.
I VagrantFile saranno disponibili sella sezione di Test dei vari sprint in seguito.

### Divisione del lavoro
Il lavoro verrà suddiviso in sprint in modo analogo (ma non uguale) al framework agile SCRUM, il lavoro su cui questi sprint si baseranno non ha alcun legame con il framework ed è descritto di seguito:
- Sprint 1: Sviluppo di una prima versione funzionante as proof-of-concept
	Test: Caso semplice, 5 macchine di cui 3 laptops in un SecDom comune, 1 server in grado di accettare richieste da uno solo dei laptop (laptop1), e il lighthouse.
- Sprint 2: Analisi e sviluppo avanzato di un'applicazione distribuibile
	Test: Caso più complesso, 6 macchine di cui 3 laptops in un SecDom, 2 servers in un SecDom differente e il lighthouse. Due det tre laptop laptop devono potersi collegare con uno solo dei server.
Aka we have a distributed server in a cluster of machines with one of them actin as gate for all the laptops.
- Sprint 3: Definizione di casi limite e possibili correzioni
	Test: [[Sprint 3 - Mistrustful colleagues#Caso Limite - Mistrustful colleagues|Caso Limite - Mistrustful colleagues]]


