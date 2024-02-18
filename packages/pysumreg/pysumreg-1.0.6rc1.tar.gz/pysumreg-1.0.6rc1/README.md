# Statistics with Calculator-style Summation Registers

Statistics of list of (x, y) pairs from calculator-style summation registers.

CONTENTS

- [Statistics with Calculator-style Summation Registers](#statistics-with-calculator-style-summation-registers)
  - [Why use this package?](#why-use-this-package)
  - [Examples](#examples)
    - [mean and standard deviation](#mean-and-standard-deviation)
    - [linear regression \& correlation coefficient](#linear-regression--correlation-coefficient)
    - [peak analysis: centroid and width of x weighted by y](#peak-analysis-centroid-and-width-of-x-weighted-by-y)
  - [Installation](#installation)
  - [About](#about)

## Why use this package?

Use this package to obtain summary statistics of a list of $(x, y)$ pairs when
the pairs are presented in sequence, such as from a control system.  It is not
necessary to retain the entire list in memory, this package will retain the
cumulative values necessary to compute all analytical results.

There are no external dependencies on add-on packages such as numpy or
scipy.  Only the [math](https://docs.python.org/3/library/math.html) package
from the Python Standard Library is used.

Statistics may be calculated at any time from the summation registers.

The $(x, y)$ values may be entered in any order.  It is not necessary to
sort them.

## Examples

```python
In [1]: import pysumreg

In [2]: reg = pysumreg.SummationRegisters()
```

### mean and standard deviation

```python
In [3]: reg.clear()
   ...: reg.add(1, -1)
   ...: reg.add(2, -2)
   ...: reg.add(3, -3)
   ...: print(f"{reg.mean_x=}")
   ...: print(f"{reg.stddev_x=}")
   ...: print(f"{reg.mean_y=}")
   ...: print(f"{reg.stddev_y=}")
   ...: print(f"{reg.min_x=}")
   ...: print(f"{reg.max_x=}")
   ...: print(f"{reg.min_y=}")
   ...: print(f"{reg.max_y=}")
   ...: print(f"{reg.x_at_max_y=}")
   ...: print(f"{reg.x_at_min_y=}")
   ...: 
reg.mean_x=2.0
reg.stddev_x=1.0
reg.mean_y=-2.0
reg.stddev_y=1.0
reg.min_x=1
reg.max_x=3
reg.min_y=-3
reg.max_y=-1
reg.x_at_max_y=1
reg.x_at_min_y=3
```

### linear regression & correlation coefficient

```python
In [4]: reg.clear()
   ...: reg.add(1, -1)
   ...: reg.add(2, -2)
   ...: reg.add(3, -3)
   ...: print(f"{reg.correlation=}")
   ...: print(f"{reg.intercept=}")
   ...: print(f"{reg.slope=}")
   ...: 
reg.correlation=-1.0
reg.intercept=0.0
reg.slope=-1.0
```

### peak analysis: centroid and width of x weighted by y

```python
In [5]: reg.clear()
   ...: reg.add(1, 0)
   ...: reg.add(2, 1)
   ...: reg.add(3, 0)
   ...: print(f"{reg.max_y=}")
   ...: print(f"{reg.centroid=}")
   ...: print(f"{reg.sigma=}")
   ...: 
reg.max_y=1
reg.centroid=2.0
reg.sigma=0.0

In [6]: reg.add(1.5, 0.5)
   ...: reg.add(2.5, 0.5)
   ...: print(f"{reg.max_y=}")
   ...: print(f"{reg.centroid=}")
   ...: print(f"{reg.sigma=}")
   ...: 
reg.max_y=1
reg.centroid=2.0
reg.sigma=0.3535533905932738
```

## Installation

This package may be installed by any of these commands:

- `pip install pysumreg`
- `conda install -c conda-forge pysumreg`
- `mamba install -c conda-forge pysumreg`
- `micromamba install -c conda-forge pysumreg`

## About

| Release | PyPI | Conda-forge | Platforms |
| --- | --- | --- | --- |
| [![Release](https://img.shields.io/github/release/prjemian/pysumreg.svg)](https://github.com/prjemian/pysumreg/releases) | [![PyPI](https://img.shields.io/pypi/v/pysumreg.svg)](https://pypi.python.org/pypi/pysumreg) | [![Conda Version](https://img.shields.io/conda/vn/conda-forge/pysumreg.svg)](https://anaconda.org/conda-forge/pysumreg) | [![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/pysumreg.svg)](https://anaconda.org/conda-forge/pysumreg) |

| Python | Unit Tests | Code Coverage |
| --- | --- | --- |
| [![Python](https://img.shields.io/pypi/pyversions/pysumreg.svg)](https://pypi.python.org/pypi/pysumreg) | ![Unit Tests](https://github.com/prjemian/pysumreg/workflows/Unit%20Tests/badge.svg) | [![Coverage Status](https://coveralls.io/repos/github/prjemian/pysumreg/badge.svg?branch=main)](https://coveralls.io/github/prjemian/pysumreg?branch=main) |

- documentation:
    https://prjemian.github.io/pysumreg/latest
- source:
    https://github.com/prjemian/pysumreg
