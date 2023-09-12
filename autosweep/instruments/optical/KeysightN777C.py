"""
https://www.keysight.com/us/en/product/N7778C/tunable-laser-source-high-power-low-sse-value-line.html

Wavelength:
1240 nm to 1380 nm (Option 113)
1340 nm to 1495 nm (Option 114)
1490 nm to 1640 nm (Option 116)
1450 nm to 1650 nm (Option 216)

Wavelength resolution 0.1 pm (17.5 MHz at 1310 nm, 14.3 MHz at 1450 nm, 12.5 MHz at 1550 nm)
"""
from autosweep.instruments import abs_instr
from autosweep.instruments.coms import visa_coms
import time

class KeysightN777C(abs_instr.AbsInstrument):
    """
    Driver written by John McMaster

    :param addrs: The VISA-resource string for this instrument
    :type addrs: str
    """

    def __init__(self, addrs: str):
        super().__init__(com=visa_coms.VisaCOM(addrs=addrs))
        model = self.model()
        if model not in ("N7776C", "N7778C", "N7779C"):
            raise ValueError(f"Unexpected model {model}")
        self.clear_errors()
        self.assert_errors()
        self._min_nm = self.source_wavelength_ask_nm("MIN")
        self._max_nm = self.source_wavelength_ask_nm("MAX")

    def get_min_nm(self):
        return self._min_nm

    def get_max_nm(self):
        return self._max_nm

    def idn_ask(self):
        return self.com.query('*IDN?').strip()

    def idn_ask_dict(self):
        vendor, model,serial,version = self.idn_ask().split(",")
        """
        Example
        IDN Keysight Technologies,N7778C,DE59800324,V2.022
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
        return self.com.query(":system:error?").strip()

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
            assert 0, "Encountered errors: %s" % (errors,)


    def validate_wavelength_nm(self, val):
        # FIXME: how to query from the instrument?
        # got current as 1310
        # Website lists acceptable wavelenghts as: 1240-1380 nm or 1340-1495 nm or 1450-1650 nm or 1490-1640 nm
        # assert 1240 <= val <= 1380, val
        assert self._min_nm <= val <= self._max_nm, f"Require {self._min_nm} <= {val} <= {self._max_nm}"

    def source_wavelength_nm(self, val):
        """
        Sets the absolute wavelength of the output.
        :WAVelength <wsp><value> [PM|NM|UM|MM|M]
        """
        self.validate_wavelength_nm(val)
        self.com.write(f":sour0:wav {val}NM")

    def source_wavelength_ask(self, val=None):
        """
        Raw: Returns the wavelength value in meters.
        Convert to nm to make consistent

        WARNING: I think min / max wavelength may drift around?
        Need to look into this more
        """
        if val is not None:
            val = val.upper()
            assert val in ("MIN", "MAX", "DEF")
            return float(self.com.query(f":sour0:wav? {val}"))
        else:
            return float(self.com.query(":sour0:wav?"))

    def source_wavelength_ask_nm(self, val=None):
        return self.source_wavelength_ask(val) * 1e9

    def lock(self, val, password="1234"):
        val = int(bool(val))
        return self.com.write(f":lock {val},{password}")

    def lock_ask(self):
        return int(self.com.query(":lock?"))

    def source_power_state(self, val):
        """
        Syntax: :SOURce0:POWer:STATe<wsp><boolean>
        Switches the laser of the chosen source on or off.
        
        Manual implies this is the same thing as the shutter
        NOTE: you can't call this even to disable when locked
        """
        val = int(bool(val))
        return self.com.write(f":sour0:pow:stat {val}")

    def source_power_state_ask(self):
        """
        Queries the laser state of the chosen source.
        """
        return int(self.com.query(":sour0:pow:stat?"))

    def source_power_mw(self, val):
        return self.com.write(f":sour0:pow {val}mW")

    def source_power_ask(self):
        """
        Returns the amplitude level of the output power.
        The value returned is the actual amplitude that is output, which may be different from the value set for the output. If these
        two figures are not the same, it is indicated in the :STATus:OPERation register.
        """
        return float(self.com.query(":sour0:pow?"))

    def source_power_unit_ask(self):
        """
        Return the current power units 

        0: dBm
        1: Watts
        """
        return int(self.com.query(":sour0:pow:unit?"))

    def source_power_unit_ask_str(self):
        raw = self.source_power_unit_ask()
        return {
            0: "dBm",
            1: "Watts",
        }[raw]

    def source_power_ask_mw(self):
        assert self.source_power_unit_ask_str() == "Watts"
        return self.source_power_ask() * 1e3

    def source_wavelength_correction_ara(self):
        """
        Realigns the laser cavity
        """
        self.com.write(f":sour0:wav:corr:ara")

    def source_wavelength_sweep_ask(self):
        """
        """
        return self.com.query(":sour0:wav:swe:chec?").strip()

    def source_wavelength_sweep_ask_assert(self):
        """
        """
        res = self.source_wavelength_sweep_ask()
        if res != "0,OK":
            raise Exception("Bad sweep configuration")

    def source_wavelength_sweep_mode(self, mode):
        mode = mode.upper()
        assert mode in ("STEP", "STEPPED", "MAN", "MANUAL", "CONT", "CONTINUOUS")
        self.com.write(f":sour0:wav:swe:mode {mode}")

    def source_wavelength_sweep_mode_ask(self):
        ret = self.com.query(":sour0:wav:swe:mode?").strip()
        assert ret in ("STEP", "MAN", "CONT")
        return ret

    def source_wavelength_sweep_start_nm(self, val):
        self.validate_wavelength_nm(val)
        self.com.write(f":sour0:wav:swe:star {val}nm")

    def source_wavelength_sweep_start_ask_nm(self):
        return float(self.com.query(":sour0:wav:swe:star?")) * 1e9

    def source_wavelength_sweep_stop_nm(self, val):
        self.validate_wavelength_nm(val)
        self.com.write(f":sour0:wav:swe:stop {val}nm")

    def source_wavelength_sweep_stop_ask_nm(self):
        return float(self.com.query(":sour0:wav:swe:stop?")) * 1e9

    def source_wavelength_sweep_step_nm(self, val):
        self.com.write(f":sour0:wav:swe:step {val}nm")

    def source_wavelength_sweep_step_ask_nm(self):
        return float(self.com.query(":sour0:wav:swe:step?")) * 1e9

    def source_wavelength_sweep_speed_nms(self, val):
        self.com.write(f":sour0:wav:swe:spe {val}nm/s")

    def source_wavelength_sweep_speed_ask_nms(self):
        return float(self.com.query(":sour0:wav:swe:spe?")) * 1e9

    def source_wavelength_sweep_cycles(self, val):
        self.com.write(f":sour0:wav:swe:cycl {val}")

    def source_wavelength_sweep_cycles_ask(self):
        return int(self.com.query(":sour0:wav:swe:cycl?"))

    def source_wavelength_sweep_dwell_ms(self, val):
        self.com.write(f":sour0:wav:swe:dwel {val}ms")

    def source_wavelength_sweep_dwell_ask_ms(self):
        return float(self.com.query(":sour0:wav:swe:dwel?")) * 1e3

    def source_wavelength_sweep_state(self, val):
        val = str(val).upper()
        assert val in ("0", "STOP", "1", "START", "STAR", "2", "PAUSE", "PAUS", "3", "CONT", "CONTINUE")
        self.com.write(f":sour0:wav:swe {val}")

    def source_wavelength_sweep_state_ask(self):
        ret = int(self.com.query(":sour0:wav:swe?"))
        assert ret in (0, 1, 2)
        return ret

    def source_wavelength_sweep_state_ask_str(self):
        val = self.source_wavelength_sweep_state_ask()
        return {
            0: "NOT_RUNNING",
            1: "RUNNING",
            2: "PAUSED",
        }[val]

    def source_wavelength_sweep_softtrigger(self):
        """
         Softtrigger does the same as a normal (hardware) trigger at the backplane.
        Usage:
        - Trigger input configuration: Start Sweep
        - Start Sweep
        - SoftTrigger
        """
        self.com.write(":sour0:sour0:wav:swe:soft")
        
    def sweep_abort_if_running(self):
        """
        Stop any active sweeps
        """
        state = self.source_wavelength_sweep_state_ask_str()
        if state != "NOT_RUNNING":
            self.source_wavelength_sweep_state("STOP")
            state = self.source_wavelength_sweep_state_ask_str()
            assert state == "NOT_RUNNING"

    def sweep_full_range(self):
        # FIXME: why is there a delta on this?
        self.source_wavelength_sweep_start_nm(self.source_wavelength_ask_nm("MIN") + 5)
        self.source_wavelength_sweep_stop_nm(self.source_wavelength_ask_nm("MAX") - 5)

    def sweep_continuous_start(self,
                   power_mw=None,
                   # Set either start/stop or full_range
                   start_nm=None, stop_nm=None, rull_range=None,
                   speed_nms=None,
                    ):
        self.sweep_abort_if_running()
        self.source_wavelength_sweep_mode("CONT")
        if power_mw:
            self.source_power_mw(power_mw)
        if speed_nms:
            self.source_wavelength_sweep_speed_nms(speed_nms)

        self.assert_errors()
        # Range setup
        if start_nm:
            self.source_wavelength_sweep_start_nm(start_nm)
        if stop_nm:
            self.source_wavelength_sweep_start_nm(start_nm)
        if rull_range:
            self.sweep_full_range()
        self.assert_errors()

        # Now that everything should be configured verify configuration
        self.source_wavelength_sweep_ask_assert()

        # Unlock and turn on laser
        self.lock(False)
        self.source_power_state(True)

        # General error sweep
        self.assert_errors()

        print("Sweep, continuous: starting")
        self.source_wavelength_sweep_state("START")


    def sweep_wait_done(self):
        while True:
            state = self.source_wavelength_sweep_state_ask_str()
            if state == "NOT_RUNNING":
                break
            time.sleep(1.0)

    def trigger_configuration(self, val):
        """
        """
        val = str(val).upper()
        assert val in ("0", "DIS", "DISABLED", "1", "DEF", "DEFAULT", "2", "PASS", "PASSTHROUGH", "3", "LOOP", "LOOPBACK")
        self.com.write(f":trig:conf {val}")

    def trigger_configuration_ask(self):
        """
        """
        ret = self.com.query("trig:conf?").strip().upper()
        assert ret in ("0", "DIS", "DISABLED", "1", "DEF", "DEFAULT", "2", "PASS", "PASSTHROUGH", "3", "LOOP", "LOOPBACK")
        return ret

    def trigger_output(self, val):
        """
        """
        val = val.upper()
        assert val in ("DIS", "DISABLED", "STF", "STFINISHED", "SWF", "SWFINISHED", "SWSTARTED")
        self.com.write(f":trig0:outp {val}")

    def trigger_output_ask(self):
        """
        """
        ret = self.com.query(":trig0:outp?").strip().upper()
        # XXX: this is what the manual says, but suspcious
        assert ret in ("DIS", "DISABLED", "STF", "STFINISHED", "SWF", "SWFINISHED", "SWSTARTED")
        return ret



    """
    Status Byte (STB)
    Operational Status Event Summary Register (OSESR)
    Operational Status Enable Summary Mask (OSESM)
    Operational Slot Status Event Register (OSSER)
    Operation Slot Status Enable Mask (OSSEM)

    The slot status register (OSSER) has a mask (OSSEM)
    that you need to enable if you want to affect OSESR
    Intention unclear. Maybe an event can trigger a write

    OSESM vs OSSEM?
    
    Questionable Status Event Summary Register (QSESR)
    Questionable Status Enable Summary Mask (QSESM)
    """

    def get_OSESM(self):
        """
        Returns the OSESM for the OSESR
        :STATus:OPERation:ENABle?
        """
        return int(self.com.query(":stat:oper:enab?"))

    def set_OSESM(self, val):
        """
        :STATus:OPERation:ENABle<wsp><value>

        Sets the bits in the Operational Status Enable Summary Mask (OSESM) that enable the contents of the OSESR to affect the
        Status Byte (STB).
        Setting a bit in this register to 1 enables the corresponding bit in the OSESR to affect bit 7 of the Status Byte.
        """
        self.com.write(f":stat:oper:enab {val}")

    def get_OSSER(self):
        """
        Returns the Operational Slot Status Event Register (OSSER) of the laser module.
        Response: The results for the individual slot events (a 16-bit unsigned integer value, where 0 ≤ value ≤ 65535):
        Bit         Description
        5-15        Not used
        4           Slot n: shutter has been opened
        3           Slot n: Zeroing ongoing
        2           Not used
        1           Slot n: Coherence Control has been switched on
        0           Slot n: Laser has been switched on
        """
        return int(self.com.query(":stat0:oper?"))

    def set_OSSEM(self, val):
        """
        :STATus0:OPERation:ENABle<wsp><value>

        Sets the bits in the Operation Slot Status Enable Mask (OSSEM) for the laser module that enable the contents of the
        Operation Slot Status Event Register (OSSER) to affect the OSESR.
        Setting a bit in this register to 1 enables the corresponding bit in the OSSER and OSESR.
        """
        self.com.write(f":stat0:oper:enab {val}")

    def get_OSCSR(self):
        """
        Reads the Operational Status Condition Summary Register. 
        """
        return int(self.com.query(":stat:oper:cond?"))

    def dump_state(self, status=False):
        print("KeysightN777-C state")
        print("  IDN", self.idn_ask())
        print("  Lock", self.lock_ask())
        print("  Is on", self.source_power_state_ask())
        print("  Wavelength")
        print("    Current: %0.3f nm" % self.source_wavelength_ask_nm())
        print("    Min: %0.3f nm" % self.source_wavelength_ask_nm("MIN"))
        print("    Max: %0.3f nm" % self.source_wavelength_ask_nm("MAX"))
        print("  Power", self.source_power_ask())
        print("  Power units", self.source_power_unit_ask_str())
        print("  Power", self.source_power_ask_mw(), "mW")
        # Advanced usage
        if status:
            print("Status")
            print("  OSSER:", self.get_OSSER())
            print("  OSEM:", self.get_OSESM())
            print("  OSCSR:", self.get_OSCSR())

if __name__ == '__main__':
    import pyvisa
    import time

    rm = pyvisa.ResourceManager()

    # Insufficient location information or the requested device or resource is not present in the system.
    # laser = KeysightN777C('TCPIP0::K-N7x778C-00324::inst0::INSTR')
    # fallback to IP address
    laser = KeysightN777C('TCPIP::192.168.111.72::INSTR')

    try:
        laser.dump_state()
        

        if 0:
            print("Check lock")
            laser.lock(True)
            laser.assert_errors()
            # can't even disable when locked
            # laser.source_power_state(False)
            laser.assert_errors()
            print("  Lock", laser.lock_ask())
            print("  Is on", laser.source_power_state_ask())



        print("")

        # shutter test
        # unclear if I need to manually control this
        if 0:
            print("")
            print("OSSER", laser.get_OSSER())
            print("OSEM", laser.get_OSESM())
            print("OSCSR", laser.get_OSCSR())
            print("")
            laser.set_OSESM(0x10)
            laser.set_OSSEM(0x10)
            print("OSSER", laser.get_OSSER())
            print("OSEM", laser.get_OSESM())
            print("OSCSR", laser.get_OSCSR())
        # wavelength test
        # xxx: how can I query the allowed wavelewngth range?
        if 0:
            print("wavelength %0.3f nm" % laser.source_wavelength_ask())
            laser.source_wavelength_set()
            print("wavelength %0.3f nm" % laser.source_wavelength_ask())

        # test fire simple
        if 0:
            print("fire the laser!")
            print("pew pew")
            laser.source_power_mw(1)
            laser.source_wavelength_nm(1310)
            laser.source_power_state(True)

            print("")
        laser.dump_state()

        # sweep test: step
        if 0:
            """
            :sour0:wav:swe:cycl 3
            set coherence?
                N7778C and N7779C
                not supported on N7776C
            
            140 nm range
            5000 steps suggested => 0.028 step s
            ize
            """

            # If an old sweep is running stop it before changing settings
            state = laser.source_wavelength_sweep_state_ask_str()
            if state != "NOT_RUNNING":
                laser.source_wavelength_sweep_state("STOP")
                state = laser.source_wavelength_sweep_state_ask_str()
                assert state == "NOT_RUNNING"

            # do we need to turn this back on?
            # or does sweep imply turning on
            laser.source_power_mw(1)
            laser.source_power_state(True)
            laser.source_wavelength_sweep_mode("STEP")
            laser.source_wavelength_sweep_start_nm(1240)
            laser.source_wavelength_sweep_stop_nm(1380)

            # laser.source_wavelength_sweep_step_nm(0.028)
            laser.source_wavelength_sweep_step_nm(10)
            laser.source_wavelength_sweep_dwell_ms(0.01)
            # hmm timed out
            # laser.source_wavelength_sweep_ask_assert()
            # laser.source_wavelength_sweep_softtrigger()
            print("Checking sweep")
            laser.source_wavelength_sweep_ask_assert()
            print(f"Sweep state:", laser.source_wavelength_sweep_state_ask_str())
            laser.assert_errors()
            print("Starting sweep")
            laser.lock(False)
            laser.source_power_state(True)
            laser.assert_errors()
            laser.source_wavelength_sweep_state("START")
            # laser.source_wavelength_sweep_step_next()
            while True:
                state = laser.source_wavelength_sweep_state_ask_str()
                print(f"Sweep state: {state}")
                if state == "NOT_RUNNING":
                    break
                time.sleep(1.0)

        # sweep test: continuous
        if 0:
            """
            :sour0:wav:swe:cycl 3
            set coherence?
                N7778C and N7779C
                not supported on N7776C
            
            140 nm range
            5000 steps suggested => 0.028 step size
            """

            laser.sweep_abort_if_running()

            # trigger out at start of sweep
            laser.trigger_configuration("DEFAULT")
            laser.trigger_output("SWSTARTED")

            # do we need to turn this back on?
            # or does sweep imply turning on
            laser.source_power_mw(1)
            laser.assert_errors()
            laser.source_wavelength_sweep_mode("CONT")
            laser.assert_errors()
            # AssertionError: Encountered errors: ['-222,"Data out of range"']
            # laser.source_wavelength_sweep_start_nm(1240)
            # this went up from 1240 to 1243 nm after changing some settings
            # why?
            # Definitely need to query range
            laser.source_wavelength_sweep_start_nm(1243)
            laser.assert_errors()
            # laser.source_wavelength_sweep_stop_nm(1380)
            laser.source_wavelength_sweep_stop_nm(1377)
            laser.assert_errors()
            laser.source_wavelength_sweep_speed_nms(100)
            laser.assert_errors()
            laser.source_wavelength_sweep_ask_assert()
            laser.assert_errors()
            # laser.source_wavelength_sweep_softtrigger()
            laser.lock(False)
            laser.source_power_state(True)
            laser.assert_errors()
            print("Sweep, continuous: starting")
            laser.source_wavelength_sweep_state("START")
            while True:
                state = laser.source_wavelength_sweep_state_ask_str()
                print(f"Sweep state: {state}")
                if state == "NOT_RUNNING":
                    break
                time.sleep(1.0)
    finally:
        laser.print_if_errors()
        # laser.idle()
