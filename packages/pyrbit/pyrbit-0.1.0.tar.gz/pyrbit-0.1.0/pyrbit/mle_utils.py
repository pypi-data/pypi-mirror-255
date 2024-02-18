import numpy
import scipy
import scipy.optimize as opti
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import pandas
import seaborn

class InvalidConfidenceEllipsisError(Exception):
    """InvalidConfidenceEllipsisError

    Raised when the confidence ellipsis can not be computed properly.
    """

    pass


def mle_sequence(
    likelihood_function,
    optimizer_kwargs,
    guess,
    *args,
    basin_hopping=False,
    basin_hopping_kwargs=None,
    **kwargs,
):
    # note: removed possibility to specify transform function
    # note: check the k_vector

    # invert sign and deal with argument shape
    ll_lambda = lambda guess, args: -likelihood_function(guess, *args)
    if not basin_hopping:
        res = opti.minimize(ll_lambda, guess, args=(args,), **optimizer_kwargs)
    else:
        if basin_hopping_kwargs is None:
            basin_hopping_kwargs = {}
        optimizer_kwargs.update({"args": (args,)})
        res = opti.basinhopping(
            ll_lambda, guess, minimizer_kwargs=optimizer_kwargs, **basin_hopping_kwargs
        )

    return res


def _confidence_ellipsis(x, cov, critical_value=5.991, **kwargs):
    # critical values can be looked up in a chisquared table with df = 2

    eigen_values, eigen_vectors = numpy.linalg.eig(cov)
    indexes = eigen_values.argsort()[::-1]
    eigen_values = eigen_values[indexes]
    eigen_vectors = eigen_vectors[:, indexes]

    ellipsis_orientation = numpy.arctan2(eigen_vectors[:, 0][1], eigen_vectors[:, 0][0])
    with numpy.errstate(invalid="raise"):
        ellipsis_large_axis = 2 * numpy.sqrt(critical_value * eigen_values[0])
        ellipsis_small_axis = 2 * numpy.sqrt(critical_value * eigen_values[1])
    return Ellipse(
        x, ellipsis_large_axis, ellipsis_small_axis, ellipsis_orientation, **kwargs
    )


def confidence_ellipse(
    inferred_parameters,
    estimated_covariance_matrix,
    confidence_levels=[0.68, 0.95],
    ax=None,
    colors=["#B0E0E6", "#87CEEB"],
    plot_kwargs={"color": "red", "marker": "D", "label": "ML estimate"},
):
    """estimated_covariance_matrix = numpy.linalg.inv(J)"""

    x = inferred_parameters

    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1)

    critical_values = [scipy.stats.chi2.ppf(cl, 2) for cl in confidence_levels]
    for critical_value, color, cl in zip(
        critical_values[::-1], colors[::-1], confidence_levels[::-1]
    ):
        try:
            _patch = _confidence_ellipsis(
                x,
                estimated_covariance_matrix,
                critical_value=critical_value,
                fill=True,
                facecolor=color,
                edgecolor="b",
                # label=f"Confidence level:{cl}",
            )
            ax.add_patch(_patch)
        except FloatingPointError:
            raise InvalidConfidenceEllipsisError(
                "The confidence ellipsis is invalid and can not be computed. Most likely the estimated covariance matrix is not positive"
            )

    ax.plot(*x, **plot_kwargs)

    return ax


def CI_asymptotical(invJ, params, critical_value=1.96):
    if invJ.shape[0] != len(params):
        raise ValueError(
            f"Size of params ({len(params)}) different from dimension of the covariance matrix ({invJ.shape[0]})"
        )
    cis = []
    for np, param in enumerate(params):

        with numpy.errstate(invalid="raise"):
            try:
                ci_low = param - critical_value * numpy.sqrt(invJ[np, np])
                ci_high = param + critical_value * numpy.sqrt(invJ[np, np])
            except FloatingPointError:
                ci_low = numpy.nan
                ci_high = numpy.nan

        cis.append((ci_low, ci_high))

    return cis


# https://stackoverflow.com/questions/43238173/python-convert-matrix-to-positive-semi-definite/43244194#43244194
# code by Ahmed Fasih
def nearestPD(A):
    """Find the nearest positive-definite matrix to input

    A Python/Numpy port of John D'Errico's `nearestSPD` MATLAB code [1], which
    credits [2].

    [1] https://www.mathworks.com/matlabcentral/fileexchange/42885-nearestspd

    [2] N.J. Higham, "Computing a nearest symmetric positive semidefinite
    matrix" (1988): https://doi.org/10.1016/0024-3795(88)90223-6
    """

    B = (A + A.T) / 2
    _, s, V = numpy.linalg.svd(B)

    H = numpy.dot(V.T, numpy.dot(numpy.diag(s), V))

    A2 = (B + H) / 2

    A3 = (A2 + A2.T) / 2

    if isPD(A3):
        return A3

    spacing = numpy.spacing(numpy.linalg.norm(A))
    # The above is different from [1]. It appears that MATLAB's `chol` Cholesky
    # decomposition will accept matrixes with exactly 0-eigenvalue, whereas
    # Numpy's will not. So where [1] uses `eps(mineig)` (where `eps` is Matlab
    # for `np.spacing`), we use the above definition. CAVEAT: our `spacing`
    # will be much larger than [1]'s `eps(mineig)`, since `mineig` is usually on
    # the order of 1e-16, and `eps(1e-16)` is on the order of 1e-34, whereas
    # `spacing` will, for Gaussian random matrixes of small dimension, be on
    # othe order of 1e-16. In practice, both ways converge, as the unit test
    # below suggests.
    I = numpy.eye(A.shape[0])
    k = 1
    while not isPD(A3):
        mineig = numpy.min(numpy.real(numpy.linalg.eigvals(A3)))
        A3 += I * (-mineig * k ** 2 + spacing)
        k += 1

    return A3


def isPD(B):
    """Returns true when input is positive-definite, via Cholesky"""
    try:
        _ = numpy.linalg.cholesky(B)
        return True
    except numpy.linalg.LinAlgError:
        return False


def compute_summary_statistics_estimation(estimated_parameters, subsample_sequence, TRUE_VALUE, ax = None,      bias_kwargs=None, std_kwargs=None,):
    if bias_kwargs is None:
        bias_kwargs = {}
    if std_kwargs is None:
        std_kwargs = {}

    n=estimated_parameters.shape[0]
    N = estimated_parameters.shape[1]
    
    TRUE_VALUE = numpy.repeat(
        numpy.asarray(TRUE_VALUE)[:, None],N , axis=1
    )

    estimated_parameters_bias = numpy.abs(
        numpy.nanmean(estimated_parameters, axis=2) - TRUE_VALUE
    )
    estimated_parameters_std = numpy.nanstd(estimated_parameters, axis=2)

    k = estimated_parameters_bias.shape[1]
    agg_data = numpy.zeros(shape=(n * k, 4))
    agg_data[:k, 0] = estimated_parameters_bias[0, :]
    agg_data[k : n * k, 0] = estimated_parameters_bias[1, :]
    agg_data[:k, 1] = estimated_parameters_std[0, :]
    agg_data[k : n * k, 1] = estimated_parameters_std[1, :]
    agg_data[:k, 2] = subsample_sequence
    agg_data[k : n * k, 2] = subsample_sequence
    agg_data[:k, 3] = 0
    agg_data[k : n * k, 3] = 1

    df = pandas.DataFrame(agg_data, columns=["|Bias|", "Std dev", "N", "parameter"])
    if n == 2:
        mapping = {"0": r"$\alpha$", "1": r"$\beta$"}
    else:
        raise NotImplementedError
    df["parameter"] = df["parameter"].map(lambda s: mapping.get(str(int(s))))
    df["N"] = df["N"].astype(int)

    if ax is None:
        return agg_data, df
    
    seaborn.barplot(
        data=df, x="N", y="|Bias|", hue="parameter", ax=ax[0], **bias_kwargs
    )
    seaborn.barplot(
        data=df, x="N", y="Std dev", hue="parameter", ax=ax[1], **std_kwargs
    )

    ax[0].set_yscale("log")
    ax[1].set_yscale("log")

    return agg_data, df, ax