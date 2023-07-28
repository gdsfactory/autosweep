from typing import TYPE_CHECKING

from ta.utils import io
if TYPE_CHECKING:
    from ta.test_exec import TestExec


def gen_reports(test_exec: 'TestExec'):
    specs = []
    for name, results in test_exec.test_results.items():
        for result in results:
            for spec in result['specs']:
                specs.append(spec)


    print(specs)
    io.write_csv(data=specs, path=test_exec.run_path / 'specs.csv')

