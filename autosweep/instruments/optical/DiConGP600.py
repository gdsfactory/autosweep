from autosweep.instruments import abs_instr
from autosweep.instruments.coms import visa_coms


class DiConGP600X1(abs_instr.AbsInstrument):
    """
    Driver written by John McMaster
    This is a very versatile instrument
    However, limit to scope assuming we are in an "X1" configuration
    Most commands are from "Table 4-11. 3D Matrix MxN Switch RS232 Serial Port (ASCII) Command Set"

    :param addrs: The VISA-resource string for this instrument
    :type addrs: str
    """

    def __init__(self, addrs: str):
        super().__init__(com=visa_coms.VisaCOM(addrs=addrs))
        print("Got comm")
        model = self.model()
        if model not in ("GP600",):
            raise ValueError(f"Unexpected model {model}")
        self.clear_errors()
        self.assert_errors()
        # Xn = 3D Matrix Switch
        if self.system_configuration_ask() != "X1":
            raise ValueError("Only X1 configuration supported")
        self._configuration = "X1"
        self._inputs, self._outputs = self.dimensions_ask()
        
    def get_inputs(self):
        return self._inputs

    def get_outputs(self):
        return self._outputs

    def idn_ask(self):
        return self.com.query('*IDN?').strip()

    def version_ask(self):
        return self.com.query('VER?').strip()

    def system_configuration_ask(self):
        return self.com.query('SYST:CONF?').strip()

    def idn_ask_dict(self):
        vendor, model,serial,version = self.idn_ask().split(",")
        """
        Example
        Dicon Fiberoptics Inc, GP600, 19A0M10D0117, 7.0
        """
        return {
            "vendor": vendor.strip(),
            "model": model.strip(),
            "serial": serial.strip(),
            "version": version.strip(),
        }

    def model(self):
        return self.idn_ask_dict()["model"]

    """
    This command appears to be broken
    doesn't return anything...
    but our code is perfect so we don't need it!
    """
    
    def system_error_ask(self):
        # for some reason it doesn't like the :
        # return self.com.query(":SYST:ERR?")
        return self.com.query("SYST:ERR?").strip()

    def clear_errors(self):
        while True:
            error = self.system_error_ask().strip()
            if error == '+0, No Error':
                break

    def print_if_errors(self):
        errors = []
        while True:
            error = self.system_error_ask().strip()
            if error == '+0, No Error':
                break
            errors.append(error)
        if errors:
            print("Encountered errors:", errors)

    def assert_errors(self):
        errors = []
        while True:
            error = self.system_error_ask().strip()
            if error == '+0, No Error':
                break
            errors.append(error)
        if errors:
            assert 0, "Encountered errors: %s" % (errors,)

    def reset(self):
        """
        Disconnect all fibers
        """
        self.com.write("RESET")

    def wen(self, val):
        """
        Enables or disables the auto save state feature
        """
        val = int(bool(val))
        self.com.write(f"WEN {val}")

    def wen_ask(self):
        return int(self.com.query("WEN?"))

    def channel(self, input, output):
        """
        Selects the 3D matrix switch channel
        Connecting an input channel to output channel 0 will switch that input to the off 
        position
        """
        assert 1 <= input <= self._inputs
        assert 0 <= output <= self._outputs
        self.com.write(f"X1 CH {input} {output}")

    def channels(self, vals):
        for input, output in vals:
            self.channel(input, output)

    def channel_ask(self, input):
        """
        Get the output for corresponding input
        """
        assert 1 <= input <= self._inputs
        ret_input, ret_output = [int(x) for x in self.com.query(f"X1 CH {input}?").split(",")]
        ret_input = int(ret_input)
        ret_output = int(ret_output)
        assert ret_input == input
        return ret_output

    def dimensions_ask(self):
        inputs, outputs = [int(x) for x in self.com.query("X1 DIM?").split(",")]
        return inputs, outputs

    def wavelengths_availible_ask(self):
        """
        Queries the 3D matrix switch’s available calibrated wavelengths
        in nm
        """
        return [float(x) for x in self.com.query("X1 WAVESAVAIL?").split(",")]

    def wavelength(self, val):
        """
        Sets the 3D matrix switch’s active wavelength
        """
        self.com.write(f"X1 W {val}")

    def wavelength_ask(self):
        """
        Queries the 3D matrix switch’s current working wavelength
        Improves mirror steering / will reduce losses
        """
        return float(self.com.query("X1 W?"))

    # didn't implement inc / dec commands
    # not how we are using this

    def print_state(self):
        print("DiConGP600 state")
        print("  IDN", self.idn_ask())
        # same info as in IDN
        # print("Firmware version", switch.version_ask())
        print("  CONF", self.system_configuration_ask())
        print("  X1")
        print("    Dimensions", self.dimensions_ask())
        print("    Wavelengths", self.wavelengths_availible_ask())
        inputs = self.get_inputs()
        outputs = self.get_outputs()
        print(f"    Channels ({inputs} inputs x {outputs} outputs)")
        for input in range(1, inputs + 1, 1):
            output = self.channel_ask(input)
            print(f"         Input {input} => output {output}")

if __name__ == '__main__':
    """
    "For INSTR, this requires a device that supports the T&M standard LAN instrument protocol"
    """
    switch = DiConGP600X1('TCPIP0::192.168.111.187::10001::SOCKET')
    print("Connect ok")
    switch.print_state()
    if 0:
        switch.com.write("RESET")
        switch.com.write(":RESET")
        switch.clear_errors()
    switch.print_state()

    print("")
    print("")
    print("")

    try:
        if 1:
            switch.print_state()
            switch.channel(1, 2)
            switch.reset()
            switch.print_state()
    finally:
        switch.print_if_errors()
