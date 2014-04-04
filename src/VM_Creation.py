#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 18:02:48 2012

@author: ubuntusanchit
"""


import libvirt
from bottle import get, run, request
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as xml
import os
import sys
import json

class GlobalVariables:
    machineList=[]
    imageList=[]
    vmtypeList=dict()
    imgfilePath=""
    machfilepath=""
    vmfilepath=""
    connHyper=[]
    xmlstring=""
    configFile="configuration.xml"
    targetImageLocation="/var/lib/libvirt/images/"
    #imgID=100    
  
    def __init__(self,mfilepath,imgfilePath,vmfilepath):
        self.machfilepath=mfilepath
        self.imgfilePath=imgfilePath
        self.vmfilepath=vmfilepath
        self.getMachineList()
        self.getImageList()
        self.getVmTypeList()
        self.getConnHyperVisor()
        self.getConfXML()
    
    def copyImage(self,source):
        try:
            for item in self.machineList:
                target=item+':'+self.targetImageLocation
                cmd="scp "+source+" "+target
                copyFlag=os.system(cmd)
                if copyFlag==0:
                    print "Image Copied Successfully"
            return True
        except:
            print "Exception in copyImage",sys.exc_info()
            return False

    def getMachineList(self):
        try:        
            filereader=open(os.path.dirname(os.path.realpath( __file__ ))+'/'+self.machfilepath,'r')
            for line in filereader:
                self.machineList.append(line.rstrip())
            filereader.close()
            print self.machineList
            return True
        except:
            print "Exception in getMachineList",sys.exc_info()
            return False

    def  getImageList(self):
        try:
            filereader=open(os.path.dirname(os.path.realpath( __file__ ))+'/'+self.imgfilePath,'r')
            for line in filereader:
                #copy image to each machine
                self.copyImage(line.strip())          
                line=line.split('/')[-1]
                self.imageList.append(line.rstrip())
            filereader.close()
            print self.imageList
            return True
        except:
            print "Exception in getImageList",sys.exc_info()
            return False           
        
    def getVmTypeList(self):
        try:
            filereader=open(os.path.dirname(os.path.realpath( __file__ ))+'/'+self.vmfilepath,'r')
            temp=""        
            for line in filereader:
                temp+=line
            filereader.close()
            self.vmtypeList=eval(temp)
            return True
        except:
            print "Exception in getVmTypeList",sys.exc_info()
            return False         

    def getConnHyperVisor(self):
        try:
            for eachmachine in self.machineList:
                hypervisor='remote+ssh://'+eachmachine+'/system'
                temp_conn  = libvirt.open(hypervisor)
                if temp_conn!=None:
                    self.connHyper.append(temp_conn)
                else:
                    print "Failed To Open Connection on machine : ",eachmachine
            return True
        except:
            print "Exception in getConnHyperVisor",sys.exc_info()
            return False
            
    def getConfXML(self):
        try:
            filereader=open(os.path.dirname(os.path.realpath( __file__ ))+'/'+self.configFile,'r')      
            for line in filereader:
                self.xmlstring+=line
            filereader.close()
            return True
        except:
            print "Exception in getConfXML",sys.exc_info()
            return False       

    def getDetailsPM(self,pmid):
        try:
            InfoConn =self.connHyper[pmid].getInfo()
            typ=self.connHyper[pmid].getType()
            capacity = {
            "cpu"  :self.connHyper[pmid].getMaxVcpus(typ),
            "ram"  : InfoConn[1] #list contain (model,memory,cpu,mhz,nodes,sockets,cores,threads) memory size is in kb
            }
            #Domain.Info returns the info about each domain which include list of (state,max memory,memory used,cpu,cpu time)
            numCPUs = [self.connHyper[pmid].lookupByID(did).info()[3] for did in self.connHyper[pmid].listDomainsID()]
            free = {
            "cpu"  : capacity['cpu'] - sum(numCPUs),
            "ram"  : self.connHyper[pmid].getFreeMemory()/2**20,#get free memory reuturns memory in bytes
            }
            numDomains= self.connHyper[pmid].numOfDomains()
            return {
            "pmid"     : pmid+1,
            "capacity" : capacity,
            "free"     : free,
            "vms"      : numDomains}
        except:
            print "Exception in getDetailsPM",sys.exc_info()
            return {}

    def getSchedule(self,vmType):
        try:
            vmtp=self.vmtypeList["types"][vmType-1]
            print vmtp
            for pmid in range(1,len(self.connHyper)+1):
                pmidInfo = self.getDetailsPM(pmid-1)
                if (pmidInfo['free']['cpu']>vmtp['cpu']):
                    print pmid
                    return pmid
            return -1
        except:
            print "Exception in getSchedule",sys.exc_info()
            return -1
        
    def createDomain(self,pmid, name, vm_type, imagepath):
        try:
            vmtp=self.vmtypeList["types"][vm_type-1]
            _createxml=self.xmlstring
            _conn=self.connHyper[pmid-1]
            #from xml.dom.minidom import parse, parseString            
            caps=parseString(_conn.getCapabilities())
            print caps
            domain_type=caps.getElementsByTagName('domain')[0].getAttribute('type')
            emulator=caps.getElementsByTagName('emulator')[0].firstChild.nodeValue
            parameter={'type':domain_type,'emulator':emulator,'ram':int(vmtp['ram'])*2**10,'vcpu':int(vmtp['cpu']),'imagepath':imagepath,'name':name}
            _createxml=_createxml.format(**parameter)
            print _createxml
            domain=_conn.createXML(_createxml,0)
            print domain.ID()
            return domain.ID()
        except:
            print "Exception in createDomain",sys.exc_info()
            return -1
    
    def destroyDomain(self,pmid,vmid):
        try:
            _conn=self.connHyper[pmid-1]
            domain=_conn.lookupByID(vmid)
            res=domain.destroy()
            if res==0:
                return {"success":1}
            else:
                return {"failure":1}
        except:
            print "Exception in destroyDomain",sys.exc_info()
            return {"failure":1}
            
    def getVMDetails(self,pmid,vmid):
        try:
            did=int(vmid)%100
            pmid=int(vmid)/100
            _conn=self.connHyper[pmid-1]
            domain=_conn.lookupByID(did)
            name=domain.name()
            imagepath=parseString(domain.XMLDesc(0)).getElementsByTagName('source')[0].getAttribute('file')
            vcpu=domain.maxVcpus()
            memory=domain.maxMemory()/2**10
            return {"vmid":vmid,"name":name,"imagePath":imagepath,"vcpu":vcpu,"memory":memory,"pmid":pmid}
        except:
            print "Exception in getVMDetails",sys.exc_info()
            return {"failure":1}
            
if __name__ == '__main__':
    _PmList=GlobalVariables(sys.argv[1],sys.argv[2],sys.argv[3])    
    @get('/pm/list')
    def api_listPm():
        return json.dumps({"pmid":range(1,len(_PmList.machineList)+1)})
    
    @get('/image/list')
    def api_list_Image():
        length=len(_PmList.imageList)
        return json.dumps({"images":[
            {"id":i+100,"name":_PmList.imageList[i]} for i in range(0,length)]})
    #localhost = socket.gethostbyname(socket.gethostname())
    run(host='localhost', port=8078)  

