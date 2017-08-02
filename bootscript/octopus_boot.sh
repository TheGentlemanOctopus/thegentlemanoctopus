#!/bin/bash

#echo 'boot script test' >> /home/odroid/boottestcron.txt
cd ../octopus_code

python run.py --config tgo_hw.ini --layout core/octopus/layouts/octopusLayout.json --timeout 10 
