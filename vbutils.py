#!/usr/bin/python

from subprocess import Popen,PIPE
import sys
import re

def listvms():
	p=Popen(args=["vboxmanage","list","vms"],stdout=PIPE,stderr=PIPE)
	p.wait()
	vms_outs=p.stdout.read()
	regex=r"\"(.*)\"\s\{[a-z0-9]{8}\-(?:[a-z0-9]{4}\-){3}[a-z0-9]{12}\}"
	res=re.finditer(regex,vms_outs)
	vms=[]
	for m in res:
		vms.append(m.group(1))
	return vms

def removevm(vname):
	p=Popen(args=["vboxmanage","unregistervm",vname,"--delete"],stdout=PIPE,stderr=PIPE)
	p.wait()
	outs=p.stdout.read()
	if outs.find("100%")>=0:
		return True
	return False

def createvm(vname, vdipath, port):
	p=Popen(args=["./createvm.sh",vname,vdipath,str(port)],stdout=PIPE,stderr=PIPE)
	p.wait()
	outs=p.stdout.read()
	if outs.find("[MYSUCCESS666]")>=0:
		return True
	return False

def removeallvms():
	for vname in listvms():
		if removevm(vname):
			print "remove %s success!"%(vname,)
		else:
			print "remove %s failed!"%(vname,)

def stopvm(vname):
	p=Popen(args=["vboxmanage","controlvm",vname,"poweroff"],stdout=PIPE,stderr=PIPE)
	p.wait()
	outs=p.stdout.read()
	if outs.find("100%")>=0:
		return True
	else:
		p=Popen(args=["vboxmanage","startvm",vname,"emergencystop"],stdout=PIPE,stderr=PIPE)
	        p.wait()
        	outs=p.stdout.read()
		outs1=p.stderr.read()
		if len(outs)>0 or len(outs1)>0:
			return False
	return True
	
if "__main__"==__name__:
	#print listvms()
	#print removevm("test8")
	#print createvm("test16","/home/xupeng/xupeng/v1-win7-64bit-profesional.vdi",20106)
	removeallvms()
