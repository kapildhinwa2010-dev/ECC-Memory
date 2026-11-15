import pytest

from ecc_memory import HelixMemory, spiral_coordinates


def test_spiral_starts_at_center():
    size = 5
    coords = spiral_coordinates(size)
    assert coords[0] == (2, 2)


def test_spiral_covers_all_cells():
    size = 4
    coords = spiral_coordinates(size)
    assert len(coords) == size * size
    assert len(set(coords)) == size * size


def test_spiral_all_in_bounds():
    size = 6
    for x, y in spiral_coordinates(size):
        assert 0 <= x < size and 0 <= y < size


def test_spiral_rejects_zero():
    with pytest.raises(ValueError):
        spiral_coordinates(0)


def test_write_read_roundtrip():
    mem = HelixMemory(size=8, record_size=4)
    mem.write("alpha", b"\x01\x02\x03\x04")
    assert isinstance(mem.read_cell("alpha"), int)


def test_write_rejects_wrong_record_size():
    mem = HelixMemory(size=8, record_size=4)
    with pytest.raises(ValueError):
        mem.write("alpha", b"\x01\x02")


def test_address_deterministic():
    mem = HelixMemory(size=8)
    assert mem.address("key") == mem.address("key")


def test_verify_true_after_write():
    mem = HelixMemory(size=8, record_size=2)
    mem.write("a", b"\x10\x20")
    mem.write("b", b"\x30\x40")
    assert mem.verify() is True


def test_corrupt_breaks_parity():
    mem = HelixMemory(size=8, record_size=2)
    mem.write("a", b"\x10\x20")
    mem.corrupt("a")
    assert mem.verify() is False


def test_usage_and_len():
    mem = HelixMemory(size=8, record_size=2)
    mem.write("a", b"\x01\x02")
    mem.write("b", b"\x03\x04")
    assert len(mem) == 2
    assert mem.usage() == pytest.approx(2 / 64)


def test_constructor_rejects_zero():
    with pytest.raises(ValueError):
        HelixMemory(size=0)


def test_spiral_size_one():
    assert spiral_coordinates(1) == [(0, 0)]


def test_repair_fixes_single_corruption():
    mem = HelixMemory(size=8, record_size=2)
    mem.write("a", b"\x12\x34")
    x, y = mem.coords[mem.address("a")]
    original = int(mem.arena[x, y])
    mem.corrupt("a")
    assert mem.verify() is False
    repaired = mem.repair()
    assert (x, y) in repaired
    assert int(mem.arena[x, y]) == original
    assert mem.verify() is True


def test_verify_detailed_locates_corruption():
    mem = HelixMemory(size=8, record_size=2)
    mem.write("a", b"\x10\x20")
    x, y = mem.coords[mem.address("a")]
    mem.corrupt("a")
    detail = mem.verify_detailed()
    assert detail["bad_rows"] == [x]
    assert detail["bad_cols"] == [y]


def test_repair_noop_on_clean_memory():
    mem = HelixMemory(size=8, record_size=2)
    mem.write("a", b"\x01\x02")
    assert mem.repair() == []


def test_column_parity_maintained_on_write():
    mem = HelixMemory(size=8, record_size=2)
    mem.write("a", b"\x10\x20")
    mem.write("b", b"\x30\x40")
    for col in range(mem.size):
        p = 0
        for row in range(mem.size):
            p ^= int(mem.arena[row, col])
        assert p == int(mem.col_parity[col])