# CCNA Automation 200-901 Labs #

This repository will be a workbook of labs for networking automation and management. Primarily will be built using ContainerLab topologies, but will include some CML automations for working with APIs as part of the exam objectives. 
This README.md is more a running thought and progress log while working through the labs, and less and instructional point of truth. 

## Baseline Test ##
Create a simple topology file for containerlab. 
Then create a script to pull from the file, and connect to devices to pull the version info. 
Script uses netmiko and yaml modules. 

## Refactor - LabTopology Class module##
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

