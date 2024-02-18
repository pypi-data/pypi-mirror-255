from ..sum_registers import SummationRegisters
import pytest


def test_create():
    reg = SummationRegisters()

    for k in reg._registers:
        assert hasattr(reg, k)
        assert getattr(reg, k) == 0, k

    for k in reg._property_methods:
        assert k in dir(reg), k  # avoids implicit evaluation during getattr()

    expected = {k: 0 for k in reg._registers}
    expected.update({k: None for k in reg._property_methods})
    expected.update({k: None for k in reg._extrema_names})
    actual = reg.to_dict(use_registers=True)
    assert actual == expected


def test_sample1():
    # example from https://goodcalculators.com/linear-regression-calculator/
    y_arr = [4.182, 3.887, 2.283, 7.327, 8.411, 7.808, 8.422, 6.330, 10.138, 5.871]
    x_arr = list(range(1, 1 + len(y_arr)))
    assert len(x_arr) == 10

    reg = SummationRegisters()
    for x, y in zip(x_arr, y_arr):
        reg.add(x, y)
    assert reg.min_x == min(x_arr)
    assert reg.max_x == max(x_arr)
    assert reg.min_y == min(y_arr)
    assert reg.max_y == max(y_arr)
    assert reg.x_at_max_y == x_arr[y_arr.index(reg.max_y)]
    assert reg.x_at_min_y == x_arr[y_arr.index(reg.min_y)]

    assert reg.n == 10
    assert round(reg.X, 3) == 55
    assert round(reg.Y, 3) == 64.659
    assert round(reg.XX, 3) == 385.000
    assert round(reg.XY, 3) == 396.562
    assert round(reg.YY, 3) == 471.451

    assert round(reg.mean_x, 3) == 5.5
    assert round(reg.mean_y, 3) == 6.466
    assert round(reg.stddev_x, 3) == 3.028
    assert round(reg.stddev_y, 3) == 2.435

    assert round(reg.slope, 3) == 0.496
    assert round(reg.intercept, 3) == 3.737
    assert round(reg.correlation, 3) == 0.617


@pytest.mark.parametrize(
    "data, expected, ndigits",
    [
        # fmt: off
        [  # sample 1 - a noisy line with positive slope
            # data from https://www.statssolver.com/simple-regression.html
            dict(x=[2, 4, 6, 8, 10], y=[9, 14, 7, 18, 27]),
            dict(
                slope=2,
                intercept=3,
                correlation=0.79,
                centroid=7.07,
                sigma=2.87,
            ),
            2
        ],
        [  # sample 2 - a noisy line with negative slope
            # data from https://www.statssolver.com/simple-regression.html
            dict(x=[4, 12, 8, 16, 10], y=[45, 35, 45, 15, 25]),
            dict(
                slope=-2.5,
                intercept=58,
                correlation=-0.86,
                min_x=4,
                max_x=16,
                min_y=15,
                max_y=45,
                centroid=8.79,
                sigma=3.68,
            ),
            2
        ],
        [  # sample 3 - a triangle centered at zero (in x)
            dict(x=[-1, -0.5, 0, 0.5, 1], y=[0, 0.5, 1, 0.5, 0]),
            dict(
                slope=0,
                intercept=0.4,
                correlation=0,
                centroid=0,
                sigma=0.35,
            ),
            2
        ],
        [  # sample 4 - some non-zero y values
            dict(x=[0, 5, 10, 20, 21, 22, 51, 105], y=[0, 0, 0, 0.1, 1, 0, 0, 0]),
            dict(
                x_at_max_y=21,
                centroid=20.91,
                sigma=0.29,
            ),
            2
        ],
        [  # sample 5 - NeXus simple example
            dict(  # https://manual.nexusformat.org/examples/python/index.html
                x=[  # mr
                    17.92608, 17.92591, 17.92575, 17.92558, 17.92541, 17.92525,
                    17.92508, 17.92491, 17.92475, 17.92458, 17.92441, 17.92425,
                    17.92408, 17.92391, 17.92375, 17.92358, 17.92341, 17.92325,
                    17.92308, 17.92291, 17.92275, 17.92258, 17.92241, 17.92225,
                    17.92208, 17.92191, 17.92175, 17.92158, 17.92141, 17.92125,
                    17.92108
                ],
                y=[  # I00
                    1037, 1318, 1704, 2857, 4516, 9998, 23819,
                    31662, 40458, 49087, 56514, 63499, 66802, 66863,
                    66599, 66206, 65747, 65250, 64129, 63044, 60796,
                    56795, 51550, 43710, 29315, 19782, 12992, 6622,
                    4198, 2248, 1321
                ]
            ),
            dict(
                x_at_max_y=17.9239,
                max_y=66863,
                centroid=17.9235,
                sigma=0.0009,
            ),
            4
        ],
        [  # sample 6 - a square wave
            dict(x=[-2, -1, 0, 1, 2, 3, 4, 5, 6], y=[0, 0, 0, 1, 1, 1, 0, 0, 0]),
            dict(
                slope=0,
                intercept=0.333,
                correlation=0,
                centroid=2,
                sigma=0.816,
            ),
            3
        ],
        # fmt: on
    ],
)
def test_samples(data, expected, ndigits):
    assert len(data["x"]) == len(data["y"])

    reg = SummationRegisters()
    for x, y in zip(data["x"], data["y"]):
        reg.add(x, y)
    for k, v in expected.items():
        assert round(getattr(reg, k), ndigits) == v, str(k)

    # are these values within expectations?
    assert reg.min_x <= reg.centroid <= reg.max_x
    assert (reg.max_x - reg.min_x) >= reg.sigma

    assert reg.linear_y(0) == reg.intercept  # OK to evaluate with full precision
    assert round(reg.linear_y(1) - reg.intercept, 2) == round(reg.slope, 2)


@pytest.mark.parametrize(
    "data, exception",
    [
        # fmt: off
        [  # array length of 0
            dict(x=[], y=[]), ZeroDivisionError
        ],
        [  # array length of 1
            dict(x=[1], y=[0]), ZeroDivisionError
        ],
        [  # array length of 2
            dict(x=[1, 2], y=[0, None]), TypeError
        ],
        # fmt: on
    ],
)
def test_exceptions(data, exception):
    """Test with "bad" data that raises exceptions."""
    reg = SummationRegisters()
    with pytest.raises(exception):
        for x, y in zip(data["x"], data["y"]):
            reg.add(x, y)
        assert reg.sigma is not None


@pytest.mark.parametrize(
    "data, expected",
    [
        # fmt: off
        [
            dict(x=[2, 1, 3], y=[5, 1, 2]),
            dict(
                mean_x=2,
                mean_y=2.67,
                stddev_x=1,
                stddev_y=2.08,
                slope=0.5,
                intercept=1.67,
                correlation=0.24,
                centroid=2.12,
                sigma=0.6,
                min_x=1,
                max_x=3,
                min_y=1,
                max_y=5,
                x_at_max_y=2,
                x_at_min_y=1,
                n=3,
                X=6,
                Y=8,
                XX=14,
                XY=17,
                XXY=39,
                YY=30,
            )
        ],
        # fmt: on
    ],
)
def test_to_dict(data, expected):
    reg = SummationRegisters()
    for x, y in zip(data["x"], data["y"]):
        reg.add(x, y)
    actual = reg.to_dict(use_registers=True)
    for k in actual.keys():
        assert k in expected, k
    for k, e in sorted(expected.items()):
        assert k in actual, k
        assert round(actual[k], 2) == e, k


def test_subtract():
    reg = SummationRegisters()
    assert reg.n == 0
    assert reg.X == 0
    assert reg.XX == 0
    assert reg.min_x is None
    assert reg.max_x is None
    assert reg.x_at_max_y is None

    reg.add(1, 1)
    assert reg.n == 1
    assert reg.X != 0
    assert reg.XX != 0
    assert reg.min_x is not None
    assert reg.max_x is not None
    assert reg.x_at_max_y is not None
    assert reg.min_x == 1
    assert reg.max_x == 1
    assert reg.x_at_max_y == 1

    reg.subtract(1, 1)
    assert reg.n == 0
    assert reg.X == 0
    assert reg.XX == 0
    assert reg.min_x is not None
    assert reg.max_x is not None
    assert reg.x_at_max_y is not None
    assert reg.min_x == 1
    assert reg.max_x == 1
    assert reg.x_at_max_y == 1
