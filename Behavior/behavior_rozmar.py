#%%
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

def loadcsvdata(bigtable=pd.DataFrame(), projectdir = Path('/home/rozmar/Network/BehaviorRig/Behavroom-Stacked-2/labadmin/Documents/Pybpod/Projects')):
    bigtable_orig = bigtable
#bigtable=pd.DataFrame()
#projectdir = Path('/home/rozmar/Network/BehaviorRig/Behavroom-Stacked-2/labadmin/Documents/Pybpod/Projects')
#projectdir = Path('/home/rozmar/Data/Behavior/Projects')
    if type(projectdir) != type(Path()):
        projectdir = Path(projectdir)
    if len(bigtable) > 0:
        sessionnamessofar = bigtable['session'].unique()
        sessionnamessofar = sessionnamessofar[:-1] # we keep reloading the last one
    else:
        sessionnamessofar = []
    projectnames = list()
    for projectname in projectdir.iterdir():
        if projectname.is_dir(): 
            projectnames.append(projectname)
            experimentnames = list()
            for experimentname in (projectname / 'experiments').iterdir():
                if experimentname.is_dir(): 
                    experimentnames.append(experimentname)
                    setupnames = list()
                    for setupname in (experimentname / 'setups').iterdir():
                        #if setupname.name == 'Foraging-0':
                        setupnames.append(setupname)
                        # a json file can be opened here
                        sessionnames = list()
                        for sessionname in (setupname / 'sessions').iterdir():
                            if sessionname.is_dir(): 
                                sessionnames.append(sessionname)
                                csvfilename = (sessionname / (sessionname.name + '.csv'))
                                if csvfilename.is_file() and sessionname.name not in sessionnamessofar: #there is a .csv file
                                    df = pd.read_csv(csvfilename,delimiter=';',skiprows = 6)
                                    df = df[df['TYPE']!='|'] # delete empty rows
                                    df = df[df['TYPE']!= 'During handling of the above exception, another exception occurred:'] # delete empty rows
                                    df = df.reset_index(drop=True) # resetting indexes after deletion
                                    df['PC-TIME']=df['PC-TIME'].apply(lambda x : datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f')) # converting string time to datetime
                                    tempstr = df['+INFO'][df['MSG']=='CREATOR-NAME'].values[0]
                                    experimenter = tempstr[2:tempstr[2:].find('"')+2]
                                    tempstr = df['+INFO'][df['MSG']=='SUBJECT-NAME'].values[0]
                                    subject = tempstr[2:tempstr[2:].find("'")+2]
                                    df['experimenter'] = experimenter
                                    df['subject'] = subject
                                    df['project'] = projectname.name
                                    df['experiment'] = experimentname.name
                                    df['setup'] = setupname.name
                                    df['session'] = sessionname.name
                                    # adding trial numbers and trial types
                                    idx = (df[df['TYPE'] == 'TRIAL']).index.to_numpy()
                                    idx = np.concatenate(([0],idx,[len(df)]),0)
                                    idxdiff = np.diff(idx)
                                    Trialnum = np.array([])
                                    for i,idxnumnow in enumerate(idxdiff): #zip(np.arange(0:len(idxdiff)),idxdiff):#
                                        Trialnum  = np.concatenate((Trialnum,np.zeros(idxnumnow)+i),0)
                                    df['Trial_number'] = Trialnum
                                    # adding trial types
                                    indexes = df[df['MSG'] == 'Trialtype:'].index+2
                                    if len(indexes)>0:
                                        if 'Trialtype' not in df.columns:
                                            df['Trialtype']=np.NaN
                                        trialtypes = df['MSG'][indexes]
                                        trialnumbers = df['Trial_number'][indexes].values
                                        for trialtype,trialnum in zip(trialtypes,trialnumbers):
                                            df['Trialtype'][df['Trial_number'] == trialnum] = trialtype
                                    # saving variables (if any)
                                    variableidx = (df[df['MSG'] == 'Variables:']).index.to_numpy()
                                    if len(variableidx)>0:
                                        d={}
                                        exec('variables = ' + df['MSG'][variableidx+2].values[0], d)
                                        for varname in d['variables'].keys():
                                            if isinstance(d['variables'][varname], (list,)):
                                                templist = list()
                                                for idx in range(0,len(df)):
                                                    templist.append(d['variables'][varname])
                                                df['var:'+varname]=templist
                                            else:
                                                df['var:'+varname] = d['variables'][varname]
                                    # saving variables (if any)
                                    variableidx = (df[df['MSG'] == 'LickportMotors:']).index.to_numpy()
                                    if len(variableidx)>0:
                                        d={}
                                        exec('variables = ' + df['MSG'][variableidx+2].values[0], d)
                                        for varname in d['variables'].keys():
                                            df['var_motor:'+varname] = d['variables'][varname]
                                    if len(bigtable) == 0:
                                        bigtable = df
                                    else:
                                        for colname in df.columns:
                                            if colname not in bigtable.columns:
                                                bigtable[colname]=np.NaN
                                        for colname in bigtable.columns:
                                            if colname not in df.columns:
                                                df[colname]=np.NaN
                                        bigtable = bigtable.append(df)
    bigtable = bigtable.drop_duplicates(subset=['TYPE', 'PC-TIME', 'MSG', '+INFO'])
    if len(bigtable) != len(bigtable_orig):
        bigtable = bigtable.reset_index(drop=True)                                
    return bigtable
#%%
#bigtable = loadcsvdata(projectdir = '/home/rozmar/Data/Behavior/Projects')

#%%
#df = bigtable

    
