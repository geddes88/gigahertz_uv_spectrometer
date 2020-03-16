import ctypes

# load BTS2048 Dll
DLLIMPORT = ctypes.WinDLL("C:\\Gigahertz-Optik\\runtimeX64\\GOMDBTS2048.dll")

#setPassword
setPassword = DLLIMPORT["GOMDBTS2048_setPassword"]
setPassword.restype = ctypes.c_int
setPassword.argtype = ctypes.c_char_p

#getHandle
getHandle = DLLIMPORT["GOMDBTS2048_getHandle"]
getHandle.restype = ctypes.c_int
getHandle.argtypes = (ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))

#releaseHandle
releaseHandle = DLLIMPORT["GOMDBTS2048_releaseHandle"]
releaseHandle.restype = ctypes.c_int
releaseHandle.argtype = ctypes.c_int

#actual program
setPassword(b"****")

#search for connected device
handle = ctypes.c_int(0);
rc = getHandle(b"BTS2048_0", ctypes.byref(handle))
if (rc == 0):
	#do something
	releaseHandle(handle)
