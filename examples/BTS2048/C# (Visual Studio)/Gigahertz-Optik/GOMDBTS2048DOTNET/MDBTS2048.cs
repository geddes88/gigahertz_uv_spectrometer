using System;
using System.Runtime.InteropServices;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Gigahertz_Optik
{
    public class MDBTS2048 : IDisposable
    {
        private bool disposed = false;
        private int handle = 0;

        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_setPassword(string password);

        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_getHandle(string device, out int handle);

        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_releaseHandle(int handle);

        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_integralSetIntegrationTimeInMs(int handle, int range, int timeInMs);
        
        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_integralGetUnit(int handle, int calibrationEntryNumber, StringBuilder unit);

        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_measure(int handle);
        
        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_getCWValue(int handle, out double value);
        
        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_spectralSetEnabled(int handle, bool enabled);
        
        [DllImport("GOMDBTS2048.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern int GOMDBTS2048_spectralSetIntegrationTimeInus(int handle, int timeInUs);

        public MDBTS2048(string device)
        {
            //set password
            GOMDBTS2048_setPassword("******");
            GOMDBTS2048_getHandle(device, out handle);
        }

        ~ MDBTS2048() {
            Dispose();
        }

        //Implement IDisposable.
        public virtual void Dispose()
        {
            if (!disposed)
            {
                // Free unmanaged objects.
                // Set large fields to null
                GOMDBTS2048_releaseHandle(handle);

                handle = -1;
                disposed = true;
            }
            GC.SuppressFinalize(this);
        }

        public int integralSetIntegrationTimeInMs(int range, int timeInMs)
        {
            return GOMDBTS2048_integralSetIntegrationTimeInMs(handle, range, timeInMs);
        }

        public int integralGetUnit(int calibrationEntryNumber, StringBuilder unit)
        {
            return GOMDBTS2048_integralGetUnit(handle, calibrationEntryNumber, unit);
        }

        public int measure()
        {
            return GOMDBTS2048_measure(handle);
        }

        public int getCWValue(out double value)
        {
            return GOMDBTS2048_getCWValue(handle, out value);
        }

        public int spectralSetEnabled(bool enabled)
        {
            return GOMDBTS2048_spectralSetEnabled(handle, enabled);
        }

        public int spectralSetIntegrationTimeInUs(int timeInUs)
        {
            return GOMDBTS2048_spectralSetIntegrationTimeInus(handle, timeInUs);
        }
    }
}
