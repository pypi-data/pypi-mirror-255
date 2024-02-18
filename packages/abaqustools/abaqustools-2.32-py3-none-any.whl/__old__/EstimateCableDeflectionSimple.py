# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 11:39:19 2021

@author: OWP
"""

#%%

import os
import numpy as np

from ypstruct import *

from .CableGeometry import *

from .. import numtools

from ..fem_corot.NonLinearSolver import *
from ..fem_corot.ProcessModel import *
from ..fem_corot.Assembly import *
from ..fem_corot.Corot import *


#%%

def EstimateCableDeflectionMain(meta,cable,bridgedeck,tower,geo):

    cable.N_def_iter=3
    
    dx_pullback_south_iter=np.zeros(cable.N_def_iter)*np.nan
    dx_pullback_north_iter=np.zeros(cable.N_def_iter)*np.nan
    dz_cable_deflection_iter=np.zeros(cable.N_def_iter)*np.nan

    for iter in np.arange(cable.N_def_iter):
  
        (r_step,Nx,IndexSpan1_U1,IndexSpan2_U1,IndexSpan1_U2,IndexSpan2_U2,IndexSpan1_U3,IndexSpan2_U3,IndexSpan1TopSouth_U1,IndexSpan1TopNorth_U1)=EstimateCableDeflectionSub(meta,cable,bridgedeck,geo)
        
        geo.dx_pullback_south=-r_step[-1][IndexSpan1TopSouth_U1]
        geo.dx_pullback_north=-r_step[-1][IndexSpan1TopNorth_U1]
        geo.dz_cable_deflection=-np.min(r_step[-1][IndexSpan1_U3])
        
        dx_pullback_south_iter[iter]=geo.dx_pullback_south
        dx_pullback_north_iter[iter]=geo.dx_pullback_north
        dz_cable_deflection_iter[iter]=geo.dz_cable_deflection
        
        if not np.isnan(cable.cs.sigma_target):
            cable.cs.A=np.max(Nx)/(cable.cs.sigma_target)
    
    numtools.starprint([
    'Initial dz_cable_deflection=' + numtools.num2strf(dz_cable_deflection_iter[0],3) + ' m' ,
    'Iterated dz_cable_deflection=' + numtools.num2strf(dz_cable_deflection_iter[-1],3) + ' m'])

    numtools.starprint(['Initial dx_pullback_south=' + numtools.num2strf(dx_pullback_south_iter[0],3) + ' m' ,
    'Iterated dx_pullback_south=' + numtools.num2strf(dx_pullback_south_iter[-1],3) + ' m'])
    
    numtools.starprint(['Initial dx_pullback_north=' + numtools.num2strf(dx_pullback_north_iter[0],3) + ' m' ,
    'Iterated dx_pullback_north=' + numtools.num2strf(dx_pullback_north_iter[-1],3) + ' m'])

    #%%  Displacement in x-dir

    U1_hanger=r_step[-1][IndexSpan1_U1[1:-1]]
    x_hat=meta.x_hanger/(geo.L_bridgedeck/2)
    cable.polycoeff_hanger_adjust=np.polyfit(x_hat,U1_hanger,3)

    #%%  Tower 

    geo.dx_pullback_south=dx_pullback_south_iter[-1]
    geo.dx_pullback_north=dx_pullback_north_iter[-1]
    
    # tower.F_pullback_south=geo.dx_pullback_south*tower.K_south
    # tower.F_pullback_north=geo.dx_pullback_north*tower.K_north
    
    #%%  Displacement of bridge deck
    (r_step2,Nx,IndexSpan1_U1,IndexSpan2_U1,IndexSpan1_U2,IndexSpan2_U2,IndexSpan1_U3,IndexSpan2_U3,IndexSpan1TopSouth_U1,IndexSpan1TopNorth_U1)=EstimateCableDeflectionSub(meta,cable,bridgedeck,geo,cableonly=True)
   
    U3_temp1=dz_cable_deflection_iter[-1]-(-np.min(r_step2[0][IndexSpan1_U3]))

    dz_cog_midspan_deflection_temp=geo.dz_cog_midspan_deflection

    geo.dz_cog_midspan_deflection=U3_temp1

    numtools.starprint(['Initial dz_cog_midspan_deflection=' + numtools.num2strf(dz_cog_midspan_deflection_temp,3) + ' m' , 
    'Iterated dz_cog_midspan_deflection=' + numtools.num2strf(geo.dz_cog_midspan_deflection,3) + ' m'])

    return (cable,geo)

#%% 

def EstimateCableDeflectionSub(meta,cable,bridgedeck,geo,cableonly=False):
    
    [meta_,cablemesh_temp]=CableGeometry(None,meta,geo,cable)
    
    NodeMatrix=np.vstack((cablemesh_temp.NodeMatrix[0]))
    ElementMatrix=np.vstack((cablemesh_temp.ElementMatrix)).astype(int)
    
    Range1=np.arange(len(NodeMatrix[:-1,0]))
    Range2=np.arange(len(NodeMatrix[:-1,0]))+1
    ElementType=np.ones(np.shape(Range2))*2
    
    ElementMatrix=np.hstack( (NodeMatrix[:-1,0],Range1,Range2,ElementType) )
    
    (e2mat,e3mat)=ElementNormal(ElementMatrix,NodeMatrix)
    
    ModelInfo=struct()
    ModelInfo.NodeMatrix=NodeMatrix
    ModelInfo.ElementMatrix=ElementMatrix
    
    ModelInfo.e2mat=e2mat
    
    ModelInfo.A=[ cable.cs.A]
    ModelInfo.Iz=[ cable.cs.I11]
    ModelInfo.Iy=[ cable.cs.I22]
    ModelInfo.It=[ cable.cs.It]
    ModelInfo.E=[ cable.cs.E]
    ModelInfo.G=[ cable.cs.G]
    ModelInfo.rho=[ cable.cs.rho]

#%% 
    
    NodeSetNameTop=['Cable_main_top_south_east', 'Cable_main_top_north_east']
    
    NodeSetNameAnch=['Cable_main_anchorage']
    
    NodeNoTop=np.zeros(2)
    for k in np.arange(2):
        NodeNoTop[k]=cablemesh_temp.NodeSet[ numtools.listindex(cablemesh_temp.NodeSetName,NodeSetNameTop[k])[0] ]
        
    NodeNoAnch=[ NodeMatrix[0,0] , NodeMatrix[-1,0] ]
    
    ModelInfo.DofLabel=numtools.genlabel(ModelInfo.NodeMatrix[:,0],'all')
    ModelInfo.DofExclude= numtools.genlabel(NodeNoAnch,['U1' , 'U2' , 'U3']) + numtools.genlabel(NodeNoTop,['U2' , 'U3']) 
    
    ModelInfo=ProcessModel(ModelInfo)
    
#%%  
    
    NodeNoSpan=ModelInfo.NodeMatrix[:,0]
    
#%% 
    
    P_cable=GravityLoad2(ModelInfo)
    
    # Load for both bridgedecks (if two) 
    pz=-np.sum(bridgedeck.inertia.m)*9.81
    
    ElementBridgeLoad=cablemesh_temp.ElementSet[numtools.listindex(cablemesh_temp.ElementSetName,'Cable_main_span')[0]]
    
    IndexElementBridgeLoad=numtools.argmin(ElementMatrix[:,0],ElementBridgeLoad)
    
    P_bridgedeck=DistLoadProjXY(ModelInfo,pz/2,IndexElementBridgeLoad)
    
    if cableonly==False:
        P_loadstep=[None]*1
        P_loadstep[0]=P_cable+P_bridgedeck
    else:
        P_loadstep=[None]*1
        P_loadstep[0]=P_cable
    
#%% 
        
    (r,r_step,Nx,KT,RHS)=NonLinearSolver(ModelInfo,P_loadstep,LoadIncrements=6,norm_tol=1e-8)

#%% 
    
    NodeNoSpan1=NodeNoSpan
    
    IndexSpan1_U1=numtools.listindex(ModelInfo.DofLabel,numtools.genlabel(NodeNoSpan1,['U1']))
    
    IndexSpan1_U2=numtools.listindex(ModelInfo.DofLabel,numtools.genlabel(NodeNoSpan1,['U2']))
    
    IndexSpan1_U3=numtools.listindex(ModelInfo.DofLabel,numtools.genlabel(NodeNoSpan1,['U3']))
    
    IndexSpan1TopSouth_U1=numtools.listindex(ModelInfo.DofLabel,numtools.genlabel(NodeNoTop[0],['U1']))[0]
    IndexSpan1TopNorth_U1=numtools.listindex(ModelInfo.DofLabel,numtools.genlabel(NodeNoTop[2],['U1']))[0]
    
    return r_step,Nx,IndexSpan1_U1,IndexSpan2_U1,IndexSpan1_U2,IndexSpan2_U2,IndexSpan1_U3,IndexSpan2_U3,IndexSpan1TopSouth_U1,IndexSpan1TopNorth_U1
    
#%% 

    # import matplotlib.pyplot as plt
    
    # plt.figure()
    # plt.plot(r_step[0][IndexSpan1_U3])
    # plt.plot(r_step[1][IndexSpan1_U3])
    # plt.show()
    
    # plt.figure()
    # plt.plot(r_step[0][IndexSpan1_U2])
    # plt.plot(r_step[0][IndexSpan2_U2])
    # plt.show()
    
    # plt.figure()
    # plt.plot(r_step[0][IndexSpan1_U1])
    # plt.plot(r_step[1][IndexSpan1_U1])
    # plt.show()
    
    # plt.ylabel('some numbers')
    # plt.show()


    
    