#!/bin/bash
make monitoring
sleep 0.5
make workers
sleep 4
make web-services
sleep 1
make mqtt-services
