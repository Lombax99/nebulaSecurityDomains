### Goal
Sviluppo di una prima versione funzionante as proof-of-concept.
### Test
5 macchine di cui 3 laptops in un SecDom comune, 1 server in grado di accettare richieste da uno solo dei laptop (laptop1), e il lighthouse.
### Requisiti
[[Nebula security domains#Requisiti|link requisiti]]
### Analisi del problema
##### Division in security domains?
With the group feature i can define a group for each security domain and set the host to allow connections from the same group(s). That's exactly what i need. Everything else will need to be dropped.
##### Default deny 
Nebula uses a logic of default deny and add allow rules, there is no way of defining specific deny rules.
##### Nebula firewall rules priority?
All nebula rules are used to define allowed connections, order doesn't matter and there is no need for priority mechanism.
##### Difference between group and groups
In nebula both "group" and "groups" can be defined, the difference is that "groups" are in AND logic and the rules apply only to hosts that have all the groups listed
##### How to auto generate?
For this first sprint i'll implement a simple script in bash, the goal is not to have a functional program but to see if a solution is possible and then improve on it.
##### What rules do we implements to block host from connecting to other host not in the same security domain?
Nebula allows us to block a connection from being made in two ways:
1) block the connection from leaving the node you are currently in:
	- Possible security fault? Can be removed/modified? Can be impersonated? Can be added in a second moment?
	- Implementato in questo modo, ogni nodo che fa parte di un SecDom non potrebbe mai iniziare una connessione con un host non facente parte di nessun SecDom, in una soluzione di questo tipo qualsiasi nodo dovrebbe far parte di un qualche SecDom inoltre ogni lighthouse dovrebbe essere parte di ogni SecDom (o abbastanza SecDom per poter parlare con ogni host definito nel network) 
1) block connection from outside hosts not part of the same group:
	- This is clearly the best option of the two
##### Formato del file di config?
Per semplicità in questo primo sprint userò il formato JSON, ogni host sarà definito come un'oggetto in una lista con tutti i parametri necessari per generare il file di config e la coppia key certificate.
##### Previous rules
What to do if a node has already some rules defined? All rules in nebula are made to allow connections to be made, given the requirements given if a rules allows a connection with a node that has not a common SecDom with the target should be dropped, if it allows a connections with a node that has a common SecDom instead the rules is superfluous and not needed.
If there are previous rules those will be overwritten.

### Test
[[Vagrant/vagrant_esempio1_nebula/Vagrantfile|Vagrantfile]]
``` Vagrant
Vagrant.configure("2") do |config|

  config.vm.box = "debian/bookworm64"

  config.vm.provider "virtualbox" do |vb|
        vb.linked_clone = true
  end


  config.vm.define "lighthouse" do |machine|
    machine.vm.hostname = "lighthouse"
    
    #fixed ssh port for staging inventory
    machine.vm.network "forwarded_port", id: "ssh", host: 2222, guest: 22
    
    machine.vm.network "private_network",
      virtualbox__intnet: "lighthouse-network",
      ip: "192.168.1.10",
      netmask: "255.255.255.0"

    #add host name to /etc/hosts
    machine.vm.provision "shell",
      inline: <<-SHELL
	 echo -e "192.168.2.11   laptop1" >> /etc/hosts
	 echo -e "192.168.2.12   laptop2" >> /etc/hosts
	 echo -e "192.168.2.13   laptop3" >> /etc/hosts
	 echo -e "192.168.3.10   server" >> /etc/hosts
	 mkdir /etc/nebula
      SHELL

	#define route to all other machines via router
    machine.vm.provision "shell",
      run: "always",
      inline: <<-SHELL
	 sudo ip route add 192.168.2.11 via 192.168.1.1
	 sudo ip route add 192.168.2.12 via 192.168.1.1
	 sudo ip route add 192.168.2.13 via 192.168.1.1
	 sudo ip route add 192.168.3.10 via 192.168.1.1
      SHELL
  end
  
  
  config.vm.define "laptop1" do |machine|
    machine.vm.hostname = "laptop1"
    
    #fixed ssh port for staging inventory
    machine.vm.network "forwarded_port", id: "ssh", host: 2224, guest: 22
    
    machine.vm.network "private_network",
      virtualbox__intnet: "laptop-network",
      ip: "192.168.2.11",
      netmask: "255.255.255.0"  

    #add lighthouse name to /etc/hosts
    machine.vm.provision "shell",
      inline: <<-SHELL
	 echo -e "192.168.1.10   lighthouse" >> /etc/hosts
	 mkdir /etc/nebula
      SHELL

	#define route to lighthouse via router
    machine.vm.provision "shell",
      run: "always",
      inline: <<-SHELL
	 sudo ip route add 192.168.1.10 via 192.168.2.1
      SHELL

  end
  
  
    config.vm.define "laptop2" do |machine|
    machine.vm.hostname = "laptop2"
    
    #fixed ssh port for staging inventory
    machine.vm.network "forwarded_port", id: "ssh", host: 2225, guest: 22
    
    machine.vm.network "private_network",
      virtualbox__intnet: "laptop-network",
      ip: "192.168.2.12",
      netmask: "255.255.255.0"  

    #add lighthouse name to /etc/hosts
    machine.vm.provision "shell",
      inline: <<-SHELL
	 echo -e "192.168.1.10   lighthouse" >> /etc/hosts
	 mkdir /etc/nebula
      SHELL

	#define route to lighthouse via router
    machine.vm.provision "shell",
      run: "always",
      inline: <<-SHELL
	 sudo ip route add 192.168.1.10 via 192.168.2.1
      SHELL

  end
  
  
    config.vm.define "laptop3" do |machine|
    machine.vm.hostname = "laptop3"
    
    #fixed ssh port for staging inventory
    machine.vm.network "forwarded_port", id: "ssh", host: 2226, guest: 22
    
    machine.vm.network "private_network",
      virtualbox__intnet: "laptop-network",
      ip: "192.168.2.13",
      netmask: "255.255.255.0"  

	#add lighthouse name to /etc/hosts
    machine.vm.provision "shell",
      inline: <<-SHELL
	 echo -e "192.168.1.10   lighthouse" >> /etc/hosts
	 mkdir /etc/nebula
      SHELL

    #define route to lighthouse via router
    machine.vm.provision "shell",
      run: "always",
      inline: <<-SHELL
	 sudo ip route add 192.168.1.10 via 192.168.2.1
      SHELL

  end


  config.vm.define "server" do |machine|
    machine.vm.hostname = "server"
    
    #fixed ssh port for staging inventory
    machine.vm.network "forwarded_port", id: "ssh", host: 2228, guest: 22
    
    machine.vm.network "private_network",
      virtualbox__intnet: "server-network",
      ip: "192.168.3.10",
      netmask: "255.255.255.0"

	#add lighthouse name to /etc/hosts
    machine.vm.provision "shell",
      inline: <<-SHELL
	 echo -e "192.168.1.10   lighthouse" >> /etc/hosts
	 mkdir /etc/nebula
      SHELL

    #define route to lighthouse via router
    machine.vm.provision "shell",
      run: "always",
      inline: <<-SHELL
	 sudo ip route add 192.168.1.10 via 192.168.3.1
      SHELL

  end


  config.vm.define "router" do |machine|
    machine.vm.hostname = "router"                                                
    #fixed ssh port for staging inventory   
    machine.vm.network "forwarded_port", id: "ssh", host: 2230, guest: 22         
    
   machine.vm.network "private_network",                                         
      virtualbox__intnet: "lighthouse-network",     
      ip: "192.168.1.1",                
      netmask: "255.255.255.0"

   machine.vm.network "private_network",                 
      virtualbox__intnet: "laptop-network",              
      ip: "192.168.2.1",                                
      netmask: "255.255.255.0"

   machine.vm.network "private_network",       
      virtualbox__intnet: "server-network",
      ip: "192.168.3.1",             
      netmask: "255.255.255.0"                                                   

   #enable forward ip
   machine.vm.provision "shell", inline: <<-SHELL
      sudo apt-get update
      sudo apt-get install traceroute
      echo -e "\nnet.ipv4.ip_forward=1" >> /etc/sysctl.conf
    SHELL
    machine.vm.provision :reload   
       
  end

end
```
### Progettazione
In this case we need 2 security domains, one for the laptops and one for connecting to the server. One of the laptops will be part of both the security domains:
- LaptopSD:
	- laptop1
	- laptop2
	- laptop3
- ServerSD:
	- laptop1
	- server

Il file di configurazione ([[esempio1.json]]) è definito come segue:
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

[[generateSD.sh]]:
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




