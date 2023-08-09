from autosweep.instruments import abs_instr
from autosweep.instruments.coms import visa_coms


class Keysight8164B(abs_instr.AbsInstrument):
    """
    Driver written by Helge Gehring, modified to work with AutoSweep.

    :param addrs: The VISA-resource string for this instrument
    :type addrs: str
    """

    def __init__(self, addrs: str):
        super().__init__(com=visa_coms.VisaCOM(addrs=addrs))

    def idn_ask(self):
        return self.com.query('*IDN?')

    def system_error_ask(self):
        return self.com.query(":system:error?")

    def source_channel_wavelength(self, source, channel, wavelength):
        """
        Sets the absolute wavelength of the output.

        :param wavelength:
            Any wavelength in the specified range (see the specifications in the appropriate User’s Guide).
            The programmable range is larger than the range specified in the User’s Guide. The programmable range is set individually
            for each instrument when it is calibrated during production.
        :return:
        """
        self.com.write(
            (f':source{source}' if source else '') +
            (f':channel{channel}' if channel else '') +
            f':wavelength {wavelength}'
        )

    def source_channel_wavelength_sweep_softtrigger(self, source=None, channel=None):
        self.com.write(
            (f':source{source}' if source else '') +
            (f':channel{channel}' if channel else '') +
            ':wavelength' +
            ':sweep' +
            ':softtrigger'
        )

    def source_channel_wavelength_sweep_state(self, source, channel, state):
        """
        Stops, starts, pauses or continues a wavelength sweep.

        :param state:
                0 or STOP: Stop the sweep.
                1 or STARt: Start a sweep, run sweep.
                2 or PAUSe: Pause the sweep. (doesn’t apply for continuous sweep)
                3 or CONTinue: Continue a sweep. (doesn’t apply for continuous sweep)

        If you enable lambda logging (see [:SOURce[n]][:CHANnel[m]]:WAVelength:SWEep:LLOGging on
        page 170 ) and modulation (see [:SOURce[n]][:CHANnel[m]]:AM:STATe[l] on page 127 ) simultaneously, a
        sweep cannot be started.

        Generally, a continuous sweep can only be started if:
        the trigger frequency, derived from the sweep speed and sweep step, is <= 40kHz, or <=1MHz for 81602A, 81606A, 81607A,
        81608A, and 81960A.
        the number of triggers, calculated from the sweep span and sweep span, is <=100001
        the start wavelength is less than the stop wavelength.
        In addition, a continuous sweep with lambda logging requires:
        the trigger output to be set to step finished
        modulation set to coherence control or off.
        """

        self.com.write(
            (f':source{source}' if source else '') +
            (f':channel{channel}' if channel else '') +
            ':wavelength' +
            ':sweep' +
            f':state {state}'
        )

    def source_channel_wavelength_sweep_state_ask(self, source=None, channel=None):
        """
        Returns the state of a sweep.

        :return: True if running
        """
        return '+1' in self.com.query(
            (f':source{source}' if source else '') +
            (f':channel{channel}' if channel else '') +
            ':wavelength' +
            ':sweep' +
            ':state?'
        )

    def trigger_channel_output(self, trigger, channel, mode):
        """
        Specifies when an output trigger is generated and arms the module.

        :param trigger:
        :param channel:
        :param mode:
            DISabled: Never.
            AVGover: When averaging time period finishes.
            MEASure: When averaging time period begins.
            MODulation: For every leading edge of a digitally-modulated (TTL) signal
            STFinished: When a sweep step finishes.
            SWFinished: When sweep cycle finishes.
            SWSTarted: When a sweep cycle starts.
        """

        self.com.write(
            f':trigger{trigger}' +
            (f':channel{channel}' if channel else '') +
            f':output {mode}'
        )

    def output_channel_state(self, output, channel, state):
        self.com.write(
            f':output{output}' +
            (f':channel{channel}' if channel else '') +
            f':state {"ON" if state else "OFF"}'
        )
