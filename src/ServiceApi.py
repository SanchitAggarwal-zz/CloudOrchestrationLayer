# -*- coding: utf-8 -*-
"""Created on Sun Sep  9 20:24:32 2012
@author: ubuntusanchit"""

import libvirt
from bottle import get, run, request
import socket
from VM_Creation import *
import json

globalVariables=GlobalVariables(sys.argv[1],sys.argv[2],sys.argv[3])

#----Image API 
@get('/image/list')
def api_list_Image():
    try:
        length=len(globalVariables.imageList)
        if length==0:
            raise Exception        
        return json.dumps({"images":[
        {"id":100+i,"name":globalVariables.imageList[i]} for i in range(0,length)]},indent=4)
    except:
        return json.dumps({"images":0},indent=4)

#----VM API 
@get('/vm/create')
def api_VM_Create():
    try:
        vm_type = int(request.query.vm_type)
        name=str(request.query.name)
        image=int(request.query.image)
        pmid =globalVariables.getSchedule(vm_type)
        if pmid<1:
            strError='No More Domains Posiible,Machine is Overloaded'
            raise Exception(strError)
        imagepath='/var/lib/libvirt/images/'+globalVariables.imageList[image-100]
        vmid = globalVariables.createDomain(pmid, name, vm_type, imagepath)
        if vmid<0:
            strError='Domains Not Created'
            raise Exception(strError)
        return json.dumps({ "vmid": pmid*100+vmid },indent=4)
    except:
        return json.dumps({ "vmid": 0,"Reason":strError},indent=4)
        
@get('/vm/query')
def api_VM_Query():
    try:
        vmid=int(request.query.vmid)
        pmid=int(request.query.vmid)
        result=globalVariables.getVMDetails(pmid,vmid)
        return json.dumps(result,indent=4)
    except:
        return json.dumps({ "Failure"},indent=4)
        
@get('/vm/destroy')
def api_VM_Destroy():
    try:
        vmid=int(request.query.vmid)%100
        pmid=int(request.query.vmid)/100        
        result=globalVariables.destroyDomain(pmid,vmid)
        return json.dumps(result,indent=4)
    except:
        return json.dumps({ "Failure"},indent=4)


@get('/vm/types')
def api_list_VmTypes():
    try:
        length=len(globalVariables.vmtypeList)
        if length==0:
            raise Exception  
        return json.dumps(globalVariables.vmtypeList,indent=4)
    except:
        return json.dumps({"VMtypes":0},indent=4)

#----Resource API
#--pysical machiine list after chechking hypervisor connection
@get('/pm/list')
def api_list_PM():
    try:
        length=len(globalVariables.connHyper)
        if length==0:
            raise Exception
        return json.dumps({"pmid":range(1,length+1)},indent=4)
    except:
        return json.dumps({"No Physical Machines<status>":0},indent=4)

#---Machine list from machine file    
'''@get('/pm/list')
def api_list_Machines():
    return json.dumps({"pmid":range(1,len(globalVariables.machineList)+1)},indent=4)'''
    
#to list the total virtual machine for a given physical machine
@get('/pm/<pmid:int>/listvms')
def api_list_VM(pmid):
	try:
         domainID = globalVariables.connHyper[pmid-1].listDomainsID()
         if len(domainID)==0:
             raise Exception
         return json.dumps({"vmids": [pmid*100+i for i in domainID]},indent=4)
	except:
		return json.dumps({"Hypervisior has no domains status":0},indent=4)

#to query the physical machine
@get('/pm/<pmid:int>')
def api_PM_Query(pmid):
    try:
        pm_info=globalVariables.getDetailsPM(pmid-1)
        if len(pm_info)==0:
             raise Exception
        return json.dumps(pm_info,indent=4)
    except:    
        return json.dumps({"PM not available status":0},indent=4)
        
        
        
if __name__ == '__main__':
    #_createDomain(0, "sanc", 0, "/home/ubuntusanchit/Desktop/VM-linux-0.2.img")
    localhost = socket.gethostbyname(socket.gethostname())
    run(host='localhost', port=8074)
