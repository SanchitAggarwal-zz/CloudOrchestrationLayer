#!/usr/bin/env python
"""

Created on Tue Sep 25 15:19:21 2012

@author: luminous
"""
import os
import libvirt
from xml.dom import minidom
import sys
from xml.dom.minidom import parse, parseString
def getXml(configFile):
    xmlstring="" 
    #if os.path.exists('/home/luminous/Desktop/ubuntu-12.04.1-alternate-amd64.iso'): 
    if os.path.exists('//10.3.8.228:/home/ubuntusanchit/Desktop/cloud-miniproject-ubuntu-12.04-amd64.vdi'): 
        print 'object exists!' 
    else:
        print "object not exist"
    filereader=open(os.path.dirname(os.path.realpath( __file__ ))+'/'+configFile,'r')      
    for line in filereader:
        xmlstring+=line
    filereader.close()
    return xmlstring

#a=os.system("scp /home/luminous/Desktop/ubuntu-12.04.1-alternate-amd64.iso root@10.3.8.228:/var/lib/libvirt/images/")
#print a
import json
print json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}],indent=4)
print json.dumps({'4': 5, '6': 7}, sort_keys=True, indent=4)

Hypervisor='qemu:///system'
conn=libvirt.open(Hypervisor)
domainID = conn.listDomainsID()
domainID=dict()
domainID.update({"san":0})
try:
    if len(domainID)==0:
             raise Exception
    print len(domainID)
except:
    print json.dumps({"Hypervisior has no domains status":0},indent=4)

print conn.getInfo()
print conn.getType()
print conn.getMaxVcpus(conn.getType())
print conn.getFreeMemory()/2**10
#print conn.getMemoryStats(0,0)
print conn.listDomainsID()
dom = conn.lookupByID(4)
print dom.maxVcpus()
print dom.maxMemory()
print dom.name()
print parseString(dom.XMLDesc(0)).getElementsByTagName('source')[0].getAttribute('file')
#numCPUs = [conn.lookupByID(did).info() for did in conn.listDomainsID()]
#print numCPUs
'''vmtype={
    "types": [
        {
            "tid": 1,
            "cpu": 1,
            "ram": 512,
            "disk": 1
        },
        {
            "tid": 2,
            "cpu": 2,
            "ram": 1024,
            "disk": 2
        },
        {
            "tid": 3,
            "cpu": 4,
            "ram": 2048,
            "disk": 3
        }
    ]
}
print vmtype["types"][1]["ram"]
#json.dumps({"vmids": [100+i for i in domainID]},indent=4)
''''''
#Hypervisor='qemu:///system'
#Hypervisor='qemu+ssh://root@10.3.11.177/system'
Hypervisor='remote+ssh://root@10.3.8.228/system'
conn=libvirt.open(Hypervisor)
if conn!=None:
	print conn.listDomainsID()

domain=conn.lookupByID(2)
raw_xml=domain.XMLDesc(1)
print raw_xml

_createxml=getXml(sys.argv[1])
caps=minidom.parseString(conn.getCapabilities())
print caps
typ=caps.getElementsByTagName('domain')[0].getAttribute('type')
print typ
emulator=caps.getElementsByTagName('emulator')[0].firstChild.nodeValue
print emulator
imagepath="/home/ubuntusanchit/Desktop/cloud-miniproject-ubuntu-12.04-amd64.vdi"
name="TestSanchit"
parameter={'type':typ,'emulator':emulator,'ram':1024,'vcpu':2,'imagepath':imagepath,'name':name}
_createxml=_createxml.format(**parameter)
#print _createxml
domain=conn.createXML(_createxml,0)
print domain.ID()'''