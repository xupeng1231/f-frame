#!/bin/bash


if [ ${#} -ne 1 ];
then
	echo "must 1 arg!!"
	exit
fi

set -e
set -x

vname=${1}

vboxmanage unregistervm ${vname} --delete
