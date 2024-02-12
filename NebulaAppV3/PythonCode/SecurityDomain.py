import sys
from ruamel.yaml import YAML, CommentToken, CommentedMap, error
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml import comments

outputDir = "../TmpFileGenerated/"


def merge(hostsSetupData, securityDomainsData):
    try:
        for host in hostsSetupData:
            for secDom in securityDomainsData:
                if secDom["name"] in host["groups"]:                #if the SecDom is in the host group list, we check if it needs to be removed
                    if not any(secDomHost['name'] == host["name"] for secDomHost in secDom["hosts"]):
                        host["groups"].remove(secDom["name"])
                elif any(secDomHost['name'] == host["name"] for secDomHost in secDom["hosts"]):              #SecDom is added only if not already present
                    host["groups"].append(secDom["name"])
    except:
        raise Exception("Date provided can't be parsed correctly")  #throws exception if data are not correctly defined
    
    return hostsSetupData



def hasLightouse(securityDomainsData):
    try:
        for SecDom in securityDomainsData:
            for string in SecDom["hosts"]:
                if "lighthouse" in string:
                    return True
        return False
    except:
        raise Exception("Could not parse Data correctly")           #throws exception if data are not correctly defined
    


def getHostsList(securityDomainsData):                              #return a list of all hosts that are in at least one SecDom
    try:
        hostsList = []
        for SecDom in securityDomainsData:
            for host in SecDom["hosts"]:
                if not host["name"] in hostsList:
                    hostsList.append(host["name"])

        return hostsList
    except:
        raise Exception("Could not parse Data correctly")           #throws exception if data are not correctly defined



def addFirewallRules(securityDomainsData, lighthouseName = "lighthouse", hostsList = None):            #optional hostList parameter, getHostList function is not the best, there could be a better way
    if hostsList == None:                                               #of creating that list, the option is left to the programmer.
        try:                                                            #The list does not need to be limited to only hosts that are part of a SecDom
            hostsList = getHostsList(securityDomainsData)               #Only host that are part of a SecDom as defined in config file will be considered obviously
        except:
            raise Exception("Could not parse Data correctly")           #throws exception if data are not correctly defined

    for host in hostsList:
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
        oldInboundConfig = configData["firewall"]["inbound"]                   #if the host is not part of any SecDom the current inbound configuration should not be overwritten
        #reset config                                                          #we overwrite all files and store the previous config in case the host is not part of any SecDom
        configData["firewall"]["inbound"] = []
        

        #save old inbound config
        oldOutboundConfig = configData["firewall"]["outbound"]                 #now the same applies to outbound rules
        #reset config                                                          #
        configData["firewall"]["outbound"] = []
        configData["firewall"]["outbound"].append({'port': 'any', 'proto': 'any', 'ca_name': lighthouseName})     #allow outbound message to lighthouse

        #add inbound rules
        for SecDom in securityDomainsData:
            for SecDomHost in SecDom["hosts"]:
                if host == SecDomHost["name"]:
                    if SecDomHost["role"] == "sender":
                        configData["firewall"]["inbound"].append({'port': 'any', 'proto': 'icmp', 'group': SecDom["name"]})     #for inbound of "SenderOnly" we allow ping only
                        configData["firewall"]["outbound"].append({'port': 'any', 'proto': 'any', 'group': SecDom["name"]})     #for outbound of "SenderOnly" we allow any sending
                    elif SecDomHost["role"] == "receiver":
                        configData["firewall"]["inbound"].append({'port': 'any', 'proto': 'any', 'group': SecDom["name"]})      #for inbound of "ReceiverOnly" configuration is the same, for outbound no sendings are allowed
                    else:
                        configData["firewall"]["inbound"].append({'port': 'any', 'proto': 'any', 'group': SecDom["name"]})      #for inbound of "Both" configuration is the same
                        configData["firewall"]["outbound"].append({'port': 'any', 'proto': 'any', 'group': SecDom["name"]})     #for outbound of "Both" we allow any sending
        
        #add newline between set of rules
        configData["firewall"]["inbound"] = comments.CommentedSeq(configData["firewall"]["inbound"])
        configData["firewall"]["inbound"].yaml_set_comment_before_after_key(1, before='\n')

        #add newline between set of rules
        configData["firewall"]["outbound"] = comments.CommentedSeq(configData["firewall"]["outbound"])
        configData["firewall"]["outbound"].yaml_set_comment_before_after_key(1, before='\n')

        #if config is still empty it means the host is not part of any SecDom and we save the previous config
        if not configData["firewall"]["inbound"]:
            configData["firewall"]["inbound"] = oldInboundConfig
        #if outbound config only has lighthouse rules it means the host is not part of any SecDom and we save the previous config
        if len(configData["firewall"]["outbound"]) == 1 :
            configData["firewall"]["outbound"] = oldOutboundConfig
        else:
            ct = CommentToken('\n\n', error.CommentMark(0), None)                                                   #print empty line between
            configData["firewall"]["outbound"][-1] = CommentedMap(configData["firewall"]["outbound"][-1])           #outbound rules and inbound rules
            configData["firewall"]["outbound"][-1].ca.items['group'] = [None, None, ct, None]                       #

        #save data in new file
        with open(outputDir + "config_" + host + ".yaml", 'w') as f:
            yaml.dump(configData, f)



def checkDuplicateSD(securityDomainsData):
    try:
        unique_SecDom = []
        for SecDom in securityDomainsData:
            if SecDom["name"] not in unique_SecDom:
                unique_SecDom.append(SecDom["name"])
            else:
                return True
        return 
    except:
        raise Exception("Could not parse Data correctly")           #throws exception if data are not correctly defined




