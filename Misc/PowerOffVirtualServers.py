__author__ = 'jonhall'
## POWEROFF VIRtUALGUESTS

import sys, getopt, socket, SoftLayer, json, string, configparser, os, argparse,csv, time

def initializeSoftLayerAPI(user, key, configfile):
    if user == None and key == None:
        if configfile != None:
            filename=args.config
        else:
            filename="config.ini"
        config = configparser.ConfigParser()
        config.read(filename)
        client = SoftLayer.Client(username=config['api']['username'], api_key=config['api']['apikey'])
    else:
        client = SoftLayer.Client(username=user, api_key=key)
    return client


## READ CommandLine Arguments and load configuration file
parser = argparse.ArgumentParser(description="PowerOffVirtualServers given a list of VSI ID's or fullyQualifiedDomainNames.")
parser.add_argument("-u", "--username", help="SoftLayer API Username")
parser.add_argument("-k", "--apikey", help="SoftLayer APIKEY")
parser.add_argument("-c", "--config", help="config.ini file to load")
parser.add_argument("-i", "--input", help="Outputfile")

args = parser.parse_args()

client = initializeSoftLayerAPI(args.username, args.apikey, args.config)

if args.input == None:
    filename=input("Filename of servers: ")
else:
    filename=args.input


## READ CSV FILE INTO PYTHON DICTIONARY
## FIELDS REQUIRED: ID, fullyQualifiedDomainName, WAIT
## ID = VM ID (found via SLCLI VS LIST) Leave empty to have script lookup by fullyQualifiedDomainName
## fullyQualifiedDomainName = SL fullyQualifiedDomainName (must be unique if you don't specify VM ID)
## WAIT = # of second to wait after powering on VM before moving to next VM
## Example csv file
## Order,id,fullyQualifiedDomainName,wait
## 1,13405579,centos02.ibmsldemo.com,60
## 2,13405577,centos0.ibmsldemo.com,30
## 3,13405581,centos03.ibmsldemo.com,30


## READ ACCOUNT LIST OF VIRTUAL GUESTS IN CASE ID ISN'T SPECIFIED
try:
    virtualGuests = client['Account'].getVirtualGuests(mask="id,fullyQualifiedDomainName,powerState.keyName")
except SoftLayer.SoftLayerAPIError as e:
    print("Error: %s, %s" % (e.faultCode, e.faultString))
    quit()

## OPEN CSV FILE TO READ LIST OF SERVERS TO SHUTDOWN
with open(filename, 'r') as csvfile:
    serverlist = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for server in serverlist:
        # IF ID isn't specified lookup ID by fullyQualifiedDomainName
        if server['id']=="":
            #Lookup ID
            for virtualGuest in virtualGuests:
                if server['fullyQualifiedDomainName']==virtualGuest['fullyQualifiedDomainName']:
                    vsiid=virtualGuest['id']
        else:
            vsiid=server['id']

        ## POWER OFF SERVERS SPECIFIED IN CSV FILE
        print ("Powering off server %s (%s)" % (server['fullyQualifiedDomainName'],vsiid))

        try:
            poweroff = client['Virtual_Guest'].powerOffsoft(id=vsiid)
        except SoftLayer.SoftLayerAPIError as e:
            print("Error: %s, %s" % (e.faultCode, e.faultString))

        ## WAIT FOR PERIOD SPECIFIED BEFORE PROCEEDING
        print ("Sleeping for %s seconds" % server['wait'])
        time.sleep(float(server['wait']))

