[Nebula quick start](https://nebula.defined.net/docs/guides/quick-start/)

#### 0) installation
- Download the right version from:
	https://github.com/slackhq/nebula/releases/latest

- Extract the executable
```
tar -xzf nebula-linux-amd64.tar.gz
```

#### 1) Creating a CA
> [!Tip]- Storing of CA private key
> Nebula offers built-in encryption of the CA private key since v1.7.0. If you do not plan to store the private key in encrypted storage (e.g. Ansible Vault or AWS Secrets Manager), it is recommended that you use the built-in encryption.
> 
> To encrypt your Nebula private key, pass the `-encrypt` flag when generating the CA and you will be prompted for a passphrase. Keep it safe - you will be prompted for it each time you sign a host using the encrypted CA key.
> 
> Nebula uses AES-256-GCM encryption with Argon2id for key derivation. The default Argon2 parameters are taken from the "FIRST RECOMMENDED" suggestion in the [Argon2 RFC](https://datatracker.ietf.org/doc/rfc9106/) (1 iteration, 4 lanes parallelism, 2 GiB RAM.) To select your own parameters, use the `-argon-iterations`, `-argon-parallelism`, and `-argon-memory` CLI flags.

```
./nebula-cert ca -name "Myorg, Inc"
```

> [!Note] 
> Password used for encription: "swordfish"

>[!Tip] info
>By default, this CA will be created with a one-year expiration, and all certificates signed will be valid until one second before expiration of the CA.
>
>Be sure to set up an alert or calendar event to [rotate your CA and certificates](https://nebula.defined.net/docs/guides/rotating-certificate-authority/) before then to ensure continued connectivity!

Pass `-duration XXhXXmXXs` to set a custom duration for the CA to be valid at creation, for example `-duration 17531h` would generate a CA valid for just under two years.

```
./nebula-cert print -path somecert.crt    #to see certificate
```
#### 2) Building the network
##### Creating a Keys and Certificates
``` sh
./nebula-cert sign -name "lighthouse" -ip "192.168.100.1/24"
./nebula-cert sign -name "laptop" -ip "192.168.100.5/24" -groups "laptop,ssh"
./nebula-cert sign -name "server" -ip "192.168.100.9/24" -groups "servers"
```
##### Creating the configuration file
Starting from this nebula [example configuration](https://github.com/slackhq/nebula/blob/master/examples/config.yml).
We need two copies, one for the lighthouse and one for the other hosts
``` sh
curl -o config.yml https://raw.githubusercontent.com/slackhq/nebula/master/examples/config.yml
cp config.yml config-lighthouse.yaml
cp config.yml config.yaml
```

modify the files:
```  config-lighthouse.yaml
ca: /etc/nebula/ca.crt
cert: /etc/nebula/lighthouse.crt
key: /etc/nebula/lighthouse.key

static_host_map:

lighthouse:
  am_lighthouse: true
```

``` config.yaml
ca: /etc/nebula/ca.crt
cert: /etc/nebula/laptop.crt    #or the correct name
key: /etc/nebula/laptop.key     #or the correct name

static_host_map:
  '192.168.100.1': ['192.168.100.1:4242']
  
lighthouse:
  am_lighthouse: false
  interval: 60
  hosts:
    - '192.168.100.1'
```

firewall settings:
```
firewall:
  outbound:    
    # Allow all outbound traffic from this node    
    - port: any      
      proto: any      
      host: any  
      
  inbound:    
    # Allow icmp between any nebula hosts    
    - port: any      
      proto: icmp      
      host: any
```

#### 3) Running Nebula
##### Distribution of files
- Lighthouse:
	1) Copy the `nebula` binary, along with the `config-lighthouse.yaml`, `ca.crt`, `lighthouse.crt`, and `lighthouse.key` to your lighthouse. **DO NOT COPY `ca.key` TO YOUR LIGHTHOUSE.**
	```
	vagrant scp <local_path> [vm_name]:<remote_path>
	```
    1) SSH to your lighthouse.
	3) Create a directory named `/etc/nebula` on your lighthouse host.
	```
	mkdir /etc/nebula
	```
	4) Move the configuration, certificates, and key into the appropriate directory.
	    _Note_: The example configuration assumes your host certificate and key are named `host.crt` and `host.key`, so you'll need to rename some of the files when you move them to the appropriate directory.
    ```
    mv config-lighthouse.yaml /etc/nebula/
    mv ca.crt /etc/nebula/
    mv lighthouse.crt /etc/nebula/
    mv lighthouse.key /etc/nebula/
    ```
     5) Start Nebula
    ```
    ./nebula -config /etc/nebula/config-lighthouse.yaml
    ```

- Hosts:
	_For this example, we are configuring the host created above, named `server`. Please substitute the correct file names as appropriate._
	
	1) Copy the `nebula` binary, along with the `config.yaml`, `ca.crt`, `server.crt`, and `server.key` to the host named `server`. **DO NOT COPY THE `ca.key` FILE.**
	2) SSH to the host you've named `server`.
	3) Create a directory named `/etc/nebula` on the Nebula host.
    ```
    mkdir /etc/nebula
    ```
	4) Move the configuration, certificates, and key into the appropriate directory.
    _Note_: The example configuration assumes your host certificate and key are named `host.crt` and `host.key`, so you'll need to rename some of the files when you move them to the appropriate directory.
    ```
    mv config.yaml /etc/nebula/
    mv ca.crt /etc/nebula/ca.crt
    mv server.crt /etc/nebula/
    mv server.key /etc/nebula/
    ```
	5) Start Nebula
    ```
    ./nebula -config /etc/nebula/config.yaml
	
	#or better
	
	sudo ./nebula -config /etc/nebula/config.yaml &> logs.txt &
    ```
##### Verifying it all works
You should now be able to ping other hosts running nebula (assuming ICMP is allowed). To ping the example lighthouse, run:
```
ping 192.168.100.1
```

#### Adding hosts to your network
It is easy to add hosts to an established Nebula network. You simply create a new host certificate and key, and then follow the steps under Running Nebula. You will not need to make changes to your lighthouse or any other hosts when adding hosts to your network, and existing hosts will be able to find new ones via the lighthouse, automatically.
