# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 15:03:00 2012

@author: ubuntusanchit
"""

import sys

def GlobalVariables():
    
def list_images():
    path=sys.argv[1]
    f=open(path,'r')
    id1=100
    images=dict()
    for line in f:
        str1=line.split('/')[-1]
        images.update({id1 : str1.rstrip()})
        id1+=1
    f.close()
    #print images.items()
    for i in images.iterkeys():
        print images[i]

        
if __name__ == '__main__':
    list_images()
    
    import libvirt
conn=0
counter=3800
pm_vm_mapping={}
vmid_dmid_mapping={}
def list_vm(pmid):
    j=0
    global conn
    global counter
    #iterate through pms list and compare with pmid and given pmid
    if(pmid==1):
        #do ssh connect to the physical machine
        conn=libvirt.open("qemu:///system")
        for id in conn.listDomainsID():
            pm_vm_mapping[j]={pmid : counter }
            vmid_dmid_mapping[j]={counter:id}
            counter+=1
            j+=1
            
    
    
        for i in pm_vm_mapping.iterkeys():
            print pm_vm_mapping[i]
    
        for i in vmid_dmid_mapping.iterkeys():
            print vmid_dmid_mapping[i]
            
            


if __name__ == '__main__':
    list_vm(1)
