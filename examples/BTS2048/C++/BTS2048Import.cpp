#include "BTS2048Import.h"

BTS2048Import::BTS2048Import()
{
	hDLLGOBTS2048 = NULL;
	handle = -1;
}

BTS2048Import::~BTS2048Import()
{
}

int __stdcall BTS2048Import::init(char* deviceName)
{
	int l_rc = 0;
	if (handle > 0)
		close();
	if (getProcAddresses(&hDLLGOBTS2048, "GOMDBTS2048.dll", 12,
		&GOMDBTS2048_setPassword, "GOMDBTS2048_setPassword",
		&GOMDBTS2048_getHandle, "GOMDBTS2048_getHandle",
		&GOMDBTS2048_releaseHandle, "GOMDBTS2048_releaseHandle",
		&GOMDBTS2048_setCalibrationEntryNumber, "GOMDBTS2048_setCalibrationEntryNumber",
		&GOMDBTS2048_getSelectedCalibrationEntryNumber, "GOMDBTS2048_getSelectedCalibrationEntryNumber",
		&GOMDBTS2048_readCalibrationEntryInfo, "GOMDBTS2048_readCalibrationEntryInfo",
		&GOMDBTS2048_measure, "GOMDBTS2048_measure",
		&GOMDBTS2048_getCWValue, "GOMDBTS2048_getCWValue",
		&GOMDBTS2048_integralGetUnit, "GOMDBTS2048_integralGetUnit",
		&GOMDBTS2048_spectralSetDynamicTimeMode, "GOMDBTS2048_spectralSetDynamicTimeMode",
		&GOMDBTS2048_spectralSetOffsetMode, "GOMDBTS2048_spectralSetOffsetMode",
		&GOMDBTS2048_spectralSetIntegrationTimeInus, "GOMDBTS2048_spectralSetIntegrationTimeInus"
		))
	{
		try {
			l_rc = GOMDBTS2048_setPassword("passw"); //replace passw with the right password
			if (l_rc == 0)
				l_rc = GOMDBTS2048_getHandle(deviceName, &handle);
		}
		catch (...) {
			l_rc = -1;
		}
	}
	else {
		l_rc = -1;
	}
	return l_rc;
}

int __stdcall BTS2048Import::writeCalibrationInfoToConsole()
{
	char calibInfo[100];
	std::cout << "Available calibration entries:" << std::endl;
	for (int i = 0; i < 52; i++)
	{
		GOMDBTS2048_readCalibrationEntryInfo(handle, i, calibInfo);
		if (*calibInfo != '\0')
		{
			std::cout << i << ": " << calibInfo << std::endl;
		}
	}
	return 0;
}

int __stdcall BTS2048Import::setCalibrationEntry(int value)
{
	int l_rc = GOMDBTS2048_setCalibrationEntryNumber(handle, value);
	return l_rc;
}

int __stdcall BTS2048Import::setSpectralMeasurementMode(bool dynamicTimeMode, int offsetMode, int integrationtime)
{
	int l_rc = GOMDBTS2048_spectralSetDynamicTimeMode(handle, dynamicTimeMode);
	if (l_rc < 0)
		return l_rc;

	l_rc = GOMDBTS2048_spectralSetOffsetMode(handle, offsetMode);
	if (l_rc < 0)
		return l_rc;

	l_rc = GOMDBTS2048_spectralSetIntegrationTimeInus(handle, integrationtime);
	return l_rc;
}

int __stdcall BTS2048Import::measure()
{
	int l_rc = GOMDBTS2048_measure(handle);
	return l_rc;
}

int __stdcall BTS2048Import::integralGetValues(double* value, char* unit)
{
	int l_rc = GOMDBTS2048_getCWValue(handle, value);
	if (l_rc < 0)
		return l_rc;

	int calibrationEntryNumber;
	l_rc = GOMDBTS2048_getSelectedCalibrationEntryNumber(handle, &calibrationEntryNumber);
	if (l_rc < 0)
		return l_rc;

	l_rc = GOMDBTS2048_integralGetUnit(handle, calibrationEntryNumber, unit);
	return l_rc;
}

int __stdcall BTS2048Import::close()
{
	int l_rc = GOMDBTS2048_releaseHandle(handle);
	handle = -1;
	return l_rc;
}

bool __stdcall BTS2048Import::getProcAddresses(HINSTANCE *p_hLibrary,
	const char* p_dllName, INT p_count, ...)
{
	va_list l_va;
	va_start(l_va, p_count);
	if ((*p_hLibrary = LoadLibrary(p_dllName)) != NULL)
	{
		FARPROC* l_procFunction = NULL;
		char* l_funcName = NULL;
		int l_idxCount = 0;
		while (l_idxCount < p_count)
		{
			l_procFunction = va_arg(l_va, FARPROC*);
			l_funcName = va_arg(l_va, LPSTR);
			if ((*l_procFunction =
				GetProcAddress(*p_hLibrary, l_funcName)) == NULL)
			{
				l_procFunction = NULL;
				return FALSE;
			}
			l_idxCount++;
		}
	}
	else
	{
		va_end(l_va);
		return false;
	}
	va_end(l_va);
	return true;
}