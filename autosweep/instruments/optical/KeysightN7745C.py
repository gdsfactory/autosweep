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

    def idn_ask(self):
        return self.com.query("*IDN?")

    def system_error_ask(self):
        return self.com.query(":system:error?")

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
        return float(self.com.query(f":fetch{n}:power?"))

    def fetch_power_all(self):
        """
        Reads all current power meter values. It does not provide its own triggering and so must be used with either continuous
        software triggering or a directly preceding immediate software trigger.
        It returns the value the previous software trigger measured. Any subsequent FETCh command will return the same value, if
        there is no subsequent software trigger.

        :return: Data values are always in Watt. (Seems no to be the case)
        """
        return self.com.query_binary_values(
            ":fetch:power:all?", datatype="f", is_big_endian=False
        )

    def initiate_channel_immediate(self, n, m):
        """
        Initiates the software trigger system and completes one full trigger cycle, that is, one measurement is made for selected [n].
        In logging mode it triggers all channels independent from [n].
        """
        if m:
            self.com.write(f":initiate{n}:channel{m}:immediate")
        else:
            self.com.write(f":initiate{n}:immediate")

    def initiate_channel_continuous(self, n, channel, continuous):
        """
        A boolean value:
        False: do not measure continuously
        True: measure continuously
        """
        if channel:
            self.com.write(
                f':initiate{n}:channel{channel}:continuous {"on" if continuous else "off"}'
            )
        else:
            self.com.write(f':initiate{n}:continuous {"on" if continuous else "off"}')

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
        self.com.write(
            f":sense{n}:function:parameter:logging {data_points},{averaging_time}"
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
        """
        result = np.array(
            self.com.query_binary_values(
                ":sense:function:result?", datatype="f", is_big_endian=False
            )
        )
        self.com.read()
        return result

    def sense_function_state(self, n, state):
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

        self.com.write(f":sense{n}:function:state {state}")

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

        return self.com.query(f"sense{n}:function:state?")

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
        self.com.write(f":trigger{n}:input {trigger_response}")

    def sense_power_range(self, range):
        """
        Sets the power range for the channel.
        The range changes at 10 dBm intervals. The corresponding ranges for linear
        measurements (measurements in Watts) is given below:
        :param range:
            The range as a float value in dBm. The number is rounded to the closest multiple of 10, because the range changes at 10
            dBm intervals. Units are in dBm.
        """

        self.com.write(f":sense:power:range {range}dBm")


if __name__ == "__main__":
    import time

    import pyvisa

    rm = pyvisa.ResourceManager()

    detector = KeysightN7745C(rm.open_resource("TCPIP::192.168.111.144::INSTR"))

    detector.sense_function_state(1, "stop")
    detector.trigger_input(1, "ignore")
    detector.initiate_channel_continuous(1, None, True)
    detector.sense_power_range(-20)

    exit()

    detector.sense_function_state(1, "logging,stop")
    detector.trigger_input(1, "Cmeasure")
    detector.sense_function_parameter_logging(0, 10000, f"{(1650 - 1450) / 20 / 10000}")
    detector.sense_function_state(1, "logging,start")

    while "PROGRESS" in detector.sense_function_state_ask(1):
        print(detector.sense_function_state_ask(1))
        time.sleep(0.5)

    data = detector.sense_function_result_ask()

    import matplotlib.pyplot as plt

    plt.plot(data)
    plt.show()
