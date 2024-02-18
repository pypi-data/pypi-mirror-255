from seaborn.regression import _RegressionPlotter
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy
import copy

# code patched from seaborn v0.12.2
class _PatchedRegressionPlotter(_RegressionPlotter):
    def scatterplot(self, ax, kws):
        """Draw the data."""
        # Treat the line-based markers specially, explicitly setting larger
        # linewidth than is provided by the seaborn style defaults.
        # This would ideally be handled better in matplotlib (i.e., distinguish
        # between edgewidth for solid glyphs and linewidth for line glyphs
        # but this should do for now.
        line_markers = ["1", "2", "3", "4", "+", "x", "|", "_"]
        if self.x_estimator is None:
            if "marker" in kws and kws["marker"] in line_markers:
                lw = mpl.rcParams["lines.linewidth"]
            else:
                lw = mpl.rcParams["lines.markeredgewidth"]
            kws.setdefault("linewidths", lw)

            if not hasattr(kws["color"], "shape") or kws["color"].shape[1] < 4:
                kws.setdefault("alpha", 0.8)

            x, y = self.scatter_data
            ax.scatter(x, y, **kws)
        else:
            # TODO abstraction
            ci_kws = {"color": kws["color"]}
            if "alpha" in kws:
                ci_kws["alpha"] = kws["alpha"]
            ci_kws["linewidth"] = mpl.rcParams["lines.linewidth"] * 1.75
            kws.setdefault("s", 50)

            xs, ys, cis = self.estimate_data
            if [ci for ci in cis if ci is not None]:
                for x, ci in zip(xs, cis):
                    ax.plot([x, x], ci, **ci_kws)
            ax.scatter(xs, ys, **kws)
            self.xs = xs
            self.ys = ys
            self.cis = cis

    def fit_statsmodels(self, grid, model, **kwargs):
        """More general regression function using statsmodels objects."""
        import statsmodels.tools.sm_exceptions as sme
        import warnings

        X, y = numpy.c_[numpy.ones(len(self.x)), self.x], self.y
        grid = numpy.c_[numpy.ones(len(grid)), grid]

        def reg_func(_x, _y, store=False):
            err_classes = (sme.PerfectSeparationError,)
            try:
                with warnings.catch_warnings():
                    if hasattr(sme, "PerfectSeparationWarning"):
                        # statsmodels>=0.14.0
                        warnings.simplefilter("error", sme.PerfectSeparationWarning)
                        err_classes = (*err_classes, sme.PerfectSeparationWarning)
                    _model = model(_y, _x, **kwargs).fit()
                    if store is True:
                        self.reg_params = _model.params
                    yhat = _model.predict(grid)
            except err_classes:
                yhat = numpy.empty(len(grid))
                yhat.fill(numpy.nan)
            return yhat

        yhat = reg_func(X, y, store=True)
        if self.ci is None:
            return yhat, None
        from seaborn import algorithms as algo

        yhat_boots = algo.bootstrap(
            X, y, func=reg_func, n_boot=self.n_boot, units=self.units, seed=self.seed
        )
        return yhat, yhat_boots


def regplot(
    data=None,
    *,
    x=None,
    y=None,
    x_estimator=None,
    x_bins=None,
    x_ci="ci",
    scatter=True,
    fit_reg=True,
    ci=95,
    n_boot=1000,
    units=None,
    seed=None,
    order=1,
    logistic=False,
    lowess=False,
    robust=False,
    logx=False,
    x_partial=None,
    y_partial=None,
    truncate=True,
    dropna=True,
    x_jitter=None,
    y_jitter=None,
    label=None,
    color=None,
    marker="o",
    scatter_kws=None,
    line_kws=None,
    ax=None,
):
    """
    # regplot.xs, regplot.ys, regplot.cis --> summary data

    """
    plotter = _PatchedRegressionPlotter(
        x,
        y,
        data,
        x_estimator,
        x_bins,
        x_ci,
        scatter,
        fit_reg,
        ci,
        n_boot,
        units,
        seed,
        order,
        logistic,
        lowess,
        robust,
        logx,
        x_partial,
        y_partial,
        truncate,
        dropna,
        x_jitter,
        y_jitter,
        color,
        label,
    )

    if ax is None:
        ax = plt.gca()

    scatter_kws = {} if scatter_kws is None else copy.copy(scatter_kws)
    scatter_kws["marker"] = marker
    line_kws = {} if line_kws is None else copy.copy(line_kws)
    plotter.plot(ax, scatter_kws, line_kws)
    return ax, plotter
