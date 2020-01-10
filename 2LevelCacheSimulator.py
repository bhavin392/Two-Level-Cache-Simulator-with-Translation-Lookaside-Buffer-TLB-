import tkinter as tk
from tkinter import filedialog
import numpy as np
import os
import math
root= tk.Tk()
root.withdraw()
filepath =filedialog.askopenfilename(filetypes = (("din files","*.din"),("trace files files","*.trace"),("out files",".out")))
file=open(filepath)
file_path = file.name
ext= os.path.splitext(file_path)
readData=file.readline()
pageTable=[]
TLB=[]
temp1=[]
temp=[]
temp2=[]
dataList=[]
instr=[]
combined=[]
blockSize=64
L2cachesize=1024*1024
cacheSize=32*1024
associativity=8
L2cacheArray = [[0] * associativity] * int(L2cachesize / (blockSize * associativity))  #declaring list for cache array 
L2lruArray = [[0] * associativity] * int(L2cachesize / (blockSize * associativity))
cacheArray = [[0] * associativity] * int(cacheSize / (blockSize * associativity))  #declaring list for cache array 
lruArray = [[0] * associativity] * int(cacheSize / (blockSize * associativity))
L2Cachehits=0
L2Cachemisses=0
TLBaccess=0
TLBmiss=0
TLBhits=0
ppn=0

def TLBfunc(dataAddr):
    virtualaddr= int(dataAddr) #convert string to integer
    vpn=virtualaddr>>12 #right shift virtual address by 12 to get virtual page number
    ppn=vpn<<2 #left shift vpn by 2 to get physical page number
    ppn=ppn>>2 # right shift ppn to remove to LSB 0's
    ppn=str(ppn)
    offset = virtualaddr & 0xFFF # anding virtual address with fff to get offset
    offset=str(offset)
    physicaladdr=ppn+offset
    physicaladdr=int(physicaladdr)
    global L2Cachehits
    global L2Cachemisses
    if L2cacheHitorMiss(physicaladdr) is 1: # if return value from cacheHitorMiss function is 1 
        L2Cachehits+=1 #L1 Cache hits+1
    else:
        L2Cachemisses+=1 
    return L2Cachehits,L2Cachemisses

def L2cacheHitorMiss(physicaladdr):
    storeAddr=physicaladdr
    offset=int(math.log(blockSize, 2))
    indexValue = int(math.log(cacheSize / (associativity * blockSize), 2))
    addrLength=32
    tag = addrLength - offset - indexValue # getting tag value 
    flag1 = int(('1' * tag + '0' * indexValue + '0' * offset), 2)# select tag value and make 0 for index and offset  
    tag = (storeAddr & flag1) >> (indexValue + offset)  # shif the tag
    flag2 = int(('0' * indexValue + '1' * indexValue+ '0' * offset), 2)# select index value and make 0 for tag and offset
    index = (storeAddr & flag2) >> (offset)

    if tag in L2cacheArray[index]:
        store= L2cacheArray[index].index(tag)
        L2lruArray[index][store]=max(lruArray[index])+1
        return 1
    else:
        if 0 in L2cacheArray[index]: # if cache array is empty assign a tag value
            store = L2cacheArray[index].index(0) # assign a tag value
            L2cacheArray[index][store]= tag
            L2lruArray[index][store] = max(lruArray[index]) + 1 # give the maximum value 
        else: #if not empty get the least recently used index and replace it 
            lru = min(L2lruArray[index])  # get least recently used index
            temp1 = L2lruArray[index].index(lru) # store into temporary variable
            L2cacheArray[index][temp1] = tag # assign new tag
            L2lruArray[index][temp1] = max(lruArray[index]) + 1 # give maximum value
        return 0

def cacheHitorMiss(dataAddr):
    storeAddr= dataAddr
    offset=int(math.log(blockSize, 2))
    indexValue = int(math.log(cacheSize / (associativity * blockSize), 2))
    addrLength=32
    tag = addrLength - offset - indexValue # getting tag value 
    flag1 = int(('1' * tag + '0' * indexValue + '0' * offset), 2)# select tag value and make 0 for index and offset  
    tag = (storeAddr & flag1) >> (indexValue + offset)  # shif the tag
    flag2 = int(('0' * indexValue + '1' * indexValue+ '0' * offset), 2)# select index value and make 0 for tag and offset
    index = (storeAddr & flag2) >> (offset)
    
    if tag in cacheArray[index]: # if tag value is in cache array
            store = cacheArray[index].index(tag)# store into a temporary variable
            lruArray[index][store] = max(lruArray[index]) + 1 # give the maximum value 
            return 1
    else:
        L2hitsdata,L2missdata=TLBfunc(storeAddr)
        global TLBaccess
        TLBaccess+=1
        if ppn not in temp2: ##created a temporary list for TLB first index to avoid accessing multidimensional list // if vpn not in temp1list
            global TLBmiss,TLBhits
            TLBmiss+=1
        else:
            TLBhits+=1
       
        

        if 0 in cacheArray[index]: # if cache array is empty assign a tag value
            store = cacheArray[index].index(0) # assign a tag value
            cacheArray[index][store]= tag
            lruArray[index][store] = max(lruArray[index]) + 1 # give the maximum value 
        else: #if not empty get the least recently used index and replace it 
            lru = min(lruArray[index])  # get least recently used index
            temp1 = lruArray[index].index(lru) # store into temporary variable
            cacheArray[index][temp1] = tag # assign new tag
            lruArray[index][temp1] = max(lruArray[index]) + 1 # give maximum value
        return 0

while readData:
    label,addr=readData.split(' ') #split data from file
    addr=addr.strip() 
    addr=int(addr,16) #convert the hex address in int
    # label=int(label)
    combined.append(addr) #made three list combined, data and instruction for storing different address;combined=all,data="0,1", instr=2 denoted by first column of input file
    if "0" in label:
        dataList.append(addr)
    if "1" in label:
        dataList.append(addr)
    else:
        instr.append(addr)
    readData=file.readline()

def DataCache(dataList): # we are interested in Data address so written a function for it
    L1Cachemisses=0 # intialize counters
    L1Cachehits=0
    # TLBhits=0
    # TLBmiss=0
    for dataAddr in dataList: # for address in data list
        virtualaddr= int(dataAddr) #convert string to integer
        vpn=virtualaddr>>12 #right shift virtual address by 12 to get virtual page number
        global ppn
        ppn=vpn<<2 #left shift vpn by 2 to get physical page number
        ppn=ppn>>2 # right shift ppn to remove to LSB 0's
        ppn=str(ppn)
        offset = virtualaddr & 0xFFF # anding virtual address with fff to get offset
        offset=str(offset)
        physicaladdr=ppn+offset
        physicaladdr=int(physicaladdr)
        if vpn not in temp: #created a temporary list for pagetable first index to avoid accessing multidimensional list // if vpn not in templist
            temp.append(vpn) #append vpn in temp
            pageTable.append([vpn,ppn]) #append vpn and ppn in pagetable
    for dataAddr in dataList:
        if vpn not in temp1: ##created a temporary list for TLB first index to avoid accessing multidimensional list // if vpn not in temp1list
            # TLBmiss+=1 # if not in TLB tlb miss+1
            if vpn in temp: #if not in TLB search for vpn in pagetable
                list1_index=temp.index(vpn) #get index value of vpn in pagetable
                pagetable=pageTable[list1_index]
                temp2.insert(list1_index,ppn) #get values(vpn,ppn) from pagetable using index value
                temp1.append(temp[list1_index]) #append to templist1
                TLB.append(pagetable) #append page table entry to TLB
            if len(TLB)>64: # set the maximum size of list of TLB as 64
                del TLB[0] # if its greater than 64 delete the first index of TLB
        # else:
        #     # TLBhits+=1  #if vpn found in TLB tlbhits+1
        if cacheHitorMiss(dataAddr) is 1: # if return value from cacheHitorMiss function is 1 
            L1Cachehits+=1 #L1 Cache hits+1
        else:
            L1Cachemisses+=1  # else L1 Cache miss+1
    return L1Cachehits,L1Cachemisses
hitsdata,missesdata=DataCache(dataList)
print("Number of Data Fetches: "+str(len(dataList)))
print("Total Cache miss: ",str(L2Cachemisses))
totalhits=hitsdata+L2Cachehits
print("Total Cache hits",str(totalhits))
print("Number of L1 Cache Hits: " + str(hitsdata))
print("Number of L1 Cache Misses: " + str(missesdata))
print("Number of TLB access:",str(TLBaccess))
print("Number of TLB hits: ",str(TLBhits))
print("Number of TLB miss: ",str(TLBmiss))
print("Number of L2 Cache hits: ",str(L2Cachehits))
print("Number of L2 Cache miss: ",str(L2Cachemisses))


TLBhitscycle=TLBhits*1
TLBmisscycle=TLBmiss*8
L1Cachehitcycle=hitsdata*4
L1Cachemisscycle=missesdata*14
L2Cachehitcycle=L2Cachehits*24
L2Cachemisscycle=L2Cachemisses*59
Totalcycle=TLBhitscycle+TLBmisscycle+L1Cachehitcycle+L1Cachemisscycle+L2Cachehitcycle+L2Cachemisscycle

print("Number of L1 hit cycle: ",str(L1Cachehitcycle))
print("Number of L1 miss cycle: ",str(L1Cachemisscycle))
print("Number of TLB hit cycle: ",str(TLBhitscycle))
print("Number of TLB miss cycle: ",str(TLBmisscycle))
print("Number of L2 hit cycle: ",str(L2Cachehitcycle))
print("Number of L2 miss cycle: ",str(L2Cachemisscycle))
print("Total cycles: ",str(Totalcycle))

# with open('pagetable.txt', 'w') as f:
#     for item in pageTable:
#         f.write("%s\n" % item)
# with open('TLB.txt', 'w') as f:
#     for item in TLB:
#         f.write("%s\n" % item)