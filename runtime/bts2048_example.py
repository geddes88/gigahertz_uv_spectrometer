import ctypes
import time
# load BTS2048 Dll
DLLIMPORT = ctypes.WinDLL("GOMDBTS2048.dll")


#device_list = DLLIMPORT["GOMDBTS2048_getDeviceList"]
#device_list.restype = ctypes.POINTER(ctypes.c_int * 10)
#print [i for i in device_list().contents] 
#setPassword
setPassword = DLLIMPORT["GOMDBTS2048_setPassword"]
setPassword.restype = ctypes.c_int
setPassword.argtype = ctypes.c_char_p
setPassword(b"dk483g92")

#getHandle
getHandle = DLLIMPORT["GOMDBTS2048_getHandle"]
getHandle.restype = ctypes.c_int
getHandle.argtypes = (ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))


cw=DLLIMPORT['GOMDBTS2048_getCenterWavelength']
cw.restype=ctypes.c_int
cw.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_double))
cw_out=ctypes.c_double();



#raw=DLLIMPORT['GOMDBTS2048_spectralGetCountsPixel']
#raw.restype=ctypes.c_int
#raw.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_double * 2048))
#raw_out=ctypes.c_double * 2048



#releaseHandle
releaseHandle = DLLIMPORT["GOMDBTS2048_releaseHandle"]
releaseHandle.restype = ctypes.c_int
releaseHandle.argtype = ctypes.c_int

#actual program

#search for connected device
handle = ctypes.c_int(0);
print handle
rc = getHandle(b"BTS2048_0", ctypes.byref(handle))
print handle
print rc
if (rc == 0):
    print 'doing something'
    measurement=DLLIMPORT["GOMDBTS2048_measure"]
    measurement.restype = ctypes.c_int
    measurement.argtypes = [ctypes.c_int]
    measurement(handle)
    bob=cw(handle,ctypes.byref(cw_out))
    jim=raw(handle,np.frombuffer(raw_out))
    print cw_out
   # time.sleep(10)
    
#    cw.restype=ctypes.c_int
#    cw_out=ctypes.c_int(1)
#    cw.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_int))
#    
#    print cw_out

#    cw.restype=ctypes.c_void_p
#    s=cw(handle)
#    s = ctypes.cast(s,ctypes.POINTER(ctypes.c_double))
#    print(s.value )
    #cc = array(frombuffer(cw, dtype=float64, count=1))
   # print cc
#    double cwValue = 0.0;
#            bts2048.getCWValue(out cwValue);
#            System.Console.WriteLine(cwValue);
#    raw=DLLIMPORT['GOMDBTS2048_spectralGetCountsPixel']
#    raw.restype = ctypes.POINTER(ctypes.c_int * 2048)
#    raw.argtypes = [ctypes.c_int]
#    print [ i for i in raw(handle).contents]
    #print 'raw', raw(handle)
 

    releaseHandle(handle)
