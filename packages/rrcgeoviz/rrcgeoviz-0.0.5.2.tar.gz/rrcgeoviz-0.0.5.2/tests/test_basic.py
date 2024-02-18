from argparse import ArgumentError, ArgumentTypeError
import pandas as pd
import pytest
from rrcgeoviz.geoviz_cli import main
from pandas.errors import EmptyDataError


def test_sysargs_fail_with_bad_paths():
    with pytest.raises(SystemExit):
        main(["thisisnt", "apath", "--test"])
    with pytest.raises(TypeError):
        main(
            [
                "./tests/optionstest.json",
                "--options",
                "./tests/optionstest.json",
                "--test",
            ]
        )
    with pytest.raises(TypeError):
        main(
            [
                "./tests/testingdata.csv",
                "--options",
                "./tests/testingdata.csv",
                "--test",
            ]
        )

    main(["./tests/testingdata.csv", "--options", "./tests/optionstest.json", "--test"])


def test_fails_with_empty_csv():
    with pytest.raises(EmptyDataError):
        main(["./tests/emptydataset.csv", "--options", "./tests/optionstest.json"])
