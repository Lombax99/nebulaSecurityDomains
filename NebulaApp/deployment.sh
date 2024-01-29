#!/bin/bash

#move to correct nebula dir
cd ../Vagrant/vagrant_nebula_project/

#send file to lighthouse
vagrant scp ../../NebulaApp/nebula lighthouse:.
vagrant scp ../../NebulaApp/config-lighthouse.yaml lighthouse:.
vagrant scp ../../NebulaApp/ca.crt lighthouse:.
vagrant scp ../../NebulaApp/lighthouse1.crt lighthouse:.
vagrant scp ../../NebulaApp/lighthouse1.key lighthouse:.
vagrant scp ../../NebulaApp/setup-lighthouse lighthouse:.

#send file to server
vagrant scp ../../NebulaApp/nebula server:.
vagrant scp ../../NebulaApp/config.yaml server:.
vagrant scp ../../NebulaApp/ca.crt server:.
vagrant scp ../../NebulaApp/server.crt server:.
vagrant scp ../../NebulaApp/server.key server:.
vagrant scp ../../NebulaApp/setup-server server:.

#send file to laptop
vagrant scp ../../NebulaApp/nebula laptop:.
vagrant scp ../../NebulaApp/config.yaml laptop:.
vagrant scp ../../NebulaApp/ca.crt laptop:.
vagrant scp ../../NebulaApp/laptop.crt laptop:.
vagrant scp ../../NebulaApp/laptop.key laptop:.
vagrant scp ../../NebulaApp/setup-laptop laptop:.

#clear file
#rm ../../NebulaApp/laptop.key
#rm ../../NebulaApp/laptop.crt
#rm ../../NebulaApp/config.yaml
#rm ../../NebulaApp/server.key
#rm ../../NebulaApp/server.crt
#rm ../../NebulaApp/lighthouse1.key
#rm ../../NebulaApp/lighthouse1.crt
#rm ../../NebulaApp/config-lighthouse.yaml


