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

git pull
if [[ $PYTHONPATH = *"/opt/heliotrope"* ]];then
	cd ../..
	export PYTHONPATH=$PWD
	echo "Update PYTHONPATH for development"
fi
