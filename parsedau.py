# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 08:33:26 2016

@author: jajens
"""
import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class daufil():
    """Class for holding info from a single DAU file"""
    
    def __init__(self, filename):
        self.rawdata = self.readfile(filename)
        self.numvehicles = 0
        self.data = []
        self.datatemplate = { 'vehicleid' : None, 
                              'df ' : None, # Data frame 
                              'datostempel' : None, 
                              'rectype' : None}
        
        
        self.parse()
        self.rename_dataframes()
        
    def readfile(self, filename):
        self.filename = filename
        with open( filename) as f: 
            rawdata = f.readlines()
        return rawdata

    def rename_dataframes(self):
        """Døper om kolonnenavn på dataframes"""
        

        newnames = { '931108' : { 
                'data9' : 'dry_spreader_on_km', 
                'data10' : 'dry_spread_w_cm', 
                'data11' : 'dry_spread_dose', 
                'data12' : 'liquid_material_percent', 
                'data13' : 'total_dry_kg', 
                'data14' : 'total_dry_liquid_931002 ', 
                'data15' : 'dry_spreader_on_bool', 
                'data16' : 'ploughworks_bool', 
                'data17' : 'liquid_spread_w_cm', 
                'data18' : 'liquid_spread_dose', 
                'data19' : 'total_liquid_liter', 
                'data20' : 'liquid_spreader_on_km', 
                'data21' : 'liquid_spreader_on_bool'
                } 
            }

        
        for (idx, d) in enumerate( self.data):
            self.data[idx]['df'].rename( columns = newnames[d['rectype']], 
                      inplace = True  )
            
        
    def parse(self):
        """Leser og dekoder DAU-data fra fil"""

    # Leser datostempel fra header. 
        (code, code2, dato, tid, junk1, junk2, junk) = \
                                  mindau.rawdata[1].split(sep=';')  

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

                
                workingdata['df'] =  createdataframe() 
                             

                
            elif line[0:7] == '931108;': 
                (rectype, dato, tid, start, latrad, lonrad, \
                 distdrive, velocity, \
                 data9, data10, data11, data12, data13, data14, data15, \
                 data16, data17, data18, data19, data20, \
                 data21, data22, data23, data24, data25, \
                 data26, data27, data28, data29, data30, \
                 data31, data32, data33, data34, vegref, \
                 data36, data37, data38, data39, data40 ) = line.split(sep=';')
                
                (fylke, katstat, vegnr, hp, meter) = vegref.split(sep='-')
                vegkat = katstat[0]
                vegstat = katstat[1]

                if not workingdata['rectype']: 
                    workingdata['rectype'] = rectype
                elif workingdata['rectype'] != rectype: 
                    message = ','.join([ 'Mixed record types!', str(rectype), 
                                        str(workingdata['rectype']) ] )  
                    raise ValueError(message)

                workingdata['df'] = workingdata['df'].append( {'rectype' : rectype,
                                        'vehicleid' : workingdata['vehicleid'], 
                                        'tid' : tid2streng( dato, tid), 
                                        'start' : start, 
                                        'lat' : np.degrees( float(latrad)), 
                                        'lon' : np.degrees( float(lonrad)), 
                                        'distdrive' : float( distdrive), 
                                        'velocity' : float( velocity), 
                                        'data9' : float(data9), 
                                        'data10' : int(data10), 
                                        'data11' : float(data11), 
                                        'data12' : data12, 
                                        'data13' : float(data13),
                                        'data14' : data14, 
                                        'data15' : int( data15), 
                                        'data16' :  data16, 
                                        'data17' : int( data17), 
                                        'data18' : float( data18),
                                        'data19' : float( data19), 
                                        'data20' : float( data20), 
                                        'data21' : int( data21), 
                                        'data22' : data22, 
                                        'data23' : data23,
                                        'data24' : data24, 
                                        'data25' : data25, 
                                        'data26' : data26, 
                                        'data27' : data27, 
                                        'data28' : data28,
                                        'data29' : data29, 
                                        'data30' : data30, 
                                        'data31' : data31, 
                                        'data32' : data32, 
                                        'data33' : data33,
                                        'data34' : data34, 
                                        'vegref' : vegref, 
                                        'data36' : data36, 
                                        'data37' : data37, 
                                        'data38' : data38,
                                        'data39' : data39, 
                                        'data40' : data40, 
                                        'fylke' : fylke, 
                                        'vegkat' : vegkat, 
                                        'vegstat' : vegstat, 
                                        'vegnr' : int(vegnr),
                                        'hp' : int(hp), 
                                        'm' : int(meter)
                                    }, ignore_index = True)
                # Føyer på datastrukturen når vi er kommet til slutten av 
                # datacrecord-serien 
                if start.upper() == 'END': 
                    workingdata['df'] = workingdata['df'].apply(
                            lambda x: pd.to_numeric(x, errors='ignore'))

                    self.data.append( workingdata)
                    print( "Har lest en serie, lagrer..")
                
            elif line[0:11] == '0002;931200':
                print( "FERDIG")
            else: 
                print( "Ukjent DAU-streng", line)

                                 
def tid2streng( daudato, dautid): 
    """Formatererer YYYYmmdd, hhmmdd => ISO-streng 'yyyy-mm-ddThh:mm:ss' """
    return daudato[0:4] + '-' + daudato[4:6] + '-' + daudato[6:8] + 'T' + \
            dautid[0:2] + ':' + dautid[2:4] + ':' + dautid[4:6]

def createdataframe():
    
    mydf =  pd.DataFrame(np.zeros(0, dtype=[
                            ('rectype', 'i4'), 
                            ('vehicleid', 'i4'),
                            ('tid', 'M' ), 
                            ('start', 'a5'), 
                            ('lat', 'f8'), 
                            ('lon', 'f8'), 
                            ('distdrive', 'f8'), 
                            ('velocity', 'f8'), 
                            ('data9', 'f8'), 
                            ('data10', 'f8'),
                            ('data11', 'f8'),
                            ('data12', 'f8'),
                            ('data13', 'f8'),
                            ('data14', 'f8'), 
                            ('data15', 'f8'),
                            ('data16', 'f8'),
                            ('data17', 'f8'),
                            ('data18', 'f8'), 
                            ('data19', 'f8'),
                            ('data20', 'f8'),
                            ('data21', 'f8'),
                            ('data22', 'f8'), 
                            ('data23', 'f8'),
                            ('data24', 'f8'),
                            ('data25', 'f8'),
                            ('data26', 'f8'), 
                            ('data27', 'f8'),
                            ('data28', 'f8'),
                            ('data29', 'f8'),
                            ('data30', 'f8'), 
                            
                            ('data31', 'f8'),
                            ('data32', 'f8'), 
                            ('data33', 'f8'),
                            ('data34', 'f8'),
                            ('vegref', 'a25'),
                            ('data36', 'f8'), 
                            ('data37', 'f8'),
                            ('data38', 'f8'),
                            ('data39', 'f8'),
                            ('data40', 'f8'), 
                            ('fylke', 'i4'),
                            ('vegkat', 'a1'),
                            ('vegstat', 'a1'), 
                            ('vegnr', 'i4'),
                            ('hp', 'i4'),
                            ('m', 'i4')
                                                        
                            ]))
    
    return mydf
    
mindau = daufil('dau-eks-0830-grenland.txt')
