using System;
using System.Threading;
using System.Windows.Forms;
using Gigahertz_Optik;
namespace Program
{
    class Program
    {
        static void Main(string[] args)
        {
            // instantiate and initialize BTS256 measurement device
            // find BTS256 with serial number "14197"
            // please replace with serialnumber of your own device
            MDBTS2048 bts2048 = new MDBTS2048("BTS2048_0");

            // set integration time for integral sensor range
            bts2048.integralSetIntegrationTimeInMs(0, 20);
            bts2048.integralSetIntegrationTimeInMs(1, 20);

            // set integration time for spectrometer device
            bts2048.spectralSetIntegrationTimeInUs(500);

            //perform measurement 
            bts2048.measure();

            // receive cw value from last measurement
            double cwValue = 0.0;
            bts2048.getCWValue(out cwValue);
            System.Console.WriteLine(cwValue);
        }
    }
}
