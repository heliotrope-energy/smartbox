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

cd ../src
install_dir=/opt/heliotrope
echo "Making install directory at "$install_dir
mkdir -p $install_dir

if [ ! -w $install_dir ]; then
	echo "The user "$USER" does not have permissions to write to /opt/heliotrope. Please fix permissions before continuing"
	exit
fi


cp -rv smartbox /opt/heliotrope/
cp -rv smartbox_gui /opt/heliotrope/
cp -rv smartbox_cli /opt/heliotrope/

if [[ $PYTHONPATH != *"$install_dir"* ]]; then
  	echo 'Adding '$install_dir' to PYTHONPATH'
	echo 'export PYTHONPATH=$PYTHONPATH:'$install_dir > ~/.bashrc
	export PYTHONPATH=$PYTHONPATH:$install_dir
fi
