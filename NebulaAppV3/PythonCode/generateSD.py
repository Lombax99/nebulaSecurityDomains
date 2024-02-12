import json
import os
import sys
import Generation as Gen
import SecurityDomain as SD
import Distibution as Dist

def checkParam():
    #checks if parameters are given correctly
    if len(sys.argv) != 3:
        print("Usage: generateSD hostSetup.json securityDomains.json")
        exit(1) 
        
    #checks if files exists
    if not os.path.exists(sys.argv[1]):
        print(sys.argv[1] + " not found")
        exit(1)
    if len(sys.argv) == 3 and not os.path.exists(sys.argv[2]):
        print(sys.argv[2] + " not found")
        exit(1)


def checkDuplicateHost(hostsSetupData):
    try:
        unique_host = []
        for host in hostsSetupData:
            if host["name"] not in unique_host:
                unique_host.append(host["name"])
            else:
                return True
        return False
    except:
        raise Exception("Could not parse Data correctly")           #throws exception if data are not correctly defined

def main():

    #1 checks if files are correct
    checkParam()
    
        #load host configuration
    try:
        hostsSetupFile = open(sys.argv[1])
        hostsSetupData = json.load(hostsSetupFile)
    except:
        print("Could not load " + sys.argv[1] + " properly, are you shure it's a correctly defined JSON file?") 
        exit(1)

        #load SecDom configuration
    try:
        securityDomainsFile = open(sys.argv[2])
        securityDomainsData = json.load(securityDomainsFile)
    except:
        print("Could not load " + sys.argv[2] + " properly, are you shure it's a correctly defined JSON file?")
        exit(1)

        #checks if lighthouse is in a SecDom, if it is print a warning
    try:
        if SD.hasLightouse(securityDomainsData):                                #can throw exception if data can't be parsed correctly
            print()
            print("WARNING: a lighthouse was found in a security domain, this is not a good practice are you shure about your configuration?")
            print()
            print("Press Enter to continue execution...")
            input() 
    except:
        print("Could not parse securityDomains.json correctly")
        print("Usage: generateSD hostSetup.json securityDomains.json")     
        exit(1)
            
        #checks for duplicate in name of hosts and in name of SD
    try:
        if SD.checkDuplicateSD(securityDomainsData):                            #can throw exception if data can't be parsed correctly
            print("Found duplicate SecDom in " + sys.argv[2])
            print("SecDom name sould be unique")
            exit(1)
    except:
        print("Could not parse securityDomains.json correctly")
        print("Usage: generateSD hostSetup.json securityDomains.json")     
        exit(1)
    
    try:
        if checkDuplicateHost(hostsSetupData):                                  #can throw exception if data can't be parsed correctly
            print("Found duplicate host in " + sys.argv[1])
            print("Host's name sould be unique")
            exit(1)
    except:
        print("Could not parse hostSetup.json correctly")
        print("Usage: generateSD hostSetup.json securityDomains.json")     
        exit(1)


    #2 update groups data in host config files with SecDom configuration
    try:
        print("updating group data in " + sys.argv[1])
        hostsSetupData = SD.merge(hostsSetupData, securityDomainsData)          #can throw exception if data can't be parsed correctly
        with open(sys.argv[1], 'w') as f:
            json.dump(hostsSetupData, f, ensure_ascii=False, indent=4)
    except:
        print("Could not parse hostSetup.json correctly")
        print("Usage: generateSD hostSetup.json securityDomains.json")
        exit(1)


    #3 key and crt generation for all hosts
    try:
        print("generating crt and key")
        Gen.generateCrt(hostsSetupData)                                         #can throw exception if data can't be parsed correctly
    except:
        print("Could not parse securityDomains.json correctly")
        print("Usage: generateSD hostSetup.json securityDomains.json")
        exit(1)


    #4 generation and editing of all config files
    try:
        print("generating hosts' config file")
        Gen.generateConf(hostsSetupData)                                        #can throw an exception if no lightouse is defined in configData
    except:
        print("could not find a lighthouse entry in " + sys.argv[1])
    
    SD.addFirewallRules(securityDomainsData)
    try:
        print("settig SecDom firewall rules")
        #SD.addFirewallRules(securityDomainsData)
    except:
        print("Could not parse securityDomains.json correctly")
        print("Usage: generateSD hostSetup.json securityDomains.json")
        exit(1)


    #5 distribution
    Dist.sendFiles(sys.argv[1])



if __name__ == "__main__":
    main()


