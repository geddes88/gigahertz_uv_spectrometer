# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 13:25:38 2017

@author: geddesag
"""

import tkinter as tk
import pygubu
import datetime
import library
import threading
import matplotlib.pyplot as plt
from library import *#dynamic_schedule, format_time,sunzen_ephem,get_file_name,config_out
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random
from matplotlib.pyplot import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from command_library import *
from PIL import ImageTk, Image
import queue
from timeit import default_timer as timer

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')




class Application:
    
    def __init__(self,giga):
        self.giga=giga
        self.root = tk.Tk()
        self.root.title('GigaPy v1.0')
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        #1: Create a builder
        self.builder = builder = pygubu.Builder()
        self.load_flag=0
        self.setup=0
        self.lock=threading.Lock()
        #2: Load an ui file
        builder.add_from_file('main_window.ui')

        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('mainwindow', self.root)
        
        # Current Info Objects - Maybe put into class or dict?
        self.utctime_entry=builder.get_object('utctime_entry',self.root)
        self.localtime_entry=builder.get_object('localtime_entry',self.root)
        self.sza_entry=builder.get_object('sza_entry',self.root)
        self.saz_entry=builder.get_object('saz_entry',self.root)
        self.countdown_entry=builder.get_object('countdown_entry',self.root)
        self.task_sza_entry=builder.get_object('task_sza_entry',self.root)
        self.countdown_entry.config({"background": "Red"})
        self.task_sza_entry.config({"background": "Red"})
        
        # Daily Info Objects
        
        self.high_sun_sza_entry=builder.get_object('high_sun_sza_entry',self.root)
        self.high_sun_time_entry=builder.get_object('high_sun_time_entry',self.root)
        self.low_sun_sza_entry=builder.get_object('low_sun_sza_entry',self.root)
        self.low_sun_time_entry=builder.get_object('low_sun_time_entry',self.root)
        self.sunrise_entry=builder.get_object('sunrise_entry',self.root)
        self.sunset_entry=builder.get_object('sunset_entry',self.root)
        self.day_length_entry=builder.get_object('day_length_entry',self.root)
   
        #Command log objects
   
        self.log_out_text=builder.get_object('log_out_text',self.root)
        self.log_out_scrollbar=builder.get_object('log_out_scrollbar',self.root)
        self.log_out_text.config(yscrollcommand=self.log_out_scrollbar.set)
        self.log_out_scrollbar.config(command=self.log_out_text.yview)
        self.current_status_label=builder.get_object('current_status_label',self.root)
        
        #Buttons
        
        self.schedule_run_button=builder.get_object('routine_obs_button',self.root)
        self.manual_scan_button=builder.get_object('manual_scan_button',self.root)
        self.scan_prop_button=builder.get_object('scan_prop_button',self.root)
        self.comment_button=builder.get_object('comment_button',self.root)
        self.guide_button=builder.get_object('guide_button',self.root)
        self.comment_button.config(command=self.user_entry)
        self.hd_checkbutton=builder.get_object('hd_checkbutton')
        self.high_density_mode = tk.BooleanVar()
        self.high_density_mode.set('true'==scan_prop_defaults['high_density'].lower())
        self.hd_checkbutton.config(variable=self.high_density_mode)
        
        #self.image_label=builder.get_object('image_canvas',self.root)

       # self.set_eht_button.config(command=self.jy.set_eht)
        self.sza=-1
        self.manual_scan_button.config(command=lambda: self.make_scheduled_meas(self.sza,mode="manual"))
        self.schedule_run_button.config(command=self.toggle_schedule_run)
        self.scan_prop_button.config(command=self.open_properties)

        self.plot_window=FigureCanvasTkAgg(f,self.root)
        self.plot_window.draw()
        self.plot_window.get_tk_widget().grid(column=1,row=0)
        self.schedule_status=0
        self.task_run=0
        toolbar_frame=tk.Frame(self.root)
        toolbar_frame.grid(row=1,column=1,sticky='w')
        toolbar=NavigationToolbar2Tk(self.plot_window,toolbar_frame)
        toolbar.update()
        self.reset_flag=1

        # self.t2=threading.Thread(target=self.threaded_solar)
        # self.t2.start()


        self.nscans = tk.IntVar()
        self.manual_int = tk.IntVar()
        self.dyn_set_int = tk.BooleanVar()
        self.delay= tk.DoubleVar()
        self.hdnscans = tk.IntVar()

        self.reset_time=datetime.datetime.utcnow()+datetime.timedelta(hours=int(site['timezone']))+datetime.timedelta(hours=24)
        self.reset_time=self.reset_time.replace(hour=1,minute=0,second=0)

        self.delay.set(float(scan_prop_defaults['delay']))
        self.nscans.set(int(scan_prop_defaults['nscans']))
        self.manual_int.set(int(scan_prop_defaults['manual_int']))
        self.dyn_set_int.set('true'==scan_prop_defaults['dynamic_int'].lower())
        self.hdnscans.set(int(scan_prop_defaults['hdnscans']))
        self.threaded_solar()

#        self.giga=gigahertz()
        giga.dynamic_time_mode=self.dyn_set_int.get()
        giga.integration_time=self.manual_int.get()
       # print(giga.dynamic_time_mode)
       # self.toggle_schedule_run()
        self.update_clock_main()
        self.root.mainloop()
        

    def open_properties(self):
        self.root3 = tk.Toplevel()
        self.root3.wm_title('Measurement Properties')
        self.builder = builder = pygubu.Builder()
        builder.add_from_file('properties.ui')
        self.propwindow = builder.get_object('prop_window', self.root3)
        self.root3.protocol('WM_DELETE_WINDOW', self.on_close2)
        
        self.dyn_set_int_checkbutton=builder.get_object('dynintcheckbutton',self.root3)
        self.manualintentry=builder.get_object('manualintentry',self.root3)
        self.nscansentry=builder.get_object('nscansentry',self.root3)
        self.delayentry=builder.get_object('delayentry',self.root3)
        self.hdnscansentry=builder.get_object('hdnscansentry',self.root3)
        self.commitbutton=builder.get_object('propcommitbutton',self.root3)
        self.resetbutton=builder.get_object('resetbutton',self.root3)
        
        #self.auto_set_eht_temp=self.auto_set_eht

        self.delay_t= tk.DoubleVar()
        self.delay_t.set(self.delay.get())

        self.nscans_t = tk.IntVar()
        self.nscans_t.set(self.nscans.get())
        
        self.hdnscans_t = tk.IntVar()
        self.hdnscans_t.set(self.hdnscans.get())
        
        self.manual_int_t = tk.DoubleVar()
        self.manual_int_t.set(self.manual_int.get())

        self.dyn_set_int_t = tk.BooleanVar()
        self.dyn_set_int_t.set(self.dyn_set_int.get())
        self.dyn_set_int_checkbutton.config(variable=self.dyn_set_int_t)
        self.manualintentry.config(textvariable=str(self.manual_int_t))
        self.nscansentry.config(textvariable=str(self.nscans_t))
        self.delayentry.config(textvariable=str(self.delay_t))
        self.hdnscansentry.config(textvariable=str(self.hdnscans_t))

        self.commitbutton.config(command=self.commit_properties)
        self.resetbutton.config(command=self.default_properties)
     
        
    def commit_properties(self):
        self.dyn_set_int.set(self.dyn_set_int_t.get())
        self.nscans.set(self.nscans_t.get())
        self.nscans.set(self.hdnscans_t.get())

        self.delay.set(self.delay_t.get())
        self.manual_int.set(self.manual_int_t.get())   
        self.write_output('Setting the following;\n Dynamic Integration - '+str(self.dyn_set_int.get())+'\n Number of Scans - '+str(self.nscans.get())+'\n High Density Number of Scans - '+str(self.hdnscans.get())+'\n Manual Integration Time  (if used) - '+str(self.manual_int.get())+'\n Time between Scans - '+str(self.delay.get()))
        
    def default_properties(self):
        self.nscans_t.set(int(scan_prop_defaults['nscans']))
        self.manual_int_t.set(float(scan_prop_defaults['manual_int']))
        self.syn_set_int_t.set('true'==scan_prop_defaults['dynamic_int'].lower())
        self.hdnscans_t.set(int(scan_prop_defaults['hdnscans']))
        self.delay_t.set(int(scan_prop_defaults['delay']))

    
    def on_close(self):
        """Function to decide what to do when the gui is closed"""
        print('closing')
       # giga.close_instrument()
        self.root.destroy()
    
    def on_close2(self):
        """Function to decide what to do when the gui is closed"""
        print('closing')

        self.root3.destroy()


    def toggle_schedule_run(self):
        """Turns the schedule on and off and reload the schedule if it has changed
        type"""

        if self.schedule_status==1:        
            self.schedule_run_button.config(text="Start Schedule")
            self.schedule_status=0
            self.write_output("Schedule Stopped")
            self.countdown_entry.config({"background": "Red"})
            self.task_sza_entry.config({"background": "Red"})
        elif self.schedule_status==0:
            self.write_output("Schedule Started")
            self.countdown_entry.config({"background": "Green"})
            self.task_sza_entry.config({"background": "Green"})

            self.schedule_run_button.config(text="Stop Schedule")
            if giga.setup==0:
                self.write_output("Setting up Gigahertz")
                t3=threading.Thread(target=giga.setup_measurement)
                t3.start()
                while t3.isAlive():
                    self.update_clock()
                    self.root.update()
                    time.sleep(0.2)
                self.write_output("Setup Complete")
            self.schedule_status=1   

        

    def threaded_solar(self):
        
       # self.high_sun_time,self.high_sun_sza,self.low_sun_time,self.low_sun_sza,self.sunrise,self.sunset,self.day_length, self.schedule,self.tasks_out=dynamic_schedule(float(site['latitude']),float(site['longitude']),float(site['timezone']),float(site['pressure']),float(site['temperature']),float(site['twilight_minsza']),float(site['twilight_maxsza']),float(site['normal_step']),float(site['twilight_step']))
        
        t2=ThreadWithReturnValue(target=dynamic_schedule,args=(float(site['latitude']),float(site['longitude']),float(site['timezone']),float(site['pressure']),float(site['temperature']),float(site['twilight_minsza']),float(site['twilight_maxsza']),float(site['normal_step']),float(site['twilight_step'])))
        t2.start()
        
        while t2.isAlive():
            self.update_clock()
            self.root.update()
            time.sleep(0.2)
        self.high_sun_time,self.high_sun_sza,self.low_sun_time,self.low_sun_sza,self.sunrise,self.sunset,self.day_length, self.schedule,self.tasks_out=t2.join()
        
        
        for i in range(len(self.schedule)):
            self.schedule[i]=self.schedule[i]-datetime.timedelta(seconds=int(scan_prop_defaults['t_meas'])/2)
        self.high_sun_sza_entry.config(text=(str("%#06.2f" % self.high_sun_sza)))
        self.high_sun_time_entry.config(text=str(self.high_sun_time))
        self.low_sun_sza_entry.config(text=(str("%#06.2f" %  self.low_sun_sza)))
        self.low_sun_time_entry.config(text=str(self.low_sun_time))
        self.sunrise_entry.config(text=str(self.sunrise.time()))
        self.sunset_entry.config(text=str(self.sunset.time()))
        self.day_length_entry.config(text=str(self.day_length))
        self.write_output("Schedule loaded")
        print(self.schedule)
        f.clf()
        f.subplots_adjust(right=0.8,top=0.95,hspace=0.4)
        self.time_series=f.add_subplot(2,1,2)
        plt.setp(self.time_series.xaxis.get_majorticklabels(), rotation=45,ha='right')
        self.time_series.set_ylabel('SZA')
        self.time_series.set_title('Todays Measurements')
        lines1,=self.time_series.plot([],[],'ow',markeredgecolor='k')
        lines2,=self.time_series.plot([],[],'ob',markeredgecolor='k')
        lines3,=self.time_series.plot([],[],'og',markeredgecolor='k')
        lines4,=self.time_series.plot([],[],'oy',markeredgecolor='k')
        lines5,=self.time_series.plot([],[],'or',markeredgecolor='k')
        lines6,=self.time_series.plot([],[],'om',markeredgecolor='k')
        lines7,=self.time_series.plot([],[],'oc',markeredgecolor='k')

        lines=[lines1,lines2,lines3,lines6,lines4,lines5,lines7]
        labels=['Scheduled','Successful Manual','Successful Scheduled','Successful HD','Failed Manual','Failed Scheduled','Failed HD']
        
        self.time_series.plot(self.schedule,self.tasks_out,'-k')
        self.time_series.plot(self.schedule,self.tasks_out,'ow',markeredgecolor='k')
       # self.time_series.xaxis.set_tick_params(rotation=45)
        self.time_series.legend(lines,labels,loc='center right',bbox_to_anchor=(1.275, 0.5))
        self.scan_results=f.add_subplot(2,1,1)
        self.scan_results.set_ylabel('PMT (V)')
        self.scan_results.set_xlabel('Step')
        print('drawing')
        self.plot_window.draw()
        
        self.reset_flag=0
        if self.schedule_status==1:
            self.write_output("Schedule Started")
            self.countdown_entry.config({"background": "Green"})
            self.task_sza_entry.config({"background": "Green"})
        print('done')   
    def update_clock_main(self):
        """Function that calls update clock every 200ms, they are separated to allow
        manual calls of update clock"""
        self.update_clock()
        self.main_loop=self.root.after(100, self.update_clock_main)   
    
    def create_archive(self):
        now=datetime.datetime.now()
        year=str(now.year)
        month="%02d" % now.month
        day="%02d" % now.day
        todayspath=year+month+day 
        
        directories_to_move=os.listdir(def_paths_files['datapath'])
        for directory in directories_to_move:
            if directory!=todayspath and os.path.exists(def_paths_files['arcpath']):
                self.write_output('Moving Directory '+directory)
                to_archive=def_paths_files['datapath']+directory
                shutil.move(to_archive,def_paths_files['arcpath'])
    def update_clock(self):
        now_utc=datetime.datetime.utcnow()
        time_out=format_time(now_utc)
        local_time=now_utc+datetime.timedelta(hours=int(site['timezone']))
        local_time_out=format_time(local_time)
       # print('updating')
        if (self.reset_time-local_time).total_seconds()<0 and self.reset_flag==0 and self.load_flag==0:
            self.reset_flag=1
            self.reset_time=self.reset_time+datetime.timedelta(hours=24)
            self.write_output('Archiving')
            self.create_archive()
            self.log_out_text.delete("1.0",tk.END)
            self.threaded_solar()
            
        self.sza,self.saz=sunzen_ephem(now_utc,float(site['latitude']),float(site['longitude']),float(site['pressure']),float(site['temperature']))

        if self.reset_flag==0 and self.load_flag==0:
            
            self.task_index=find_next_time(np.array(self.schedule),local_time)
            self.next_task_time=self.schedule[self.task_index]
            if self.high_density_mode.get() and self.task_run==0 and self.schedule_status==1 and local_time<self.schedule[-1] and local_time>self.schedule[0]:
                self.write_output('Making High Density Measurement')
                self.make_hd_meas()
                self.write_output('Finished High Density Measurement')
           
            elif self.next_task_time-local_time<=datetime.timedelta(seconds=1) and self.task_run==0 and self.task_index!=-1 and self.schedule_status==1:
                    
                    self.write_output('Running Task')
                    self.make_scheduled_meas(self.tasks_out[self.task_index])
                    self.write_output('Finished Task')
            elif self.task_index==-1 and self.schedule_status==1:
                self.countdown_entry.configure(text="Completed")
                self.countdown_entry.config({"background": "White"})
                self.task_sza_entry.configure(text='n/a')
                self.task_sza_entry.config({"background": "White"})
    

            else:
                self.countdown_entry.configure(text=format_countdown(self.next_task_time-local_time))
                self.task_sza_entry.configure(text="%.2f" % self.tasks_out[self.task_index])


        self.utctime_entry.configure(text=time_out)
        self.localtime_entry.configure(text=local_time_out)
        self.sza_entry.configure(text="%.2f" % self.sza)
        self.saz_entry.configure(text="%.2f" % self.saz)
        #self.root.after(100, self.update_clock)
        #print('finished updating')

    def write_output(self,text):
        """Write text to the output and to the log file"""
        self.timestamp=format_time(datetime.datetime.utcnow()+datetime.timedelta(hours=int(site['timezone'])))    

        self.create_log_file()
        with self.lock:
            self.log=open(self.schedule_pathout,"a")
            self.log.write(self.timestamp+" "+text+"\n")
            self.log.close()
            self.log_out_text.insert("0.0",self.timestamp+" "+text+"\n")
            
    def create_log_file(self):
        now=datetime.datetime.now()
        year=str(now.year)
        month="%02d" % now.month
        day="%02d" % now.day
        hour="%02d" % now.hour
        todayspath=year+month+day   
        self.timestamp=format_time(now)
        self.schedule_pathout=def_paths_files['datapath']+todayspath+"/"+todayspath+".log"
            
        if not os.path.exists(os.path.dirname(self.schedule_pathout)):
            try:
                os.makedirs(os.path.dirname(self.schedule_pathout))
            except:
                pass
            
        if not os.path.exists(self.schedule_pathout):
            f=open(self.schedule_pathout,"a")
            f.write("** weather, other comments\n")
            f.close()

    def user_entry(self):
        """Opens a new window to allow user input"""
        self.user_entry = tk.Toplevel()
        self.user_entry.wm_title("User Entry")
        #self.user_entry.grab_set()
        self.user_entry.focus()
        comment_label=tk.Label(self.user_entry,text="Enter User Comment")
        comment_label.grid(row=0,column=0,sticky=tk.W)
        self.user_comment = tk.Text(self.user_entry,width=80,wrap=tk.CHAR)
        self.user_comment.grid(row=1,column=0,columnspan=2,rowspan=10,sticky=tk.N+tk.S+tk.E+tk.W)
        comment_button=tk.Button(self.user_entry,text="Write",relief="raised",command=self.write_comment,width=16)
        comment_button.grid(row=11,column=1,sticky=tk.E,padx=5,pady=6)   
        
    def write_comment(self):
        """Grab the text from the user comment and write it to the log and screen, destroys
        the window once complete"""
        text=str(self.user_comment.get("1.0","end-1c"))
        self.write_output("## "+text)
        self.user_entry.destroy()
        

        
    def toggle_buttons(self,state):
        self.manual_scan_button.config(state=state)
        self.scan_prop_button.config(state=state)
    
    def make_hd_meas(self):
        """Super high density measurements"""
        self.task_run=1
        start=datetime.datetime.utcnow()+datetime.timedelta(hours=int(site['timezone']))
        self.toggle_buttons('disabled')
        self.write_output("Beginning High Density Measurement")
        self.current_status_label.config(text='Making HD Measurement')
        self.current_status_label.config({"background": "Green"})
        
        if giga.setup==0:
            self.write_output("Setting up Gigahertz")
            t3=threading.Thread(target=giga.setup_measurement)
            t3.start()
            while t3.isAlive():
                self.update_clock()
                self.root.update()
                time.sleep(0.2)
            self.write_output("Setup Complete")

        all_scans=[]
        all_data=pd.DataFrame()
        fail_counts=0

        i=0
        
        self.scan_results.cla()
        self.scan_results.set_title(datetime.datetime.strftime(start,"%Y-%m-%d %H:%M")+", Starting SZA - %.2f" % self.sza)
        colors=cm.jet(np.linspace(0,1,self.hdnscans.get()))
        for i in range(self.hdnscans.get()):
            self.end=datetime.datetime.now()

            self.write_output("Making Scan Number "+str(i+1)+" of "+str(self.hdnscans.get()))
            self.end=datetime.datetime.now()
            que = queue.Queue()
            t3=threading.Thread(target=lambda q, arg1: q.put(giga.acquire_spectra(arg1)), args=(que, self.sza))
            t3.start()

            while t3.isAlive():
                self.update_clock()
                self.root.update()
                time.sleep(0.2)
            self.write_output("Finished Scan Number "+str(i+1)+" of "+str(self.hdnscans.get()))

            measurement_panda=que.get()
            all_data=all_data.append(measurement_panda)
        #    print measurement_panda
            if measurement_panda['rc'][0]==0:
                
                all_scans.append(measurement_panda['raw_pixel_counts'][0])
                sza_in=all_data['sza'].mean()

                self.scan_results.plot(measurement_panda['pixel_wavelengths'][0],measurement_panda['calibrated_pixel_counts'][0],color=colors[i],label="Single Scan")
                self.plot_window.draw()
            else:
                fail_counts+=1
                self.write_output('Scan Failed, RC '+str(measurement_panda['rc'][0])+' - '+measurement_panda['rc_message'][0])

#            
        if len(all_scans)!=0:
            self.write_output("Measurment Complete, "+str(fail_counts)+" Failed Scans")
            self.time_series.plot(start,sza_in,'mo',label='Successful High Density',markeredgecolor='k')
            create_panda_file(def_paths_files['datapath'],all_data,start,sza_in,hd=True)

        else:
            self.write_output("Measurment Failed")
            self.time_series.plot(start,sza_in,'co',label='Failed High Density',markeredgecolor='k')
        self.plot_window.draw()

        self.task_run=0
        self.toggle_buttons('normal')
#
        self.current_status_label.config(text='Current Status: Idle')
        self.current_status_label.config({"background": "White"})
    def make_scheduled_meas(self,sza_in,mode="scheduled"):
        self.task_run=1
        start=datetime.datetime.utcnow()+datetime.timedelta(hours=int(site['timezone']))
        self.toggle_buttons('disabled')
        if mode =="manual":
            self.write_output("Beginning Manual Measurement")
            
            self.current_status_label.config(text='Making Manual Measurement')
            self.current_status_label.config({"background": "Green"})

        else:
            self.write_output("Beginning Scheduled Measurement - SZA = %.2f" % sza_in)

            self.current_status_label.config(text='Making Scheduled Measurement - SZA = %.2f' % sza_in)
            self.current_status_label.config({"background": "Green"})
        if giga.setup==0:
            self.write_output("Setting up Gigahertz")
            t3=threading.Thread(target=giga.setup_measurement)
            t3.start()
            while t3.isAlive():
                self.update_clock()
                self.root.update()
                time.sleep(0.2)
            self.write_output("Setup Complete")

        all_scans=[]
        all_data=pd.DataFrame()
        fail_counts=0
        meas_start=timer()
        meas_end=timer()
        i=0
        while meas_end-meas_start<int(scan_prop_defaults['t_meas']):
        #for i in range(self.nscans.get()):
            wall_start=timer()
            self.end=datetime.datetime.now()

            # ...

            self.write_output("Making Scan Number "+str(i+1)+" of "+str(self.nscans.get()))
            self.end=datetime.datetime.now()
            que = queue.Queue()
            t3=threading.Thread(target=lambda q, arg1: q.put(giga.acquire_spectra(arg1)), args=(que, self.sza))
            t3.start()

            while t3.isAlive():
                self.update_clock()
                self.root.update()
                time.sleep(0.2)
            self.write_output("Finished Scan Number "+str(i+1)+" of "+str(self.nscans.get()))

            measurement_panda=que.get()
            all_data=all_data.append(measurement_panda)
        #    print measurement_panda
            if measurement_panda['rc'][0]==0:
                
                all_scans.append(measurement_panda['calibrated_pixel_counts'][0])
                sza_in=all_data['sza'].mean()

                self.scan_results.cla()
                self.scan_results.set_title(datetime.datetime.strftime(measurement_panda['timestamp_local'][0],"%Y-%m-%d %H:%M")+", Mean SZA - %.2f" % sza_in)
                self.scan_results.plot(measurement_panda['pixel_wavelengths'][0],measurement_panda['calibrated_pixel_counts'][0],'-b',label="Single Scan")
                self.scan_results.plot(measurement_panda['pixel_wavelengths'][0],np.average(all_scans,axis=0),'-r',label="Average")
                self.scan_results.legend(loc='center right',bbox_to_anchor=(1.7, 0.5))
                self.plot_window.draw()
            else:
                fail_counts+=1
                self.write_output('Scan Failed, RC '+str(measurement_panda['rc'][0])+' - '+measurement_panda['rc_message'][0])
            wall_end=timer()
            while wall_end-wall_start<self.delay.get():
                self.update_clock()
                self.root.update()
                time.sleep(0.2)
                wall_end=timer()
            meas_end=timer()
            i=i+1
#                if breaker==1:
#                    break
            #self.write_output("Measurment Complete, Gain = "+str(gain))


#            else:
#                break

#            else:
#                fail_counts+=1
#                self.write_output("Failed to set gain due to low or variable light")
#               # breaker=1
#            
        if len(all_scans)!=0:
            self.write_output("Measurment Complete, "+str(fail_counts)+" Failed Scans")
            if mode =="manual":
                self.time_series.plot(start,sza_in,'bo',label='Successful Manual',markeredgecolor='k')
            else:
                self.time_series.plot(start,sza_in,'go',label='Successful Scheduled',markeredgecolor='k')
            create_panda_file(def_paths_files['datapath'],all_data,start,sza_in)

        else:
            self.write_output("Measurment Failed")
            if mode =="manual":
                self.time_series.plot(start,sza_in,'yo',label='Failed Manual',markeredgecolor='k')
            else:
                self.time_series.plot(start,sza_in,'ro',label='Failed Scheduled',markeredgecolor='k')
        self.plot_window.draw()

        self.task_run=0
        self.toggle_buttons('normal')
#
        self.current_status_label.config(text='Current Status: Idle')
        self.current_status_label.config({"background": "White"})
#        

 




if __name__ == '__main__':
    "Start App!"
    giga=gigahertz()
    config=configparser.ConfigParser()
    config.read('gigapy.ini')
    site=config_out('site',config)
    scan_prop_defaults=config_out('scan',config)
    def_paths_files=config_out('pathsfiles',config)
    app = QtGui.QApplication([])
    f=Figure(figsize=(12.5,9.5),dpi=100)

    Application(giga)

