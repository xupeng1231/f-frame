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
                if None == r.get("thisvname")
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
        return self.running

    @property
    def alive(self):
        return int(float(time.time()))+ 60 - self.beat <= 300

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
    crash_dir="\\home\\xupeng\\xuzz\\crashes"
    base_dir="\\home\\xupeng\\xuzz"
    def __init__(self,vnames,max_runnings=8):

        self.machine_daemon=None
        self.crash_daemon=None
        self.info_daemon=None

        self.max_runnings=max_runnings
        self.workings=[]
        self.paralysises=[]
        self.vms={}
        for vname in vnames:
            self.vms[vname]=Machine(name=vname)

        if not os.path.exists(Fuzzer.base_dir):
            os.makedirs(Fuzzer.base_dir)
        if not os.path.exists(Fuzzer.crash_dir):
            os.makedirs(Fuzzer.crash_dir)

        self.log("__init__ finish")

    def start_fuzz(self):
        log("start_fuzz ...")
        for vname in self.vms.keys()[0:self.max_runnings]:
            log("\tinit run [%s]"%(vname,))
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
            time.sleep(300)
            log("machine daemon alive ...")
            for vname in self.workings:
                if self.vms[vname].alive

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
                log("\tbeats: %s"%(str(self.beats),))
                print "crashes_md5:",crashes_md5
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

