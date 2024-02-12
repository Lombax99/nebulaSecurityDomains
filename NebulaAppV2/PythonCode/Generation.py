import os
from ruamel.yaml import YAML, CommentToken, error
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml import comments

scriptDir = "../scripts/"
outputDir = "../TmpFileGenerated/"
configFilePath = "../config-default.yaml"

def generateCrt(hostsSetupData):
    try:
        os.chdir(scriptDir)
        for host in hostsSetupData:
            if len(host["groups"]) == 0:
                          #./nebula-cert sign -name "server" -ip "192.168.100.9/24"
                os.system("./nebula-cert sign -name \"" + host["name"] + "\" -ip \"" + host["nebula_ip"] + "\"")
            else:
                          #./nebula-cert sign -name "server" -ip "192.168.100.9/24" -groups "servers"
                os.system("./nebula-cert sign -name \"" + host["name"] + "\" -ip \"" + host["nebula_ip"] + "\" -groups \"" + ",".join(host["groups"]) + "\"")
            #move file to specific directory
            os.rename(host["name"]+".crt", outputDir + host["name"]+".crt")
            os.rename(host["name"]+".key", outputDir + host["name"]+".key")
    except:
        raise Exception("Could not parse Data correctly")           #throws exception if data are not correctly defined



def getLighthouseIP(hostSetupData):
    for host in hostSetupData:
        if "lighthouse" in host["name"]:
            return host["nebula_ip"][:-3]
    raise Exception("No lighthouse found in config file")



# allows dump of list with squared brakets in yaml file --> "192.168.100.1": ["192.168.1.10:4242"]
def flist(list):
    retval = comments.CommentedSeq(list)
    retval.fa.set_flow_style()  # fa -> format attribute
    return retval

def generateConf(hostsSetupData):

    try:
        lighthouseIP = getLighthouseIP(hostsSetupData)              #find lighthouse virtual ip first in case lighthouse is not the first defined host in config file
    except:                                                         #lighthouse virtual ip is needed in all config files of any host
        raise Exception("No lighthouse found in config file")

    for host in hostsSetupData:

        #load YAML file
        yaml=YAML()   # default, if not specfied, is 'rt' (round-trip)
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        yaml.sort_base_mapping_type_on_output = False
        yaml.indent(mapping=4, sequence=4, offset=2)
        try:
            configFile = open(configFilePath)
            configData = yaml.load(configFile)
        except:
            print("Could not load " + configFilePath + " properly, are you shure it's a correctly defined YAML file?") 
            exit(1)

        #set data as needed
        if "lighthouse" in host["name"]:                                                                #set lightouse config file
            lighthouseIP = host["nebula_ip"][:-3]
            lighthouseMachineIP = host["machine_ip"]
                              
            configData["static_host_map"] = {                                                           #set static_host_map:  "192.168.100.1": ["192.168.1.10:4242"]
                    DoubleQuotedScalarString(lighthouseIP): flist([DoubleQuotedScalarString(lighthouseMachineIP + ":4242")])
                }                                                                                       #cast to DoubleQuotedScalarString to print string within double quotes
            configData["lighthouse"]["am_lighthouse"] = True
            configData["lighthouse"]["hosts"] = [DoubleQuotedScalarString(lighthouseIP)]
            configData["relay"]["am_relay"] = True

            ct = CommentToken('\n\n', error.CommentMark(0), None)                                       #this two lines are to print the empty line
            configData["firewall"]["outbound"][0].ca.items['host'] = [None, None, ct, None]             #between outbound and inbound rules

            configData["firewall"]["inbound"] = [{'port': 'any', 'proto': 'any', 'host': 'any'}]        #connection with the lightouse is always allowed by default

        else:                                                                                           #set host config file
            configData["static_host_map"] = {
                    DoubleQuotedScalarString(lighthouseIP): flist([DoubleQuotedScalarString(lighthouseMachineIP + ":4242")])
                }
            configData["lighthouse"]["am_lighthouse"] = False
            configData["lighthouse"]["hosts"] = [DoubleQuotedScalarString(lighthouseIP)]

            configData["relay"] = {                                                                     #recreate configData["relay"] to have "relays"
                "relays": [DoubleQuotedScalarString(lighthouseIP)]                                      #as the first element
                }                                                                                       #
            configData["relay"]["am_relay"] = False                                                     #"am_relay" and "use_relay"
            configData["relay"]["use_relays"] = True                                                    #redefined as default value

            ct = CommentToken('\n\n', error.CommentMark(0), None)                                       #this three lines are to print an empty line
            configData["relay"] = comments.CommentedMap(configData["relay"])                            #between "use_relay" and "tun"
            configData["relay"].ca.items["use_relays"] = [None, None, ct, None]                         #

            ct = CommentToken('\n\n', error.CommentMark(0), None)                                       #print empty line between
            configData["firewall"]["outbound"][0].ca.items['host'] = [None, None, ct, None]             #outbound rules and inbound rules
            configData["firewall"]["inbound"] = []                                                      #
            configData["firewall"]["inbound"].append({'port': 'any', 'proto': 'icmp', 'host':'any'})    # ping enabled by default in all the hosts 

        #save data in new file called config_HOSTNAME.yaml
        with open(outputDir + "config_" + host["name"] + ".yaml", 'w') as f:
            yaml.dump(configData, f)
