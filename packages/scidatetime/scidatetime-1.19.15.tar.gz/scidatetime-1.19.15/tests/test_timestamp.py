from scidatetime import *


def test_fixed_second():
    v = 1695106243
    x = DateTime(v)
    assert x.getTime() == int(v * 1e3)


def test_second():
    utc0_time = DateTime(1695106243)
    target = DateTime('2023-09-19 06:50:43') - time_timezone * 1e3
    assert utc0_time == target


def test_small_timestamp():
    assert DateTime(0).year == 2000
    assert DateTime(None).year == 2000
    assert DateTime(100).year == 2000
    assert DateTime(380 * 86400).year == 2001
    assert DateTime(-380 * 86400).year == 1998
