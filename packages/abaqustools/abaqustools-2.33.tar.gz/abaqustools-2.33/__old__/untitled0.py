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
from abaqustools import abq

from abaqustools import odbexport

#%%

folder_name=r'C:\Cloud\OD_OWP\Work\Python\Github\abaqustools\develop\test_retract'
input_name='Sulafjorden_tower'

abq.runjob(folder_name,input_name)


folder_python=r'C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/odbexport'

for k in np.arange(10):
    
    odbexport.export.static(folder_name,input_name,folder_name,folder_python,stepnumber=k,framenumber=-1,postfixh5='_StepB' + str(k),variables=['u','sf'])

umax=[]

for k in np.arange(10):

    hf = h5py.File(input_name + '_StepB' + str(k) + '.h5', 'r')

    # Frequencies
    u = np.array(hf.get('u'))
    
    # Labels corresponding to each row of phi (each DOF), as a list of strings
    u_label = np.array(hf.get('u_label'))
    u_label=u_label[:].astype('U10').ravel().tolist()

    umax.append(np.max(abs(u)))
    
    hf.close()
    
#%%

folder_name=r'C:\Cloud\OD_OWP\Work\Python\Github\abaqustools\develop\test_retract'
input_name='Sulafjorden_tower_nograv'

abq.runjob(folder_name,input_name)


folder_python=r'C:/Cloud/OD_OWP/Work/Python/Github/abaqustools/odbexport'

for k in np.arange(10):
    
    odbexport.export.static(folder_name,input_name,folder_name,folder_python,stepnumber=k,framenumber=-1,postfixh5='_StepB' + str(k),variables=['u'])

umax_nograv=[]

for k in np.arange(10):

    hf = h5py.File(input_name + '_StepB' + str(k) + '.h5', 'r')

    # Frequencies
    u = np.array(hf.get('u'))
    
    # Labels corresponding to each row of phi (each DOF), as a list of strings
    u_label = np.array(hf.get('u_label'))
    u_label=u_label[:].astype('U10').ravel().tolist()

    umax_nograv.append(np.max(abs(u)))
    
    hf.close()
    
    
    
#%% Plot single mode

plt.figure()

f=np.arange(1,10+1,1)

h1=plt.plot(f,umax, label='Grav')
h1=plt.plot(f,umax_nograv, label='No grav')

plt.xlabel('f []')
plt.ylabel('Deflection [m ]')

plt.legend()

plt.show()



