### Goal
Development of a first working version as proof-of-concept.

### Requirements
[[Nebula security domains#Requisiti|requirements' link]]

### Problem analysis
##### Division in security domains?
With the group feature i can define a group for each security domain and set the host to allow connections from the same group(s). That's exactly what i need. Everything else will need to be dropped.
##### Default deny 
Nebula uses a logic of default deny and add allow rules, there is no way of defining specific deny rules.
##### Nebula firewall rules priority?
All nebula rules are used to define allowed connections, order doesn't matter and there is no need for priority mechanism.
##### Difference between group and groups
In nebula both "group" and "groups" can be defined, the difference is that "groups" are in AND logic and the rules apply only to hosts that have all the groups listed.
##### How to auto generate?
For this first sprint i'll implement a simple script in bash, the goal is not to have a functional program but to see if a solution is possible and then improve on it.
##### What rules do we implements to block host from connecting to other host not in the same security domain?
Nebula allows us to block a connection from being made in two ways:
1) block the connection from leaving the node you are currently in:
	- Possible security fault? Can be removed/modified? Can be impersonated? Can be added in a second moment?
	- Implemented in this way, every node that is part of a SecDom could never initiate a connection with a host that is not part of any SecDom, in such a solution any node would have to be part of some SecDom also every lighthouse would have to be part of every SecDom (or enough SecDoms to be able to talk to every host defined in the network)
1) block connection from outside hosts not part of the same group:
	- This is clearly the best option of the two
##### Config file format?
For simplicity in this first sprint I will use the JSON format, each host will be defined as an object in a list with all the parameters needed to generate the config file and the key certificate pair.
##### Previous rules
What to do if a node has already some rules defined? All rules in nebula are made to allow connections to be made, given the requirements given if a rules allows a connection with a node that has not a common SecDom with the target should be dropped, if it allows a connections with a node that has a common SecDom instead the rules is superfluous and not needed.
If there are previous rules those will be overwritten.

### Test
[[Vagrant/vagrant_esempio1_nebula/Vagrantfile|Vagrantfile]]
5 machines including 3 laptops in a common SecDom, 1 server that can accept requests from only one of the laptops (laptop1), and the lighthouse.

### Design
In this case we need 2 security domains, one for the laptops and one for connecting to the server. One of the laptops will be part of both the security domains:
- LaptopSD:
	- laptop1
	- laptop2
	- laptop3
- ServerSD:
	- laptop1
	- server

The configuration file ([[esempio1.json]]) is defined as follows:
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

The script [[generateSD.sh]]:
``` shell
#!/bin/bash

# check parameter, Usage: Usage: ./generateSD JSON_FILEPATH
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

# check if jq is installed, jq is used to read and work with JSON files
# I could make the script install jq but that would require the script
# to be runned with sudo permission which is not normally required
if ! command -v jq &> /dev/null
then
echo "jq could not be found"
echo "i really really wanted to work with json so i need jq, pls install jq"
echo "to install:"
echo " sudo apt update"
echo " sudo apt install jq"
exit 1
fi

# check if file is a JSON file
if ! jq -e . >/dev/null 2>&1 <<<$(cat $1); then
echo "not a valid JSON file"
exit 1
fi


# common parameter definition
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
	sed "/static_host_map:/a\ \ \"$LIGHTHOUSE_NEBULA_IP\":\[\"$LIGHTHOUSE_MACHINE_IP:4242\"]" config-host-default.yaml > config_$HOST_NAME.yaml    # defining "static_host_map" parameter
	sed -i "/\ \ hosts:/a\ \ \ \ -\ \"$LIGHTHOUSE_NEBULA_IP\"" config_$HOST_NAME.yaml    # defining "hosts" parameter
	sed -i "/^\ \ relays/a\ \ \ \ -\ $LIGHTHOUSE_NEBULA_IP" config_$HOST_NAME.yaml    # defining "relays" parameter needed for the setup
	
	#step 3 - adding firewall rules for SecDom 
	echo " inbound:" >> config_$HOST_NAME.yaml
	jq -c ".[$i].security_domains[]" esempio1.json | tr -d \" | while read domain;
	do
		echo " - port: any" >> config_$HOST_NAME.yaml
		echo " proto: any" >> config_$HOST_NAME.yaml
		echo " group:" >> config_$HOST_NAME.yaml
		echo " - $domain" >> config_$HOST_NAME.yaml
		echo "" >> config_$HOST_NAME.yaml
	done
	  
	#step 4 - deployment of the file in the machine
	cd ~/Desktop/nebulaProject/Vagrant/vagrant_esempio1_nebula
	vagrant scp ../../NebulaApp/setup-host $HOST_NAME:.
	vagrant scp ../../NebulaApp/nebula $HOST_NAME:.
	vagrant scp ../../NebulaApp/ca.crt $HOST_NAME:.
	vagrant scp ../../NebulaApp/$HOST_NAME.crt $HOST_NAME:.
	vagrant scp ../../NebulaApp/$HOST_NAME.key $HOST_NAME:.
	vagrant scp ../../NebulaApp/config_$HOST_NAME.yaml $HOST_NAME:.
	  
done

#step 5 - generation and deployment of file for lighhtouse
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




