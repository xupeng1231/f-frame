#!/usr/bin/python
import time
import redis
import vbutils
import traceback
import threading
import os
import hashlib
import datetime

pool=redis.ConnectionPool(host="192.168.4.2",port=6379,decode_response=True)
hash=hashlib.md5()


def log(log_text):
    log_path = os.path.join(Fuzzer.base_dir, "log.txt")
    try:
        with open(log_path, "at") as log_file:
            log_file.write("[%s]   %s\n" % (datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), log_text))
    except:
        traceback.print_exc()

class Machine:
    def __init__(self,name):
        self.name=name

    def init_run(self):
        try:
            r=redis.Redis(connection_pool=pool)
            r.set("thisvname",self.name)
            self.run()
            time.sleep(60)
            for _ in range(48):
                if None == r.get("thisvname"):
                    return True
                time.sleep(5)
            r.delete("thisvname")
        except:
            traceback.print_exc()
            self.stop()
            return False
    def run(self):
        if not self.running:
            t=threading.Thread(target=vbutils.startvm,args=(self.name,))
            t.setDaemon(True)
            t.start()
            time.sleep(6)
        return self.running

    def stop(self):
        if self.running:
            t=threading.Thread(target=vbutils.stopvm,args=(self.name,))
            t.setDaemon(True)
            t.start()
            time.sleep(6)
        return not self.running

    def restart(self):
        self.stop()
        time.sleep(10)
        self.run()
        time.sleep(30)
        for _ in range(30):
            if self.alive:
                break
            time.sleep(3)
        return self.alive

    def destroy(self):
        t = threading.Thread(target=vbutils.removevm, args=(self.name,))
        t.setDaemon(True)
        t.start()

    @property
    def alive(self):
        return int(float(time.time()))+ 60 - self.beat <= 600

    @property
    def running(self):
        return self.name in vbutils.listrunningvms()

    @property
    def exist(self):
        return self.name in vbutils.listvms()

    @property
    def beat(self):
        for _ in range(2):
            try:
                r = redis.Redis(connection_pool=pool)
                beat=r.get(self.name)
                if None == beat:
                    return 0
                else:
                    return int(float(r.get(self.name)))
            except:
                traceback.print_exc()
        return 0



class Fuzzer:
    crash_dir = "\\home\\xupeng\\xuzz\\crashes"
    base_dir = "\\home\\xupeng\\xuzz"
    port_base = 20800
    vdi_path=""dfddf
    create_vm_lock=threading.Lock()

    def __init__(self,max_runnings=8):

        self.machine_daemon=None
        self.crash_daemon=None
        self.info_daemon=None

        self.max_runnings=max_runnings
        self.workings=[]
        self.vms={}
        for vname in vbutils.listvms():
            if vname.find("fuzz")>=0:
                self.vms[vname]=Machine(name=vname)

        if not os.path.exists(Fuzzer.base_dir):
            os.makedirs(Fuzzer.base_dir)
        if not os.path.exists(Fuzzer.crash_dir):
            os.makedirs(Fuzzer.crash_dir)

        self.log("__init__ finish")

    def start_fuzz(self):
        log("start_fuzz ...")
        for vname in self.vms.keys()[0:self.max_runnings]:
            log("\tinit run [%s] ..."%(vname,))
            status=self.vms[vname].init_run()
            log("\tinit run [%s] finish:%s" % (vname,str(status)))
            self.workings.append(vname)
        self.machine_daemon=threading.Thread(target=self.daemon_machine,daemon=True)
        self.crash_daemon=threading.Thread(target=self.daemon_crash,daemon=True)
        self.info_daemon=threading.Thread(target=self.daemon_info,daemon=True)
        self.machine_daemon.start()
        self.crash_daemon.start()
        self.info_daemon.start()
        log("start_fuzz finish")

    def daemon_machine(self):
        while True:
            time.sleep(180)
            log("machine daemon alive ...")
            paralysises=[]
            for vname in self.workings:
                if not self.vms[vname].alive:
                    log("\trestart %s ..."%(vname,))
                    index=self.workings.index(vname)
                    if index in range(len(self.workings)):
                        del self.workings[index]
                    if vname not in paralysises:
                        paralysises.append(vname)
                    status=self.vms[vname].restart()
                    log("\trestart %s finish:%s"%(vname,str(status)))

            for vname in paralysises:
                if self.vms[vname].alive:
                    if vname not in self.workings:
                        self.workings.append(vname)
                    log("\t%s alive!"%(vname,))
                else:
                    if vname in self.workings:
                        index=self.workings.index(vname)
                        del self.workings[index]

                    if vname in self.vms.keys():
                        self.vms[vname].destroy()
                        del self.vms[vname]

                    log("\tdestroy %s"%(vname,))

            self.keep_vm_num()

    def keep_vm_num(self):
        if len(self.workings) < self.max_runnings:
            for vname in self.vms.keys():
                if vname in self.workings:
                    continue
                log("\tinit run [%s] ..." % (vname,))
                status = self.vms[vname].init_run()
                log("\tinit run [%s] finish:%s" % (vname, str(status)))
                self.workings.append(vname)

        if len(self.workings) < self.max_runnings:
            self.create_vm()


    def create_vm(self):
        Fuzzer.create_vm_lock.acquire()
        vname="fuzzer-"
        port=Fuzzer.port_base
        for i in range(1,1000):
            if vname+str(i) not in self.vms.keys():
                vname+=str(i)
                port+=i
                break
        log("create vm %s %s ..."%(vname,str(port)))
        status=False
        try:
            status=vbutils.createvm(vname,Fuzzer.vdi_path,port)
        except:
            traceback.print_exc()
        log("create vm %s %s finish:%s" % (vname, str(port),str(status)))
        if status:
            self.vms[vname]=Machine(name=vname)

            Fuzzer.create_vm_lock.release()
            return vname
        else:
            try:
                vbutils.removevm(vname)
            except:
                traceback.print_exc()

            Fuzzer.create_vm_lock.release()
            return None


    def daemon_crash(self):
        while True:
            time.sleep(300)
            log("crash daemon alive ...")
            if not os.path.exists(Fuzzer.crash_dir):
                os.makedirs(Fuzzer.crash_dir)
            try:
                r=redis.Redis(connection_pool=pool)
                crash_num=r.llen("crashes")
                log("\tcrash num:%s"%(str(crash_num),))
                if crash_num > 0:
                    for i in range(crash_num):
                        crash_string=r.lpop("crashes")
                        hash.update(crash_string)
                        crash_md5=hash.hexdigest()
                        log("\t\tsave crash file %s"%(crash_md5,))
                        with open(os.path.join(Fuzzer.crash_dir,crash_md5),"wb") as crash_file:
                            crash_file.write(crash_string)
            except:
                traceback.print_exc()

    def daemon_info(self):
        while True:
            time.sleep(20)
            log("info daemon alive ...")
            try:
                r=redis.Redis(connection_pool=pool)
                crashes_md5=[]
                md5_num = r.llen("crashes_md5")
                for i in range(md5_num):
                    crashes_md5.append(r.lindex("crashes_md5",i))
                log("\tworkings: %s" % (str(self.workings),))
                log("\tbeats: %s"%(str(self.beats),))
                log("\tcrashes_md5: %s"%(str(crashes_md5),))
            except:
                traceback.print_exc()

    @property
    def beats(self):
        beats={}
        for _ in range(2):
            try:
                r=redis.Redis(connection_pool=pool)
                for vname in self.vms.keys():
                    beat=r.get(vname)
                    if None == beat:
                        beat=0
                    beat = int(float(time.time()))-int(float(beat))
                    beats[vname]=beat
                return beats
            except:
                traceback.print_exc()
        return beats



if __name__=="__main__":
    r=redis.Redis(connection_pool=pool)
    for vm in vbutils.listrunningvms():
        vbutils.stopvm(vm)
    #for vm in vbutils.listvms():
        #vbutils.removevm(vm)

    #for vm in vbutils.listvms():
        #r.set("thisvname",vname)

