from datetime import datetime
from functools import reduce

import pytest

from timeframe import BatchTimeFrame, TimeFrame


def test_batch_timeframe_initialze_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))

    tf_list = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list)
    assert btf.duration == sum(tf.duration for tf in tf_list)
    assert btf.len_timeframes == len(tf_list)


def test_batch_timeframe_initialze_with_duplicate_timeframes_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))

    tf_list = [tf1, tf2, tf3, tf4, tf5]
    unique_tfs = tf_list[:3]

    btf = BatchTimeFrame(tf_list)
    assert btf.duration == sum(tf.duration for tf in unique_tfs)
    assert btf.len_timeframes == len(unique_tfs)


def test_batch_timeframe_initialze_wrong_type_raises_type_error():
    with pytest.raises(TypeError):
        BatchTimeFrame(1)

    with pytest.raises(TypeError):
        BatchTimeFrame(1.0)

    with pytest.raises(TypeError):
        BatchTimeFrame("dummy")

    with pytest.raises(TypeError):
        BatchTimeFrame([1, 1.0, "dummy"])

    with pytest.raises(TypeError):
        BatchTimeFrame([TimeFrame(datetime(2021, 1, 17), datetime(2021, 1, 18)), 1])


def test_batch_timeframe_initialze_empty_list_is_find_as_well():
    btf = BatchTimeFrame([])

    assert btf.duration == 0


def test_batch_timeframe_initialze_with_overlapped_elements_prunes_extras():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 13))
    tf5 = TimeFrame(datetime(2021, 1, 17, 14, 30), datetime(2021, 1, 17, 14, 40))
    TimeFrame(datetime(2021, 1, 17, 14, 50), datetime(2021, 1, 17, 17))
    tf7 = TimeFrame(datetime(2021, 1, 17, 14, 35), datetime(2021, 1, 17, 18, 30))

    tf_list = [tf1, tf2, tf3, tf4, tf5, tf5, tf7]

    # union = reduce(lambda x, y: x + y, tf_list[1:], tf_list[0])
    union = reduce(lambda x, y: x + y, tf_list)
    expected_len = 2  # calculated manually

    btf = BatchTimeFrame(tf_list)

    assert btf.duration == union.duration
    assert btf.len_timeframes == expected_len


def test_batch_timeframe_includes_another_batch_timeframe_with_overlap():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 19), datetime(2021, 1, 17, 19, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list2)

    assert btf1.includes(btf2)


def test_batch_timeframe_doesnt_include_another_batch_timeframe_with_minor_overlap():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 13), datetime(2021, 1, 17, 23))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list2)

    assert not btf1.includes(btf2)


def test_batch_timeframe_doesnt_include_another_batch_timeframe_without_overlap():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list2)

    assert not btf1.includes(btf2)


def test_batch_timeframe_includes_timeframe_accurately():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 9), datetime(2021, 1, 17, 12))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 55))
    tf6 = TimeFrame(datetime(2021, 1, 17, 18, 30), datetime(2021, 1, 17, 19, 30))

    tf_list1 = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list1)

    assert not btf.includes(tf4)
    assert btf.includes(tf5)
    assert btf.includes(tf6)


def test_batch_timeframe_includes_with_wrong_type_raises_error():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))

    tf_list1 = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list1)

    with pytest.raises(TypeError):
        btf.includes(1)

    with pytest.raises(TypeError):
        btf.includes(1.0)

    with pytest.raises(TypeError):
        btf.includes("dummy")

    with pytest.raises(TypeError):
        btf.includes([])

    with pytest.raises(TypeError):
        btf.includes([1, 1.0, "dummy"])
