#!/usr/bin/env bash

# get enmapbox project
rm -rf context/enmapbox
git clone --recurse-submodules https://github.com/EnMAP-Box/enmap-box.git ./context/enmapbox
