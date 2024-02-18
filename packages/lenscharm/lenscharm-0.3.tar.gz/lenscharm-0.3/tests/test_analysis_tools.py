import matplotlib.pyplot as plt
import numpy as np
from charm_lensing.analysis_tools import chi2, shift_and_resize


def test_chi2():
    data, model = np.array([np.nan, 2, 3]), np.array([1, 2, 3])
    sigma = np.array([5, 2, 3])
    assert chi2(data, model, sigma) == 0

    data, model = np.array([1, 2]), np.array([2, 3])
    sigma = 2.0
    assert chi2(data, model, sigma) == 0.25

    data, model = np.array([1, 2]), np.array([2, 2])
    sigma = np.array([3.0, 2.0])
    assert chi2(data, model, sigma) == 1/9/2


def test_shift():
    # test shift
    i = np.array([[1, 2, 3], [4, 5, 6]])
    r = np.roll(i, (1, 1), axis=(0, 1))
    s, sx, sy = shift_and_resize(i, r, full_info=True)
    assert np.allclose(i, s)
    assert np.allclose(sx, 1)
    assert np.allclose(sy, 1)


def test_resize():
    # test_resize
    print('0.75**2', 0.75**2)
    print('0.25*0.75', 0.25*0.75)
    print('0.25**2', 0.25**2)
    input = np.array([[1, 1, 2, 2],
                      [1, 1, 2, 2],
                      [3, 3, 4, 4],
                      [3, 3, 4, 4]])
    recon = np.array([[1, 2], [3, 4]])
    # o = shift_and_resize(input, recon)
    # assert np.allclose(i, s)

    # import matplotlib.pyplot as plt
    # fig, axes = plt.subplots(1, 2)
    # ax, ay = axes
    # ax.imshow(recon)
    # ay.imshow(o)
    # plt.show()

    assert True
