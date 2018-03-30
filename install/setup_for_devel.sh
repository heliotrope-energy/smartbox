#!/bin/bash

set -o pipefail
if [ "$EUID" = 0 ]; then
	echo "Do not run this install script as root. Fix permissions as needed"
	exit
fi

if [[ $PWD != *"smartbox/install"* ]]; then
	echo "Please run this file from the install directory"
	exit
fi
echo "Pulling files from github"
git pull
if [[ $PYTHONPATH = *"/opt/heliotrope"* ]];then
	cd ../src
	echo "Update PYTHONPATH for development"
fi
if [[ $PYTHONPATH != *"smartbox/src"* ]]; then
	cd ../src
	export PYTHONPATH=$PWD:$PWD/smartbox_msgs
fi
