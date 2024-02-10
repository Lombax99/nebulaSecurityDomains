In the previous sprint we saw that using the group feature of nebula allows us to implements all the nebula security domains as needed by requirements.
The solution implemented though, as all the first ideas, is not the best. Knowing that it's possible in this sprint we will reanalyze the project in every aspects and implement a new solution with a different case scenario:
In this second case we will have 3 laptops, 2 servers and 1 lighthouse. We want all the laptops to be able to connect to one of the servers, the servers should be able to connect to each other but the laptops should only connect to one of them.
Aka we have a distributed server in a cluster of machines with one of them actin as gate for all the laptops.

### Analisi del problema

##### Single Responsibility principle
In the previous config file we had to define on top of all the hosts and the Security Domains other data like lighthouse and hosts actual and virtual IP (although the actual IP of all the hosts was not necessary in the end... my bad), the reason being that we asked to the script to generate all certificates and key on top of the configuration files that had to then be modified. From a project point of view we asked a singe script to do everything. Let's reanalyze the process and see how to handle it better.
The workflow of the system can be defined with the following points:
1) The Security Domain config file is created
2) Certification and Keys are created for every node of the network
3) Configuration files are created for every host
4) Configuration files are modified to implements Security Domain logic
5) Distribution to all the nodes
By separating the creation of the config file from the modification to implement the firewall rules we could simplify the nebula Security Domain config file.
##### Formato del file di config?
Nel primo sprint abbiamo usato JSON come tecnologia per definire il file di configurazione delle SecDom ma abbiamo altre opzioni?
Tra le tecnologie esistente le più comuni sono JSON, YAML (usato da nebula stesso) e TOML:
- JSON è forse il più semplice ed intuitivo
- YAML sembra guadagnare punti essendo usato da nebula stesso
- TOML è più recente dei precedenti e rappresenta una versione più semplice di YAML
Dopo qualche ricerca la mia scelta ricade comunque su JSON per i seguenti motivi:
- YAML è molto più complesso ed error prone di quanto non si pensi (see the [yaml document from hell](https://ruudvanasseldonk.com/2023/01/11/the-yaml-document-from-hell) for reference)
- TOML nonostante sia più sicuro di YAML non è particolarmente intuitivo
- JSON è intuitivo, molto meno error prone (per ora il file va generato a mano quindi questo è un grosso punto a favore) ed è sempre possibile convertire da JSON a YAML, non è necessariamente vero il contrario.

Per quanto riguarda la disposizione dei dati nel file si possono seguire due strade:
1) scrivo una lista di security domains, in ogni domain definisco la lista di host che vi appartengono
	VANTAGGI:
		- Più intuitivo per l'utente in fase di definizione della rete
		- Risponde facilmente a domande come "chi fa parte di questo SecDom?"
2) scrivo una lista di host, in ogni host definisco la lista di security domain a cui appartiene
	VANTAGGI:
		- Più facile da implementare a livello di codice
		- Risponde più facilmente a domande come "a quali SecDom fa parte questo host?"
Ovviamente User Friendliness >> tutto il resto, il primo punto vince a mani basse...

NOTA1: come definito in precedenza gli unici dati che dovrebbero apparire nel file sono l'ID degli Hosts e i SecDom a cui appartengono, dati come IP e parametri particolari non dovrebbero farne parte.

NOTA2: Gli ID degli host non devono essere necessariamente univoci per questo progetto tuttavia renderli tali non solo è buona prassi ma faciliterebbe tutto e porterebbe vantaggi all'utente finale.

NOTA3: Per quanto sia intuitivo JSON generare in automatico il file di config rimuoverebbe il problema (almeno in parte) di un file scritto male, questo però implicherebbe avere un'applicazione per gestire la rete con GUI e tutto quanto che al momento esula dal progetto.
([Defined Networking's Managed Nebula](https://www.defined.net/) 👀👀)

NOTA4: A questo punto mi ritrovo con due file di config, uno con i dati con gli ip e uno con i security domains, lascio che a livello di codice si gestiscano i conflitti e si assicuri che siano ben formati ma questo porta a nuovi possibili problemi, gli id devono essere corretti nei due file e devono essere definiti tutti, in compenso ho modo di fare merge dei dati delle SecDom in entrambi i file e avere entrambe le opzioni definite sopra per visualizzare la struttura della mia rete. La soluzione perfetta sarebbe abbandonare completamente la generazione manuale di questi file e passare ad un tool software per definire l'intera rete e nascondere i formati dei file salvati allìutente finale permettendogli di accedere e modificare le informazioni legate alla struttura della rete attraverso il tool.
##### What about the Lighthouse? Can it be part of a security domain?
Un lighthouse ha comunque bisogno degli stessi file di ogni altro host, i punti 2, 3 e 5 del workflow sono quindi necessari anche per esso, rimane da capire se un lighthouse possa essere parte di un SecDom o meno.
Data la natura di Nebula, ogni host (ad eccezione di casi estremamente particolari) deve potersi collegare almeno una volta ad un lighthouse per funzionare correttamente.
*Lighthouses allow Nebula nodes to discover the routable IP addresses of other nodes (i.e. to locate each other.) If the Nebula nodes can't connect to a shared Lighthouse, the only other way they might know where to look is if you define a [static_host_map](https://nebula.defined.net/docs/config/static-host-map/) entry for each other.* 
Risulta quindi chiaro che ogni host della rete debba potersi collegare ad un lighthouse, per situazioni in cui il lighthouse è uno solo, limitarne la connessione tramite SecDom sarebbe un errore grave. Tuttavia in Nebula è possibile implementare diversi lighthouses, in quel caso potrebbe essere possibile. Ritengo comunque non sia una buona pratica per il semplice motivo che il principale vantaggio nel negare l'accesso ad un lighthouse sarebbe solo utile a fini di ridistribuzione del carico di lavoro nella rete ma per fare ciò nebula definisce strumenti migliori attraverso il file di config, non è quindi compito dei SecDom occuparsi di ciò.
Piccolo extra: nebula comunica con encrypting peer-to-peer, non è possibile sniffare il traffico di passaggio attraverso il lighthouse, inoltre in caso di attacco si potrebbe valutare la possibilità di bloccare determinati hosts da comunicare con il lighthouse ma non è compito di questo progetto gestire un caso del genere.

Final answer then is no but practically speaking i can't block a user from putting a node called "lighthouse" in the config, maybe i should at least print some warning telling them it's not a good practice
##### How easy it is to modify the network layout, rules and security domains?
it will be enough if it's not more complicated than the normal nebula host configuration method.
Maybe regenerate only the files that would actually be changed?
It's cool but a bit too complicated while working with a simple config file. If i had a full application to menage all the networks it's would be a must.
([Defined Networking's Managed Nebula](https://www.defined.net/) 👀👀)
##### What about scalability?
How scalable is this system?
All'aumentare del numero di nodi la complessità nel file JSON cresce linearmente così come il tempo di creazione dei file, non dovrebbe quindi essere un punto critico dell'applicazione.
##### How to auto generate?
Usare uno script linux presenta diversi limiti:
- Non è facilmente portabile in altre piattaforme e/o architetture (se non addirittura impossibile)
- sfrutta "jq" un tool non necessariamente presente, per poter assicurare l'esecuzione richiederebbe installazione automatica e di conseguenza sudo permission --> grave
- è monolitico
Per la nuova versione useremo un linguaggio di programmazione distribuibile su diverse piattaforme ed organizzato il più possibile a componenti.
La mia scelta ricade su Python per facilità d'uso e familiarità.
##### Security issues?
Is there a way to inject modification or other forms of attacks?
- Posso dare per scontato che il canale di trasferimento dei file sia sicuro?
- Posso sicuramente modificare il file in un nodo manualmente...
Questi problemi esulano dal progetto e non verranno trattati... comunque si non è sicurissimo.
##### Deployment of the files?
Ogni nodo nel network deve avere:
- una coppia chiave certificato personale
- il certificato della CA (ma non la chiave)
- il file di config
- l'eseguibile di nebula (o nebula installato)
Needs to deploy on linux, Freebsd, windows, macOS, iOS, android.
Questi problemi esulano dal progetto e non verranno trattati. 
([Defined Networking's Managed Nebula](https://www.defined.net/) 👀👀)

### Progettazione


### PROBLEM CASE: Mistrustful Colleagues
This new solution is a great advancement compared to the first shell script we had but it's not perfect, in this specific case for example what happens when we decide to have all the laptop able to connect to the server but not to each other? As of right now each and every laptop would need a specific Security Domain with the server.
In the next sprint we will face this problem and search for a possible solution.