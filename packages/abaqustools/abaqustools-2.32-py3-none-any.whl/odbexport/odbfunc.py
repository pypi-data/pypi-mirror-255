# -*- coding: utf-8 -*-                       
from sys import path
import numpy as np
import odbAccess
import os
from textRepr import *
from timeit import default_timer as timer

def p(pstring):
    prettyPrint(pstring)

# This module is imported in Abaqus by "import odbfunc"
# The folder containing odbfunc.py must first be added to the system path

#%%

def open_odb(foldername_odb,jobname):
    
    # Open ODB file
    
    # Inputs:
    # foldername_odb: string with folder name
    # jobname: string with job name
    
    # Outputs:
    # odb_id: ODB object

    if jobname.endswith('.odb'):
        jobname=jobname[:-4]
    
    odb_id=odbAccess.openOdb(foldername_odb+'/'+jobname + '.odb')
    return odb_id

def close_odb(odb_id):

    # Close ODB file

    # Inputs:
    # odb_id: ODB object

    odb_id.close()

#%%

def exporthistoryoutput(odb_id,stepnumber,hist_str,AssemblyName=None):

    # Export history outputs
    
    # Inputs:
    # odb_id: ODB object
    # stepnumber: step number for export, usually -1
    # hist_str: string with desired quantity, e.g. EIGFREQ,GM,DAMPRATIO,EIGREAL,EIGIMAG
    
    # Outputs:
    # OutputVector: vector with numbers

    StepNames=odb_id.steps.keys()
    NameOfStep=StepNames[stepnumber]
    
    if AssemblyName is None:
        AssemblyNameKeys=odb_id.steps[NameOfStep].historyRegions.keys()
        AssemblyName=AssemblyNameKeys[0]
    
    HistoryOutputKeys=odb_id.steps[NameOfStep].historyRegions[AssemblyName].historyOutputs.keys()
    
    # If key not found, return zero
    if hist_str not in HistoryOutputKeys:
        OutputVector=np.array([0])
        return OutputVector
    else:
        HistoryOutput=odb_id.steps[NameOfStep].historyRegions[AssemblyName].historyOutputs[hist_str]
        
    OutputVector=np.array([HistoryOutput.data[j][1] for j in range(0,len(HistoryOutput.data))])
    
    return OutputVector
    
#%%

def exportdisplacement(odb_id,stepnumber,framenumber=None):

    # Export displacement field (U,UR) for a single step and multiple frames
    
    # Inputs:
    # odb_id: ODB object
    # stepnumber: step number for export, usually -1
    # framenumber: frame number(s) for export, None gives all frames in step, 'skipfirst' gives all except frame 0
    
    # Outputs:
    # DisplacementMatrix: matrix with each frame as column (e.g. N_DOF*N_frames)
    # LabelVector: list with DOF labels of all N_DOF

    StepNames=odb_id.steps.keys()
    NameOfStep=StepNames[stepnumber]
    SelectedStep=odb_id.steps[NameOfStep]
    
    if framenumber is None:
        framenumber=range(len(SelectedStep.frames))
    elif framenumber=='skipfirst':
        framenumber=range(1,len(SelectedStep.frames))
    elif isinstance(framenumber,int):
        framenumber=np.array([framenumber])
    
    SelectedFrame=SelectedStep.frames[-1]
    if not SelectedFrame.fieldOutputs.has_key('U'):
        DisplacementMatrix=np.array([0])
        LabelVector=np.array([0])
        return DisplacementMatrix,LabelVector
    
    N_node=len(SelectedFrame.fieldOutputs['U'].values)          
    N_frame=len(framenumber)    
    
    DisplacementMatrix=np.zeros((N_node*6,N_frame))
    
    t_start=timer()
    for z in np.arange(len(framenumber)):
        
        SelectedFrame=SelectedStep.frames[framenumber[z]]
        
        OutputTrans=SelectedFrame.fieldOutputs['U']
        OutputTransValues=OutputTrans.values
        
        OutputRot=SelectedFrame.fieldOutputs['UR']
        OutputRotValues=OutputRot.values
        
        U_temp=np.array([OutputTransValues[n].data for n in range(N_node) ])
        UR_temp=np.array([OutputRotValues[n].data for n in range(N_node) ])
        
        Displacement_temp=np.hstack((U_temp,UR_temp)).flatten()
        DisplacementMatrix[:,z]=Displacement_temp
    
    LabelVectorTemp=[ [str(OutputTransValues[n].nodeLabel) + '_' + s  for s in OutputTrans.componentLabels] + [str(OutputRotValues[n].nodeLabel) + '_' + s  for s in OutputRot.componentLabels] for n in range(N_node) ]
    LabelVector=[item for sublist in LabelVectorTemp for item in sublist]
    
    t_end=timer()
    print('Time displacement ' + str(t_end-t_start) + ' s')
    return DisplacementMatrix,LabelVector

#%%

def exportnodecoord(odb_id,stepnumber,framenumber):

    # Export node coordinates (Node,x,y,z) for a single step and a single frame
    
    # Inputs:
    # odb_id: ODB object
    # stepnumber: step number for export, usually -1
    # framenumber: frame number for export, usually 0
    
    # Outputs:
    # NodeCoord: matrix with [nodenumber,x,y,z] as rows, size N_NODE*4

    StepNames=odb_id.steps.keys()
    NameOfStep=StepNames[stepnumber]
    SelectedStep=odb_id.steps[NameOfStep]
            
    SelectedFrame=SelectedStep.frames[framenumber]
    if 'COORD' not in SelectedFrame.fieldOutputs.keys():
        NodeCoordMatrix=np.array([0 , 0 , 0])
        NodeCoordLabelVector=np.array([0])
        NodeCoord=np.hstack((NodeCoordLabelVector,NodeCoordMatrix))
        return NodeCoord
        
    t_start=timer()
    CoordValues=SelectedFrame.fieldOutputs['COORD'].values
    NodeCoordMatrix=np.array([CoordValues[ii].data for ii in range(len(CoordValues))])
    NodeCoordLabelVector=np.zeros((np.shape(NodeCoordMatrix)[0],1))
    NodeCoordLabelVector[:,0]=np.array([CoordValues[ii].nodeLabel for ii in range(len(CoordValues))])
    
    t_end=timer()
    print('Time nodecoord ' + str(t_end-t_start) + ' s')
    
    NodeCoord=np.hstack((NodeCoordLabelVector,NodeCoordMatrix))
    
    return NodeCoord
        
#%%

def exportsectionforce(odb_id,stepnumber,framenumber=None):

    # Export section forces (SF,SM) for a single step and multiple frames
    
    # Inputs:
    # odb_id: ODB object
    # stepnumber: step number for export, usually -1
    # framenumber: frame number for export, '' gives all frames in skip, 'skipfirst' gives all except frame 0
    
    # Outputs:
    # SectionForceMatrix: matrix with each frame as column ( e.g. N_SF*N_MODES)
    # ElementLabelVector: list with SF labels

    StepNames=odb_id.steps.keys()
    NameOfStep=StepNames[stepnumber]
    SelectedStep=odb_id.steps[NameOfStep]
    
    if framenumber is None:
        framenumber=range(len(SelectedStep.frames))
    elif framenumber=='skipfirst':
        framenumber=range(1,len(SelectedStep.frames))
    elif isinstance(framenumber,int):
        framenumber=np.array([framenumber])
    
    SelectedFrame=SelectedStep.frames[-1]
    if 'SF' not in SelectedFrame.fieldOutputs.keys():
        SectionForceMatrix=np.array([0 , 0 , 0])
        ElementLabelVector=np.array(['SF_not_found'])
        return SectionForceMatrix,ElementLabelVector
    
    ElementLabelAll=[ SelectedFrame.fieldOutputs['SF'].values[n].baseElementType for n in range(len(SelectedFrame.fieldOutputs['SF'].values)) ]
    index_B=[n for n, l in enumerate(ElementLabelAll) if l.startswith('B')]
        
    SectionForceMatrix=np.zeros((len(index_B)*6,len(framenumber)))
    
    for z in np.arange(len(framenumber)):
        
        SelectedFrame=SelectedStep.frames[framenumber[z]]
        
        OutputSF=SelectedFrame.fieldOutputs['SF']
        OutputSFValues=OutputSF.values
        
        OutputSM=SelectedFrame.fieldOutputs['SM']
        OutputSMValues=OutputSM.values
        
        SF_temp=np.array([OutputSFValues[n].data for n in index_B ])
        SM_temp=np.array([OutputSMValues[n].data for n in index_B ])
        
        Output_SF_temp=np.hstack((SF_temp,SM_temp)).flatten()
        SectionForceMatrix[:,z]=Output_SF_temp
        
    SF_ComponentLabels=OutputSF.componentLabels
    
    
    # For SM:
    # Error in abaqus documentation? States 2 1 3 in odb file, but that is wrong.
    # >> OutputSM.componentLabels
    # >> ('SM2', 'SM1', 'SM3')    
    
    
    # Overwrite labels manually:    
    SM_ComponentLabels=('SM1', 'SM2', 'SM3') 
    # Important to verify results are reasonable
    
    ElementLabelVectorTemp=[ [str(OutputSFValues[n].elementLabel) + '_' + s  for s in SF_ComponentLabels] + [str(OutputSMValues[n].elementLabel) + '_' + s  for s in SM_ComponentLabels] for n in index_B ]
    ElementLabelVector=[item for sublist in ElementLabelVectorTemp for item in sublist]
    
    return SectionForceMatrix,ElementLabelVector
    
    # From abaqus manual:
    # Section forces, moments, and transverse shear forces
    # SF1 Axial force.
    # SF2 Transverse shear force in the local 2-direction (not available for B23, B23H, B33, B33H).
    # SF3 Transverse shear force in the local 1-direction (available only for beams in space, not available for B33, B33H).
    # SM1 Bending moment about the local 1-axis.
    # SM2 Bending moment about the local 2-axis (available only for beams in space).
    # SM3 Twisting moment about the beam axis (available only for beams in space).

#%%

def exportelconn(odb_id):

    # Export element connectivity (which elements are connected to which nodes)
    
    # Inputs:
    # odb_id: ODB object
    
    # Outputs:
    # ElementConnectivity: matrix with rows [Elno,Nodeno_start,Nodeno_end]
    
    t_start=timer()

    InstanceKeys=odb_id.rootAssembly.instances.keys()
    
    for k in range(len(InstanceKeys)):

        SelectedInstance=odb_id.rootAssembly.instances[InstanceKeys[k]]
        SelectedInstanceElements=SelectedInstance.elements
        
        ElType=[SelectedInstanceElements[j].type for j in range(len(SelectedInstanceElements))]
        
        Index_B31 = [i for i, s in enumerate(ElType) if 'B31' in s]
        Index_B33 = [i for i, s in enumerate(ElType) if 'B33' in s]
        Index_B32 = [i for i, s in enumerate(ElType) if 'B32' in s]
        
        ElementConnectivity_B31=np.array( [ [SelectedInstanceElements[j].label , int(SelectedInstanceElements[j].connectivity[0]) , int(SelectedInstanceElements[j].connectivity[1]) ]  for j in Index_B31 ] )
        ElementConnectivity_B33=np.array( [ [SelectedInstanceElements[j].label , int(SelectedInstanceElements[j].connectivity[0]) , int(SelectedInstanceElements[j].connectivity[1]) ]  for j in Index_B33 ] )
        ElementConnectivity_B32=np.array( [ [SelectedInstanceElements[j].label , int(SelectedInstanceElements[j].connectivity[0]) , int(SelectedInstanceElements[j].connectivity[1]) , int(SelectedInstanceElements[j].connectivity[2]) ]  for j in Index_B32 ] )

    # If empty, then set shape to 3 or 4 columns
    if Index_B31==[]:
        ElementConnectivity_B31=np.array([]).reshape(0,3)
    
    if Index_B33==[]:
        ElementConnectivity_B33=np.array([]).reshape(0,3)
    
    if Index_B32==[]:
        ElementConnectivity_B32=np.array([]).reshape(0,4)
        
    # Delete middle node for 3 node element
    ElementConnectivity_B32_del=np.delete(ElementConnectivity_B32,2,1)
    
    ElementConnectivity=np.vstack((ElementConnectivity_B31,ElementConnectivity_B33,ElementConnectivity_B32_del))
    
    t_end=timer()
    print('Time elconn ' + str(t_end-t_start))
    
    return ElementConnectivity

#%%

def exportelsets(odb_id):

    # Export element sets
    
    # Inputs:
    # odb_id: ODB object
    
    # Outputs:
    # ElementSetNumbers: vector with set number (separated by 0 between each set)
    # ElementSetNames: list with names

    InstanceKeys=odb_id.rootAssembly.instances.keys()
    ElementSetNumbers=[]
    ElementSetNames=[]
    
    t_start=timer()
    for k in range(len(InstanceKeys)):

        SelectedInstance=odb_id.rootAssembly.instances[InstanceKeys[k]]
        ElementSetKeys=SelectedInstance.elementSets.keys()
        ElementSetNames=np.append(ElementSetNames,ElementSetKeys)
        
        for i in range(len(ElementSetKeys)):
            
            Elements=SelectedInstance.elementSets[ElementSetKeys[i]].elements
            ElementNumbers_temp=[Elements[ii].label for ii in range(len(Elements))]
            ElementNumbers_temp=np.append(ElementNumbers_temp,0)
            ElementSetNumbers=np.append(ElementSetNumbers,ElementNumbers_temp)
            
    t_end=timer()
    print('Time elsets ' + str(t_end-t_start))
    return ElementSetNumbers,ElementSetNames
    
#%%

def save2txt(folder_save,name_save,A_matrix,atype='string',prefix=''):

    # Save numeric array or string array to txt file
    
    # Inputs:
    # folder_save: string with folder name for export
    # name_save: string with name for export
    # A_matrix: the array to export
    # atype: 'string' or 'number' specifies text or numeric data
    # prefix: prefix in front of name_save
    
    if atype=='number' or atype==1:
        np.savetxt((folder_save+'\\'+prefix+name_save+'.txt'), A_matrix , delimiter=',', fmt='%.6e')
    elif atype=='string' or atype==2:
        np.savetxt((folder_save+'\\'+prefix+name_save+'.txt'), A_matrix , delimiter=' ', fmt='%s')
    
#%%

def save2npy(folder_save,name_save,A_matrix,prefix=''):

    # Save numeric array or string array to npy file
    
    # Inputs:
    # folder_save: string with folder name for export
    # name_save: string with name for export
    # A_matrix: the array to export
    # prefix: prefix in front of name_save
    
    np.save((folder_save+'\\'+prefix+name_save), A_matrix)
    
