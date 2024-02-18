# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 20:46:28 2023

@author: oyvinpet
"""
# Example truss model where diagonals are modelled with variable (used-defined)
# stiffness in joint connections

#%%

import numpy as np
import sys
sys.path.append('C:/Cloud/OD_OWP/Work/Python/Github')

from abaqustools import kw
from abaqustools import abq


#%%

keypoints = np.array([
[1, 0.0,    0.0],
    [2, 2665.0, 3583.81],
    [3, 10500.0,  4756.52],
    [4, 21000.0,  5610.16],
    [5, 31500.0, 6463.81],
    [6, 31881, 6462.74],
    [7, 42000.0, 6405.97],
    [8, 52500.0, 6259.24],
    [9, 62260.0, 6043.12],
    [10, 63000.0, 6023.60],
    [11, 73500.0, 4886.25],
    [12, 84000.0, 3748.90],
    [13, 91835.0, 2361.37],
    [14, 94500.0, -1295.50],
    [15, 5870.0, 20.24 ],
    [16, 15199.72, 52.42],   
    [17, 26021.78, 89.74],
    [18, 36750.0, -60.18],
    [19, 41578.70, -127.66],
    [20, 42421.50, -139.44],
    [21, 47250, -206.92],
    [22, 52079.23, -274.40],
    [23, 52922.28, -286.18],
    [24, 57750, -353.66],
    [25, 69839.78, -522.61],
    [26, 79805.52, -834.95],
    [27, 88630.0, -1111.53],
    [28, 21000.0, -5753.25], 
    [29, 75304.99, -5753.25]
    ])
 
keypoints[:,1::] = keypoints[:,1::]/1000

segments_part1 = np.array([
    [1, 1, 2],
    [3, 3, 4],
    [4, 4, 5],
    [5, 5, 6],
    [9, 9, 10],
    [10, 10, 11],
    [11, 11, 12],
    [13, 13, 14],
    [33, 18, 7],
    [35, 21,8]
    ])
 
segments_part2 = np.array([
    [2, 2, 3],
    [12, 12, 13],
    [14, 1, 15],
    [15, 15, 16],
    [24, 26, 27],
    [25, 27, 14],
    [38, 10, 25],
    [31, 17, 5],
    [34, 7, 21],
    [36, 8, 24],
    [38, 10, 25],
    [45, 28, 17],
    [46, 25, 29],

    ])
 
segments_part3 = np.array([
    [26, 2, 15],
    [28, 3, 16],
    [41, 26, 12],
    [43, 27, 13],
    [44, 16, 28],
    [19, 20, 21],
    [20, 21, 22],
    [21, 23, 24],
    [22, 24, 25],
    [47, 29, 26],
    [41, 26, 12],
    [43, 27, 13],    
    [17, 17, 18], 
    [18, 18, 19], 
    [6, 6, 7],
    [7, 7, 8],
    [8, 8, 9],
    ])
 
segments_part4 = np.array([
    [27, 15, 3],
    [16, 16, 17],
    [32, 6, 18],
    [23, 25, 26],
    [42, 12, 27]
    ])
 
segments_part5 = np.array([
    [30, 4, 17],
    [39, 25, 11]
    ])
 
segments_part6 = np.array([
    [29, 16, 4],
    [37, 24, 10],
    [40, 11, 26]
    ])


#%%  Open input file

foldername=r'C:\Cloud\OD_OWP\Work\Python\Github\abaqustools\develop\nordsenga'
input_filename='nordsenga_truss.inp'
jobname='nordsenga_truss'

fid=open(input_filename,'w')

#%%  Define structure

kw.part(fid,'part_truss')

node_matrix=np.column_stack((keypoints[:,0],keypoints[:,1],keypoints[:,0]*0,keypoints[:,2]))

kw.node(fid,node_matrix,'NODES_TRUSS')

#kw.element(fid,nodes_el_chord,'B31','Truss_chord')
#kw.beamgeneralsection(fid,'Truss_chord', 7850, [1e-4,1e-6,0,1e-6,1e-6], [0,1,0], [210e9,81e9])

# Diagonals
matrix_members=np.vstack((segments_part1,segments_part2,segments_part3,
                        segments_part4,segments_part5,segments_part6))

for k in np.arange(len(matrix_members)):
    
    node1=matrix_members[k,1]
    node2=matrix_members[k,2]
    
    idx1=np.where(node_matrix[:,0]==node1)[0][0]
    coord1=node_matrix[idx1,1:]
    
    idx2=np.where(node_matrix[:,0]==node2)[0][0]
    coord2=node_matrix[idx2,1:]
    
    setname='MEMBER' + str(k+1)
    
    # Stiffness for x,y,z,rx,ry,rz (local system)
    kj1=[1e12,1e12,1e12,1e12,0,0]
    kj2=[1e12,1e12,1e12,1e12,0,0]
       
    kw.elementjointc(fid, node1, node2, coord1 , coord2 , 1000+k*100, 1000+k*100,'B31',setname, [0,1,0],kj1,kj2,offset1=0.1,offset2=0.1,max_length=0.2) #

    kw.beamgeneralsection(fid, setname, 7850, [1e-5,1e-7,0,1e-7,1e-7], [0,1,0], [210e9,81e9])


kw.nset(fid,'support',[1,28,29,14])

#%% 

kw.partend(fid)

kw.comment(fid,'ASSEMBLY',True)
    
kw.assembly(fid,'assembly_truss')
    
kw.instance(fid,'part_truss','part_truss')
    
kw.instanceend(fid)
    
kw.assemblyend(fid)

#%%  Step modal analysis

kw.step(fid,'NAME=STEP_MODAL','')
kw.frequency(fid,50,'displacement')

kw.boundary(fid,'new','support',[1,6,0],'part_truss')

#kw.boundary(fid,'new','NODES_CHORD',[2,2,0],'part_truss')
    
kw.fieldoutput(fid,'NODE',['U' , 'COORD'],'','')
kw.fieldoutput(fid,'ELEMENT',['SF','S'],'','')

kw.stepend(fid)

#%%  Close file

fid.close()

#%%  Run job
    
# Check input file for duplicate node or element numbers
abq.checkduplicate(input_filename)
    
abq.runjob(foldername,input_filename,jobname)



