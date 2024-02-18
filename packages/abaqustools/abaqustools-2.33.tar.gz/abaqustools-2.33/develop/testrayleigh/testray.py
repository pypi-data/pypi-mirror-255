# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 09:57:51 2023

@author: oyvinpet
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 12:36:35 2022

@author: oyvinpet
"""

#%%

import sys
import numpy as np
import h5py
import matplotlib.pyplot as plt

sys.path.append('C:/Cloud/OD_OWP/Work/Python/Github')

# import abaqustools
from abaqustools import abq,gen

from abaqustools import odbexport


#%%

InputFileName='Testray_05.inp'

fid=open(InputFileName,'w')

L=100
N_node=100
nodenum_base=[1000]
elnum_base=[1000]
partname='Part_beam'
assemblyname='Assembly_beam'


x_node=np.linspace(0,L,N_node)
y_node=x_node*0
z_node=x_node*0

nodenum=nodenum_base[0]+np.arange(1,len(x_node)+1).astype(int)
elnum=elnum_base[0]+np.arange(1,len(x_node)).astype(int)

nodematrix_01=np.column_stack((nodenum,x_node,y_node,z_node))
elmatrix_01=np.column_stack((elnum,nodenum[:-1],nodenum[1:]))

kw.part(fid,partname)

kw.node(fid,nodematrix_01,'Nodes_01')

kw.element(fid,elmatrix_01,'B31','Elements_01')

kw.nset(fid, 'End_01', [nodenum[0],nodenum[-1]])
kw.nset(fid, 'Mid', [nodenum[int(N_node/2)]])

kw.beamgeneralsection(fid,'Elements_01',7850,[0.2 , .0003 , 0 , .0001 , .01],[0,1,0],[210e9,81e9])
# kw.line(fid,'*DAMPING, ALPHA=0.03,BETA=0.02')

kw.partend(fid)

kw.comment(fid,'ASSEMBLY',True)

kw.assembly(fid,assemblyname)

kw.instance(fid,partname,partname)

kw.instanceend(fid)

kw.assemblyend(fid)


kw.step(fid,'NLGEO=NO, NAME=STEP1','Static')

kw.static(fid,'1e-3, 1, 1e-6, 1')

#kw.gravload(fid,'new',[''],9.81)

kw.boundary(fid,'new','End_01',[1,6,0],partname)
kw.boundary(fid,'new','Nodes_01',[2,2,0],partname)

kw.fieldoutput(fid,'NODE',['U' , 'RF' , 'COORD'],'','FREQUENCY=100')
kw.fieldoutput(fid,'ELEMENT',['SF'],'','FREQUENCY=100')

kw.stepend(fid)

kw.step(fid,'NAME=STEP_MODAL','')
kw.frequency(fid,10,'mass')
kw.fieldoutput(fid,'NODE',['U' , 'COORD'],'','')
kw.fieldoutput(fid,'ELEMENT',['SF'],'','')
kw.stepend(fid)

kw.step(fid,'NAME=STEP_COMPLEXMODAL','')
kw.line(fid,'*COMPLEX FREQUENCY')
kw.line(fid,'10')
kw.line(fid,'*GLOBAL DAMPING, ALPHA=0.03,BETA=0.02')

kw.fieldoutput(fid,'NODE',['U' , 'COORD'],'','')
kw.fieldoutput(fid,'ELEMENT',['SF'],'','')
kw.stepend(fid)

#kw.step(fid,'NAME=STEPD','Dyn')
#kw.line(fid,'*DYNAMIC,ALPHA=0,INITIAL=YES') #
#kw.line(fid,'0.01,20,0.001,0.05') #ALPHA=0,INITIAL=YES
#kw.fieldoutput(fid,'NODE',['U' , 'COORD'],'','')
#kw.Dload(fid,'DELETE','','','')
#kw.stepend(fid)


kw.step(fid,'NAME=STEPD','Dyn')
kw.line(fid,'*MODAL DYNAMIC') #
kw.line(fid,'0.1,250') #ALPHA=0,INITIAL=YES



kw.line(fid,'*AMPLITUDE,NAME=MYAMP,DEFINITION=TABULAR') #
kw.line(fid,'0,0') #
kw.line(fid,'1,1') #
kw.line(fid,'1.1,0') #

kw.line(fid,'*CLOAD,AMPLITUDE=MYAMP')
kw.line(fid,partname + '.mid' + ',3,-100')
kw.Dload(fid,'DELETE','','','')

kw.fieldoutput(fid,'NODE',['U' , 'COORD'],'','')

kw.historyoutput(fid)
kw.historyoutputnode(fid,'U',partname + '.mid')
    
kw.Dload(fid,'DELETE','','','')
kw.stepend(fid)


fid.close()



#%%
foldername=r'C:\Cloud\OD_OWP\Work\Python\Github\abaqustools\develop\testrayleigh'

inputname=InputFileName

abq.runjob(foldername, inputname)
