#include "BTS2048Import.h"
#include <iostream>

int main(int argc, char* argv[])
{
	BTS2048Import bts2048;

	//search for a BTS2048 device
	//first you have to replace the right password in the BTS2048Import.cpp
	int error = bts2048.init("BTS2048_0");
	if (error == 0)
	{
		char userinput[10];
		//write all available calibration entries to the console
		bts2048.writeCalibrationInfoToConsole();

		//let the user choose a calibration
		std::cout << "Please choose a calibration number:";
		std::cin.getline(userinput, 10);
		bts2048.setCalibrationEntry(atoi(userinput));

		//set measurement mode and start a new measurement
		//dynamicTimeMode = true
		//offsetMode = 0
		//spectralIntegrationTime = 50ms
		bts2048.setSpectralMeasurementMode(true, 0, 50000);
		error = bts2048.measure();
		
		//if no error occured read the integral values
		if (error == 0)
		{
			double value;
			char unit[2048];
			bts2048.integralGetValues(&value, unit);
			std::cout << "integral sensor = " << value << " " << unit << std::endl;
		}
		else
		{
			std::cout << "error occured: " << error << std::endl;
		}
		bts2048.close();
	}
	else
	{
		std::cout << "error occured: " << error << std::endl;
	}
	system("PAUSE");
}

