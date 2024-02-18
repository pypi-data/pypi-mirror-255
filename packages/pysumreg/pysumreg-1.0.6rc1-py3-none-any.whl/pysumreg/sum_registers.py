"""
Statistics of list of (x, y) pairs from calculator-style summation registers.

* mean, standard deviation, max, min of x & y
* linear regression & correlation coefficient
* peak analysis: centroid and width of x weighted by y

.. autosummary::
   ~SummationRegisters

References:

* "Engineering Statistics with a Programmable Calculator", William Volk,
  1982, McGraw-Hill Companies, New York, ISBN 10: 007067552,
  ISBN 13: 9780070675520.
* https://goodcalculators.com/linear-regression-calculator/
* https://www.statssolver.com/simple-regression.html
"""

import math


class SummationRegisters:
    """
    Summation registers in the style of a pocket calculator.

    Operations

    .. autosummary::
       ~clear
       ~add
       ~subtract
       ~to_dict

    Statistical Parameters

    .. autosummary::
       ~mean_x
       ~mean_y
       ~stddev_x
       ~stddev_y

    Linear Parameters

    .. autosummary::
       ~slope
       ~intercept
       ~correlation
       ~linear_y

    Peak Parameters

    .. autosummary::
       ~centroid
       ~sigma
    """

    _property_methods = """
        mean_x
        mean_y
        stddev_x
        stddev_y
        slope
        intercept
        correlation
        centroid
        sigma
    """.split()
    _registers = "n X Y XX XY XXY YY".split()
    _extrema_names = "min_x max_x min_y max_y x_at_max_y x_at_min_y".split()

    def __init__(self) -> None:
        self.clear()

    def clear(self):
        """Clear the :math:`\sum{}` summation registers."""
        self.n = 0
        self.X = 0
        self.Y = 0
        self.XX = 0
        self.XY = 0
        self.XXY = 0
        self.YY = 0
        self.max_x = None
        self.max_y = None
        self.min_x = None
        self.min_y = None
        self.x_at_max_y = None
        self.x_at_min_y = None

    def _assess_extrema(self, x, y):
        """Assess min & max of x & y."""
        self.min_x = min(x, self.min_x or x)
        self.max_x = max(x, self.max_x or x)
        self.min_y = min(y, self.min_y or y)
        self.max_y = max(y, self.max_y or y)
        if y == self.min_y:
            self.x_at_min_y = x
        if y == self.max_y:
            self.x_at_max_y = x

    def add(self, x, y):
        """:math:`\sum{+}`: Add :math:`(x, y)` ordered pair to the registers."""
        self.n += 1
        self.X += x
        self.Y += y
        self.XX += x * x
        self.XY += x * y
        self.XXY += x * x * y
        self.YY += y * y

        self._assess_extrema(x, y)

    def subtract(self, x, y):
        """:math:`\sum{-}`: Subtract :math:`(x, y)` ordered pair from the registers."""
        self.n -= 1
        self.X -= x
        self.Y -= y
        self.XX -= x * x
        self.XY -= x * y
        self.XXY -= x * x * y
        self.YY -= y * y

        self._assess_extrema(x, y)

    def to_dict(self, use_registers=False):
        """
        Return all statistics as dictionary.

        Returns ``None`` for any unavailable or undefined values.

        PARAMETERS

        ``use_registers`` bool:
            Include values of the summation registers.
            (default: ``False``)
        """

        def param(k):
            try:
                v = getattr(self, k)
            except Exception:
                v = None
            return v

        d = {k: param(k) for k in self._property_methods}
        d.update({k: param(k) for k in self._extrema_names})
        if use_registers:
            d.update({k: param(k) for k in self._registers})

        return d

    def __repr__(self):
        dd = self.to_dict(use_registers=True)
        vv = ", ".join([f"{k}={v}" for k, v in sorted(dd.items())])
        return f"{self.__class__.__name__}({vv})"

    @property
    def mean_x(self):
        r"""
        Average of :math:`x` values.

        .. math:: \bar{x} = {\sum{x} \over n}
        """
        return self.X / self.n

    @property
    def mean_y(self):
        r"""
        Average of :math:`y` values.

        .. math:: \bar{y} = {\sum{y} \over n}
        """
        return self.Y / self.n

    @property
    def stddev_x(self):
        r"""
        Standard deviation of :math:`x` values.

        .. math:: \sigma_x^2 = {{\sum{x^2} - \bar{x}\sum{x}} \over {n-1}}
        """
        numerator = max(0, self.XX - self.mean_x * self.X)
        denominator = self.n - 1
        return math.sqrt(numerator / denominator)

    @property
    def stddev_y(self):
        r"""
        Standard deviation of :math:`y` values.

        .. math:: \sigma_y^2 = {{\sum{y^2} - \bar{y}\sum{y}} \over {n-1}}
        """
        numerator = max(0, self.YY - self.mean_y * self.Y)
        denominator = self.n - 1
        return math.sqrt(numerator / denominator)

    @property
    def slope(self):
        r"""
        First order term (:math:`b_1`) in linear fit of :math:`(x,y)`.

        .. math:: y = b_0 + b_1 x

        .. math:: b_1 = {{n\sum{xy} - \sum{x}\sum{y}} \over {n\sum{x^2} - \sum{x}\sum{x}}}

        See: :meth:`intercept`, :meth:`linear_y`
        """
        return (
            # fmt: off
            (self.n*self.XY - self.X*self.Y)
            /
            (self.n*self.XX - self.X*self.X)
            # fmt: on
        )

    @property
    def intercept(self):
        r"""
        Zero order term (:math:`b_0`) in linear fit of :math:`(x,y)`.

        .. math:: y = b_0 + b_1 x

        .. math:: b_0 = {{\sum{y} - b_1\sum{x}} \over n}

        See: :meth:`slope`, :meth:`linear_y`
        """
        return (
            # fmt: off
            (self.Y - self.slope*self.X)
            /
            self.n
            # fmt: on
        )

    def linear_y(self, x):
        r"""
        Compute :math:`\hat{y}` given :math:`x` using slope and intercept.

        .. math:: \hat{y} = b_0 + b_1 x

        See: :meth:`intercept`, :meth:`slope`
        """
        return self.intercept + self.slope * x

    @property
    def correlation(self):
        r"""
        Regression correlation coefficient (:math:`r`) of :math:`(x, y)`.

        .. math:: r = {{n\sum{xy} - \sum{x}\sum{y}} \over \sqrt{(n\sum{x^2}-\sum{x}\sum{x}) (n\sum{y^2}-\sum{y}\sum{y})}}
        """
        return (
            # fmt: off
            (self.n*self.XY - self.X*self.Y)
            /
            math.sqrt(
                (self.n*self.XX - self.X*self.X)
                *
                (self.n*self.YY - self.Y*self.Y)
            )
            # fmt: on
        )

    @property
    def centroid(self):
        r"""
        Centroid (:math:`x_c`) of :math:`(x, y)`.

        .. math:: x_c = { \sum{x y} \over \sum{y} }

        Regardless of the input :math:`(x, y)` signal modality (single peak,
        multiple peaks, no peaks at all), it is possible to estimate the center
        (centroid, :math:`x_c`) and width (:math:`2\sigma`) of the :math:`x`
        values assuming the :math:`y` values are their associated weights.
        The center should fall between the minimum and maximum given :math:`x`
        values.

        See: :meth:`sigma`
        """
        return self.XY / self.Y

    @property
    def sigma(self):
        r"""
        The y-weighted variance (:math:`\sigma_c^2`) of :math:`(x, y)`.

        .. math:: \sigma_c^2 = {\sum{y{(x-x_c)}^2} \over \sum{y}}

        Regardless of the input :math:`(x, y)` signal modality (single peak,
        multiple peaks, no peaks at all), it is possible to estimate the center
        (centroid, :math:`x_c`) and width (:math:`2\sigma_c`) of the :math:`x`
        values assuming the :math:`y` values are their associated weights.
        The sigma should be less than the span of the :math:`x` values.

        See: :meth:`centroid`
        """
        return math.sqrt((self.XXY - self.centroid * self.XY) / self.Y)
