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

