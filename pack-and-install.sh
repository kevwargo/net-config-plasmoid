#!/bin/bash

plasmapkg -r net-config-switch
zip -r net-config-switch.zip net-config-switch/
plasmapkg -i net-config-switch.zip
