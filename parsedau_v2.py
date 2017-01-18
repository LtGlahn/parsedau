# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 08:33:26 2016

@author: jajens
"""
import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb

class daufil():
    """Class for holding info from a single DAU file"""
    
    def __init__(self, filename):
        self.rawdata = self.readfile(filename)
        self.numvehicles = 0
        self.data = []
        self.datatemplate = { 'vehicleid' : None, 
                              'df' : None, # Data frame 
                              'datostempel' : None, 
                              'rectype' : None,
                              'datalist' : [] # List of tuples with data records
                            }
        
        
        self.parse()
        
    def readfile(self, filename):
        self.filename = filename
        with open( filename) as f: 
            rawdata = f.readlines()
        return rawdata

    def removeempty(self): 
        pass
    
#df.drop(df.columns[[21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]],axis=1, inplace=True)
#df.dtypes
#df.drop('data36', axis=1, inplace=True)
#df.drop('data37', axis=1, inplace=True)
#df.drop('data38', axis=1, inplace=True)
#df.drop('data39', axis=1, inplace=True)
#df.drop('data40', axis=1, inplace=True)
        
        
    def createdataframe(self, workingdata ): 
        
        
        colnames = getcolnames(workingdata['rectype'])
        tempdf = pd.DataFrame.from_records( 
                workingdata['datalist'], 
                columns = colnames, coerce_float = True)
            
        # Converting to numbers 
        if workingdata['rectype'] == '931108': 
            
            tempdf[['distdrive', 'velocity', 'dry_spreader_on_km', 
                    'dry_spread_w_cm', 'dry_spread_dose', 
                    'liquid_material_percent', 'total_dry_kg', 
                    'total_dry_liquid_931002', 'liquid_spread_w_cm', 
                    'liquid_spread_dose', 'total_liquid_liter', 
                    'liquid_spreader_on_km' ]] = tempdf[[ 'distdrive', 
                    'velocity', 'dry_spreader_on_km', 
                    'dry_spread_w_cm', 'dry_spread_dose', 
                    'liquid_material_percent', 'total_dry_kg', 
                    'total_dry_liquid_931002', 'liquid_spread_w_cm', 
                    'liquid_spread_dose', 'total_liquid_liter', 
                    'liquid_spreader_on_km']].apply(pd.to_numeric, 
                            errors='ignore')
                    
        tempdf['tid'] = tempdf['tid'].apply(pd.to_datetime, errors='ignore')

        return tempdf

        
    def parse(self):
        """Leser og dekoder DAU-data fra fil"""

    # Leser datostempel fra header. 
        (code, code2, dato, tid, junk1, junk2, junk) = \
                                  self.rawdata[1].split(sep=';')  

        self.datostempel = tid2streng(dato, tid)
        if junk1: 
            print("interesting info found DAU header line 1 pos 5", junk1)
        if junk2: 
            print("interesting info found DAU header line 1 pos 2", junk2)
          
        for line in self.rawdata[2:len(self.rawdata)]:
            line = line.replace(',', '.').rstrip()
            if line[0:7] == '931100;':
                (junk, dato, tid, vehicleid, junk) = line.split(sep=';')
                self.numvehicles += 1
                workingdata = copy.deepcopy( self.datatemplate)
                workingdata['vehicleid'] = vehicleid
                workingdata['datostempel'] = tid2streng( dato, tid)

                
            elif line[0:7] == '931108;': 
                
                datarec = line.split(sep=';')
 
                if not workingdata['rectype']: 
                    workingdata['rectype'] = datarec[0]
                elif workingdata['rectype'] != datarec[0]: 
                    message = ','.join([ 'Mixed record types!', 
                                        str(datarec[0]), 
                                        str(workingdata['rectype']) ] )  
                    raise ValueError(message)
                
                
                # Konverter radianer => grader
                datarec[4] = np.degrees( float(datarec[4]))
                datarec[5] = np.degrees( float(datarec[5]))
                
                tid = tid2streng(datarec[1], datarec[2] )
                (fylke, katstat, vegnr, hp, meter) = datarec[34].split(sep='-')
                vegkat = katstat[0]
                vegstat = katstat[1]
                datarec.extend( [tid, workingdata['vehicleid'], 
                                 fylke, vegkat, vegstat, vegnr, hp, meter, 
                                 self.filename])

                # Føyer record til listen 
                workingdata['datalist'].append( tuple(datarec) )

 
                # Føyer på datastrukturen når vi er kommet til slutten av 
                # datacrecord-serien 
                if datarec[3].upper() == 'END': 

                    workingdata['df'] = self.createdataframe( workingdata )
                    self.data.append( workingdata)
                    print( "Har lest en serie, lagrer..")
                
            elif line[0:11] == '0002;931200':
                print( "FERDIG")
                
            else: 
                print( "Ukjent DAU-streng", line)
                
        

def getcolnames( rectype):
    if rectype == '931108':
        colnames = [ 'rectype', 'dato', 'klokke', 'start', 'lat', 
      'lon', 'distdrive', 'velocity', 'dry_spreader_on_km', 'dry_spread_w_cm', 
      'dry_spread_dose', 'liquid_material_percent', 'total_dry_kg', 'total_dry_liquid_931002', 'dry_spreader_on_bool', 
      'ploughworks_bool', 'liquid_spread_w_cm', 'liquid_spread_dose', 'total_liquid_liter', 'liquid_spreader_on_km', 
      'liquid_spreader_on_bool', 'data22', 'data23', 'data24', 'data25', 
      'data26', 'data27', 'data28', 'data29', 'data30', 
      'data31', 'data32', 'data33', 'data34', 'vegref', 
      'data36', 'data37', 'data38', 'data39', 'data40', 
      'tid', 'vehicleid', 'fylke', 'vegkat', 'vegstat', 
      'vegnr', 'hp', 'm', 'filename' ]

    else: 
        raise ValueError( ':'.join([ 'Unknown record type', rectype] ))
                    
    return colnames
                                 
def tid2streng( daudato, dautid): 
    """Formatererer YYYYmmdd, hhmmdd => ISO-streng 'yyyy-mm-ddThh:mm:ss' """
    return daudato[0:4] + '-' + daudato[4:6] + '-' + daudato[6:8] + 'T' + \
            dautid[0:2] + ':' + dautid[2:4] + ':' + dautid[4:6]


    
mindau = daufil('dau-eks-0830-grenland.txt')
