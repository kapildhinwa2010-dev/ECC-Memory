# ECC-Memory

[![CI](https://github.com/kapildhinwa2010-dev/ECC-Memory/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/ECC-Memory/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kapildhinwa2010-dev/ECC-Memory/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/ECC-Memory/actions/workflows/codeql.yml)

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Error-correcting spiral memory: row AND column XOR parity locate and repair single-cell corruption.

**Part of the [Kapildhinwa2010-dev Toolkit](https://github.com/kapildhinwa2010-dev/Kapildhinwa2010-dev).**

## What it does

HelixMemory writes records across consecutive spiral cells. Every cell
is protected by a row XOR parity and a column XOR parity: verify_detailed()
names the bad rows and columns, and repair() corrects a single corrupted
cell (bad column locates it, row parity recovers the byte). This is the
strongest parity scheme in the toolkit family - the safe design that the
source experiments kept.

## Install

    pip install -r requirements.txt

## Quick start

    from ecc_memory import HelixMemory

    mem = HelixMemory(size=8, record_size=4)
    mem.write("alpha", b"\x01\x02\x03\x04")
    mem.corrupt("alpha")
    assert not mem.verify()
    mem.repair()
    assert mem.read_record("alpha") == b"\x01\x02\x03\x04"

## API

- write / read_record / read_cell / verify / verify_detailed / repair /
  corrupt / usage
- spiral_coordinates(size)

## Honest results and limitations

- Only SINGLE-cell corruption is correctable. Two flipped cells in the
  same row or column are detectable but repair() returns [] and the
  data stays broken.
- The parity bytes themselves are unprotected; a flip in a parity byte
  looks like a data corruption and triggers a wrong "repair".
- Keys hash by character sum: different keys can map to overlapping
  cell ranges and silently overwrite each other.
- This is XOR parity, not Reed-Solomon: it corrects one bad cell, not
  burst errors. Research toy, not trustworthy storage.

## License

MIT - see [LICENSE](LICENSE).
