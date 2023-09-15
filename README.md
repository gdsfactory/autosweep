# AutoSweep Test Framework 0.0.2

The AutoSweep project is designed to run automated device testing.
It's designed to be highly modular, giving a framework with which to organize test sequences and manage instruments, while keeping track of device metadata, saving raw data, generating reports and handling errors.

## Installation

After cloning the repository, you can install it using `pip install .`.
If you want to develop features within Test Automation, you'll find the pip `-e` option useful, `pip install -e .`, this allows you to make
edits to the code and execute tests from the python environment the package was installed in without reinstalling it via pip.

After installation, execute the python script in `tests/test_exec/run_test_exec.py`. You\'ll see a a folder of virtual
test data generated in the folder `tests/test_exec/data`. Open the script and browse the test data to become more familiar with the operation of the code.
