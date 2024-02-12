import os
import sys
from ruamel.yaml import YAML, CommentToken, error
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml import comments

scriptDir = "../scripts/"
outputDir = "../TmpFileGenerated/"
configFilePath = "../config-default.yaml"

def generateCrt(hostsSetupData):
    os.chdir(scriptDir)
    for host in hostsSetupData:
        if len(host["groups"]) == 0:
            #./nebula-cert sign -name "server" -ip "192.168.100.9/24"
            os.system("./nebula-cert sign -name \"" + host["name"] + "\" -ip \"" + host["nebula_ip"] + "\"")
        else:
            #./nebula-cert sign -name "server" -ip "192.168.100.9/24" -groups "servers"
            os.system("./nebula-cert sign -name \"" + host["name"] + "\" -ip \"" + host["nebula_ip"] + "\" -groups \"" + ",".join(host["groups"]) + "\"")
        os.rename(host["name"]+".crt", outputDir + host["name"]+".crt")
        os.rename(host["name"]+".key", outputDir + host["name"]+".key")



def getLighthouseIP(hostSetupData):
    for host in hostSetupData:
        if "lighthouse" in host["name"]:
            return host["nebula_ip"][:-3]
    raise Exception("No lighthouse found in config file")



def flist(x):
    retval = comments.CommentedSeq(x)
    retval.fa.set_flow_style()  # fa -> format attribute
    return retval

def generateConf(hostsSetupData):

    try:
        lighthouseIP = getLighthouseIP(hostsSetupData)
    except:
        raise Exception("No lighthouse found in config file")

    for host in hostsSetupData:
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

            '''"nebula_ip": "192.168.100.1/24",
            "machine_ip": "192.168.1.10",'''

        #set data as needed
        if "lighthouse" in host["name"]:
            lighthouseIP = host["nebula_ip"][:-3]
            lighthouseMachineIP = host["machine_ip"]
                                                #  "192.168.100.1": ["192.168.1.10:4242"]
            configData["static_host_map"] = {
                    DoubleQuotedScalarString(lighthouseIP): flist([DoubleQuotedScalarString(lighthouseMachineIP + ":4242")])
                }
            configData["lighthouse"]["am_lighthouse"] = True
            configData["lighthouse"]["hosts"] = [DoubleQuotedScalarString(lighthouseIP)]
            configData["relay"]["am_relay"] = True

            ct = CommentToken('\n\n', error.CommentMark(0), None)
            configData["firewall"]["outbound"][0].ca.items['host'] = [None, None, ct, None]
            configData["firewall"]["inbound"] = [{'port': 'any', 'proto': 'any', 'host': 'any'}]        #connection with the lightouse is always allowed by default

        else:
            configData["static_host_map"] = {
                    DoubleQuotedScalarString(lighthouseIP): flist([DoubleQuotedScalarString(lighthouseMachineIP + ":4242")])
                }
            configData["lighthouse"]["am_lighthouse"] = False
            configData["lighthouse"]["hosts"] = [DoubleQuotedScalarString(lighthouseIP)]
            configData["relay"] = {
                "relays": [DoubleQuotedScalarString(lighthouseIP)]
                }
            configData["relay"]["am_relay"] = False
            configData["relay"]["use_relays"] = True
            ct = CommentToken('\n\n', error.CommentMark(0), None)
            configData["relay"] = comments.CommentedMap(configData["relay"])
            configData["relay"].ca.items["use_relays"] = [None, None, ct, None]

            ct = CommentToken('\n\n', error.CommentMark(0), None)
            configData["firewall"]["outbound"][0].ca.items['host'] = [None, None, ct, None]
            configData["firewall"]["inbound"] = []
            configData["firewall"]["inbound"].append({'port': 'any', 'proto': 'icmp', 'host':'any'})    # ping enabled by default in all the hosts 
            '''
            for group in host["groups"]:
                #configData["firewall"]["inbound"][-1] = comments.CommentedMap(configData["firewall"]["inbound"][-1])
                #configData["firewall"]["inbound"][-1].ca.items["group"] = [None, None, None, None]
                #print(configData["firewall"]["inbound"][-1].ca)
            CS = comments.CommentedSeq
            configData["firewall"]["inbound"] = CS(configData["firewall"]["inbound"])
            configData["firewall"]["inbound"].yaml_set_comment_before_after_key(1, before='\n')
            '''

        #yaml.dump(configData, sys.stdout)


        #save data in new file
        with open(outputDir + "config_" + host["name"] + ".yaml", 'w') as f:
            yaml.dump(configData, f)
