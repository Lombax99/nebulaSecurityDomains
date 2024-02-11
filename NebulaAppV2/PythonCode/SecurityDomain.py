import sys

#IMPORTANTE, il merge deve tenere conto del fatto che potrebbe essere stato fatto un merge in precedenza e non dovrebbero esserci duplicazioni
def merge(hostsSetupData, securityDomainsData):
    try:
        for host in hostsSetupData:
            for secDom in securityDomainsData:
                if secDom["name"] in host["groups"]:
                    break
                elif host["name"] in secDom["hosts"]:
                    host["groups"].append(secDom["name"])
    except:
        raise Exception("Date provided can't be parsed correctly")
    
    return hostsSetupData

    #e se devo rimuovere qualcuno da un SecDom? come cambia il file con i grouppi?


def addFirewallRules():
    pass