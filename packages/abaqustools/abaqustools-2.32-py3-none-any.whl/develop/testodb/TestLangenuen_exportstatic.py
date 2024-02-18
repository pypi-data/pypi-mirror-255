
import os
import sys
import numpy as np

FolderODB='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/develop/testodb'
JobName='TestLangenuen'
FolderSave='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/develop/testodb'
FolderPython='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/odbexport'
prefix='TestLangenuen_export_'

# Import functions for export
sys.path.append(FolderPython)
import odbfunc

# Open ODB
myOdb=odbfunc.open_odb(FolderODB,'TestLangenuen')

# Step and frames to export
StepNumber=-2
FrameNumber=-1

# Displacements
(u,u_label)=odbfunc.exportdisplacement(myOdb,StepNumber,FrameNumber=FrameNumber)
odbfunc.save2txt(FolderSave,'u',u,atype=1,prefix=prefix)
odbfunc.save2txt(FolderSave,'u_label',u_label,atype=2,prefix=prefix)

# Section forces
(sf,sf_label)=odbfunc.exportsectionforce(myOdb,StepNumber,FrameNumber=FrameNumber)
odbfunc.save2txt(FolderSave,'sf',sf,atype=1,prefix=prefix)
odbfunc.save2txt(FolderSave,'sf_label',sf_label,atype=2,prefix=prefix)

# Node coordinates
nodecoord=odbfunc.exportnodecoord(myOdb,StepNumber,0)
odbfunc.save2txt(FolderSave,'nodecoord',nodecoord,atype=1,prefix=prefix)

# Element connectivity
elconn=odbfunc.exportelconn(myOdb)
odbfunc.save2txt(FolderSave,'elconn',elconn,atype=1,prefix=prefix)

# Element sets
(elset,elset_label)=odbfunc.exportelsets(myOdb)
odbfunc.save2txt(FolderSave,'elset',elset,atype=1,prefix=prefix)
odbfunc.save2txt(FolderSave,'elset_label',elset_label,atype=2,prefix=prefix)

# Close ODB
odbfunc.close_odb(myOdb)
