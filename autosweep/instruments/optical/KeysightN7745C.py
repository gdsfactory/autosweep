import numpy as np

from autosweep.instruments import abs_instr
from autosweep.instruments.coms import visa_coms


class KeysightN7745C(abs_instr.AbsInstrument):
    """
    Driver written by Helge Gehring, modified to work with AutoSweep.

    :param addrs: The VISA-resource string for this instrument
    :type addrs: str
    """

    def __init__(self, addrs: str):
        super().__init__(com=visa_coms.VisaCOM(addrs=addrs))
        model = self.model()

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
        
    def model(self):
        return self.idn_ask_dict()["model"]

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

    def assert_n(self, n):
        assert 1 <= n <= 8, f"Require channel 1 <= {n} <= 8"

    def fetch_power_ask(self, n):
        """
        Reads the current power meter value. It does not provide its own triggering and so must be used with either continuous
        software triggering or a directly preceding immediate software trigger.
        It returns the value the previous software trigger measured. Any subsequent FETCh command will return the same value, if
        there is no subsequent software trigger.

        :return: The current value as a float value in dBm,W or dB.
                If the reference state is absolute, units are dBm or W.
                If the reference state is relative, units are dB.
        """
        return float(self.com.query(f":FETCH{n}:POWER?"))

    def fetch_power_all(self):
        """
        Reads all current power meter values. It does not provide its own triggering and so must be used with either continuous
        software triggering or a directly preceding immediate software trigger.
        It returns the value the previous software trigger measured. Any subsequent FETCh command will return the same value, if
        there is no subsequent software trigger.

        :return: Data values are always in Watt. (Seems no to be the case)
        """
        return self.com.com.query_binary_values(
            ":FETCH:POWER:ALL?", datatype="f", is_big_endian=False
        )

    def initiate_channel_immediate(self, n, m):
        """
        Initiates the software trigger system and completes one full trigger cycle, that is, one measurement is made for selected [n].
        In logging mode it triggers all channels independent from [n].
        """
        if m:
            self.com.write(f":INITIATE{n}:CHANNEL{m}:IMMEDIATE")
        else:
            self.com.write(f":INITIATE{n}:IMMEDIATE")

    def initiate_channel_continuous(self, n, channel, continuous):
        """
        A boolean value:
        False: do not measure continuously
        True: measure continuously
        """
        arg = "on" if continuous else "off"
        if channel:
            self.com.write(f":INITIATE{n}:CHANNEL{channel}:CONTINUOUS {arg}")
        else:
            self.com.write(f":INITIATE{n}:CONTINUOUS {arg}")

    def sense_function_parameter_logging(self, n, data_points, averaging_time):
        """
        Sets the number of data points and the averaging time for the logging data acquisition function.

        :param data_points:
            Data Points is the number of samples that are recorded before the logging mode is completed.
            Data Points is an integer value.
        :param averaging_time:
            Averaging time is a time value in seconds. There is no time delay between averaging time periods.
            Use :SENSe[n]:FUNCtion:PARameter:STABility? if you want to use delayed measurement.
            NOTE: Setting parameters for the logging function sets some parameters, including hidden parameters, for the stability and
            MinMax functions and vice versa.
            If you specify no units for the averaging time value in your command, seconds are used as the default.

        See :SENSe[n]:FUNCtion:STATe for information on starting/stopping a data acquisition function.
        See :SENSe[n]:FUNCtion:RESult? for information on accessing the results of a data acquisition function.
        NOTE: Before using this command, ensure to stop logging for all available channel.
        Details can be found in the Application Note "Transient Optical Power Measurements with the N7744A and N7745A"
        http://literature.cdn.keysight.com/litweb/pdf/5990-3710EN.pdf.
        """
        # self.assert_n(n)
        assert data_points >= 1
        assert averaging_time >= 0
        self.com.write(
            f":SENSE{n}:FUNCTION:PARAMETER:LOGGING {data_points},{averaging_time}"
        )

    def sense_function_result_ask(self):
        """
        The last data acquisition function’s data array as a binary block.
        One measurement value is a 4 byte little-endian IEEE 754 single precision value.
        For Logging and Stability Data Acquisition functions.
        For the MinMax Data Acquisition function, the query returns the minimum, maximum and current power values.
        See Data Types for more information on Binary Blocks.
        See How to Log Results for information on logging using VISA calls. There are some tips about how to use float format
        specifiers to convert the binary blocks (32 Bit / IEEE 754 single precision format).

        example: :sens1:func:stat logg,star

        :return: the data array of the last data acquisition function.

        pyvisa.errors.VisaIOError: VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.
        This can happen when the measurement isn't ready / never triggered
        """
        result = np.array(
            self.com.com.query_binary_values(
                ":SENSE:FUNCTION:RESULT?", datatype="f", is_big_endian=False
            )
        )
        self.com.read()
        return result

    def sense_function_state(self, n, state, mode):
        """

        :param state:
            LOGGing: Logging data acquisition function
            STABility: Stability data acquisition function
            MINMax: MinMax data acquisition function
            STOP: Stop data acquisition function
            STARt: Start data acquisition function
            See :SENSe[n][:CHANnel[m]]:FUNCtion:PARameter:LOGGing for more information on the logging data acquisition function.
            Stop any function before you try to set up a new function. Some parameters cannot be set until you stop the function.
        :return:
        """

        self.assert_n(n)
        state = str(state).upper()
        assert state in ("LOGG", "LOGGING", "STAB", "STABILITY", "MINM", "MINMAX")
        mode = str(mode).upper()
        assert mode in ("STOP", "STAR", "START")
        self.com.write(f":SENSE{n}:FUNCTION:STATE {state},{mode}")

    def sense_function_state_ask(self, n):
        """
        Returns the function mode and the status of the data acquisition function.

        :return:
            NONE No function mode selected
            LOGGING_STABILITY Logging or stability data acquisition function
            MINMAX MinMax data acquisition function
            PROGRESS Data acquisition function is in progress
            COMPLETE Data acquisition function is complete
        """

        self.assert_n(n)
        function, state = self.com.query(f"SENSE{n}:FUNCTION:STATE?").strip().split(",")
        assert function in ("NONE", "LOGGING_STABILITY", "MINMAX"), function
        assert state in ("PROGRESS", "COMPLETE"), state
        return function, state

    def sense_function_state_ask_state(self, n):
        _function, state = self.sense_function_state_ask(n)
        return state

    def sense_function_state_ask_is_running(self, n):
        _function, state = self.sense_function_state_ask(n)
        return state == "PROGRESS"

    def trigger(self, val):
        """
        Generates a hardware trigger.

        val:
        1 or NODEA: Is identical to a trigger at the Input Trigger Connector.
        2 or NODEB: Generates trigger at the Output Trigger Connector.
        """
        val = str(val).upper()
        assert val in ("NODEA", "1", "NODEB", "2"), val
        self.com.write(f":TRIGGER {val}")

    def trigger_the_input(self):
        self.trigger("NODEA")

    def trigger_input(self, n, trigger_response):
        """
        Sets the incoming trigger response and arms the module.

        :param trigger_response:
            IGNore: Ignore incoming trigger
            SMEasure: Start a single measurement. If a measurement function is active, see :SENSe[n]:FUNCtion:STATe on
            page 80, one sample is performed and the result is stored in the data array,
            :SENSe[n]:FUNCtion:RESult? on page 77.
            CMEasure: Start a complete measurement. If a measurement function is active, :SENSe[n]:FUNCtion:STATe on
            page 80, a complete measurement function is performed.
            MMEasure: Defines how many samples ares stored before trigger event.
            PREtrigger: Not possible
            THReshold: Similar to PRE, but the starting event is minimum and maximum threshold values. If you don't want
                        both limit, you can write NAN instead of number.
        """
        self.assert_n(n)
        trigger_response = trigger_response.upper()
        assert trigger_response in (
            "SME",
            "SMEASURE",
            "CMEASURE",
            "CME",
            "MMEASURE",
            "MM",
        )
        self.com.write(f":TRIGGER{n}:INPUT {trigger_response}")

    def sense_power_range_auto(self, n, val):
        val = str(val).upper()
        assert val in ("0", "OFF", "1", "ON")
        self.com.write(f":SENSE{n}:POWER:RANGE:AUTO {val}")

    def sense_power_range_auto_ask(self, n):
        return int(self.com.query(f":SENSE{n}:POWER:RANGE:AUTO?"))

    def sense_power_range_dbm(self, n, range):
        """
        Sets the power range for the channel.
        The range changes at 10 dBm intervals. The corresponding ranges for linear
        measurements (measurements in Watts) is given below:
        :param range:
            The range as a float value in dBm. The number is rounded to the closest multiple of 10, because the range changes at 10
            dBm intervals. Units are in dBm.
        """
        range = int(range)
        # XXX: or could be tolerant to the rounding
        assert range in (+10, 0, -10, -20, -30)
        self.com.write(f":SENSE{n}:POWER:RANGE {range}dBm")

    def sense_power_range_ask(self, n):
        """
        NOTE: this is always dB even if units are W
        """
        self.assert_n(n)
        return float(self.com.query(f":SENSE{n}:POWER:RANGE?").strip())

    def sense_power_range_ask_w(self, n):
        """
        Range           Upper Linear Power Limit
        +10 dBm         19.999 mW
        0 dBm           1999.9 mW
        -10 dBm         199.99 mW
        -20 dBm         19.999 mW
        -30 dBm         1999.9 nW
        """
        # returned as float, but is in clear 10 db increments
        dbm = int(self.sense_power_range_ask(n))
        return {
            +10: 2e-2,
            0: 2e-3,
            -10: 2e-4,
            -20: 2e-5,
            -30: 2e-6,
        }[dbm]

    def sense_power_range_ask_mw(self, n):
        return self.sense_power_range_ask_w(n) * 1e3

    def sense_power_unit(self, n, val):
        val = str(val).upper()
        assert val in ("0", "DBM", "1", "WATT")
        self.com.write(f":SENSE{n}:POWER:UNIT {val}")

    def sense_power_unit_ask(self, n):
        """
        :SENSe[n][:CHANnel[m]]:POWer:UNIT?
        """
        return int(self.com.query(f":SENSE{n}:POWER:UNIT?"))

    def sense_power_unit_ask_str(self, n):
        return {
            0: "dBm",
            1: "Watt",
        }[self.sense_power_unit_ask(n)]

    def sense_power_gain_auto_ask(self, n):
        """
        • 0 = Auto Gain Off.
        This is the position for best transient response.
        • 1 = Auto Gain On (Default)
        This is the Position for best dynamic.
        """
        return int(self.com.query(f":SENSE{n}:POWER:GAIN:AUTO?"))

    def sense_power_wavelength_nm(self, n, val):
        self.com.write(f":SENSE{n}:POWER:WAVELENGTH {val}NM")

    def sense_power_wavelength_ask(self, n):
        self.assert_n(n)
        return float(self.com.query(f":SENSE{n}:POWER:WAVELENGTH?"))

    def sense_power_wavelength_ask_nm(self, n):
        return self.sense_power_wavelength_ask(n) * 1e9


if __name__ == "__main__":
    import time

    import pyvisa

    rm = pyvisa.ResourceManager()

    detector = KeysightN7745C("TCPIP::192.168.111.70::INSTR")
    print(detector.idn_ask())

    if 0:
        detector.sense_function_state(1, "STOP")
        detector.trigger_input(1, "IGNORE")
        detector.initiate_channel_continuous(1, None, True)
        detector.sense_power_range_dbm(-20)

    if 1:
        detector.clear_errors()
        detector.assert_errors()

        # Diff around 200
        nm_min = 1450
        nm_max = 1650
        nm_per_sec = 10
        samples = 10000
        total_seconds = (nm_max - nm_min) / nm_per_sec
        tsample = total_seconds / samples
        print("Desired sweep")
        print(f"  Range: {nm_min} nm to {nm_max} nm")
        print(f"  Samples {samples}")
        print(f"  nm_per_sec {nm_per_sec}")
        print(f"  total_seconds {total_seconds}")
        print(f"  tsample {tsample}")

        n = 1
        detector.sense_function_state(n, "LOGGING", "STOP")
        detector.sense_power_unit(n, "Watt")
        detector.trigger_input(n, "CMEASURE")
        detector.sense_power_range_auto(n, "OFF")
        detector.sense_power_range_dbm(n, +10)
        """
        10000 points
        Sweep 1450 to 1650 nm
        50 ms / nm => Sweep 200 nm in 10 sec
        """
        # detector.sense_function_parameter_logging(0, samples, tsample)
        detector.sense_function_parameter_logging(1, samples, tsample)
        detector.sense_function_state(n, "LOGGING", "START")
        detector.assert_errors()

        # Force trigger in lieu of hardware trigger
        detector.trigger_the_input()

        # while 'PROGRESS' == detector.sense_function_state_ask_state(n):
        while detector.sense_function_state_ask_is_running(n):
            print(detector.sense_function_state_ask(n))
            time.sleep(0.1)

        print("done, getting data")
        data = detector.sense_function_result_ask()

        print("plotting")
        import matplotlib.pyplot as plt

        plt.plot(data)
        plt.show()
