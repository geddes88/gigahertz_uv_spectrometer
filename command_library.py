import ctypes
import numpy as np
import time
import datetime
import pandas as pd
import os


# load BTS2048 Dll
DLLIMPORT = ctypes.WinDLL("GOMDBTS2048.dll")


def gaussian_smooth(spectrum, wavelengths, fwhm):
    sigma = fwhm / np.sqrt(8 * np.log(2))
    spec_smooth = []
    for wav_centre in wavelengths:
        subset = np.where((wavelengths < wav_centre + 30 * fwhm) & (wavelengths > wav_centre - 30 * fwhm))
        gaussian = np.exp(-(wavelengths[subset] - wav_centre) ** 2 / (2 * sigma ** 2))
        gaussian = gaussian / sum(gaussian)
        weighted_y = spectrum[subset] * gaussian
        spec_smooth.append(sum(weighted_y))
    return spec_smooth


errors = {'15000': 'Communication problem', '-15001': 'Setup file invalid for the BTS2048',
          '-15002': 'Setup file could not be opened',
          '-15004': 'az mode outside the permissible range (valid values: 0 - 2)',
          '-15005': 'Communication channel cannot be initialized', '-15006': 'Firmware version too low',
          '-15007': 'Problem sending file', '-15008': 'Problem receiving file',
          '-15009': 'BTS2048 sending an undefined error', '-15010': 'Delta uv limit < 0',
          '-15014': 'Error main data eeprom', '-15015': 'Error color data eeprom',
          '-15016': 'This command is not valid for communication per USB',
          '-15017': 'Error zero adjust integral amplifier', '-15020': 'Error dark current measurement',
          '-15026': 'Exception received', '-15027': 'Filter not valid for the selected calibration table entry',
          '-15030': 'Measurement value not available since the integral measurement was not performed in the last '
                    'measurement',
          '-15031': 'No values available', '-15032': 'Wrong password entered',
          '-15033': 'Calibration: Actual weighting function not set',
          '-15034': 'Calibration: calibration lamp spectrum not set', '-15035': 'Calibration: calibration name not set',
          '-15036': 'Calibration: spectral calibration factors not set',
          '-15037': 'Calibration: integral calibration factors not set',
          '-15038': 'Calibration: spectral SI unit not set', '-15039': 'Calibration: integral SI unit not set',
          '-15040': 'Calibration: filter assignment not set',
          '-15041': 'The wavelength range selected is too large or the step size too small resulting in a data size '
                    'larger than 3300 values',
          '-15024': 'Error in technical performance pre-calculation',
          '-15043': 'Error in calculation of the CRI values',
          '-15044': 'Error in calculation of the radiometric values over the wavelength',
          '-15045': 'Error in correction with VL. Possible causes: Y = 0 -> color calcuation was probably not '
                    'performed Integral measurement value = 0 -> error in integral measurement or integral measurement '
                    'not performed',
          '-15047': 'Timeout of a triggered measurement',
          '-15048': 'Selected wavelength 1 was larger or equal to the wavelength 2',
          '-15049': 'wrong format of IP-address',
          '-15051': 'Confiugration conflict (e.g. static dark value in combination with dynamic evaluation of '
                    'integration time)',
          '-15053': 'color calculation cant be switched on, the defined wavelengths dont include the complete '
                    'viewable range (380m - 780nm)',
          '-15054': 'The called method is not available for the connected measurement device',
          '-15055': 'No external power supply connected', '-15100': 'Parameters out of the permissible range',
          '-15997': 'No BTS2048 connected',
          '-15998': 'BTS2048 with a different serial number as the one expected connected', '-15999': 'Unknown error',
          '15003': 'File not found: no default file had been previously saved. Therefore, no default data exists',
          '15011': 'The integral unit reports an overload', '15012': 'The integral unit reports an underload',
          '15023': 'The spectral unit reports an overload',
          '15028': 'The integration time for the integral unit was matched to the valid grid',
          '15046': 'If dark mode is set to static and the integration time of the spectral unit set to dynamic, '
                   'the dark mode is automatically changed to dynamic since static mode is not allowed in this case',
          '15052': 'color calculation becomes deactivated, because the defined wavelengths dont include the complete '
                   'viewable range (380m - 780nm)',
          '15056': 'Integration time became adapted because, the cooling was switched off',
          '15057': 'The spectral unit reports an overload an the integral unit reports an overload',
          '15058': 'The spectral unit reports an overload an the integral unit reports an underload',
          '15094': 'Array low signal and integral overload', '15095': 'Array low signal and integral underload'}


#
# check_bool=DLLIMPORT["GOMDBTS2048_isDHCP"]
# check_bool.restype = ctypes.c_int
# check_bool.argtypes = (ctypes.c_int,ctypes.POINTER(ctypes.c_bool))
# cool_result=ctypes.c_bool(False)
# rc = check_bool(giga.handle, ctypes.byref(cool_result))
# if rc!=0:
#    print 'Failed to check cooling state - '+str(rc)
# cool_result.value
#    

# wrap hello to make sure the free is done

# do the deed
def create_panda_file(directory, panda_in, time_in, sza_in, hd=False):
    now = time_in
    year = str(now.year)
    month = "%02d" % now.month
    day = "%02d" % now.day
    hour = "%02d" % now.hour
    minute = "%02d" % now.minute
    suffix = 0
    todayspath = year + month + day
    filepath_out = directory + todayspath
    sza = "%06.2f" % sza_in

    if not hd:
        filename_out = year + month + day + "_" + hour + minute + "_" + sza + ".dat"
    else:
        filename_out = year + month + day + "_" + hour + minute + "_" + sza + "_hd.dat"
        del panda_in['spectrum']
        del panda_in['spectrum_wavelengths']
        del panda_in['calibrated_pixel_counts']
        del panda_in['pixel_wavelengths']
    while suffix < 999:
        filename_out = year + month + day + hour + "." + str(suffix)
        if not os.path.exists(filepath_out + "\\" + filename_out):
            break
        suffix = suffix + 1
    log_file = filepath_out + "\\" + filename_out

    if not os.path.exists(os.path.dirname(log_file)):
        try:
            os.makedirs(os.path.dirname(log_file))
        except Exception as e:
            print(e)
            pass

    panda_in.to_pickle(log_file)


""" Ok what do we need to make this thing go? The basics work and we get a rough 
spectrum, lets setup some python wrapper functions to make it all easier! """


class Gigahertz(object):
    def __init__(self):
        self.handle = ctypes.c_int(0)
        self.dynamic_time_mode = True
        self.integration_time = 500000
        self.offset_mode = 2
        self.min_wav = 200
        self.max_wav = 430.
        self.step = 0.13
        self.setup = False
        self.wav_map, self.wav_cal = None, None
        self.initialize_spectrometer(connection_type='USB')

    def get_ip_address(self):
        buffer_size = 16
        the_buffer = ctypes.create_string_buffer(buffer_size)
        ip = DLLIMPORT["GOMDBTS2048_getIPAddress"]
        ip.restype = ctypes.c_int
        ip.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t)
        results = ip(self.handle, the_buffer, buffer_size)
        print(results)
        print(the_buffer.value)

    def get_calibration_info(self):
        """get the current programmed wavelength assignment of the pixels, im 
        assuming we probably won't need this, can fit to solar. Should be linearish.
        
        also returns the sensitivity spectrum for each pixel
        """
        load_calib = DLLIMPORT["GOMDBTS2048_calibLoadFromDevice"]
        load_calib.restype = ctypes.c_int
        load_calib.argtype = ctypes.c_int
        rc_out = []
        rc = load_calib(self.handle)
        if rc != 0:
            rc_out.append(rc)
            print('Failed to load calib, error code - ' + str(rc))

        wav_map = np.zeros(2048, dtype=np.float64)
        c_wav = np.ctypeslib.as_ctypes(wav_map)
        wav_map_f = DLLIMPORT['GOMDBTS2048_calibGetWavelengthMapping']
        wav_map_f.restype = ctypes.c_int
        wav_map_f.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_double)
        rc = wav_map_f(self.handle, c_wav)
        if rc != 0:
            rc_out.append(rc)

            wav_map = np.array([np.nan] * 2048)
            print('Failed to get wavelength mapping, error code - ' + str(rc))

        wav_cal = np.zeros(2048, dtype=np.float64)
        c_wav_cal = np.ctypeslib.as_ctypes(wav_cal)
        wav_cal_f = DLLIMPORT['GOMDBTS2048_calibGetCalibrationFactorsSpectral']
        wav_cal_f.restype = ctypes.c_int
        wav_cal_f.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_double)
        rc = wav_cal_f(self.handle, c_wav_cal)
        if rc != 0:
            rc_out.append(rc)

            wav_cal = np.array([np.nan] * 2048)
            print('Failed to get wavelength mapping, error code 2 - ' + str(rc))

        return rc_out, wav_map, wav_cal

    def setup_measurement(self):
        rc_out = []
        rc = self.configure_spectral_measurement(self.dynamic_time_mode, self.integration_time, self.offset_mode)
        if len(rc) > 0:
            for i in rc:
                rc_out.append(i)
        rc = self.set_wavelength_range(self.min_wav, self.max_wav, self.step)
        if len(rc) > 0:
            for i in rc:
                rc_out.append(i)
        rc, self.wav_map, self.wav_cal = self.get_calibration_info()
        if len(rc) > 0:
            for i in rc:
                rc_out.append(i)

        self.setup = True
        self.print_rc_messages(rc_out)
        return rc_out

    def print_rc_messages(self, rc_list):
        if len(rc_list) > 0:
            for rc in rc_list:
                if str(rc) in list(errors.keys()):
                    print(errors[str(rc)])
                else:
                    print(str(rc) + " Unknown Error")

    def close_instrument(self):
        releasehandle = DLLIMPORT["GOMDBTS2048_releaseHandle"]
        releasehandle.restype = ctypes.c_int
        releasehandle.argtype = ctypes.c_int
        releasehandle(self.handle)

    def initialize_spectrometer(self, connection_type="USB", ip="192.168.161.123"):

        setpassword = DLLIMPORT["GOMDBTS2048_setPassword"]
        setpassword.restype = ctypes.c_int
        setpassword.argtype = ctypes.c_char_p
        # setPassword(b"dk483g92")
        setpassword(b"54hfd3-z")
        # getHandle
        gethandle = DLLIMPORT["GOMDBTS2048_getHandle"]
        gethandle.restype = ctypes.c_int
        gethandle.argtypes = (ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))

        if connection_type == "USB":
            rc = gethandle(b"BTS2048_42607", ctypes.byref(self.handle))
        else:
            rc = gethandle(b"BTS2048_0_IP" + ip.encode("utf-8"), ctypes.byref(self.handle))

        if rc != 0:
            print('Failed to get handle, error code - ' + str(rc))
        # self.set_dhcp(True)

    def set_dhcp(self, state):

        dhcp = DLLIMPORT["GOMDBTS2048_setDHCPServer"]
        dhcp.restype = ctypes.c_int
        dhcp.argtypes = (ctypes.c_int, ctypes.c_bool)
        rc = dhcp(self.handle, ctypes.c_bool(state))
        if rc != 0:
            print('Failed to set dhcp server - ' + str(rc))

    def set_wavelength_range(self, min_wav, max_wav, step):
        self.min_wav = min_wav
        self.max_wav = max_wav
        self.step = step

        """Set wavvelength range, probably won't use. It's only used to grid and interpolate the output"""
        wav_function = DLLIMPORT['GOMDBTS2048_setWavelengthRange']
        wav_function.restype = ctypes.c_int
        wav_function.argtypes = (ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double,)
        rc = wav_function(self.handle, ctypes.c_double(self.min_wav), ctypes.c_double(self.max_wav),
                          ctypes.c_double(self.step))
        rc_out = []
        if rc != 0:
            rc_out.append(rc)
            print('Failed to set wavelength parameters, error code - ' + str(rc))

        return rc_out

    def toggle_cooling(self, state):
        toggle_cooling = DLLIMPORT["GOMDBTS2048_setCooling"]
        toggle_cooling.restype = ctypes.c_int
        toggle_cooling.argtypes = (ctypes.c_int, ctypes.c_bool)
        rc = toggle_cooling(self.handle, ctypes.c_bool(state))
        if rc != 0:
            print('Failed to set cooling error code - ' + str(rc))

    def check_cooling_status(self):
        check_cooling = DLLIMPORT["GOMDBTS2048_getCoolingState"]
        check_cooling.restype = ctypes.c_int
        check_cooling.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_int))
        cool_result = ctypes.c_int(-1)
        rc = check_cooling(self.handle, ctypes.byref(cool_result))
        if rc != 0:
            print('Failed to check cooling state - ' + str(rc))
        return cool_result.value

    def check_straylight_status(self):
        check_stray = DLLIMPORT["GOMDBTS2048_OORSLCorrectionGetMode"]
        check_stray.restype = ctypes.c_int
        check_stray.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_int))
        stray_result = ctypes.c_int(-1)
        rc = check_stray(self.handle, ctypes.byref(stray_result))
        if rc != 0:
            print('Failed to check straylight state - ' + str(rc))
        return stray_result.value

    def spectra_output(self):
        """What do we want to return? may as well get it all - raw, calibrated..."""
        raw_arr = np.zeros(2048, dtype=np.float64)
        c_raw = np.ctypeslib.as_ctypes(raw_arr)
        raw_pixel_f = DLLIMPORT['GOMDBTS2048_spectralGetCountsPixel']
        raw_pixel_f.restype = ctypes.c_int
        raw_pixel_f.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_double)
        rc = raw_pixel_f(self.handle, c_raw)
        if rc != 0:
            raw_arr = np.array([np.nan] * 2048)
            print('Failed to get raw pixel counts, error code - ' + str(rc))

        cal_arr = np.zeros(2048, dtype=np.float64)
        c_cal = np.ctypeslib.as_ctypes(cal_arr)
        cal_pixel_f = DLLIMPORT['GOMDBTS2048_spectralGetSpectrumCalibratedPixel']
        cal_pixel_f.restype = ctypes.c_int
        cal_pixel_f.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_double)
        rc2 = cal_pixel_f(self.handle, c_cal)
        if rc2 != 0:
            cal_arr = np.array([np.nan] * 2048)
            print('Failed to get calibrated pixel counts, error code - ' + str(rc2))

        dark_arr = np.zeros(2048, dtype=np.float64)
        c_dark = np.ctypeslib.as_ctypes(dark_arr)
        dark_f = DLLIMPORT['GOMDBTS2048_spectralGetLastUsedOffset']
        dark_f.restype = ctypes.c_int
        dark_f.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_double)
        rc2 = dark_f(self.handle, c_dark)
        if rc2 != 0:
            dark_arr = np.array([np.nan] * 2048)
            print('Failed to get dark counts, error code - ' + str(rc2))

        wav_arr_p = np.zeros(2048, dtype=np.float64)
        c_wav = np.ctypeslib.as_ctypes(wav_arr_p)
        wav_arr_f = DLLIMPORT['GOMDBTS2048_spectralGetLambdas']
        wav_arr_f.restype = ctypes.c_int
        wav_arr_f.argtypes = ctypes.c_int, ctypes.c_bool, ctypes.POINTER(ctypes.c_double)
        rc2 = wav_arr_f(self.handle, ctypes.c_bool(False), c_wav)
        if rc2 != 0:
            wav_arr_p = np.array([np.nan] * 2048)
            print('Failed to get pixel_wavlengths, error code - ' + str(rc2))

        spec_length = int((self.max_wav - self.min_wav) / self.step) + 1
        spec_arr = np.zeros(int(spec_length), dtype=np.float64)
        wav_arr_s = np.zeros(int(spec_length), dtype=np.float64)
        c_spec = np.ctypeslib.as_ctypes(spec_arr)
        c_wav = np.ctypeslib.as_ctypes(wav_arr_s)

        spec_f = DLLIMPORT['GOMDBTS2048_spectralGetSpectrumCalibratedWavelength']
        spec_f.restype = ctypes.c_int
        spec_f.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_double)
        rc2 = spec_f(self.handle, c_spec)
        if rc2 != 0:
            spec_arr = np.array([np.nan] * int(spec_length))
            print('Failed to get calibrated pixel counts, error code - ' + str(rc2))

        rc2 = wav_arr_f(self.handle, ctypes.c_bool(True), c_wav)
        if rc2 != 0:
            wav_arr_s = np.array([np.nan] * int(spec_length))
            print('Failed to get pixel_wavlengths, error code - ' + str(rc2))

        """Measure the temperature of the sensor, returns in Kelvin"""
        get_integration = DLLIMPORT["GOMDBTS2048_spectralGetIntegrationTimeInus"]
        get_integration.restype = ctypes.c_int
        get_integration.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_int))
        integration_time = ctypes.c_int(-999)
        rc = get_integration(self.handle, ctypes.byref(integration_time))
        if rc != 0:
            print('Failed to get integration gime - ' + str(rc))
            out = -999
        else:
            out = integration_time.value

        """Measure the temperature of the sensor, returns in Kelvin"""

        scale_factor_f = DLLIMPORT["GOMDBTS2048_getLastScaleWithVLFactor"]
        scale_factor_f.restype = ctypes.c_int
        scale_factor_f.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_double))
        scale_factor = ctypes.c_double(-999)
        rc = scale_factor_f(self.handle, ctypes.byref(scale_factor))
        if rc != 0:
            print('Failed to get integration gime - ' + str(rc))
            out2 = -999
        else:
            out2 = scale_factor.value

        return raw_arr, cal_arr, spec_arr, wav_arr_s, wav_arr_p, dark_arr, out, out2

    def acquire_spectra(self, sza=-999.99):
        """Make a measurement, returns 2048 array of raw coutns per pixel and the calibrated measurement per pixel
        will probably end up using the raw as we'll need to apply our own calibrations"""
        timestamp = datetime.datetime.utcnow()
        timestamp2 = datetime.datetime.now()
        measurement = DLLIMPORT["GOMDBTS2048_measure"]
        measurement.restype = ctypes.c_int
        measurement.argtypes = [ctypes.c_int]
        rc = measurement(self.handle)
        print(rc)
        rc_out = []
        if rc != 0:
            rc_out.append(rc)
        if rc == 0:
            raw_arr, cal_arr, spec_arr, wav_arr_s, wav_arr_p, dark_arr, out, out2 = self.spectra_output()

            temperature = self.measure_temperature()
        else:
            spec_length = int((self.max_wav - self.min_wav) / self.step) + 1

            temperature = np.nan
            raw_arr = [np.nan] * 2048
            cal_arr = [np.nan] * 2048
            spec_arr = [np.nan] * spec_length
            wav_arr_s = [np.nan] * spec_length
            wav_arr_p = [np.nan] * 2048
            dark_arr = [np.nan] * 2048
            out = np.nan
            out2 = np.nan

        output_panda = pd.DataFrame()

        output_panda['raw_pixel_counts'] = [np.array(raw_arr)]
        output_panda['calibrated_pixel_counts'] = [np.array(cal_arr)]
        output_panda['spectrum'] = [np.array(spec_arr)]
        output_panda['spectrum_wavelengths'] = [np.array(wav_arr_s)]
        output_panda['pixel_wavelengths'] = [np.array(wav_arr_p)]
        output_panda['dark_pixel_counts'] = [np.array(dark_arr)]
        output_panda['integration_time'] = out
        output_panda['scale_factor'] = out2
        output_panda['temperature'] = temperature
        output_panda['sza'] = sza
        output_panda['rc'] = rc
        output_panda['rc_message'] = 'No Errors'
        if rc != 0 and str(rc):
            if str(rc) in list(errors.keys()):
                output_panda['rc_message'] = errors[str(rc)]
            else:
                output_panda['rc_message'] = 'Unknown Error'
        output_panda['timestamp_utc'] = timestamp
        output_panda['timestamp_local'] = timestamp2
        return output_panda

    def pre_measure_offset(self):
        measurement = DLLIMPORT["GOMDBTS2048_spectralMeasurePremeasuredOffset"]
        measurement.restype = ctypes.c_int
        measurement.argtypes = [ctypes.c_int]
        rc = measurement(self.handle)
        print('measurement return - ' + str(rc))
        raw_arr, cal_arr, spec_arr, wav_arr_s, wav_arr_p, dark_arr, out, out2 = self.spectra_output()
        return raw_arr, cal_arr, spec_arr, wav_arr_s, wav_arr_p, dark_arr, out, out2

    def get_filter_position(self):
        get_filter = DLLIMPORT["GOMDBTS2048_getFilterPosition"]
        get_filter.restype = ctypes.c_int
        get_filter.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_int))
        filter_type = ctypes.c_int(-999)
        rc = get_filter(self.handle, ctypes.byref(filter_type))
        if rc != 0:
            print('Failed to get filter - ' + str(rc))
        out = filter_type.value
        return out

    def measure_temperature(self):
        """Measure the temperature of the sensor, returns in Kelvin"""
        get_temperature = DLLIMPORT["GOMDBTS2048_getTemperature"]
        get_temperature.restype = ctypes.c_int
        get_temperature.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_double))
        temperature = ctypes.c_double(-999)
        rc = get_temperature(self.handle, ctypes.byref(temperature))
        if rc != 0:
            print('Failed to check temperature - ' + str(rc))
        out = temperature.value + 273.15
        return out

    def configure_spectral_measurement(self, dynamic_time_mode, integration_time, offset_mode):
        """Set the following spectral parameters: 
            Dynamic time mode, boolean - True for dynamicaly set integration
            time, false for fixed
        
            Integration time, integer (2-4000000) - if not using dynamic mode, set the integration time
            in us
            
            Offset mode - integer (0,1,2 or 3) - 0 No offset, 1 - static, 2 dynamic, 3 premeasured
            
            
        """

        if integration_time >= 4 * 1e6:
            self.toggle_cooling(True)
            ready = 0
            while ready != 2:
                ready = self.check_cooling_status()
                if ready == 1:
                    print("Waiting to cool down")
                if ready == 0:
                    break
                if ready == 2:
                    print("Cooling complete")
                time.sleep(1)
        rc_out = []
        dtm_function = DLLIMPORT['GOMDBTS2048_spectralSetDynamicTimeMode']
        dtm_function.restype = ctypes.c_int
        dtm_function.argtypes = (ctypes.c_int, ctypes.c_bool)
        rc = dtm_function(self.handle, ctypes.c_bool(dynamic_time_mode))
        if rc != 0:
            rc_out.append(rc)
            print('Failed to set dynamic time mode, error code - ' + str(rc))

        it_function = DLLIMPORT['GOMDBTS2048_spectralSetIntegrationTimeInus']
        it_function.restype = ctypes.c_int
        it_function.argtypes = (ctypes.c_int, ctypes.c_int)
        rc = it_function(self.handle, ctypes.c_int(integration_time))
        if rc != 0:
            rc_out.append(rc)
            print('Failed to set integration time, error code - ' + str(rc))

        offset_function = DLLIMPORT['GOMDBTS2048_spectralSetOffsetMode']
        offset_function.restype = ctypes.c_int
        offset_function.argtypes = (ctypes.c_int, ctypes.c_int)
        rc = offset_function(self.handle, ctypes.c_int(offset_mode))
        if rc != 0:
            rc_out.append(rc)
            print('Failed to set offset mode, error code - ' + str(rc))
        return rc_out
