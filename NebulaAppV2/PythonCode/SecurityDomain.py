import sys
from ruamel.yaml import YAML, CommentToken, error
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml import comments

outputDir = "../TmpFileGenerated/"

#IMPORTANTE, il merge deve tenere conto del fatto che potrebbe essere stato fatto un merge in precedenza e non dovrebbero esserci duplicazioni
def merge(hostsSetupData, securityDomainsData):
    try:
        for host in hostsSetupData:
            for secDom in securityDomainsData:
                if secDom["name"] in host["groups"]:
                    if not host["name"] in secDom["hosts"]:         #e se devo rimuovere qualcuno da un SecDom? come cambia il file con i grouppi?
                        host["groups"].remove(secDom["name"])
                elif host["name"] in secDom["hosts"]:
                    host["groups"].append(secDom["name"])
    except:
        raise Exception("Date provided can't be parsed correctly")
    
    return hostsSetupData



def hasLightouse(securityDomainsData):
    try:
        for SecDom in securityDomainsData:
            for string in SecDom["hosts"]:
                if "lighthouse" in string:
                    return True
        return False
    except:
        raise Exception("Could not parse Data correctly")


def getHostsList(securityDomainsData):
    hostsList = []

    for SecDom in securityDomainsData:
        for host in SecDom["hosts"]:
            if not host in hostsList:
                hostsList.append(host)

    #print(hostsList)
    return hostsList



def addFirewallRules(securityDomainsData, hostsList = None):
    
    if hostsList == None:
        hostsList = getHostsList(securityDomainsData)

    for host in hostsList:
        #print(host)

        #open file as YAML
        yaml=YAML()   # default, if not specfied, is 'rt' (round-trip)
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        yaml.sort_base_mapping_type_on_output = False
        yaml.indent(mapping=4, sequence=4, offset=2)

        try:
            configFile = open(outputDir + "config_" + host + ".yaml")
            configData = yaml.load(configFile)
        except:
            print("Could not load " + outputDir + "config_" + host + ".yaml" + " properly, are you shure it's a correctly defined YAML file?") 
            exit(1)
        
        #save old inbound config
        oldConfig = configData["firewall"]["inbound"]
        #reset config
        configData["firewall"]["inbound"] = []



        #add rules
        for SecDom in securityDomainsData:
            if host in SecDom["hosts"]:
                
                configData["firewall"]["inbound"].append({'port': 'any', 'proto': 'any', 'group': SecDom["name"]})    # ping enabled by default in all the hosts 
        
        #add newline between rules
        CS = comments.CommentedSeq
        configData["firewall"]["inbound"] = CS(configData["firewall"]["inbound"])
        configData["firewall"]["inbound"].yaml_set_comment_before_after_key(1, before='\n')




        #if config is still empty save old config
        if not configData["firewall"]["inbound"]:
            configData["firewall"]["inbound"] = oldConfig

        #yaml.dump(configData, sys.stdout)


        #save data in new file
        with open(outputDir + "config_" + host + ".yaml", 'w') as f:
            yaml.dump(configData, f)



def checkDuplicateSD(securityDomainsData):
    unique_SecDom = []
    for SecDom in securityDomainsData:
        if SecDom["name"] not in unique_SecDom:
            unique_SecDom.append(SecDom["name"])
        else:
            return True
    return False




