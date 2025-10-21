#!/bin/bash
# Script to test the consang binary in the distribution folder
# It builds the distribution first, then runs ged2gwb to convert a GEDCOM file,
# and finally runs consang on the generated database.

make distrib-python > /dev/null 2>&1
cd "/home/nico/Dev/Legacy/geneweb/distribution/bases"
../gw/ged2gwb -f /home/nico/Dev/Legacy/geneweb/src/python/gedcom/ged/uk.ged -o uk > /dev/null 2>&1
cd "/home/nico/Dev/Legacy/geneweb/distribution/bases"
../gw/consang -q uk