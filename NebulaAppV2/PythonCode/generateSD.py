import json
import os
import sys
import Generation as Gen
import SecurityDomain as SD
import Distibution as Dist


TEST = False

def checkParam():
    #a check if parameters are given correctly
    if len(sys.argv) != 3:
        print("Usage: generateSD hostSetup.json securityDomains.json")
        exit(1) 
        
    #b check if files exists
    if not os.path.exists(sys.argv[1]):
        print(sys.argv[1] + " not found")
        exit(1)
    if len(sys.argv) == 3 and not os.path.exists(sys.argv[2]):
        print(sys.argv[2] + " not found")
        exit(1)


def checkDuplicateHost(hostsSetupData):
    unique_host = []
    for host in hostsSetupData:
        if host["name"] not in unique_host:
            unique_host.append(host["name"])
        else:
            return True
    return False


def main():

    '''
    The workflow of the system can be defined with the following points:
    1) The Security Domain config file is created
    2) Certification and Keys are created for every node of the network
    3) Configuration files are created for every host
    4) Configuration files are modified to implements Security Domain logic
    5) Distribution to all the nodes
    '''

    #1 checking if file is correct
    checkParam()
    
    #c check if hostsSetup file opens correctly and is a json file
    try:
        hostsSetupFile = open(sys.argv[1])
        hostsSetupData = json.load(hostsSetupFile)      #this is now a list
    except:
        print("Could not load " + sys.argv[1] + " properly, are you shure it's a correctly defined JSON file?") 
        exit(1)

    #c check if securityDomains file opens correctly and is a json file
    try:
        securityDomainsFile = open(sys.argv[2])
        securityDomainsData = json.load(securityDomainsFile)
    except:
        print("Could not load " + sys.argv[2] + " properly, are you shure it's a correctly defined JSON file?")
        exit(1)

    #d check if lighthouse is in a SecDom, in caso positivo lanciare un warning
    try:
        if SD.hasLightouse(securityDomainsData):
            print()
            print("WARNING: a lighthouse was found in a security domain, this is not a good practice are you shure about your configuration?")
            print()
            print("Press Enter to continue execution...")
            input() 
    except:
        print("Could not parse securityDomains.json correctly")
        print("Usage: generateSD hostSetup.json securityDomains.json")     
        exit(1)



    #2 merging dei dati nei due file per generare un solo file di config da usare per tutto il processo
    
    #come gestisco il merge? Non ha senso farlo ogni volta, ha senso farlo solo se il file è stato cambiato in qualche modo
    #in questo caso per non complicarmi la vita lo farò fare ad una funzione che viene lanciata ogni volta
    #in futuro potrebbe essere utile implementare una logica che decida se lanciare questa funzione o meno
            
    #e check for double in name of hosts (should be case insensitive?) and in name of SD !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if SD.checkDuplicateSD(securityDomainsData):
        print("Found duplicate SecDom in " + sys.argv[2])
        print("SecDom name sould be unique")
        exit(1)

    if checkDuplicateHost(hostsSetupData):
        print("Found duplicate host in " + sys.argv[1])
        print("Host's name sould be unique")
        exit(1)

    try:
        hostsSetupData = SD.merge(hostsSetupData, securityDomainsData)
        with open(sys.argv[1], 'w') as f:
            json.dump(hostsSetupData, f, ensure_ascii=False, indent=4)
    except:
        print("Could not parse hostSetup.json correctly")
        print("Usage: generateSD hostSetup.json securityDomains.json")
        exit(1)



    #3 generazione di key e crt per tutti gli host
    Gen.generateCrt(hostsSetupData)



    #4 generazione e modifica di tutti i file di config
    try:
        Gen.generateConf(hostsSetupData)
    except:
        print("could not find a lighthouse entry in " + sys.argv[1])


    # NOTE: cosa succede se voglio portare questo script in un'altra applicazione che non usa il file di conf degli host singoli?
    SD.addFirewallRules(securityDomainsData)



    #5 distribution
    Dist.sendFiles(sys.argv[1])



if __name__ == "__main__":
    main()


