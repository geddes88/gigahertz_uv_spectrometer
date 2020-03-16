# -*- coding: utf-8 -*-
"""
Created on Thu May 19 11:35:49 2016

@author: geddesag

Title: Brukerpy Development Code Library

Desc.: Library of functions to be used in the brukerpy module, also serves as
a test bed for new ideas
"""


"""

The first bit of code is to calculate the Solar Zenith Angle given a time and
a place. This will then be implemented later. Two examples will be used and 
tested, Pyephem and the code developed in house

"""

from matplotlib.pyplot import *
import datetime
import ephem
import time
import numpy as np
#from default_settings import *
import os.path
import subprocess
import win32com.client
import ConfigParser
from threading import Thread
from scipy.stats import pearsonr
import pandas as pd
import shutil

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return
        
def find_next_time(array,value):
    diff=(array-value)
    for i in range(len(diff)):
        if diff[i]>datetime.timedelta(0,0,0):
            break
    if diff[i]<datetime.timedelta(0,0,0):
        i=-1
    return i
def align_spectrum(scan,shift):
    """Aligning of the spectrum to the solar reference, this is based on the
    original method, not sure why I cant just interpolate. The shift is hardcoded
    at the moment for each scan, this is because the wvlerr and soalr shift will
    be dependent on better line calculations from BL
    
    This is far faster than interpolation, and now it seems to work well with the new
    alignment calculation"""
    scan=np.array(scan)
    shift=shift#+0.4 """HERE"""
    coarse=int(shift+0.5)
    #print coarse
    if coarse>0:
        for i in range(0,len(scan)-coarse,1):
            scan[i]=scan[i+coarse]
        scan[i:]=scan[-1]
    
    elif coarse<0:
        for i in range(len(scan)-1,0-coarse,-1):
            scan[i]=scan[i+coarse]
        scan[:i]=scan[0]
        
    fine=shift-int(shift+0.5)
    
    #print fine
    if fine!=0:
        d=scan[0]
        for i in range(1,len(scan)-1):
            d1=scan[i]
            scan[i]=((d-2*d1+scan[i+1])*fine+scan[i+1]-d)*fine/2+d1
            d=d1
          
    return scan
    
def solar_shift(ref,scan):
    """Calculate the shift required to the calcium doublet"""

    #scan=list(reversed(list(scan)))
    wav_arr=np.arange(0,len(scan))
    LLOi=9#find_nearest(wav_arr,LLO)
    LHIi=len(scan)-9#find_nearest(wav_arr,LHI)

    """Detrend- find linear slope and remove from array"""
    
    f=np.polyfit(wav_arr[LLOi:LHIi],ref[LLOi:LHIi],1)
    ref_temp=ref-np.polyval(f,wav_arr)
    f=np.polyfit(wav_arr[LLOi:LHIi],scan[LLOi:LHIi],1)
    scan_temp=scan-np.polyval(f,wav_arr)   

    """Make high interpolation versions"""
    x=wav_arr#arange(wav_arr[0],wav_arr[-1]+0.2,0.2)
    #f=interpolate.interp1d(wav_arr,scan_temp,bounds_error=False,fill_value='extrapolate')
    scan_high=scan_temp#f(x)
    
    #f=interpolate.interp1d(wav_arr,ref_temp,bounds_error=False,fill_value='extrapolate')
    ref_high=ref_temp#f(x)
    
#    LLOi=0
#    LHIi=-1
    correlation1=[]
    correlation2=[]

    shiftlim=4
  #  with Timer() as q:
    """Maxmise the correlation between the reference and scan"""
    for i in range(9):
        correlation1.append(pearsonr(ref_high[LLOi:LHIi],scan_high[LLOi+i-shiftlim:LHIi+i-shiftlim])[0])

   # print "max corr",q.secs
    corr=correlation1#(array(correlation1)+array(correlation2))/2.
    max_index=np.argmax(corr)
    
    """Calculate the shift required"""
    coarse=max_index-shiftlim
    if not max_index>=8:
        #print "here"
        fine=(corr[max_index-1]-corr[max_index+1]) / (corr[max_index-1]-2.*corr[max_index]+corr[max_index+1])/2.
    else:
        fine=0
    shift=(coarse+fine)

   # print shift*0.2
    return shift

def config_out(section,config):
    #print "here"
    config=config
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None

    return dict1
    





    
def find_nearest(array,value):
    idx = (abs(array-value)).argmin()
    return idx

def FNR(D,P3):
	#function used by SunZen
	return ((D/P3)-int(D/P3))*P3
 
def get_file_name(now,sza):
    
    year=str(now.year)
    month="%02d" % now.month
    day="%02d" % now.day
    block="%05.d" % 0
    sza="%03d" % sza


    suffix=0
    todayspath=year+month+day
    filepath_out=def_paths_files['datapath']+"\\"+todayspath
    filename_out=year+month+day+"_block_"+block+"_SZA_"+sza+".std"+str(suffix)

    
       
        
    """
    Here we check if the output file already exists, and if it does, it increases the suffix value.
    The limit here is a maximum suffix value of 999, but dont worry, it breaks the loop if it creates an 
    acceptable file name. Probably on suffix value 3 or 4 at most really. 
    """

    while suffix<999:
        filename_out=year+month+day+"_block_"+block+"_SZA_"+sza+".std"+str(suffix)
        if os.path.exists(filepath_out+"\\"+filename_out)==False:
            
            break
        suffix=suffix+1
       # filename_out=year+month+day+"_block_"+block+"_SZA_"+sza+".std"+str(suffix)
    return filepath_out,filename_out

def decdeg2dms(dd):
   is_positive = dd >= 0
   dd = abs(dd)
   minutes,seconds = divmod(dd*3600,60)
   degrees,minutes = divmod(minutes,60)
   degrees = degrees if is_positive else -degrees
   return str(int(degrees))+":"+str(int(minutes))+":"+str(seconds)
   
   
def day_to_date(year,day):
    date_in=datetime.datetime(year, 1, 1) + datetime.timedelta(day - 1)
    return date_in.year,date_in.month,date_in.day
def sunzen_ephem(time,Lat,Lon,psurf,temp):
    
    observer = ephem.Observer()
    observer.lon = decdeg2dms(Lon)
    observer.lat = decdeg2dms(Lat)
    observer.date = time
 
    observer.pressure=psurf
    observer.temp=temp
    sun = ephem.Sun(observer)
   # sun.compute(observer)
    alt_atr = float(sun.alt)
    solar_altitude=180.0*alt_atr/np.pi
    solar_zenith=90.0-solar_altitude
    solar_azimuth=180*float(sun.az)/np.pi
    return solar_zenith, solar_azimuth

def format_countdown(timedelta_obj):
    days=timedelta_obj.days
    hours, remainder = divmod(timedelta_obj.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    out =str('%02d:%02d:%02d' % (int(hours), int(minutes), int(seconds)))
    return out           

def format_time(datetime_obj):
    out =str('%02d:%02d:%02d' % (int(datetime_obj.hour), int(datetime_obj.minute), int(datetime_obj.second)))
    return out

def dict_to_panda(dictionary):
    panda_out=pd.DataFrame()
    for key in dictionary.keys():
        panda_out[key]=[dictionary[key]]
    return panda_out

            

def dynamic_schedule(lat,lon,utc_offset,psurf,temp,twilight_minsza,twilight_maxsza,normal_step,twilight_step):

    """read schedule 'a' and compute an expected time schedule based on the szas and times required
    """
    time_utc=datetime.datetime.utcnow()
   
    time_local=time_utc+datetime.timedelta(hours=utc_offset)
    
    times_local=[]
    sza_ref=[] 
    times_utc=[]
    
    for i in range(86400):
        times_utc.append(datetime.datetime(time_local.year,time_local.month,time_local.day,0,0,0)+datetime.timedelta(seconds=i)-datetime.timedelta(hours=utc_offset))
        sza_ref.append(sunzen_ephem(times_utc[i],lat,lon,psurf,temp)[0])
        times_local.append(times_utc[i]+datetime.timedelta(hours=utc_offset))

    sza_time_local=[]
    high_sun_idx=np.where(np.array(sza_ref)==min(np.array(sza_ref)))[0][0]
    low_sun_idx=np.where(np.array(sza_ref)==max(np.array(sza_ref)))[0][0]
    high_sun_sza=sza_ref[high_sun_idx]
    low_sun_sza=sza_ref[low_sun_idx]
    high_sun_time=format_time(times_local[high_sun_idx].time())
    low_sun_time=format_time(times_local[low_sun_idx].time())
    
    morning_stop=high_sun_idx-3600
    afternoon_start=high_sun_idx+3600

   # start_time=find_nearest(array(sza_ref[0:high_sun_idx]),start_obs)
   # stop_time=find_nearest(array(sza_ref[high_sun_idx:]),stop_obs)+high_sun_idx
    sunrise_idx=find_nearest(np.array(sza_ref[0:high_sun_idx]),90.0)
    sunset_idx=find_nearest(np.array(sza_ref[high_sun_idx:]),90.0)+high_sun_idx
    sunrise_s=sza_ref[sunrise_idx]
    sunset_s=sza_ref[sunset_idx]
    
    sunrise=times_local[sunrise_idx]
    sunset=times_local[sunset_idx]
    
    
    day_length=str(times_local[sunset_idx]-times_local[sunrise_idx])
    
    """Last little thing, may or may not be useful. if nearest value to 90 is above 91 or below 89, 
    the sun is permanently set or risen. So I return an n/a value for the formatted string."""
    
    if sunrise_s<=89 or sunrise_s>=91.:
        sunrise="n/a"
        day_length="n/a"
    
    if sunset_s<=89 or sunset_s>=91.:
        sunset="n/a"    
        day_length="n/a" 
     
    szas_combined=np.arange(0,95,normal_step)
    #szas2=np.arange(twilight_minsza,twilight_maxsza,twilight_step)
    #szas_combined=np.concatenate((szas,szas2))
    
    schedule_times=[times_local[high_sun_idx]-datetime.timedelta(hours=1),times_local[high_sun_idx]-datetime.timedelta(minutes=45),times_local[high_sun_idx]-datetime.timedelta(minutes=30),times_local[high_sun_idx]-datetime.timedelta(minutes=15),times_local[high_sun_idx],times_local[high_sun_idx]+datetime.timedelta(minutes=15),times_local[high_sun_idx]+datetime.timedelta(minutes=30),times_local[high_sun_idx]+datetime.timedelta(minutes=45),times_local[high_sun_idx]+datetime.timedelta(hours=1)]
    task_ids=[sza_ref[high_sun_idx-3600],sza_ref[high_sun_idx-2700],sza_ref[high_sun_idx-1800],sza_ref[high_sun_idx-900],sza_ref[high_sun_idx],sza_ref[high_sun_idx+900],sza_ref[high_sun_idx+1800],sza_ref[high_sun_idx+2700],sza_ref[high_sun_idx+3600]]

    
    for sza in szas_combined:
        if sza>sza_ref[morning_stop]:
            index_1=find_nearest(np.array(sza_ref[0:morning_stop]),sza)
            schedule_times.append(times_local[index_1])
            task_ids.append(sza)
            index_2=find_nearest(np.array(sza_ref[afternoon_start:]),sza)
            schedule_times.append(times_local[index_2+afternoon_start])
            task_ids.append(sza)
    #time.sleep(120)
    schedule_times,task_ids=zip(*sorted(zip(schedule_times,task_ids)))
    schedule_times=np.array(schedule_times)
    task_ids=np.array(task_ids)
    return high_sun_time, high_sun_sza, low_sun_time, low_sun_sza, sunrise, sunset,day_length, schedule_times,task_ids
    
