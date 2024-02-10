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
    echo "    sudo apt update"
    echo "    sudo apt install jq" 
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
   sed "/static_host_map:/a\ \ \"$LIGHTHOUSE_NEBULA_IP\":\ [\"$LIGHTHOUSE_MACHINE_IP:4242\"]" config-host-default.yaml > config_$HOST_NAME.yaml
   sed -i "/\ \ hosts:/a\ \ \ \ -\ \"$LIGHTHOUSE_NEBULA_IP\"" config_$HOST_NAME.yaml
   sed -i "/^\ \ relays/a\ \ \ \ -\ $LIGHTHOUSE_NEBULA_IP" config_$HOST_NAME.yaml
   
   echo "  inbound:" >> config_$HOST_NAME.yaml
   jq -c ".[$i].security_domains[]" esempio1.json | tr -d \" | while read domain; 
   do
      echo "    - port: any" >> config_$HOST_NAME.yaml
      echo "      proto: any" >> config_$HOST_NAME.yaml
      echo "      group:" >> config_$HOST_NAME.yaml
      echo "        - $domain" >> config_$HOST_NAME.yaml
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
