.. pysumreg documentation master file, created by
   sphinx-quickstart on Fri Nov 25 10:34:29 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PySumReg
=========

Statistics of sequence of :math:`(x, y)` pairs from calculator-style summation registers.

Why use this package?
========================

Use this package to obtain summary statistics of a list of :math:`(x, y)` pairs
when the pairs are presented in sequence, such as from a control system.  It is
not necessary to retain the entire list in memory, this package will retain the
cumulative values necessary to compute all analytical results.

There are no external dependencies on add-on packages such as numpy or
scipy.  Only the *math* (https://docs.python.org/3/library/math.html) package
from the Python Standard Library is used.

Statistics may be calculated at any time from the summation registers.

The :math:`(x, y)` values may be entered in any order.  It is not necessary to
sort them.

Examples
========

We start these examples by first creating a set of registers:

.. code-block:: python

   import pysumreg
   reg = pysumreg.SummationRegisters()

Mean and Standard Deviation
----------------------------

Find the mean and standard deviation of a set of ordered pairs:

.. code-block:: python

   reg.clear()
   reg.add(1, -1)
   reg.add(2, -2)
   reg.add(3, -3)
   print(f"{reg.mean_x=}")
   print(f"{reg.stddev_x=}")
   print(f"{reg.mean_y=}")
   print(f"{reg.stddev_y=}")
   print(f"{reg.min_x=}")
   print(f"{reg.max_x=}")
   print(f"{reg.min_y=}")
   print(f"{reg.max_y=}")
   print(f"{reg.x_at_max_y=}")
   print(f"{reg.x_at_min_y=}")

which prints these results::

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

Linear Analysis
---------------

Using the same data as above, assess if this is a good linear fit. The
correlation coefficient provides a measure of the correlation between the
:math:`x` and :math:`y` values.  Value of 1.0 indicates an exact fit to a
straight line with positive slope (-1 means anti-correlated: a negative straight
line).  Zero means that the :math:`x` and :math:`y` values are not correlated,
no linear fit.

.. code-block:: python

   reg.clear()
   reg.add(1, -1)
   reg.add(2, -2)
   reg.add(3, -3)
   print(f"{reg.correlation=}")
   print(f"{reg.intercept=}")
   print(f"{reg.slope=}")

which prints these results::

   reg.correlation=-1.0
   reg.intercept=0.0
   reg.slope=-1.0

Peak Analysis
---------------

Assuming that the data might represent a peak, compute parameters describing its
center and width.  We obtain the width (:math:`~2\sigma_c`) from the variance
(:math:`\sigma_c^2`) of the :math:`x` values weighted by the :math:`y` values.

.. code-block:: python

   reg.clear()
   reg.add(1, 0)
   reg.add(2, 1)
   reg.add(3, 0)
   print(f"{reg.max_y=}")
   print(f"{reg.centroid=}")
   print(f"{reg.sigma=}")

which prints these results::

   reg.max_y=1
   reg.centroid=2.0
   reg.sigma=0.0

With only three values, it's an exact fit to the underlying statistical model of
the variance. We need more data (with :math:`y` values that are not zero) to
obtain a non-zero :math:`\sigma_c`:

.. code-block:: python

   reg.add(1.5, 0.5)
   reg.add(2.5, 0.5)
   print(f"{reg.max_y=}")
   print(f"{reg.centroid=}")
   print(f"{reg.sigma=}")

which prints these results::

   reg.max_y=1
   reg.centroid=2.0
   reg.sigma=0.3535533905932738

Summary
--------

Print the entire contents of the summation registers object:

.. code-block:: python

   reg

which prints these results (re-formatted for display here)::

    SummationRegisters(
      X=10.0,
      XX=22.5,
      XXY=8.25,
      XY=4.0,
      Y=2.0,
      YY=1.5,
      centroid=2.0,
      correlation=0.0,
      intercept=0.4,
      max_x=3,
      max_y=1,
      mean_x=2.0,
      mean_y=0.4,
      min_x=1,
      min_y=0.5,
      n=5,
      sigma=0.3535533905932738,
      slope=0.0,
      stddev_x=0.7905694150420949,
      stddev_y=0.4183300132670378,
      x_at_max_y=2,
      x_at_min_y=3
    )

-----

Installation
========================

This package may be installed by any of these commands:

* ``pip install pysumreg``
* ``conda install -c conda-forge pysumreg``
* ``conda install -c conda-forge pysumreg``
* ``mamba install -c conda-forge pysumreg``
* ``micromamba install -c conda-forge pysumreg``

About
========================

:documentation: https://prjemian.github.io/pysumreg/latest
:source: https://github.com/prjemian/pysumreg
:version:   |version|
:release:   |release|
:published: |today|

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   sum_registers
   changes
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
