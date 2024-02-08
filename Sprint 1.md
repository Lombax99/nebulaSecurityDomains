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
With the group feature i can define a group for each security domain and set the host to allow connections from thw same group(s). That's exactly what i need.
##### How to auto generate?
A simple script is enough? All need to be from a single setting file.
- Might as well use this file to generate all the info of the network and not just the security domains...
##### What rules do we implements to block host from connecting to other host not in the same security domain?
1) block connection from leaving the node you are currently in:
	- Possible security fault? Can be modified? Can be impersonated? Can be added in a second moment?
	- In questo caso posso solo bloccare tutto quello che esce ad esclusione di bersagli appartenenti ad un gruppo, questo vuol dire che o fai parte di un qualche gruppo o nessuno ti parlerà mai.
1) block connection from outside hosts not part of the same group:
	- How do i know if an outside request is from a host with a group in common with me? Nebula takes care of that.
Check [[Nebula security domains#What about scalability?|scalability issues]].
##### Nebula firewall rules priority?
If i set two rules, one allows any connection from a group and another block request from a specific host. If the host is part of the group i'd assume that the request are still blocked because a more specific rule has priority over a more general, is this the case?
And what if a laptop is in two groups with conflicting rules, which ore takes priority?
##### Difference between group and groups
In nebula both "group" and "groups" can be defined, the difference is that "groups" are in AND logic and the rules apply only to hosts that have all the groups listed
##### Default deny 
Nebula uses a logic of default deny and add allow rules, there is no way of defining specific deny rules.
##### Formato del file di config
Un bel JSON non sarebbe male ma è la versione migliore? Molto probabilmente si
### Progettazione
In this case we need 2 security domains, one for the laptops and one for connecting to the server. One of the laptops will be part of both the security domains:
- LaptopSD:
	- laptop1
	- laptop2
	- laptop3
- ServerSD:
	- laptop1
	- server

Per fare il file di conf posso usare il formato json ed elaborare il tutto tramite jq

``` json
[
	{
		"name": "lighthouse",
		"nebula_ip": "192.168.100.1",
		"machine_ip": "192.168.1.10"
	},
	  
	{
		"name": "laptop1",
		"nebula_ip": "192.168.100.11/24",
		"machine_ip": "192.168.2.11",
		"security_domains": ["LaptopSD", "ServerSD"]
	},
	  
	{
		"name": "laptop2",
		"nebula_ip": "192.168.100.12/24",
		"machine_ip": "192.168.2.12",
		"security_domains": ["LaptopSD"]
	},
	  
	{
		"name": "laptop3",
		"nebula_ip": "192.168.100.13/24",
		"machine_ip": "192.168.2.13",
		"security_domains": ["LaptopSD"]
	},
	  
	{
		"name": "server",
		"nebula_ip": "192.168.100.21/24",
		"machine_ip": "192.168.3.10",
		"security_domains": ["ServerSD"]
	}
]
```

Lo script:
``` shell
#!/bin/bash
  
if [ "$#" -ne 1 ]; then
echo "Usage: $0 JSON_FILEPATH" >&2
exit 1
fi
if ! [ -e "$1" ]; then
echo "$1 not found" >&2
exit 1
fi
if ! [ -f "$1" ]; then
echo "$1 not a file" >&2
exit 1
fi
  
if ! command -v jq &> /dev/null
then
echo "jq could not be found"
echo "i really really wanted to work with json so i need jq, pls install jq"
echo "to install:"
echo " sudo apt update"
echo " sudo apt install jq"
exit 1
fi
  
if ! jq -e . >/dev/null 2>&1 <<<$(cat $1); then
echo "not a valid JSON file"
exit 1
fi

  
FILE_PATH=$1
LIGHTHOUSE_NEBULA_IP=$(jq '.[] | select(.name=="lighthouse").nebula_ip' $FILE_PATH | tr -d \" )
LIGHTHOUSE_MACHINE_IP=$(jq '.[] | select(.name=="lighthouse").machine_ip' $FILE_PATH | tr -d \" )
NUMBER_OF_HOST=$(jq 'length' $FILE_PATH)
  
for i in $(seq 1 $((NUMBER_OF_HOST - 1)))
do
cd ~/Desktop/nebulaProject/NebulaApp
  
HOST_NAME=$(jq ".[$i].name" $FILE_PATH | tr -d \" )
HOST_IP=$(jq ".[$i].nebula_ip" $FILE_PATH | tr -d \" )
SECURITY_DOMAINS=$(jq -rc ".[$i].security_domains[]" $FILE_PATH | tr '\n' ",")
  
#step 1 - generate certificate and key
./nebula-cert sign -name $HOST_NAME -ip $HOST_IP -groups "${SECURITY_DOMAINS::-1}"
  
#step 2 - generate config file
sed "/static_host_map:/a\ \ \"$LIGHTHOUSE_NEBULA_IP\":\[\"$LIGHTHOUSE_MACHINE_IP:4242\"]" config-host-default.yaml > config_$HOST_NAME.yaml
sed -i "/\ \ hosts:/a\ \ \ \ -\ \"$LIGHTHOUSE_NEBULA_IP\"" config_$HOST_NAME.yaml
sed -i "/^\ \ relays/a\ \ \ \ -\ $LIGHTHOUSE_NEBULA_IP" config_$HOST_NAME.yaml
echo " inbound:" >> config_$HOST_NAME.yaml
jq -c ".[$i].security_domains[]" esempio1.json | tr -d \" | while read domain;
do
echo " - port: any" >> config_$HOST_NAME.yaml
echo " proto: any" >> config_$HOST_NAME.yaml
echo " group:" >> config_$HOST_NAME.yaml
echo " - $domain" >> config_$HOST_NAME.yaml
echo "" >> config_$HOST_NAME.yaml
done
  
#step 3 - deployment of the file in the machine
cd ~/Desktop/nebulaProject/Vagrant/vagrant_esempio1_nebula
vagrant scp ../../NebulaApp/setup-host $HOST_NAME:.
vagrant scp ../../NebulaApp/nebula $HOST_NAME:.
vagrant scp ../../NebulaApp/ca.crt $HOST_NAME:.
vagrant scp ../../NebulaApp/$HOST_NAME.crt $HOST_NAME:.
vagrant scp ../../NebulaApp/$HOST_NAME.key $HOST_NAME:.
vagrant scp ../../NebulaApp/config_$HOST_NAME.yaml $HOST_NAME:.
  
done
  
#step 4 - deployment of file in lighhtouse
  
cd ~/Desktop/nebulaProject/NebulaApp
./nebula-cert sign -name "lighthouse" -ip "192.168.100.1/24"
  
cd ~/Desktop/nebulaProject/Vagrant/vagrant_esempio1_nebula
vagrant scp ../../NebulaApp/setup-host lighthouse:.
vagrant scp ../../NebulaApp/nebula lighthouse:.
vagrant scp ../../NebulaApp/ca.crt lighthouse:.
vagrant scp ../../NebulaApp/lighthouse.crt lighthouse:.
vagrant scp ../../NebulaApp/lighthouse.key lighthouse:.
vagrant scp ../../NebulaApp/config-lighthouse-default.yaml lighthouse:.
```





