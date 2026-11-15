"""Tests for ECC-Memory: 2-D parity detection, location and repair."""

import pytest

from ecc_memory import HelixMemory, spiral_coordinates


def test_record_roundtrip():
    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    assert memory.read_record("alpha") == b"\x01\x02\x03\x04"


def test_single_cell_corruption_detected_and_repaired():
    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    memory.corrupt("alpha")
    assert memory.verify() is False
    repaired = memory.repair()
    assert len(repaired) == 1
    assert memory.verify() is True
    assert memory.read_record("alpha") == b"\x01\x02\x03\x04"


def test_verify_detailed_reports_rows_and_cols():
    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    memory.corrupt("alpha")
    detail = memory.verify_detailed()
    assert len(detail["bad_rows"]) == 1 and len(detail["bad_cols"]) == 1


def test_double_corruption_detectable_not_repairable():
    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    # flip two different cells by hand
    x0, y0 = memory.coords[memory.address("alpha")]
    x1, y1 = memory.coords[(memory.address("alpha") + 2) % len(memory.coords)]
    memory.arena[x0, y0] ^= 0xFF
    memory.arena[x1, y1] ^= 0xFF
    assert memory.verify() is False
    assert memory.repair() == []


def test_write_validates():
    memory = HelixMemory(size=8, record_size=4)
    with pytest.raises(ValueError):
        memory.write("a", b"wrong-length")


def test_spiral_covers_grid_once():
    coords = spiral_coordinates(6)
    assert len(coords) == 36 and len(set(coords)) == 36
