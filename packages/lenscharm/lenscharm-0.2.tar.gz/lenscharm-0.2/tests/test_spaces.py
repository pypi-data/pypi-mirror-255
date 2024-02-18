import pytest
import numpy as np
from charm_lensing.spaces import (
    coords, get_xycoords, get_klcoords, get_centered_slice,
    Space
)
from dataclasses import asdict
from nifty8 import RGSpace


def test_coords():
    # Test case 1
    shape = 5
    distance = 1
    expected_output = np.array([-2, -1, 0, 1, 2])
    assert np.array_equal(coords(shape, distance), expected_output)

    # Test case 2
    shape = 6
    distance = 0.5
    expected_output = np.array([-1.25, -0.75, -0.25, 0.25, 0.75,  1.25])
    assert np.allclose(coords(shape, distance), expected_output)


def test_get_xycoords():
    # Test case 1
    shape = (5, 5)
    distances = (1, 1)
    expected_output = np.array([
        [[-2, -1,  0,  1,  2],
         [-2, -1,  0,  1,  2],
         [-2, -1,  0,  1,  2],
         [-2, -1,  0,  1,  2],
         [-2, -1,  0,  1,  2]],

        [[-2, -2, -2, -2, -2],
         [-1, -1, -1, -1, -1],
         [0,  0,  0,  0,  0],
         [1,  1,  1,  1,  1],
         [2,  2,  2,  2,  2]]
    ])
    assert np.array_equal(get_xycoords(shape, distances), expected_output)

    # Test case 2
    shape = (3, 4)
    distances = (0.5, 1)
    expected_output = np.array([
        [[-0.5,  0.,  0.5],
         [-0.5,  0.,  0.5],
         [-0.5,  0.,  0.5],
         [-0.5,  0.,  0.5]],

        [[-1.5, -1.5, -1.5],
         [-0.5, -0.5, -0.5],
         [0.5,  0.5,  0.5],
         [1.5,  1.5,  1.5]]
    ])
    assert np.allclose(get_xycoords(shape, distances), expected_output)

    # Test case 3
    shape = (3, 4)
    distances = (1, 0.5)
    assert get_xycoords(shape, distances).shape == (2, 4, 3)


def test_get_klcoords():
    # Test case 1
    shape = (5, 5)
    distances = (1, 1)
    expected_output = np.array([
        [[0.,  0.2,  0.4, -0.4, -0.2],
         [0.,  0.2,  0.4, -0.4, -0.2],
         [0.,  0.2,  0.4, -0.4, -0.2],
         [0.,  0.2,  0.4, -0.4, -0.2],
         [0.,  0.2,  0.4, -0.4, -0.2]],

        [[0.,  0.,  0.,  0.,  0.],
         [0.2,  0.2,  0.2,  0.2,  0.2],
         [0.4,  0.4,  0.4,  0.4,  0.4],
         [-0.4, -0.4, -0.4, -0.4, -0.4],
         [-0.2, -0.2, -0.2, -0.2, -0.2]]])
    assert np.allclose(get_klcoords(shape, distances), expected_output)

    # Test case 2
    shape = (3, 4)
    distances = (0.5, 1)
    expected_output = np.array([
        [[0.,  0.25, -0.5, -0.25],
         [0.,  0.25, -0.5, -0.25],
         [0.,  0.25, -0.5, -0.25]],

        [[0.,  0.,  0.,  0.],
         [0.66666667,  0.66666667, 0.66666667,  0.66666667],
         [-0.66666667, -0.66666667, -0.66666667, -0.66666667]]
    ])
    assert np.allclose(get_klcoords(shape, distances), expected_output)

    # Test case 3
    shape = (2, 3, 4)
    distances = (2, 1, 0.5)
    with pytest.raises(AssertionError):
        get_klcoords(shape, distances)


def test_get_centered_slice():
    # Test case 1
    extended_shape = (9, 9)
    original_shape = (5, 5)
    expected_output = (slice(2, 7), slice(2, 7))
    assert get_centered_slice(
        extended_shape, original_shape) == expected_output

    # Test case 2
    extended_shape = (11, 12)
    original_shape = (3, 4)
    expected_output = (slice(4, 7), slice(4, 8))
    assert get_centered_slice(
        extended_shape, original_shape) == expected_output

    # Test case 3
    extended_shape = (7, 7, 7)
    original_shape = (3, 3, 3)
    expected_output = (slice(2, 5), slice(2, 5), slice(2, 5))
    assert get_centered_slice(
        extended_shape, original_shape) == expected_output

    # Test case 4
    extended_shape = (10, 10)
    original_shape = (5, 5)
    expected_output = (slice(None), slice(3, 8), slice(3, 8))
    assert get_centered_slice(
        extended_shape, original_shape, coordinates=True) == expected_output


def test_Space():
    # Test case 1
    shape = (5, 5)
    distances = (1, 1)
    extend_factor = 2
    space = Space(shape, distances, extend_factor=extend_factor)

    # Test that the shape and distances are correctly stored in the instance
    assert space.shape == shape
    assert space.distances == distances

    # Test that the coordinates are correctly generated
    expected_coords = get_xycoords(shape, distances)
    assert np.array_equal(space.coords(), expected_coords)

    # Test that the extend method returns a new Space object with the correct shape
    extended_shape = tuple(int(s * extend_factor) for s in shape)
    extended_space = space.extend()
    assert extended_space.shape == extended_shape

    # Test that the __post_init__ method calculates the extent correctly
    expected_extent = (-2.5, 2.5, -2.5, 2.5)
    assert np.array_equal(space.extent, expected_extent)

    # Test that asdict method returns a dictionary containing the expected fields
    expected_dict = {
        'shape': shape,
        'distances': distances,
        'space_key': '',
        'extend_factor': 2.0,
        'nifty_domain': RGSpace(shape, distances),
        'center': np.array((0., 0.)),
        'extent': expected_extent
    }
    for key, val in asdict(space).items():
        if isinstance(val, np.ndarray):
            assert np.array_equal(val, expected_dict[key])
        else:
            assert val == expected_dict[key]
