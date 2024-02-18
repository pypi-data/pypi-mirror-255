# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 12:36:35 2022

@author: oyvinpet
"""

#%%

import sys

sys.path.append('C:/Cloud/OD_OWP/Work/Python/Github')

# import abaqustools
#from abaqustools import suspensionbridge

from abaqustools import odbexport

#%%

FolderODB='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/develop/testodb'
NameODB='TestLangenuen'
FolderSave=FolderODB
FolderPython='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/odbexport'

    
    
#odbexport.export.modal(FolderODB,NameODB,FolderSave,FolderPython)


odbexport.export.static(FolderODB,NameODB,FolderSave,FolderPython,StepNumber=-2,FrameNumber=-1)