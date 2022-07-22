import pandas as pd
import numpy as np
import wradlib as wrl
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import re
import sys
import os
import moviepy.video.io.ImageSequenceClip

# Helper function to make a video.
def makevideo(image_folder,video_name):
    fps=1
    image_files = [os.path.join(image_folder,img)
                for img in os.listdir(image_folder)
                if img.endswith(".png")]
    
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(image_folder+'.mp4')

# Helper function to sort the files.
def sorted_nicely( l ):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

import warnings
warnings.filterwarnings('ignore')
try:
    get_ipython().magic("matplotlib inline")
except:
    plt.ion()
fig = plt.figure(figsize=(20,20))
import os
import math
import plotly.express as px
import pandas as pd

def convertlat(row,lat1,lon1,azi):
    R = 6378.1 
    d = row['rng']
    brng = math.radians(azi) 
    
    lat1 = math.radians(lat1) 
    lon1 = math.radians(lon1) 

    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
        math.cos(lat1)*math.sin(d/R)*math.cos(brng))

    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),
                math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)

    return lat2
def convertlon(row,lat1,lon1,azi):
    R = 6378.1 
    d = row['rng']
    brng = math.radians(azi) 
    
    lat1 = math.radians(lat1) 
    lon1 = math.radians(lon1) 

    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
        math.cos(lat1)*math.sin(d/R)*math.cos(brng))

    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),
                math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)

    return lon2

 


def convertionfunction(data,sweep,azi,rng,latitude,longitude):
    # Range is in meter. Convert range to kilometer by dividing 1000.
    rng = rng/1000
    datalat = pd.DataFrame()
    datalon = pd.DataFrame()
    
    
    datalat['rng'] = rng
    datalon['rng'] = rng
    count=0
    # Iterate through azi.

    for loop in azi:
        count=count+1
        datalat['lat'+"angle"+str(count)] = datalat.apply(convertlat, args=(latitude, longitude,loop),axis=1)
        datalon['lon'+"angle"+str(count)] = datalon.apply(convertlon, args=(latitude, longitude,loop),axis=1)
    
    del datalat['rng']
    del datalon['rng']

    latvalues = datalat.values.transpose()
    latvalues = latvalues.reshape(1,latvalues.shape[0]*latvalues.shape[1])
    
    lonvalues = datalon.values.transpose()
    lonvalues = lonvalues.reshape(1,lonvalues.shape[0]*lonvalues.shape[1])
    
    data['lat'] =  latvalues.tolist()[0]
    data['lon'] = lonvalues.tolist()[0]
 
    data.to_csv("Sweepnumber_"+str(sweep)+".csv")
    
    
def changecoordinatesystem(outdict):
    # Read the data.
    latitude = outdict['variables']['latitude']['data']
    longitude = outdict['variables']['longitude']['data']

    # Read the range parameter.
    r = outdict['variables']['range']['data']
    # Read the number of sweeps.
    nsweeps = outdict['variables']['sweep_number']['data']
    # Read sweep start ray index.
    ssidx = outdict['variables']['sweep_start_ray_index']['data']
    # Read sweep end ray index.
    seidx = outdict['variables']['sweep_end_ray_index']['data']
    # Read the angel.
    sazi = outdict['variables']['azimuth']['data']
    alldata = pd.DataFrame()
    azi = {}
    rng = {}
    
    # For each sweep, read the information and store it in the dictionary.
    listof2Dvariables = []
     
    # Extract all the variables which has 2 dimensions.
    for key, value in outdict['variables'].items(): 
        if len(value['data'].shape) == 2:
            listof2Dvariables.append(key)
   
    # Iterate through each sweeps.
    for loop in range(0,len(nsweeps)):
        alldata=pd.DataFrame()
        for loop2 in listof2Dvariables:
            temp = outdict['variables'][loop2]['data'][ssidx[loop]:seidx[loop],:]  
            temp = np.array(temp)
            alldata[loop2] = temp.reshape(1,temp.shape[0]*temp.shape[1]).tolist()[0]
        
        azi[loop] = sazi[ssidx[loop]:seidx[loop]]
        rng[loop] = r
        convertionfunction(alldata,loop,azi[loop],rng[loop],latitude,longitude)

    


coordinates = changecoordinatesystem(wrl.io.read_generic_netcdf('cfrad.20201201_000407_to_20201201_000954_OMAD_Idle.nc'))




