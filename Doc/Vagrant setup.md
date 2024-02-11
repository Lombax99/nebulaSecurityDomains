### Vagrant file
``` Vagrantfile
Vagrant.configure("2") do |config|

  config.vm.box = "debian/bookworm64"

  config.vm.provider "virtualbox" do |vb|
        vb.linked_clone = true
  end


  config.vm.define "lighthouse" do |machine|
    machine.vm.hostname = "lighthouse"
    
    #fixed ssh port for staging inventory
    machine.vm.network "forwarded_port", id: "ssh", host: 2222, guest: 22
    machine.vm.network "private_network", virtualbox__intnet: "homelab-staging",ip: "192.168.100.1"
  
  end


  config.vm.define "laptop" do |machine|
    machine.vm.hostname = "laptop"
    
    #fixed ssh port for staging inventory
    machine.vm.network "forwarded_port", id: "ssh", host: 2224, guest: 22
    machine.vm.network "private_network", virtualbox__intnet: "homelab-staging",ip: "192.168.100.5"
  
  end


  config.vm.define "server" do |machine|
    machine.vm.hostname = "server"
    
    #fixed ssh port for staging inventory
    machine.vm.network "forwarded_port", id: "ssh", host: 2226, guest: 22
    machine.vm.network "private_network", virtualbox__intnet: "homelab-staging",ip: "192.168.100.9"
  
  end


end
```

### Vagrant commands
**vagrant init** -> to initialize a new project in a dir
**vagrant up** -> starts all machines
**vagrant status** -> see status of all machines
**vagrant ssh _machineName_** -> connect via ssh to the specified machine
**vagrant halt** -> shuts down the running machine Vagrant is managing.
**vagrant global-status [--prune]** -> check all VM managed (--prune to clear old data)
**vagrant box [list/add/remove/prune]** -> manage vagrant boxes
**vagrant destroy** -> This command destroys all **VM resources** (but not any vagrant resources) so all the VirtualBox VM files are destroyed but the box remained untouched. 
**vagrant remove** -> This command remove (destroy) the **vagrant resources** so if you want to create a new VM later against the base box, vagrant would need to re-download from internet. Note that after you have created the VM, you can remove the box and vagrant will still work correctly so `vagrant remove` has no effect on the VirtualBox resources and all VMs remain untouched




