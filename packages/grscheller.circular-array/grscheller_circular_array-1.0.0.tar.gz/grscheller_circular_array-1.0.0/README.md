# PyPI grscheller.circular-array Project

Python module implementing an indexable circular array data structure.

* See the [grscheller.circular-array][1] project on PyPI
* Detailed [API documentation][2] all versions

## Overview

The CircularArray class implements an auto-resizing, indexable, double
sided queue data structure. O(1) indexing and O(1) pushes and pops
either end. Useful as an improved version of a Python list. Used in
a has-a relationship by grscheller.datastructure when implementing other
data structures where its functionality is more likely restricted than
augmented.

## Usage

from grscheller.circular_array import CircularArray

---

[1]: https://pypi.org/project/grscheller.circular-array/
[2]: https://grscheller.github.io/circular-array/
