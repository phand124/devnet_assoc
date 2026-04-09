# CCNA Automation 200-901 Labs #

This repository will be a workbook of labs for networking automation and management. Primarily will be built using ContainerLab topologies, but will include some CML automations for working with APIs as part of the exam objectives. 
This README.md is more a running thought and progress log while working through the labs, and less and instructional point of truth. 

## Baseline Test ##
Create a simple topology file for containerlab. 
Then create a script to pull from the file, and connect to devices to pull the version info. 
Script uses netmiko and yaml modules. 

### Refactor - LabTopology Class module ###
Working on refactor to streamline lab topology work. 
Class will contain methods for loading the correct topology file from the root of the project, parsing the YAML for the nodes, confirming the lab is running with `clab inspect`, and for establishing a connection. 
Baseline test used netmiko, most work will need to be built using NETCONF / RESTCONF. 
The connection method should check if the nodes are an IOL image or XE image, for using the appropriate connection method. 
The class definition will also allow for loading of the nested `.env` that should be in the same directory as the `.clab.yaml`.

## API Work ##
API work is consolidated within a directory within `scripts/`
Using the Star Wars API, https://swapi.info/api, built a simple script to use the `requests` module. 

### Flask example ###
A simple API using Flask, includes the following routes:
 - A basic GET to act as a Hello, World and returns a 200 - OK. 
 - A POST that includes data field requirements.
 - A protected route that uses Basic Auth. 

Postman was used for quickly testing and visualizing the API. 
The POST incorporates a separate Class. Format the JSON in the body of the message as raw data, and ensure the Content-Type is set to application/json 
This has some error checking, will return a 201 - Created on success, 400 - Bad Request for incomplete fields, and 500 - Internal Server Errror for any other exceptions. 

The protected route has multiple parts in order to walk through all the steps required to check authentication. 
You essential wrap the checks in a decorator function that is able to be passed to the specified route. 

## Netconf / YANG Models / RESTCONF ##
Mostly used in SDN controller software, not scripts that are meant to control devices directly, though can be used.  YANG data models are best located on https://netconfcentral.org to narrow down the correct source for the model in question.  Uses SSH for transport with a defualt port of 830.

Netconf uses XML to parse data according to the appropriate YANG model. Some examples added in corresponding directory under `scripts/`. Netconf relies on RPC calls and primarily uses the following messages:
- `get`
- `get-config`
- `edit-config`

Noteable Python modules necessary for NetCONF scriting are:
- `pyang` - Used to validate YANG models according to RFCs 6020, 7950, and 6110. 
- `ncclient` - Used to establish and manage NETCONF connections to devices. 


Note: The example scripts  listed were provided by CBT Nugget for demonstration purposes. 

### RESTCONF ###
RESTCONF uses HTTP(s) for transport. RESTCONF can also pass JSON payloads, but defaults to XML.
JSON needs to be specified in the headers, `Content-Type` to send and `Accept` to recieve. 

Since RESTCONF uses a RESTful API, you can use Postman for queries. 
`https://<IP>/restconf/data/module:container` in genral as the base URL. 

Used Devnet Sandbox to poll the Always On Cat8000 unit. - 443 was blocked outisde of the box, so this was a failure.

## ACI and APIC ##
Set up a `uv workspace` in order to load and work with the ACIToolkit SDK in the corresponding directory of the project. 
Have to link the main `pyproject.toml` to the one created within the workspace directory. 

#WIP - unable to connect to sandbox when labbing.
Want to get tenants up to 15, and then create a tenant with a hand ful of MOs, then cleanup. 
