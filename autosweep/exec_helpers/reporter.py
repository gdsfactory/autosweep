from typing import TYPE_CHECKING
import jinja2

from autosweep.utils import io
from autosweep import sweep
if TYPE_CHECKING:
    from autosweep.test_exec import TestExec


class ResultsHold:
    """
    A class to hold results, including specs and entries that will go into the HTML report. Individual tests run by the
    TestExec add entries to this instance. Finally, the results are validated and passed onto the method which generates
    the appropriate files by the TestExec.
    """

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
        """
        Add a spec entry

        :param report_heading: The heading in the report to associate with this spec
        :type report_heading: str
        :param spec: The spec name
        :type spec: str
        :param unit: The unit of the spec. If there is no unit, pass an empty string.
        :type unit: str
        :param value: The value of the spec.
        :type value: int, float, or bool
        :return: None
        """
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

    def clear_specs(self, report_heading: str) -> None:
        """
        Clears all specs associated with a given report heading

        :param report_heading: The heading in the report for which to clear specs
        :type report_heading: str
        :return: None
        """
        if not isinstance(report_heading, str):
            raise TypeError("'report_heading' argument must be of type 'str'")

        if report_heading not in self._specs:
            raise ValueError(f"the 'report_heading', '{report_heading}' is not a valid value")

        self._specs[report_heading] = []

    def add_report_entry(self, report_heading: str, fig_hdlr: sweep.FigHandler | None = None,
                         info: dict | None = None) -> None:
        """
        Adds a report entry to the results. This consists of a figure or a collection of text.

        :param report_heading: The heading in the report for which to associate the figure or info
        :type report_heading: str
        :param fig_hdlr: The figure to plot in the report, only one figure per report heading is supported
        :type fig_hdlr: autosweep.sweep.vis_utils.FigHandler, optional
        :param info: A collection of supplimentary information that will be printed under the heading
        :type info: dict, optional
        :return: None
        """
        if not isinstance(report_heading, str):
            raise TypeError("'report_name' argument must be of type 'str'")
        if fig_hdlr is not None and not isinstance(fig_hdlr, sweep.FigHandler):
            raise TypeError("The optional argument 'fig_hdlr' must be of type 'autosweep.sweep.FigHandler'")
        if info is not None and not isinstance(info, dict):
            raise TypeError("The optional argument 'info' must be of type 'dict'")

        if report_heading in self._entries:
            raise ValueError(f"The report_heading '{report_heading}', is already defined.")

        self._entries[report_heading] = {'fig': fig_hdlr, 'info': info}

    def validate(self) -> None:
        """
        The TestExec runs this method after all testing is complete to validate the contents of the report

        :return: None
        """
        for report_name in self._specs:
            if report_name not in self._entries:
                raise Exception(f"The spec report_name, '{report_name}' does not have a corresponding report entry.")


def gen_reports(test_exec: 'TestExec') -> None:
    """
    This function takes information from the test_exec to produce the report and csv data.

    :param test_exec: The test exec
    :type test_exec: autosweep.test_exec.TestExec
    :return: None
    """

    # write the CSV
    specs = []
    for name, results in test_exec.test_results.specs.items():
        specs.extend(iter(results))
    if specs:
        io.write_csv(data=specs, path=test_exec.run_path / 'specs.csv')
    else:
        test_exec.logger.warning("No specs to report, the CSV will not be generated.")

    entries = []
    for name, result in test_exec.test_results.entries.items():
        entry = {'name': name}

        if specs := test_exec.test_results.specs.get(name):
            entry['specs'] = specs

        if fig_hdlr := result.get('fig'):
            entry['fig'] = fig_hdlr.to_base64()

        if info := result.get('info'):
            entry['info'] = parse_info(info)

        entries.append(entry)

    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(str(test_exec.html_path)))

    template = environment.get_template("template.html")

    html_str = template.render(entries=entries)
    html_path = test_exec.run_path / 'report.html'
    with open(html_path, "w") as f:
        f.write(html_str)


def parse_info(info: dict) -> dict:
    """
    A function to parse the info into a format that can be embedded into the template.

    :param info: The info to parse
    :type info: dict
    :return: The parsed info
    :rtype: dict
    """
    return info

