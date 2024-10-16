### Goal
In the previous sprint we saw that using the group feature of nebula allows us to implements all the nebula security domains as needed by requirements.
The solution implemented though, as all the first ideas, is not the best. Knowing that it's possible in this sprint we will reanalyze the project in every aspects and implement a new solution with a different case scenario.

### Problem analysis
##### Single Responsibility principle
In the previous config file we had to define on top of all the hosts and the Security Domains other data like lighthouse and hosts actual and virtual IP (although the actual IP of all the hosts was not necessary in the end... my bad), the reason being that we asked to the script to generate all certificates and key on top of the configuration files that had to then be modified. From a project point of view we asked a singe script to do everything. Let's reanalyze the process and see how to handle it better.
The workflow of the system can be defined with the following points:
1) The Security Domain config file is created
2) Certification and Keys are created for every node of the network
3) Configuration files are created for every host
4) Configuration files are modified to implements Security Domain logic
5) All generated files are distributed to the hosts
By separating the creation of the config file from the modification to implement the firewall rules we could simplify the nebula Security Domain config file.
##### Config file format?
In the first sprint we used JSON as the technology to define the SecDom configuration file but do we have other options?
Of the existing technologies the most common are JSON, YAML (used by nebula itself) and TOML:
- JSON is perhaps the simplest and most intuitive
- YAML seems the most suitable solution being used by nebula itself
- TOML is newer than the previous ones and represents a simpler version of YAML
After some research my choice still falls on JSON for the following reasons:
- YAML is much more complex and error prone than you think (see the [yaml document from hell](https://ruudvanasseldonk.com/2023/01/11/the-yaml-document-from-hell) for reference)
- TOML despite being more secure than YAML is not particularly intuitive
- JSON is intuitive, much less error prone (for now the file has to be generated by hand so this is a big plus) and it is always possible to convert from JSON to YAML, the opposite is not necessarily true.

Regarding the arrangement of the data in the file, two paths can be followed:
1) I write a list of security domains, in each domain I define the list of hosts that belong to it.
	ADVANTAGES:
		- More intuitive for the user when defining the network
		- Easily answers questions such as "who belongs to this SecDom?"
2) I write a list of hosts, in each host I define the list of security domains to which it belongs
	ADVANTAGES:
		- Easier to implement at the code level
		- Easier to answer questions such as "which SecDom does this host belong to?"
Obviously User Friendliness takes precedence over everything else, so the first point is also the best.

NOTE1: As defined above the only data that should appear in the file are the IDs of the Hosts and the SecDoms to which they belong, data such as IPs and special parameters should not be part of it.

NOTE2: Host IDs need not be unique for this project however making them so is not only good practice but would facilitate everything and benefit the end user.

NOTE3: As intuitive as it is JSON, automatically generating the config would remove the problem (at least in part) of a poorly written file, this however would involve having an application to manage the network with GUI and all, that is currently beyond the scope of this project.
([Defined Networking's Managed Nebula](https://www.defined.net/) 👀👀)

##### What about the Lighthouse? Can it be part of a security domain?
A lighthouse still needs the same files as any other host; steps 2, 3, and 5 of the workflow are therefore necessary for it as well; the question remains whether a lighthouse can be part of a SecDom or not.
Given the nature of Nebula, every host (except in extremely special cases) must be able to connect at least once to a lighthouse to function properly.

Lighthouses allow Nebula nodes to discover the routable IP addresses of other nodes (i.e. to locate each other.) If the Nebula nodes can't connect to a shared Lighthouse, the only other way they might know where to look is if you define a [static_host_map](https://nebula.defined.net/docs/config/static-host-map/) entry for each other.

It is therefore clear that every host in the network should be able to connect to a lighthouse, for situations where there is only one lighthouse, limiting its connection via SecDom would be a serious mistake. However in Nebula it is possible to implement several lighthouses, in that case it might be possible. 
However, I think it is not a good practice for the simple reason that the main benefit in denying access to a lighthouse would only be useful for the purpose of redistributing the workload in the network but to do that nebula defines better tools through the config file, so it is not the job of SecDom to take care of that.
Little extra: nebula communicates with peer-to-peer encrypting, it is not possible to sniff the traffic passing through the lighthouse, also in case of an attack one could consider blocking certain hosts from communicating with the lighthouse but it is not the task of this project to handle such a case.

Final answer then is no, but practically speaking i can't block a user from putting a node called "lighthouse" in the config, maybe i should at least print some warning telling them it's not a good practice
##### What about scalability?
As the number of nodes increases, the complexity in the JSON file increases linearly as does the file creation time.
##### How to auto generate?
Using a linux script has several limitations:
- It is not easily portable to other platforms and/or architectures (if not impossible)
- it exploits "jq" a tool not necessarily present, in order to ensure execution it would require automatic installation and consequently sudo permission --> bad
- is monolithic
For the new version we will use a programming language that is distributable on different platforms and organized as much as possible in components.
My choice falls on Python for ease of use and familiarity.
##### Deployment of the files?
Each node in the network must have:
- a personal certificate key pair
- the CA's certificate (but not the key)
- the config file
- the nebula executable (or nebula installed)
Needs to deploy on linux, Freebsd, windows, macOS, iOS, android.
These issues are beyond the scope of this project and will not be addressed. 
([Defined Networking's Managed Nebula](https://www.defined.net/) 👀👀)

### Test
[[Vagrant/vagrant_esempio2_nebula/Vagrantfile|Vagrantfile]]
In this second case we will have 6 machines including 3 laptops in one SecDom, 2 servers in a different SecDom, and the lighthouse. Two of the three laptops must be able to connect with only one of the servers.
We are simulating a distributed server in a cluster of machines with one of them acting as a gate for some of the laptops.

### Design
In this case we need 3 security domains, one for the laptops, one for the servers and one for connecting to the server.
The configuration file ([[NebulaAppV2/securityDomains.json|securityDomains]]) is defined as follows:
```JSON
[
    {
        "name": "serverSD",
        "hosts": ["server1", "server2"]
    },

    {
        "name": "serverAccessSD",
        "hosts": ["server1", "laptop1", "laptop2"]
    },

    {
        "name": "laptopSD",
        "hosts": ["laptop1", "laptop2", "laptop3"]
    }
]
```

The main class mirrors the 5-point structure defined earlier to which a number of initial checks on parameters, files, and data are appended.
Almost all functions are placed in a try-catch construct to handle errors in the provided files.
[[NebulaAppV2/PythonCode/generateSD.py|generateSD.py]]
``` python
def main():
	
    #1 checks if files are correct
    checkParam()
    
       #load host configuration
    try:
        hostsSetupFile = open(sys.argv[1])
        hostsSetupData = json.load(hostsSetupFile)
    except:
        print("...") 
        exit(1)
	
       #load SecDom configuration
    try:
        securityDomainsFile = open(sys.argv[2])
        securityDomainsData = json.load(securityDomainsFile)
    except:
        print("...")
        exit(1)
	
       #checks if lighthouse is in a SecDom, if it is print a warning
    try:
        if SD.hasLightouse(securityDomainsData):   
            print("...")
    except:
        print("...")   
        exit(1)
    
       #checks for duplicate in name of hosts and in name of SD
    try:
        if SD.checkDuplicateSD(securityDomainsData):
            print("...")
            exit(1)
    except:
        ...
    
    try:
        if checkDuplicateHost(hostsSetupData):
            print("...")
            exit(1)
    except:
        ...
	
	
    #2 update groups data in host config files with SecDom configuration
    try:
        hostsSetupData = SD.merge(hostsSetupData, securityDomainsData)
        with open(sys.argv[1], 'w') as f:
            json.dump(hostsSetupData, f, ensure_ascii=False, indent=4)
    except:
        ...
	
	
    #3 key and crt generation for all hosts
    try:
        Gen.generateCrt(hostsSetupData)
    except:
        ...
	
	
    #4 generation and editing of all config files
    try:
        Gen.generateConf(hostsSetupData)
    except:
	    # can throw an exception if no lightouse is defined in configData
        print("could not find a lighthouse entry in " + sys.argv[1])
    try:
        SD.addFirewallRules(securityDomainsData)
    except:
        ...
	
	
    #5 distribution
    Dist.sendFiles(sys.argv[1])
```

NOTE: At this point I end up with two config files, one with the data containing the ip's and one with the security domains, in this case I have a way to merge the SecDom data into both files and have both options defined earlier to view the structure of my network. The perfect solution would be to completely abandon the manual generation of these files and switch to a software tool to define the entire network and hide the saved file formats from the end user while allowing them to access, view, and modify the information related to the network structure through the tool.

A library was defined to generate node data: [[NebulaAppV2/PythonCode/Generation.py|Generation.py]]
```python
scriptDir = "../scripts/"
outputDir = "../TmpFileGenerated/"
configFilePath = "../config-default.yaml"

def generateCrt(hostsSetupData):
    try:
        for host in hostsSetupData:
            if len(host["groups"]) == 0:
                os.system("./nebula-cert ...")
            else:
                os.system("./nebula-cert ...")
    except:
        raise Exception("Could not parse Data correctly")
```

```python
def generateConf(hostsSetupData):
    try:
        lighthouseIP = getLighthouseIP(hostsSetupData)
    except:
        raise Exception("No lighthouse found in config file")

    for host in hostsSetupData:
        #load YAML file
        yaml=YAML()   # default, if not specfied, is 'rt' (round-trip)
		...
		
        try:
            configFile = open(configFilePath)
            configData = yaml.load(configFile)
        except:
            print("...") 
            exit(1)

        #set data as needed
        if "lighthouse" in host["name"]:  #set lightouse config file
            lighthouseIP = host["nebula_ip"][:-3]
            lighthouseMachIP = host["machine_ip"]
            
            configData["static_host_map"] = {
                    DQSS(lighthouseIP): flist([DQSS(lighthouseMachIP + ":4242")])
                }           #cast to DoubleQuotedScalarString (DQSS) 
			
            configData["lighthouse"]["am_lighthouse"] = True
            configData["lighthouse"]["hosts"] = [DQSS(lighthouseIP)]
            configData["relay"]["am_relay"] = True
			...
            configData["firewall"]["inbound"] = [{'port': 'any', 'proto': 'any', 'host': 'any'}]  #connection with the lightouse is always allowed by default

        else:       #set host config file
            configData["static_host_map"] = {
                    DQSS(lighthouseIP): flist([DQSS(lighthouseMachIP + ":4242")])
                }
            configData["lighthouse"]["am_lighthouse"] = False
            configData["lighthouse"]["hosts"] = [DQSS(lighthouseIP)]
			
            configData["relay"] = {
                "relays": [DQSS(lighthouseIP)]
                }       
            configData["relay"]["am_relay"] = False    
            configData["relay"]["use_relays"] = True  
			 ...
            configData["firewall"]["inbound"] = []
            configData["firewall"]["inbound"].append({'port': 'any', 'proto': 'icmp', 'host':'any'})    # ping enabled by default in all the hosts 
		
        #save data in new file called config_HOSTNAME.yaml
        with open(outputDir + "config_" + host["name"] + ".yaml", 'w') as f:
            yaml.dump(configData, f)
```


A second library was defined to implement all SecDom-related functions: [[NebulaAppV2/PythonCode/SecurityDomain.py|SecurityDomain.py]]
``` python
def merge(hostsSetupData, securityDomainsData):
    try:
        for host in hostsSetupData:
            for secDom in securityDomainsData:
                if secDom["name"] in host["groups"]:                #if the SecDom is in the host group list, we check if it needs to be removed
                    if not host["name"] in secDom["hosts"]:
                        host["groups"].remove(secDom["name"])
                elif host["name"] in secDom["hosts"]:               #SecDom is added only if not already present
                    host["groups"].append(secDom["name"])
    except:
        raise Exception("...")
    return hostsSetupData
```
In the merge we pay attention to add a SecDom only if not already present and to remove SecDom in case they are not needed (for possible changes of a previous configuration)

```python
def getHostsList(securityDomainsData):
    try:
        hostsList = []
        for SecDom in securityDomainsData:
            for host in SecDom["hosts"]:
                if not host in hostsList:
                    hostsList.append(host)
        return hostsList
    except:
        raise Exception("...")


def addFirewallRules(securityDomainsData, hostsList = None):
    if hostsList == None:                                               
        try:                                                            
            hostsList = getHostsList(securityDomainsData)               
        except:
            raise Exception("Could not parse Data correctly")

    for host in hostsList:
        #open file as YAML
        yaml=YAML()
        ...
        try:
            configFile = open(outputDir + "config_" + host + ".yaml")
            configData = yaml.load(configFile)
        except:
            print("...") 
            exit(1)
        
        #save old inbound config
        oldConfig = configData["firewall"]["inbound"]                   
        #reset config                                                   
        configData["firewall"]["inbound"] = []
		
        #add rules
        for SecDom in securityDomainsData:
            if host in SecDom["hosts"]:
                configData["firewall"]["inbound"].append({'port': 'any', 'proto': 'any', 'group': SecDom["name"]})
        
        ...
		
		#save previous data if needed
        if not configData["firewall"]["inbound"]:
            configData["firewall"]["inbound"] = oldConfig
		
        #save data in new file
        with open(outputDir + "config_" + host + ".yaml", 'w') as f:
            yaml.dump(configData, f)
```
The optional hostList parameter is given because getHostList is not particularly efficient, there could be a better way of creating that list, the option is left to the programmer.
The list does not need to be limited to only hosts that are part of a SecDom but only host that are part of a SecDom as defined in config file will be considered obviously.

If a host is not part of any SecDom the current configuration should not be overwritten, to achieve this we first save the current inbound configuration and in the end we check if config is still empty, if it is it means the host is not part of any SecDom and we save the previously saved config.

### PROBLEM CASE: Mistrustful Colleagues
This new solution is a great advancement compared to the first shell script we had but it's not perfect, in this specific case for example what happens when we decide to have all the laptop able to connect to the server but not to each other? As of right now each and every laptop would need a specific Security Domain with the server.
In the next sprint we will face this problem and search for a possible solution.