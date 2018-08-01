#!/usr/bin/python
import time
import redis
import vbutils
import traceback
import threading

pool=redis.ConnectionPool(host="192.168.4.2",port=6379,decode_response=True)

class Machine:
	def __init__(self,name):
		self.name=name

	def init_run(self):
		try:
			r=redis.Redis(connection_pool=pool)
			r.set("thisvname",self.name)
			self.run()
			time.sleep(300)
			return None == r.get("thisvname")
		except:
			traceback.print_exc()
			return False
	def run(self):
		if not self.running:
			t=threading.Thread(target=vbutils.startvm,args=(self.name,))
			t.setDaemon(True)
			t.start()
			time.sleep(5)
		return self.running

	def stop(self):
		if self.running:
			t=threading.Thread(target=vbutils.stopvm,args=(self.name,))
			t.setDaemon(True)
			t.start()
			time.sleep(5)
		return not self.running

	def restart(self):
		self.stop()
		time.sleep(18)
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
				return int(float(r.get(self.name)))
			except:
				traceback.print_exc()
		return 0



class Fuzzer:
	def __init__(self):


if __name__=="__main__":
	r=redis.Redis(connection_pool=pool)
	for vm in vbutils.listrunningvms():
		vbutils.stopvm(vm)
	#for vm in vbutils.listvms():
		#vbutils.removevm(vm)
	
	#for vm in vbutils.listvms():
		#r.set("thisvname",vname)
		
