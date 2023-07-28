from typing import TYPE_CHECKING
import jinja2

from ta.utils import io
from ta import sweep
if TYPE_CHECKING:
    from ta.test_exec import TestExec


class ResultsHold:

    def __init__(self):
        self._specs = {}
        self._entries = {}

    @property
    def specs(self) -> dict:
        return self._specs

    @property
    def entries(self) -> dict:
        return self._entries

    def add_spec(self, report_heading: str, spec: str, unit: str, value: int | float | bool) -> None:
        # type checking
        if not isinstance(report_heading, str):
            raise TypeError("'report_heading' argument must be of type 'str'")
        if not isinstance(spec, str):
            raise TypeError("'spec' argument must be of type 'str'")
        if not isinstance(unit, str):
            raise TypeError("'unit' argument must be of type 'str'")
        if not isinstance(value, (int, float, bool)):
            raise TypeError("'value' argument must be of type 'int', 'float', or 'bool'")

        if report_heading not in self._specs:
            self._specs[report_heading] = []

        self._specs[report_heading].append({'spec': spec, 'unit': unit, 'value': value})

    def clear_specs(self, report_name: str):
        if not isinstance(report_name, str):
            raise TypeError("'report_name' argument must be of type 'str'")

        if report_name not in self._specs:
            raise ValueError(f"the 'report_name', '{report_name}' is not a valid value")

        self._specs[report_name] = []

    def add_report_entry(self, report_heading: str, fig_hdlr: sweep.FigHandler | None = None, info: dict | None = None):
        """
        Overwriting previous value

        :param report_heading:
        :param fig_hdlr:
        :param info:
        :return:
        """
        if not isinstance(report_heading, str):
            raise TypeError("'report_name' argument must be of type 'str'")
        if fig_hdlr is not None and not isinstance(fig_hdlr, sweep.FigHandler):
            raise TypeError("The optional argument 'fig_hdlr' must be of type 'ta.sweep.FigHandler'")
        if info is not None and not isinstance(info, dict):
            raise TypeError("The optional argument 'info' must be of type 'dict'")

        if report_heading in self._entries:
            raise ValueError(f"The report_heading '{report_heading}', is already defined.")

        self._entries[report_heading] = {'fig': fig_hdlr, 'info': info}

    def validate(self):
        for report_name in self._specs:
            if report_name not in self._entries:
                raise Exception(f"The spec report_name, '{report_name}' does not have a corresponding report entry.")


def gen_reports(test_exec: 'TestExec'):

    # write the CSV
    specs = []
    for name, results in test_exec.test_results.specs.items():
        for result in results:
            specs.append(result)

    if specs:
        io.write_csv(data=specs, path=test_exec.run_path / 'specs.csv')
    else:
        test_exec.logger.warning("No specs to report, the CSV will not be generated.")

    entries = []
    for name, result in test_exec.test_results.entries.items():
        entry = {'name': name}

        specs = test_exec.test_results.specs.get(name)
        if specs:
            entry['specs'] = specs

        fig_hdlr = result.get('fig')
        if fig_hdlr:
            entry['fig'] = fig_hdlr.to_base64()

        info = result.get('info')
        if info:
            entry['info'] = parse_info(info)

        entries.append(entry)

    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("/Users/vesselinvelev/github/test-automation/ta/html"))
    template = environment.get_template("template.html")

    html_str = template.render(entries=entries)
    html_path = test_exec.run_path / 'report.html'
    with open(html_path, "w") as f:
        f.write(html_str)


def parse_info(info: dict):
    return info

