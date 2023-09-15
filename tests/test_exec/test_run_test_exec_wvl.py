import logging
import pathlib

# this is a new test, defined in new_test.py
import new_test

import autosweep as ap

# used to find the latest run in a collection of data runs


def test_exec_wv() -> None:
    # sets up the python logging module to interact with autosweep
    ap.init_logger()

    # register the all tests inside 'new_test' so they are available for the TestExec. This can be used with instruments as
    # well to make them available to the instrument manager.

    ap.register_classes(new_test)
    logging.info("Demonstration of basic TestExec functionality:")
    dirpath = pathlib.Path(__file__).parent.absolute()

    # DUTInfo contains metadata related to the device under test
    dut = ap.DUTInfo(part_num=ap.PN("WVL-0345", 1), ser_num=ap.SN("123456"))
    # The recipe file contains the test sequence to run on the DUT
    recipe = ap.Recipe.read_json(path=dirpath / "recipe_wvl.json")
    # The station config contains details related to the setup itself, including the instrumentation and how to access it
    station_cfg = ap.StationConfig.read_json(path=dirpath / "station_config.json")

    # Takes the data
    take_data = False

    if take_data:
        with ap.TestExec(
            dut_info=dut, recipe=recipe, station_config=station_cfg, reanalyze=False
        ) as t:
            t.run_recipe()

        logging.info("Done!")


if __name__ == "__main__":
    test_exec_wv()
