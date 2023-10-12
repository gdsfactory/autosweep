import warnings

import numpy as np

from autosweep.instruments import abs_instr
from autosweep.instruments.coms import visa_coms


class KeysightN778C(abs_instr.AbsInstrument):
    """
    Driver written by Lucas Grosjean

    :param addrs: The VISA-resource string for this instrument
    :type addrs: str
    """

    def __init__(self, addrs: str):
        super().__init__(com=visa_coms.VisaCOM(addrs=addrs))
        model = self.model()
        if model not in ("N7786C", "N7788C"):
            if model in ("N7781C", "N7785C"):
                warnings.warn(
                    "Some functions may not be available."
                    + "Please check the datasheet."
                )
            else:
                raise ValueError(f"Unexpected model {model}")
        self.clear_errors()
        self.assert_errors()

    def idn_ask(self):
        return self.com.query("*IDN?").strip()

    def idn_ask_dict(self):
        vendor, model, serial, version = self.idn_ask().split(",")
        """
        Example
        IDN Keysight Technologies,N7786C,MY59700220,V2.022
        """
        return {
            "vendor": vendor.strip(),
            "model": model.strip(),
            "serial": serial.strip(),
            "version": version.strip(),
        }

    def system_error_ask(self):
        return self.com.query(":SYSTEM:ERROR?").strip()

    def clear_errors(self):
        while True:
            error = self.system_error_ask().strip()
            if error == '+0,"No error"':
                break

    def print_if_errors(self):
        errors = []
        while True:
            error = self.system_error_ask().strip()
            if error == '+0,"No error"':
                break
            errors.append(error)
        if errors:
            print("Encountered errors:", errors)

    def assert_errors(self):
        errors = []
        while True:
            error = self.system_error_ask().strip()
            if error == '+0,"No error"':
                break
            errors.append(error)
        if errors:
            assert 0, f"Encountered errors: {errors}"
        
    def model(self):
        return self.idn_ask_dict()["model"]
        
    def measure_stokes_params(self, normalized: bool = True):
        """
        Returns the measured S0, S1, S2 and S3 stokes parameter.

        Args:
            If normalized parameters should be returned
        
        Returns:
            S0, S1, S2, S3 if not normalized
            s1, s2, s3 if normalized
        """
        S_list = self.com.query(":POL:SOP?").strip().split(",")
        S0, S1, S2, S3 = [float(Selem) for Selem in S_list]
        if normalized:
            return S1 / S0, S2 / S0, S3 / S0
        else:
            return S0, S1, S2, S3

    def fetch_stokes_params(self):
        """
        Returns the measured S0, S1, S2 and S3 stokes parameter
        from the last measurement.

        Args:
            If normalized parameters should be returned
        
        Returns:
            S0, S1, S2, S3 if not normalized
            s1, s2, s3 if normalized
        """
        S_list = self.com.query(":POL:SOP:FETCH?").strip().split(",")
        S0, S1, S2, S3 = [float(Selem) for Selem in S_list]
        if normalized:
            return S1 / S0, S2 / S0, S3 / S0
        else:
            return S0, S1, S2, S3

    def measure_optical_power(self):
        """
        Returns the measured optical power in configured power unit.
    
        Returns:
            Measurement optical power
        """
        return float(self.com.query(":POL:POW?"))

    def fetch_optical_power(self):
        """
        Returns the power from last measurement.
    
        Returns:
            Measurement optical power from last measurement
        """
        return float(self.com.query(":POL:POW:FETCH?"))

    def set_optical_power_unit(self, unit):
        """
        Sets the power unit.

        Args:
            Power unit
        """
        unit = str(unit).upper()
        assert unit in ("0", "DBM", "1", "WATT")
        self.com.write(f":POL:POW:UNIT {unit}")

    def ask_optical_power_unit(self):
        """
        Returns the power unit.

        Returns:
            Power unit
        """
        raw = self.com.query(":POL:POW:UNIT?").strip()
        return {
            "0": "dBm",
            "1": "Watts",
        }[raw]

    def set_wavelength_nm(self, wl: float):
        """
        Sets the current wavelength.

        Args:
            Wavelength [nm]
        """
        min_wl = float(self.com.query(":POL:WAV? MIN")) * 1e9
        max_wl = float(self.com.query(":POL:WAV? MAX")) * 1e9

        if not(min_wl < wl < max_wl):
            raise ValueError(
                "Wavelength need to be comprised between"
                + f"{min_wl}nm and {max_wl}nm."
            )

        self.com.write(f":POL:WAV {wl}NM")

    def set_min_wavelength_nm(self, wl: float):
        """
        Sets the minimum wavelength.

        Args:
            Wavelength [nm]
        """
        min_avail_wl = float(self.com.query(":POL:WAV? MIN")) * 1e9
        if not(min_avail_wl <= wl):
            raise ValueError(f"Wavelength need to be above{min_avail_wl}nm.")

        self.com.write(f":POL:WAV {wl}NM MIN")

    def set_max_wavelength_nm(self, wl: float):
        """
        Sets the minimum wavelength.

        Args:
            Wavelength [nm]
        """
        max_avail_wl = float(self.com.query(":POL:WAV? MAX")) * 1e9
        if not(wl <= max_avail_wl):
            raise ValueError(f"Wavelength need to be below{max_avail_wl}nm.")

        self.com.write(f":POL:WAV {wl}NM MAX")

    def ask_wavelength(self, val: str = None):
        """
        Returns the set wavelength.

        Args:
            Wavelength of interest (min, max or default)
        
        Returns:
            Wavelength at the asked position [nm]
        """
        if val is not None:
            val = val.upper()
            assert val in ("MIN", "MAX", "DEF")
            return float(self.com.query(f":POL:WAV? {val}"))
        else:
            return float(self.com.query(f":POL:WAV?"))

    def set_gain(self, val: int = 5):
        """
        Sets the gain level.

        Args:
            0...5 = High Bandwith about 250kHz
            6,7 = Medium Bandwith about 100kHz
            8,9 = Slow Bandwith about 10kHz
            Note - Use only gain between 0 and 7 for Stabilizer Mode
            because 8 and 9 have a small Bandwith.
            For best results check the Leveling of the Polarimeter. 
            Look at the POL:SWE:LPR? command.
            Maximum Speed is at Gain 0 to 5
            Even Gains have Factors of 10 and odd Gains Factors of 8.
            Choose what fits better
        """
        if not(0 <= val <= 9):
            raise ValueError("Gain should be comprised between 0 and 9.")

        return self.com.write(f":POL:GAIN {val}")

    def ask_gain(self):
        """
            Returns the gain level.
        
        Returns:
            Value of the gain (from 0 to 9)
        """
        return int(self.com.query(":POL:GAIN?"))

    def set_auto_gain(self, val: bool = True):
        """
            Enable or disable autogain.

        Args:
            If autogain should be set on (True) or turned off (False)
        """
        agflag = 1 if val else 0
        self.com.write(f":POL:AGFL {agflag}")

    def ask_auto_gain_state(self):
        """
            Ask if autogain.

        Returns:
            True if autogain, False else
        """
        agflag = bool(int(self.com.query(":POL:AGFL?")))
        return agflag

    def disable_logging(self):
        """
            Stops logging.
        """
        self.com.write(":POL:SWE:STOP")
    
    def zero_photodiodes(self):
        """
            Zeros photodiodes.
            (That means dark current is measured
            and will be subtracted from future measurements.)
        """
        self.com.write(":POL:ZERO")

    def ask_zero_succesful(self):
        """
            Returns zero results.

        Returns:
            True if last zeroing was succesful else False if failed
        """
        zero_success = bool(int(self.com.query(":POL:ZERO?")))
        return zero_success

    def set_number_loops(self, val: int = 0):
        """
            Sets the number of loops,
            which should be logged after starting.

        Args:
            Number of loops (0 for endless)
        """
        self.com.write(f":POL:SWE:LOOP {val}")

    def ask_number_loops(self):
        """
            Gets the number of loops,
            which should be logged after starting.

        Returns:
            Number of loops
        """
        return int(self.com.query(":POL:SWE:LOOP?"))

    def start_logging(self, mode: str = None):
        """
        Starts the polarimeter logging.

        Args:
            None to start logging as previously configured
            SOP: Starts logging and sets loop to 1
            SOPCONTINUOUS: Starts logging and sets loop to 0 (endless logging)
        """
        if not(mode):
            self.com.write(":POL:SWE:STAR")
        else:
            mode = mode.upper()
            assert mode in ("SOP", "SOPCONTINUOUS")
            self.com.writef(f":POL:SWE:STAR {mode}")

    def ask_logging_state(self):
        """
        Returns the current logging state.

        Returns:
            - Logging state
                "IDLE" -> Logging stopped
                "SAMPLIG" -> Lgging running
                "READY" -> Logging not running
            - Data availability
                "NO_DATA" -> No data available
                "DATA_AVAILABLE" -> Data available
        """
        return self.com.query(":POL:SWE:STAT?").strip().split(",")

    def get_measured_stokes_params(self, val: str = None):
        """
        Returns the logged measured results.

        Returns:
            None: returns 4,* dimensional array with S0, S1, S2, S3
            SOP: returns 4,* dimensional array with S0, S1, S2, S3
            NORMalized: returns 3,* dimensional array with S1, S2, S3
        """
        if val is None:
            return np.array(
                self.com.com.query_binary_values(
                    ":POL:SWE:GET?", datatype="f", is_big_endian=False
                ).reshape((-1, 4)).T
            )
        val = val.upper()
        assert val in ("SOP", "NORM", "NORMALIZED") 
        if val == "SOP":
            return np.array(
                self.com.com.query_binary_values(
                    ":POL:SWE:GET? SOP", datatype="f", is_big_endian=False
                ).reshape((-1, 4)).T
            )
        else:
            return np.array(
                self.com.com.query_binary_values(
                    ":POL:SWE:GET? NORM", datatype="f", is_big_endian=False
                ).reshape((-1, 3)).T
            )

    def get_measured_power(self):
        """
        Returns the logged measured power.

        Returns:
            Numpy array of power [Watt]
        """
        return np.array(
            self.com.com.query_binary_values(
                ":POL:FUNC:RES?", datatype="f", is_big_endian=False
            )
        )


    def get_number_logged_loops(self):
        """
            Returns the number of already finished logging loops.
        
        Returns:
            Number of finished and logged loops
        """
        return int(self.com.write(":POL:SWE:GET:IND?"))

    def set_number_sweeps(self, val: int):
        """
            Sets the number of samples/logging count.

        Args:
            Number of samples (1-1048576)        
        """
        if not(1 <= val <= 1048576):
            raise ValueError(
                "Number of samples should be comprised between 1 and 1048576."
            )

        self.com.write(f":POL:SWE:SAMP {val}")

    def ask_number_sweeps(self):
        """
        Gets the number of samples/logging count.

        Returns:
            Number of samples/logging count
        """
        return int(self.com.query(":POL:SWE:SAMP?"))

    def ask_number_logged_values(self):
        """
        Gets the number of already logged values.
        Will be 0, if logging finished.

        Returns:
             Number of already logged samples.
        """
        return int(self.com.query(":POL:SWE:SAMP:CURR?"))
    
    def set_sweep_rate_nm_per_s(self, val: float):
        """
        Sets the sweep rate in nm/s
        When performing a swept measurement, very often, the wavelength is changed over time.
        This parameter allows you to inform the instrument about the speed
        at which the wavelength of the laser source is changing.
        The start wavelength is given by the property Wavelength.
        This works for disabled trigger input only. If you want to
        sweep with trigger input, please set sweep step: set_sweep_step_nm()

        Args:
            Sweep rate [nm/s]
        """
        trig_input = self.com.query(":POL:TRIG:INP?")
        if not(trig_input == "NONE"):
            raise ValueError(
                "The sweet rate [nm/s] can only be set "
                + "with disabled trigger."
            )

        self.com.write(f":POL:SWE:RAT {val}NM/S")

    def ask_sweep_rate_nm_per_s(self):
        """
        Returns the sweep rate in nm/s.

        Returns:
            Sweep rate [nm/s]
        """
        return float(self.com.query(":POL:SWE:RAT?"))
    
    def set_sampling_rates_nm_per_s(
        self, srate: float, averaging_time: float = None
        ):
        """
        Sets the sampling rate.

        Args:
            - Sampling rate [Hz]
            - Averaging time [s, optional]
        """

        if not averaging_time:
            self.com.write(
                f":POL:SWE:RAT {srate}Hz"
            )
        else:
            self.com.write(
                f":POL:SWE:RAT {srate}Hz,{averaging_time}s"
            )
    
    def ask_sampling_rates(self):
        """
        Gets the sampling rate and averaging time.

        Returns:
            - Sampling rate [Hz]
            - Averaging time [s]
        """
        self.com.query(":POL:SWE:SRAT?")

    def ask_quality_gain(self):
        """
        Returns how well the ADC range was used for the last peak power.
        
        Returns:
            Value estimating the quality of the gain
            Value < 0.5 -> Measurement sweep should
                           be repeated with a higher
                           amplifier gain setting.
            Value > 1.0 -> Risk over overflow.
                           Select a lower amplifier setting.
        """
        quality = float(self.com.query(":POL:SWE:LPR?"))
        if quality < 0.5:
            warnings.warn(
                "GAIN IS TOO LOW."
                + "Please increase gain and repeat the measurement."
            )
        elif quality > 1.0:
            warnings.warn(
                "GAIN IS TOO LOW."
                + "Please lower the gain, risk of overflow"
            )

        return quality

    def set_sweep_step_nm(self, val: float):
        """
        Sets the sweep (wavelength) step in nm.

        Args:
            Sweep step [nm]
        """
        self.com.write(f":POL:SWE:STEP {val}NM")

    def ask_sweep_step_nm(self):
        """
        Get the sweep (wavelength) step done for every trigger while logging.
        
        Returns:
            Wavelength step [nm]
        """
        return float(self.com.query(":POL:SWE:STEP?")) * 1e9
    
    def set_pre_trigger_samples(self, val:int):
        """
        Sets the number of pre samples.
        (Sample before the trigger event).

        Args:
            Number of pre samples
        """
        if val > 1048576:
            raise ValueError(
                "Number of pre samples should be lower than 1048576."
            )

        self.com.write(f":POL:SWE:TRIG:PRE:SAMP {val}")

    def ask_pre_trigger_samples(self):
        """
        Returns the number of pre samples.

        Returns:
            Number of pre samples set
        """
        return int(self.com.query(":POL:SWE:TRIG:PRE:SAMP?"))
    
    def set_post_trigger_samples(self, val: int):
        """
        Sets the number of post samples. 
        (Sample after the trigger event).

        Args:
            Number of post samples
        """
        if val > 1048576:
            raise ValueError(
                "Number of post samples should be lower than 1048576."
            )

        self.com.write(f":POL:SWE:TRIG:POST:SAMP {val}")

    def ask_post_trigger_samples(self):
        """
        Returns the number of post samples.

        Returns:
            Number of post samples set
        """
        return int(self.com.query(":POL:SWE:TRIG:POST:SAMP?"))
    
    def set_trigger_input(
        self, val: str, pmin: float = None, pmax: float = None
        ):
        """
        Defines the trigger input.

        Args:
            NONE: Don't wait for trigger
            TTLHIGH: Wait for rising edge on BNC input
            TTLLOW: Wait for falling edge on BNC input
            SOPCHANGE: Wait for specified change of SOP
            PRETRIGGER_TTLHIGH: Specified numbers of samples are logged
                                before rising edge on BNC input
            PRETRIGGER_TTLLOW: Specified numbers of samples are logged
                               before falling edge on BNC input
            SMEasure: One sample for every trigger will be logged
            CMEasure: One trigger excutes one loop
                      with specified number of samples
            MMEasure: One trigger executes specified number of loops
                      with specified number of samples
            THReshold: Define minimum and maximum treshold power [Watt] limits for triggering.
                       You have to pass two paramters additionally.
            If you don't want minimum or maximum limit,
            send NAN instead of number.
        """
        val = val.upper()
        assert val in (
            "NONE",
            "TTLHIGH",
            "TTLLOW",
            "SOPCHANGE",
            "PRETRIGGER_TTLHIGH",
            "PRETRIGGER_TTLLOW",
            "SMEASURE",
            "SME",
            "CMEASURE",
            "CME",
            "MMEASURE",
            "MME",
            "THRESHOLD",
            "THR"
        )

        if val in ("THRESHOLD", "THR"):
            if not(pmin or pmax):
                raise ValueError("THReshold requires a minimum and a maximum power.")
            self.com.write(f":POL:TRIG:INP {val},{pmin},{pmax}")
        self.com.write(f":POL:TRIG:INP {val}")
    
    def ask_trigger_input(self):
        """
        Returns input triger configuration.

        Returns:
            Input trigger configuration
        """
        return self.com.query(":POL:TRIG:INP?")

    def set_trigger_output(self, val: str):
        """
        Defines trigger output.

        Args:
            DISabled: no trigger at output BNC
            AVGover: trigger when averaging starts at output BNC
            MEASure: trigger when measuring starts at output BNC
        """
        val = val.upper()
        assert val in (
            "DIS",
            "DISABLED",
            "AVG",
            "AVGOVER",
            "MEAS",
            "MEASURE"
        )
        self.com.write(f":POL:TRIG:OUTP {val}")
    
    def ask_trigger_output(self):
        """
        Returns trigger output configuration.

        Returns:
            Trigger output configuration
        """
        return self.com.query(":POL:TRIG:OUTP?")

    def set_trigger_delay_us(self, val: float):
        """
        Set time delay between input trigger and trigger event

        Args:
            Delay value [us]
        """
        factor = int(val * 32)

        if not(0 <= factor <= 997):
            raise ValueError(
                "Delay should be comprised between 0 and "
                + f"{997/32}us."
            )

        self.com.write(f":POL:TRIG:OFFS {factor}")
    
    def ask_trigger_delay_us(self):
        """
        Returns delay after which event is executed when trigger event occurs.

        Returns:
            Delay value [us]
        """
        factor = int(self.com.query(":POL:TRIG:OFFS?"))
        return factor / 32

    def set_trigger_offset(self, val: int):
        """
        Defines number of triggers,
        which will be ignored before first trigger event.

        Args:
            Trigger offset
        """
        self.com.write(f":POL:TRIG:OFFS {val}")
    
    def ask_trigger_offset(self):
        """
        Returns number of triggers,
        which will be ignored before first trigger event.

        Args:
            Trigger offset
        """
        return int(self.com.query(":POL:TRIG:OFFS?"))

    # Scrambler functions not implemented

    def set_stabilizer_mode(self, val: bool = True):
        """
        Sets the Stabilizer Operating Mode.
        
        Args:
            If stabilization should be enable True
            or disabled False
        """
        stabflag = 1 if val else 0
        self.com.write(f":STAB:STAB {stabflag}")

    def ask_stabilizer_mode(self):
        """
        Gets the Stabilizer Operating Mode.

        Returns:
            True if stabilization is enabled, False else
        """
        return bool(int(self.com.query(":STAB:STAB?")))
    
    def set_stabilizer_stokes_params_target(
        self, s1: float, s2: float, s3: float
        ):
        """
        Sets the target SOP for the Stabilizer.

        Args:
            - s1, normalized Stokes vector
            - s2, normalized Stokes vector
            - s3, normalized Stokes vector
        """
        self.com.write(f"STAB:SOP {s1},{s2},{s3}")
    
    def ask_stabilizer_stokes_params_target(self):
        """
        Gets the target SOP.
        
        Returns:
            - s1, normalized Stokes vector
            - s2, normalized Stokes vector
            - s3, normalized Stokes vector
        """
        s1, s2, s3 = self.com.query(":STAB:SOP?").strip().split(",")
        return float(s1), float(s2), float(s3)


if __name__ == "__main__":
    import pyvisa

    rm = pyvisa.ResourceManager()
