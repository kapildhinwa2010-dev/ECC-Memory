# ECC-Memory

ECC-Memory is a small Python library that stores fixed-size byte records in an in-memory square array, assigns record starts using a center-out spiral index, and maintains row and column XOR parity. Its `HelixMemory` class can check parity and repair one corrupted data cell when the parity information identifies exactly one bad row and one bad column.

This is an experimental, process-local data structure—not persistent or production-grade storage. The arena and parity are held in NumPy arrays in memory; the project does not implement disk I/O, serialization, or a command-line interface.

## Features

- Generate a center-out spiral traversal of a square grid with `spiral_coordinates(size)`.
- Write and read fixed-length byte records with `HelixMemory.write()` and `read_record()`.
- Inspect the first byte of a record with `read_cell()`.
- Check all row and column parity with `verify()` or inspect mismatching indices with `verify_detailed()`.
- Attempt repair of one damaged cell with `repair()`; the method returns the repaired `(row, column)` coordinate or an empty list when its single-cell repair condition is not met.
- Simulate corruption of a record's first byte with `corrupt()` and report the number of distinct written keys and an approximate grid usage fraction with `len(memory)` and `memory.usage()`.

## Requirements and installation

The project requires Python 3.9 or later and NumPy 1.24 or later. Install the project from its repository directory with:

```bash
python -m pip install .
```

For development and tests, install the declared requirements (which include pytest):

```bash
python -m pip install -r requirements.txt
```

There is no CLI. Use the Python module and its `HelixMemory` class directly.

## Example

```python
from ecc_memory import HelixMemory

memory = HelixMemory(size=8, record_size=4)
memory.write("alpha", b"\x01\x02\x03\x04")

assert memory.read_record("alpha") == b"\x01\x02\x03\x04"
assert memory.verify()

# Demonstrate detection and repair of one changed data cell.
memory.corrupt("alpha")
assert not memory.verify()
repaired_cells = memory.repair()
assert len(repaired_cells) == 1
assert memory.verify()
assert memory.read_record("alpha") == b"\x01\x02\x03\x04"
```

`record_size` defaults to 4 and must be positive. Each `write()` requires a byte sequence exactly that length. Record bytes occupy consecutive spiral cells, wrapping at the end of the traversal.

## Tests

Run the tests from the repository root:

```bash
python -m pytest -q
```

On the reviewed commit `69dcfa2191375b3acb9a44c6bbd9464cc21accd9`, this command completed with **6 passed**. The GitHub Actions CI definition also specifies pytest, compilation, and a module-import smoke test on Python 3.10, 3.11, and 3.12; this local result is not a statement about the status of a GitHub Actions run.

## Limitations

- Repair handles only the case of exactly one bad data row and one bad data column. Multiple corrupted cells are not generally correctable; `repair()` can return an empty list while data remains damaged.
- The parity arrays themselves have no independent protection.
- Keys map to a start index using the sum of their character code points modulo the number of spiral cells. Different keys can map to the same or overlapping record ranges, and writes can overwrite cells used by other records.
- The arena is volatile process memory. There is no persistence, recovery after process exit, concurrency control, or storage-capacity management beyond the fixed grid.
- This XOR scheme is not a general-purpose error-correction code and provides no guarantee for arbitrary multi-cell faults or parity corruption.

## License

The repository includes an MIT License. See [LICENSE](LICENSE) for its terms and copyright notice.
