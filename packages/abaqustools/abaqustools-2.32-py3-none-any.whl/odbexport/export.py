# -*- coding: utf-8 -*-

#%%

import sys
import os
import time
import numpy as np
import putools
import h5py

#%%

def static(folder_odb,jobname,folder_save,folder_python,variables=None,stepnumber=None,framenumber=None,deletetxt=True,saveh5=True,prefix=None,postfixh5='_exportstatic',exportscript=None):

    # Export static response
    #
    # Inputs:
    # folder_odb: folder of odb file
    # jobname: name of odb file
    # folder_save: folder to export to
    # folder_python: folder where the python abaqustools repo is located (must be added in abaqus)
    # variables: list of variables to export
    # stepnumber: stepnumber to export
    # framenumber: framenumber(s) to export
    # deletetxt: delete txt files
    # saveh5: save to h5
    # prefix: prefix for txt files
    # postfixh5: postfix for h5 file
    # exportscript: name of python script that is created

    # Stepnumber
    if stepnumber is None:
        stepnumber=-1
    
    # Framenumber
    if framenumber is None:
        framenumber=-1

    # Variables to export
    if variables is None:
       variables=['u' , 'sf' , 'nodecoord' , 'elconn' , 'elset']

    # Script py file
    if exportscript is None:
       exportscript=jobname + '_exportstatic'
    
    # Run main
    exportmain(folder_odb,jobname,folder_save,folder_python,variables,stepnumber,framenumber,deletetxt=deletetxt,saveh5=saveh5,prefix=prefix,postfixh5=postfixh5,exportscript=exportscript)

def modal(folder_odb,jobname,folder_save,folder_python,variables=None,stepnumber=None,framenumber=None,deletetxt=True,saveh5=True,prefix=None,postfixh5='_exportmodal',exportscript=None):
    
    # Export modal response
    #
    # Inputs:
    # folder_odb: folder of odb file
    # jobname: name of odb file
    # folder_save: folder to export to
    # folder_python: folder where the python abaqustools repo is located (must be added in abaqus)
    # variables: list of variables to export
    # stepnumber: stepnumber to export
    # framenumber: framenumber(s) to export
    # deletetxt: delete txt files
    # saveh5: save to h5
    # prefix: prefix for txt files
    # postfixh5: postfix for h5 file
    # exportscript: name of python script that is created    # stepnumber
       
    if stepnumber is None:
        stepnumber=-1
    
    # framenumber
    if framenumber is None:
        framenumber='skipfirst'
    
    # Variables to export
    if variables is None:
       variables=['f' , 'gm' , 'phi' , 'phi_sf' , 'nodecoord' , 'elconn']

    # Script py file
    if exportscript is None:
       exportscript=jobname + '_exportmodal'
       
    # Run main
    exportmain(folder_odb,jobname,folder_save,folder_python,variables,stepnumber,framenumber,deletetxt=deletetxt,saveh5=saveh5,prefix=prefix,postfixh5=postfixh5,exportscript=exportscript)

#%%

def exportmain(folder_odb,jobname,folder_save,folder_python,variables,stepnumber,framenumber,deletetxt=True,saveh5=True,prefix=None,postfixh5=None,exportscript=None):

    # Main script for export
    #
    # Inputs:
    # folder_odb: folder of odb file
    # jobname: name of odb file
    # folder_save: folder to export to
    # folder_python: folder where the python abaqustools repo is located (must be added in abaqus)
    # variables: list of variables to export
    # stepnumber: stepnumber to export
    # framenumber: framenumber(s) to export
    # deletetxt: delete txt files
    # saveh5: save to h5
    # prefix: prefix for txt files    # saveh5: save to h5
    # postfixh5: postfix for h5 file
    # exportscript: name of python script that is created

    # Cut odb extension
    if jobname.endswith('.odb'):
        jobname=jobname[:-4]
    
    # Prefix for saving txt files
    if prefix is None:
        prefix=jobname+'_export_'
    
    # Postfix for h5 file
    if postfixh5 is None:
        postfixh5=jobname+'_export'
    
    # Check if ODB file is found
    file_name=folder_odb + '\\' + jobname + '.odb'
    file_exist_logic=os.path.isfile(file_name)
    if not file_exist_logic:
        print('***** ' + file_name)
        raise Exception('***** ODB file not found')
        
    # Check if python folder and python files are given correctly
    file_name=folder_python + '\\' + 'odbfunc.py'
    file_exist_logic=os.path.isfile(file_name)
    if not file_exist_logic:
        print('***** ' + folder_python)
        raise Exception('***** Supplied python (odbexport) folder and odbfunc module not found')    
 
    # Ensure list
    if isinstance(variables,str):
        variables=[variables]
        
    # Lower case
    variables=[x.lower() for x in variables]

    # Check input variables
    variables_allowed= ['u' , 'sf' , 'phi' , 'phi_sf' , 'f' , 'gm' , 'nodecoord' , 'elconn' , 'elset' ]
    for k in np.arange(len(variables)):
        if not variables[k] in variables_allowed:
            print('***** Check variable ' + variables[k])
            raise Exception('***** Variable identifier not allowed')
            
    # Write py-file for export
    writepyscript(folder_odb,jobname,folder_save,folder_python,variables,stepnumber,framenumber,exportscript=exportscript,prefix=prefix)
    
    # Run py-file in abaqus
    system_cmd='abaqus cae noGUI=' + folder_save + '/' + exportscript + '.py'
    sys_out=os.popen(system_cmd).read()
    
    idx_error=sys_out.find('error')

    if idx_error>0:
        print(sys_out)
        raise Exception('***** Export aborted due to errors, see above')
            
                
    # Save h5 file        
    if saveh5==True:

        # Base for txt files
        hf_name=folder_save + '/' + jobname + postfixh5 + '.h5'
        
        # Overwrite file
        if os.path.exists(hf_name):
            os.remove(hf_name)
            time.sleep(1)
            
        hf = h5py.File(hf_name,'w')
        dt = h5py.special_dtype(vlen=str)
            
        for k in np.arange(len(variables)):
            
            # Base for txt files
            filename_base=folder_save + '/' + prefix      
            
            # Read txt file
            data_from_txt=np.genfromtxt(filename_base+variables[k]+'.txt', delimiter=',')
            
            
            if variables[k]=='u':
            
                hf.create_dataset('u',data=data_from_txt)
                hf['u'].attrs.modify('Type', 'Displacement')
                hf['u'].attrs.modify('Unit', 'm, rad')
                
                fid=open(filename_base+'u_label.txt','r'); label=fid.read().splitlines(); fid.close()  
                hf.create_dataset('u_label',data=label,dtype=dt)
                hf['u_label'].attrs.modify('Type', 'DOF labels')
                
            elif variables[k]=='sf':
            
                hf.create_dataset('sf',data=data_from_txt)
                hf['sf'].attrs.modify('Type', 'Section force')
                hf['sf'].attrs.modify('Unit', 'm, rad')
                
                fid=open(filename_base+'sf_label.txt','r'); label=fid.read().splitlines(); fid.close()  
                hf.create_dataset('sf_label',data=label,dtype=dt)
                hf['sf_label'].attrs.modify('Type', 'Element labels')
                
            elif variables[k]=='phi':
            
                hf.create_dataset('phi',data=data_from_txt)
                hf['phi'].attrs.modify('Type', 'Modal displacement')
                hf['phi'].attrs.modify('Unit', 'm, rad')
                
                fid=open(filename_base+'phi_label.txt','r'); label=fid.read().splitlines(); fid.close()  
                hf.create_dataset('phi_label',data=label,dtype=dt)
                hf['phi_label'].attrs.modify('Type', 'DOF labels')
                
            elif variables[k]=='phi_sf':
            
                hf.create_dataset('phi_sf',data=data_from_txt)
                hf['phi_sf'].attrs.modify('Type', 'Modal section force')
                hf['phi_sf'].attrs.modify('Unit', 'N, Nm')
                
                fid=open(filename_base+'phi_sf_label.txt','r'); label=fid.read().splitlines(); fid.close()  
                hf.create_dataset('phi_sf_label',data=label,dtype=dt)
                hf['phi_sf_label'].attrs.modify('Type', 'Element labels')        
                
            elif variables[k]=='f':
            
                hf.create_dataset('f',data=data_from_txt)
                hf['f'].attrs.modify('Type', 'Natural frequency')
                hf['f'].attrs.modify('Unit', 'Hz')
                
            elif variables[k]=='gm':
            
                hf.create_dataset('gm',data=data_from_txt)
                hf['gm'].attrs.modify('Type', 'Generalized mass')
                hf['gm'].attrs.modify('Unit', 'kg')
                
            elif variables[k]=='nodecoord':
            
                hf.create_dataset('nodecoord',data=data_from_txt)
                hf['nodecoord'].attrs.modify('Type', 'Node coordinate')
                hf['nodecoord'].attrs.modify('Unit', 'Node number, m')     
                
            elif variables[k]=='elconn':
            
                hf.create_dataset('elconn',data=data_from_txt)
                hf['elconn'].attrs.modify('Type', 'Element connectivity')
                hf['elconn'].attrs.modify('Unit', 'Element number, Node number')                     
                
            elif variables[k]=='elset':
           
                hf.create_dataset('elset',data=data_from_txt)
                hf['elset'].attrs.modify('Type', 'Element sets')
                hf['elset'].attrs.modify('Unit', 'Element number')      
           
                fid=open(filename_base+'elset_label.txt','r'); label=fid.read().splitlines(); fid.close()  
                hf.create_dataset('elset_label',data=label,dtype=dt)
                hf['elset_label'].attrs.modify('Type', 'Element labels')    
                            

    hf.close()
    
    # Delete txt files identified by prefix
    if deletetxt==True:
        deletefiles(folder_save,prefix,['.txt'])

#%% 

def exporth5(hf_name,h5_var,h5_data,h5_isnum):
    
    # NOT USED
    
    # Save h5 file with data
    #
    # Inputs:
    # hf_name: full name of h5 file
    # h5_var: list of variable names
    # h5_data: list of data
    # h5_isnum: list of logics
    
    hf = h5py.File(hf_name,'w')
    dt = h5py.special_dtype(vlen=str)
    
    for k in np.arange(len(h5_var)):
        
        # If data is not numeric (text), convert
        if h5_isnum[k]==True:
            hf.create_dataset(h5_var[k],data=h5_data[k])
        else:
            data_temp=np.array(h5_data[k],dtype=dt)
            hf.create_dataset(h5_var[k],data=data_temp)
        

def deletefiles(foldername,name_match,extensions):
    
    # Delete files that match criteria
    #
    # Inputs:
    # foldername: name of folder to search
    # name_match: file name (partial match allowed)
    # extensions: list of extensions allowed
    
    # Find files that match
    filenames_dir=os.listdir(foldername)
    idx_match=putools.num.listindexsub(filenames_dir,name_match)
    
    for k in np.arange(len(idx_match)):
            
        filename_remove=filenames_dir[idx_match[k]]
        
        # Only files with specified extensions
        match_logic=[list_sub in filename_remove for list_sub in extensions]
        if sum(match_logic)>0:
            os.remove(foldername + '/' + filename_remove)

#%% Export modal script

def writepyscript(folder_odb,jobname,folder_save,folder_python,variables,stepnumber,framenumber,exportscript='Export',prefix='_export'):
    
    # Write py script that exports in abaqus
    # Inputs:
    # folder_odb: folder of odb file
    # jobname: name of odb file
    # folder_save: folder to export to
    # folder_python: folder where the python abaqustools repo is located (must be added in abaqus)
    # variables: list of variables to export
    # stepnumber: stepnumber to export
    # framenumber: framenumber(s) to export
    # exportscript: name of python script that is created
    # prefix: prefix for txt files
    
    # Ensure list
    if isinstance(variables,str):
        variables=[variables]
    
    # Format folder
    folder_odb=folder_odb.replace('\\','/')
    folder_save=folder_save.replace('\\','/')
    
    Lines=['']
    
    Lines.append('import os')
    Lines.append('import sys')
    Lines.append('import numpy as np')
    Lines.append('')
    
    Lines.append('folder_odb=' + '\'' + folder_odb + '\'')
    Lines.append('jobname=' + '\'' + jobname + '\'')
    Lines.append('folder_save=' + '\'' + folder_save + '\'')
    Lines.append('folder_python=' + '\'' + folder_python + '\'')
    
    Lines.append('prefix=' + '\'' + prefix + '\'')
    Lines.append('')
    
    Lines.append('# Import functions for export (odbexport package)')
    Lines.append('sys.path.append(folder_python)')
    Lines.append('import odbfunc')
    Lines.append('')
    
    Lines.append('# Open ODB')
    Lines.append( 'odb_id=odbfunc.open_odb(folder_odb,jobname)')
    Lines.append('')
    
    if isinstance(stepnumber,str):
        stepnumber_str=stepnumber
    else:
        stepnumber_str=str(stepnumber)
    
    if isinstance(framenumber,str):
        framenumber_str=framenumber
        if framenumber_str=='skipfirst':
            framenumber_str='\'skipfirst\''
    else:
        framenumber_str=str(framenumber)
        
    Lines.append('# Step and frames to export')
    Lines.append( 'stepnumber=' + stepnumber_str)
    Lines.append( 'framenumber=' + framenumber_str)
    Lines.append('')

    if 'f' in variables:
        Lines.append('# Frequencies')
        Lines.append( 'f=odbfunc.exporthistoryoutput(odb_id,stepnumber,' + '\'' + 'EIGFREQ' + '\'' +  ')' )
        Lines.append( 'odbfunc.save2txt(folder_save,' +  '\'f\'' + ',f,atype=1,prefix=prefix)' )
        Lines.append('')

    if 'gm' in variables:
        Lines.append('# Generalized mass')
        Lines.append( 'gm=odbfunc.exporthistoryoutput(odb_id,stepnumber,' + '\'' + 'GM' + '\'' +  ')' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'gm\'' + ',gm,atype=1,prefix=prefix)' )
        Lines.append('')

    if 'phi' in variables:
        Lines.append('# Mode shapes')
        Lines.append( '(phi,phi_label)=odbfunc.exportdisplacement(odb_id,stepnumber,framenumber=framenumber' + ')' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'phi\'' + ',phi,atype=1,prefix=prefix)' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'phi_label\'' + ',phi_label,atype=2,prefix=prefix)' )
        Lines.append('')

    if 'phi_sf' in variables:
        Lines.append('# Modal section forces')
        Lines.append( '(phi_sf,phi_sf_label)=odbfunc.exportsectionforce(odb_id,stepnumber,framenumber=framenumber' + ')' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'phi_sf\'' + ',phi_sf,atype=1,prefix=prefix)' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'phi_sf_label\'' + ',phi_sf_label,atype=2,prefix=prefix)' )
        Lines.append('')

    if 'u' in variables:
        Lines.append('# Displacements')
        Lines.append( '(u,u_label)=odbfunc.exportdisplacement(odb_id,stepnumber,framenumber=framenumber' + ')' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'u\'' + ',u,atype=1,prefix=prefix)' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'u_label\'' + ',u_label,atype=2,prefix=prefix)' )
        Lines.append('')

    if 'sf' in variables:
        Lines.append('# Section forces')
        Lines.append( '(sf,sf_label)=odbfunc.exportsectionforce(odb_id,stepnumber,framenumber=framenumber' + ')' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'sf\'' + ',sf,atype=1,prefix=prefix)' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'sf_label\'' + ',sf_label,atype=2,prefix=prefix)' )
        Lines.append('')
        
    if 'nodecoord' in variables:
        Lines.append('# Node coordinates')
        Lines.append( 'nodecoord=odbfunc.exportnodecoord(odb_id,stepnumber' + ',0)' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'nodecoord\'' + ',nodecoord,atype=1,prefix=prefix)' )
        Lines.append('')
        
    if 'elconn' in variables:
        Lines.append('# Element connectivity')
        Lines.append( 'elconn=odbfunc.exportelconn(odb_id)' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'elconn\'' + ',elconn,atype=1,prefix=prefix)' )
        Lines.append('')
        
    if 'elset' in variables:
        Lines.append('# Element sets')
        Lines.append( '(elset,elset_label)=odbfunc.exportelsets(odb_id)' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'elset\'' + ',elset,atype=1,prefix=prefix)' )
        Lines.append( 'odbfunc.save2txt(folder_save,' + '\'elset_label\'' + ',elset_label,atype=2,prefix=prefix)' )
        Lines.append('')
    
    Lines.append('# Close ODB')
    Lines.append( 'odbfunc.close_odb(odb_id)' )
        
    # Write py script
    fid=open(folder_save + '\\' + exportscript + '.py', 'w')
    for Lines_sub in Lines:
        fid.write( Lines_sub + '\n')

    fid.close()

