#!/usr/bin/python

import redis
import vbutils


pool=redis.ConnectionPool(host="192.168.4.2",port=6379,decode_response=True)

if __name__=="__main__":
	r=redis.Redis(connection_pool=pool)
	for vm in vbutils.listrunningvms():
		vbutils.stopvm(vm)
	#for vm in vbutils.listvms():
		#vbutils.removevm(vm)
	
	#for vm in vbutils.listvms():
		#r.set("thisvname",vname)
		
