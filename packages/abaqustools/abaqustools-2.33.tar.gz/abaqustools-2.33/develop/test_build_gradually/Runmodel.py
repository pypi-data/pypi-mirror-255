# -*- coding: utf-8 -*-
"""
Created on Sat May 13 09:01:11 2023

@author: oyvinpet
"""

#%%

import sys

sys.path.append('C:/Cloud/OD_OWP/Work/Python/Github')

# import abaqustools
# from abaqustools import suspensionbridge
from abaqustools import odbexport
from abaqustools import abq


#%%

foldername=r'C:\Cloud\OD_OWP\Work\Python\Github\abaqustools\develop\test_build_gradually'

inputname='HalogalandModel2.inp'

abq.runjob(foldername, inputname)


#%%

# FolderODB=foldername
# NameODB='HalogalandModel2'
# FolderSave=FolderODB
# FolderPython='C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/odbexport'

# odbexport.export.modal(FolderODB,NameODB,FolderSave,FolderPython)

