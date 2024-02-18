
import os
import sys
import numpy as np

foldername_odb='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/develop/test_retract'
jobname='Langenuen_tower'
folder_save='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/develop/test_retract'
folder_python='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/odbexport'
prefix='Langenuen_tower_export_'

# Import functions for export (odbexport package)
sys.path.append(folder_python)
import odbfunc

# Open ODB
odb_id=odbfunc.open_odb(foldername_odb,jobname)

# Step and frames to export
stepnumber=9
framenumber=-1

# Displacements
(u,u_label)=odbfunc.exportdisplacement(odb_id,stepnumber,framenumber=framenumber)
odbfunc.save2txt(folder_save,'u',u,atype=1,prefix=prefix)
odbfunc.save2txt(folder_save,'u_label',u_label,atype=2,prefix=prefix)

# Section forces
(sf,sf_label)=odbfunc.exportsectionforce(odb_id,stepnumber,framenumber=framenumber)
odbfunc.save2txt(folder_save,'sf',sf,atype=1,prefix=prefix)
odbfunc.save2txt(folder_save,'sf_label',sf_label,atype=2,prefix=prefix)

# Close ODB
odbfunc.close_odb(odb_id)
