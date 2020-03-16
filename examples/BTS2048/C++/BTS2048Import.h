#ifndef BTS2048ImportH
#define BTS2048ImportH

#include <Windows.h>
#include "stdio.h"
#include <iostream>

class BTS2048Import
{
public:
	BTS2048Import();
	virtual ~BTS2048Import();
	int __stdcall init(char* deviceName);
	int __stdcall close();
	int __stdcall writeCalibrationInfoToConsole();
	int __stdcall setCalibrationEntry(int value);
	int __stdcall setSpectralMeasurementMode(bool dynamicTimeMode, int offsetMode, int integrationtime);
	int __stdcall integralGetValues(double* value, char* unit);
	int __stdcall measure();

private:
	int handle;
	HINSTANCE hDLLGOBTS2048;
	bool __stdcall getProcAddresses(HINSTANCE *p_hLibrary, const char* p_dllName, int p_count, ...);

	int(__stdcall *GOMDBTS2048_setPassword)(char* password);
	int(__stdcall *GOMDBTS2048_getHandle)(char* deviceName, int* handle);
	int(__stdcall *GOMDBTS2048_releaseHandle)(int handle);

	int(__stdcall *GOMDBTS2048_setCalibrationEntryNumber)(int handle, int calibrationEntryNumber);
	int(__stdcall *GOMDBTS2048_getSelectedCalibrationEntryNumber)(int handle, int* calibrationEntryNumber);
	int(__stdcall *GOMDBTS2048_readCalibrationEntryInfo)(int handle, int calibrationEntryNumber, char* calibrationName);

	int(__stdcall *GOMDBTS2048_spectralSetDynamicTimeMode)(int handle, bool value);
	int(__stdcall *GOMDBTS2048_spectralSetOffsetMode)(int handle, int value);
	int(__stdcall *GOMDBTS2048_spectralSetIntegrationTimeInus)(int handle, int timeInus);

	int(__stdcall *GOMDBTS2048_measure)(int handle);
	int(__stdcall *GOMDBTS2048_getCWValue)(int handle, double* value);
	int(__stdcall *GOMDBTS2048_integralGetUnit)(int handle, int calibrationEntryNumber, char* unit);
};
#endif