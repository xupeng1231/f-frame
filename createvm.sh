#!/bin/bash

set -e
set -x

if [ ${#} -ne 3 ];
then
	echo "need 3 args!"
	exit
fi

VNAME=${1} 
TEMPVDI=${2}
VRDEPORT=${3}
DISKPATH="/home/xupeng/vm-disks/$VNAME.vdi"

echo "copying vdi"
vboxmanage clonehd ${TEMPVDI} ${DISKPATH}
echo "copy finished"

vboxmanage createvm --name ${VNAME} --ostype "Windows7_64" --register

vboxmanage modifyvm ${VNAME} --memory 4096 --cpus 2

vboxmanage storagectl ${VNAME} --name "IDE Controller" --add ide --bootable on

vboxmanage storageattach ${VNAME} --storagectl "IDE Controller" --port 0 --device 0 --type hdd --medium ${DISKPATH} 

vboxmanage modifyvm ${VNAME} --vrde on

vboxmanage modifyvm ${VNAME} --vrdeport ${VRDEPORT}

vboxmanage modifyvm ${VNAME} --vrdeaddress 192.168.4.2

vboxmanage modifyvm ${VNAME} --vrdeauthtype null  

vboxmanage modifyvm ${VNAME} --vrdeauthlibrary default

echo "[MYSUCCESS666]"

#vboxmanage startvm ${VNAME} --type headless

