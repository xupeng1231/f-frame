#!/usr/bin/python

from subprocess import Popen,PIPE
import sys
import re
import datetime
import os
import traceback

def log(log_text):
    log_path = os.path.join("/home/xupeng/xuzz", "log.txt")
    try:
        with open(log_path, "at") as log_file:
            log_file.write("[%s]   %s\n" % (datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), log_text))
    except:
        traceback.print_exc()


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

def listrunningvms():
    p=Popen(args=["vboxmanage","list","runningvms"],stdout=PIPE,stderr=PIPE)
    p.wait()
    vms_outs=p.stdout.read()
    regex=r"\"(.*)\"\s\{[a-z0-9]{8}\-(?:[a-z0-9]{4}\-){3}[a-z0-9]{12}\}"
    res=re.finditer(regex,vms_outs)
    vms=[]
    for m in res:
        vms.append(m.group(1))
    return vms

def createvm(vname, vdipath, port):
    vms=listvms()
    if vname in vms:
        return False
    p=Popen(args=["./createvm.sh",vname,vdipath,str(port)],stdout=PIPE,stderr=PIPE)
    p.wait()
    outs=p.stdout.read()
    if outs.find("[MYSUCCESS666]")>=0:
        return True
    return False

def removevm(vname):
    p=Popen(args=["vboxmanage","unregistervm",vname,"--delete"],stdout=PIPE,stderr=PIPE)
    p.wait()
    outs=p.stderr.read()
    if outs.find("100%")>=0:
        return True
    return False

def startvm(vname):
    log("vbutils::startvm %s ..."%(vname,))
    p=Popen(args=["vboxmanage","startvm",vname,"--type","headless"],stdout=PIPE,stderr=PIPE)
    p.wait()
    outs=p.stdout.read()
    if outs.find("successfully started.")>=0:
        log("vbutils::startvm %s finish:%s" % (vname,"True"))
        return True
    log("vbutils::startvm %s finish:%s" % (vname, "False"))
    return False

def stopvm(vname):
    p=Popen(args=["vboxmanage","controlvm",vname,"poweroff"],stdout=PIPE,stderr=PIPE)
    p.wait()
    outs=p.stdout.read()
    if outs.find("100%")>=0:
        return True
    else:
        p=Popen(args=["vboxmanage","startvm",vname,"--type","emergencystop"],stdout=PIPE,stderr=PIPE)
        p.wait()
        outs=p.stdout.read()
        outs1=p.stderr.read()
        if len(outs)>0 or len(outs1)>0:
            return False
    return True

if "__main__"==__name__:
    for vm in listrunningvms():
        print "stop %s"%(vm,),stopvm(vm)
    for vm in listvms():
        print "remove %s"%(vm,),removevm(vm)
    for i in range(0,16):
        vname="fuzzer-"+str(i)
        print "create %s"%(vname,),createvm(vname,"/home/xupeng/xupeng/fuzz-vdi/v1-win7-64bit-profesional.vdi",20600+i)
        print "start %s"%(vname,),startvm(vname)
