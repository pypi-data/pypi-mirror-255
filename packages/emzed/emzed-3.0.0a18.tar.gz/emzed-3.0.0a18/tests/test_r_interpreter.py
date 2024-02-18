#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

from emzed import to_table
from emzed.r_connect import RError, RInterpreter


def test_0():
    rip = RInterpreter()
    assert rip is not None


def test_native_types():
    ip = RInterpreter()

    assert ip.execute("x <-3").x == 3
    assert ip.execute("x <-1.0").x == 1.0
    assert ip.execute("x <-'abc'").x == "abc"

    ip.y = 42
    assert ip.execute("x <- y").x == 42

    ip.y = 1.0
    assert ip.execute("x <- y").x == 1.0

    ip.y = "abc"
    assert ip.execute("x <- y").x == "abc"


def test_tables(regtest):
    ip = RInterpreter()
    t = to_table("a", [1, 2], int)

    # transfer Table tor R:
    ip.t = t

    # fetch Table from R
    assert ip.execute("s <- t").s.rows == t.rows

    # fetch pandas.DataFrame from R
    df = ip.get_raw("s")
    assert df.to_numpy().tolist() == [1, 2]

    df = ip.get_raw("mtcars")
    print(df, file=regtest)

    ip.ddf = df

    print(ip.ddf, file=regtest)
    print(ip.mtcars, file=regtest)


def test_dump_stdout(regtest, capsys):
    ip = RInterpreter()

    ip.execute("print(mtcars)")
    print(capsys.readouterr().out, file=regtest)


def test_table_full(regtest):
    t = to_table("names", ("uwe", "schmit"), str)
    t.add_column("idx", (1, 2), int)
    t.add_column("mass", (1.0, 1.11), float)
    t.add_column("class", (True, False), bool)

    ip = RInterpreter()
    ip.t = t

    print(t, file=regtest)
    print(ip.t, file=regtest)
    print(ip.get_df_as_table("t"), file=regtest)
    print(ip.get_df_as_table("t", col_types=(str, int, float, str)), file=regtest)


def test_r_error_pickling():
    import dill

    # loads failed because the old constructor or RError had no "default constructor"
    err = dill.loads(dill.dumps(RError("test")))
    assert err.value == "test"


def test_interpolation():
    ip = RInterpreter()
    ip.execute("x<-%(name)r", name="Uwe")
    assert ip.x == "Uwe"
