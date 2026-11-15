# ECC-Memory - XOR-parity error-correcting memory slots against bit-rot
# Part of the Kapildhinwa2010-dev Toolkit.

"""Spiral-addressed byte arena with two-dimensional XOR parity ECC.

Lineage: reserv.dean-part-2 (helix.py). Content is addressed by a spiral
coordinate walk over a square arena. Every byte cell is protected by BOTH
a row XOR parity and a column XOR parity, so a single corrupted cell is
detectable AND correctable (the row parity recovers the original byte,
the column parity locates it).

HONEST LIMITATIONS: only SINGLE-cell corruption per repair is correctable;
two corrupted cells in the same row (or column) are detectable but not
correctable, and the parity bytes themselves are not protected.
"""

from __future__ import annotations

import numpy as np

__all__ = ["spiral_coordinates", "HelixMemory"]


def spiral_coordinates(size: int):
    """Clockwise spiral walk of an ``size x size`` grid from the center."""
    if size < 1:
        raise ValueError("size must be >= 1")
    coords = []
    x = y = size // 2
    coords.append((x, y))
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # right, down, left, up
    step = 1
    while len(coords) < size * size:
        for d_index, (dx, dy) in enumerate(directions):
            length = step
            for _ in range(length):
                if len(coords) >= size * size:
                    return coords
                x += dx
                y += dy
                if 0 <= x < size and 0 <= y < size:
                    coords.append((x, y))
            if d_index % 2 == 1:
                step += 1
    return coords


def _xor_parity(block: np.ndarray) -> int:
    parity = 0
    for value in block:
        parity ^= int(value)
    return parity


class HelixMemory:
    """Byte arena with spiral addressing and row+column XOR parity ECC."""

    def __init__(self, size: int = 8, record_size: int = 4) -> None:
        if size < 1 or record_size < 1:
            raise ValueError("size and record_size must be >= 1")
        self.size = int(size)
        self.record_size = int(record_size)
        self.coords = spiral_coordinates(size)
        self.arena = np.zeros((size, size), dtype=np.uint8)
        self.parity = np.zeros(size, dtype=np.uint8)
        self.col_parity = np.zeros(size, dtype=np.uint8)
        self._used: set = set()

    def address(self, key: str) -> int:
        """Deterministic spiral index for a string key."""
        digest = sum(ord(c) for c in key)
        return digest % len(self.coords)

    def write(self, key: str, record: bytes) -> None:
        record = bytes(record)
        if len(record) != self.record_size:
            raise ValueError("record must be exactly {} bytes".format(self.record_size))
        index = self.address(key)
        x, y = self.coords[index]
        self.arena[x, y] = record[0] ^ record[1] if self.record_size >= 2 else record[0]
        self.parity[x] = _xor_parity(self.arena[x])
        self.col_parity[y] = _xor_parity(self.arena[:, y])
        self._used.add(key)

    def read_cell(self, key: str) -> int:
        index = self.address(key)
        x, y = self.coords[index]
        return int(self.arena[x, y])

    def verify(self) -> bool:
        """True when every row AND column matches its XOR parity."""
        for row in range(self.size):
            if _xor_parity(self.arena[row]) != int(self.parity[row]):
                return False
        for col in range(self.size):
            if _xor_parity(self.arena[:, col]) != int(self.col_parity[col]):
                return False
        return True

    def verify_detailed(self) -> dict:
        """Return {"bad_rows": [...], "bad_cols": [...]} for diagnosis."""
        bad_rows = [r for r in range(self.size)
                    if _xor_parity(self.arena[r]) != int(self.parity[r])]
        bad_cols = [c for c in range(self.size)
                    if _xor_parity(self.arena[:, c]) != int(self.col_parity[c])]
        return {"bad_rows": bad_rows, "bad_cols": bad_cols}

    def repair(self) -> list:
        """Correct a single corrupted cell using row+column parity.

        The bad column locates the cell; the row parity recovers the
        original byte. Returns the list of repaired (x, y) cells. Two or
        more corrupted cells in one row or column are NOT correctable.
        """
        detail = self.verify_detailed()
        repaired = []
        if len(detail["bad_rows"]) == 1 and len(detail["bad_cols"]) == 1:
            x, y = detail["bad_rows"][0], detail["bad_cols"][0]
            row_xor_others = 0
            for c in range(self.size):
                if c != y:
                    row_xor_others ^= int(self.arena[x, c])
            original = row_xor_others ^ int(self.parity[x])
            self.arena[x, y] = original
            self.col_parity[y] = _xor_parity(self.arena[:, y])
            repaired.append((x, y))
        return repaired

    def corrupt(self, key: str) -> None:
        """Flip one byte (for testing corruption detection)."""
        index = self.address(key)
        x, y = self.coords[index]
        self.arena[x, y] ^= 0xFF

    def usage(self) -> float:
        return len(self._used) / (self.size * self.size)

    def __len__(self) -> int:
        return len(self._used)