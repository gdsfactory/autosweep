class TestResult:

    def __init__(self):
        self._results = {}

    def _get_internal_report_name(self, report_name: str):
        if not isinstance(report_name, str):
            raise TypeError("'report_name' argument must be of type 'str'")

    def add_spec(self, report_name: str, spec: str, value: int | float | bool, unit: str):
        # type checking

        if not isinstance(spec, str):
            raise TypeError("'spec' argument must be of type 'str'")
        if not isinstance(value, (int, float, bool)):
            raise TypeError("'value' argument must either type 'int' or 'float' or 'bool'")
        if not isinstance(unit, str):
            raise TypeError("'unit' argument must be of type 'str'")

    def clear_specs(self, report_name: str):
        if not isinstance(report_name, str):
            raise TypeError("'report_name' argument must be of type 'str'")

        self._results[report_name]['specs'] = []
