from pyrbit.mem_utils import MemoryModel
from pyrbit.mle_utils import mle_sequence
from pyrbit.plot_utils import regplot
import seaborn
import numpy
import matplotlib.pyplot as plt


class ACTR(MemoryModel):
    def __init__(self, nitems, d, s, tau, buffer_size=256, seed=None):
        super().__init__(nitems, seed=seed)
        self.d, self.s, self.tau = d, s, tau
        self.buffer_size = buffer_size
        self.reset()

    def reset(self, d=None, s=None, tau=None):
        if d is not None:
            self.d = d
        if s is not None:
            self.s = s
        if tau is not None:
            self.tau = tau

        self.counter_pres = numpy.zeros((self.nitems,))
        self.counter_time = numpy.full((self.nitems, self.buffer_size), numpy.inf)

    def _print_info(self):
        print(f"d: \t {self.counter_pres}")
        print(f"time: \t {self.counter_time}")

    def _compute_item_activation(self, item, time=None):
        if time is None:
            time = numpy.max(self.counter_time)
        self.activation = numpy.log(
            numpy.sum((time - self.counter_time[item]) ** (-self.d))
        )
        return self.activation

    def _compute_item_probabilities(self, item, time=None):
        activation = self._compute_item_activation(item, time=time)
        return 1 / (1 + numpy.exp((self.tau - activation) / self.s))

    def compute_probabilities(self, time=None):
        cip = numpy.vectorize(self._compute_item_probabilities)
        return cip(list(range(self.nitems)), time=time)

    def update(self, item, time):
        if len(time) == 1:
            n = numpy.asarray(self.counter_pres[item], dtype=numpy.int32)
            self.counter_time[item, n] = time
            self.counter_pres[item] += 1
        else:
            n = numpy.asarray(self.counter_pres[item], dtype=numpy.int32)
            self.counter_time[item, n : n + len(time)] = time
            self.counter_pres[item] += len(time)


# helper functions for simulations
def simulate_arbitrary_traj(actr, N, seed=None):
    recall = []
    times = []
    query_times = []
    rng = numpy.random.default_rng(seed=seed)

    for trial in range(N):
        actr.reset()
        nrepet = rng.integers(low=1, high=10, size=(1,))
        _times = numpy.sort(rng.random(size=(int(nrepet),)) * 100)
        times.append(_times)
        actr.update(0, _times)
        query_time = rng.random(size=(1,)) * 100 + _times[-1]
        query_times.append(query_time)
        recall.append(actr.query_item(0, query_time))
    return recall, times, query_times


def gen_data(actr_model, N, seed=None):
    recalls, times, query_times = simulate_arbitrary_traj(actr_model, N, seed=seed)
    recalls = [int(r[0]) for r in recalls]
    deltatis = [qtime - time for time, qtime in zip(times, query_times)]
    return recalls, deltatis


## visualisations


def diagnostics(d, deltatis, recall, ax=None, **kwargs):
    return logregplot(d, deltatis, recall, ax=None, **kwargs)


def logregplot(d, deltatis, recall, ax=None, label_prefix="", **kwargs):
    x_bins = kwargs.pop("x_bins", None)
    if x_bins is None:
        x_bins = int(len(recall) ** (1 / 3))
    activation = [
        numpy.log(numpy.sum(numpy.asarray(deltati) ** -d)) for deltati in deltatis
    ]
    return _logregplot_activation(
        activation, recall, ax=ax, x_bins=x_bins, label_prefix=label_prefix, **kwargs
    )


## inference


def identify_actr_from_recall_sequence(
    recall_sequence,
    deltas,
    guess=(0.5, 0.25, -0.7),
    optim_kwargs={"method": "L-BFGS-B", "bounds": [(0, 1), (-5, 5), (-5, 5)]},
    verbose=True,
    basin_hopping=False,
    basin_hopping_kwargs=None,
):
    infer_results = mle_sequence(
        _actr_sequence_likelihood_transform,
        optim_kwargs,
        guess,
        deltas,
        recall_sequence,
        basin_hopping=basin_hopping,
        basin_hopping_kwargs=basin_hopping_kwargs,
    )

    if verbose:
        print(infer_results)

    return infer_results


def actr_observed_information_matrix(recall_sequence, deltatis, d, s, tau):
    return _actr_get_sequence_observed_information_matrix(
        recall_sequence, deltatis, d, s, tau
    )[0]


def _actr_get_sequence_observed_information_matrix(
    recall_sequence, deltatis, d, s, tau
):
    J_11 = 0
    J_12 = 0
    J_13 = 0
    J_22 = 0
    J_23 = 0
    J_33 = 0

    for recall, deltati in zip(
        recall_sequence,
        deltatis,
    ):
        if recall == 1:
            J_11 += actr_ddq1_dd_dd_sample(tau, s, d, deltati)
            J_12 += actr_ddq1_dd_ds_sample(tau, s, d, deltati)
            J_13 += actr_ddq1_dd_dtau_sample(tau, s, d, deltati)
            J_22 += actr_ddq1_ds_ds_sample(tau, s, d, deltati)
            J_23 += actr_ddq1_ds_dtau_sample(tau, s, d, deltati)
            J_33 += actr_ddq1_dtau_dtau_sample(tau, s, d, deltati)
        elif recall == 0:
            J_11 += actr_ddq0_dd_dd_sample(tau, s, d, deltati)
            J_12 += actr_ddq0_dd_ds_sample(tau, s, d, deltati)
            J_13 += actr_ddq0_dd_dtau_sample(tau, s, d, deltati)
            J_22 += actr_ddq0_ds_ds_sample(tau, s, d, deltati)
            J_23 += actr_ddq0_ds_dtau_sample(tau, s, d, deltati)
            J_33 += actr_ddq0_dtau_dtau_sample(tau, s, d, deltati)
        else:
            raise ValueError(f"recall is not either 1 or 0, but is {recall}")

    J = -numpy.array([[J_11, J_12, J_13], [J_12, J_22, J_23], [J_13, J_23, J_33]])
    return J, len(recall_sequence)


def _actr_sequence_likelihood_transform(
    theta,
    deltas,
    recalls,
    transform=None,
):
    ll = 0
    d, s, tau = theta
    if transform is None:
        transform = lambda d, s, tau: (d, s, tau)
    for n, (deltati, recall) in enumerate(zip(deltas, recalls)):
        dll = _actr_log_likelihood_sample(recall, deltati, d, s, tau, transform)
        ll += dll

    return ll


def _logregplot_activation(activation, recall, ax=None, label_prefix="", **kwargs):
    ci = kwargs.pop("ci", None)
    recall_event_kwargs = kwargs.pop("recall_event_kwargs", {})

    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1)

    regplot(
        x=activation,
        y=recall,
        scatter=False,
        fit_reg=True,
        logistic=True,
        ax=ax,
        ci=ci,
        label=label_prefix + "Logistic Regression",
        **kwargs,
    )

    regplot(
        x=activation,
        y=recall,
        scatter=True,
        fit_reg=False,
        ax=ax,
        label=label_prefix + "Recall events",
        **recall_event_kwargs,
    )

    regplot(
        x=activation,
        y=recall,
        scatter=True,
        fit_reg=False,
        ax=ax,
        label=label_prefix + "Estimated recall probability",
        **kwargs,
    )

    ax.set_ylabel("Recall probability")
    ax.set_xlabel("Activation")
    return ax


def _actr_log_likelihood_sample(recall, deltas, d, s, tau, transform):
    # rescaling value to linear
    d, s, tau = transform(d, s, tau)
    if recall == 1:  # Warning: passing to array converts recall to float
        return actr_q1_sample(tau, s, d, deltas)
    elif recall == 0:
        return actr_q0_sample(tau, s, d, deltas)

    else:
        raise ValueError(f"Recall is not 0 or 1, but is {recall}")


def logistic(x):
    return 1 / (1 + numpy.exp(-x))


def activation(deltati, d):
    deltati = numpy.asarray(deltati)
    return numpy.log(numpy.sum(deltati ** (-d)))


def softplus(x):
    return numpy.log(1 + numpy.exp(x))


## ============ for observed information matrix ============= ##
## p1, q1, p0, q0
def actr_p1_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return logistic(X)


def actr_p0_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return logistic(-X)


def actr_q1_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -softplus(-X)


def actr_q0_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -softplus(X)


## first order derivatives


def da_dd(deltati, d):
    deltati = numpy.asarray(deltati)
    num = -numpy.sum(numpy.log(deltati) * deltati ** (-d))
    denom = numpy.sum(deltati ** (-d))
    return num / denom


def actr_dq1_ds_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return (tau - a) / s**2 * logistic(-X)


def actr_dq1_dtau_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -1 / s * logistic(-X)


def actr_dq1_dd_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return 1 / s * logistic(-X) * da_dd(deltati, d)


def actr_dq0_ds_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -(tau - a) / s**2 * logistic(X)


def actr_dq0_dtau_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return 1 / s * logistic(X)


def actr_dq0_dd_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -1 / s * logistic(X) * da_dd(deltati, d)


## Second order derivatives


def dda_ddd(deltati, d):
    deltati = numpy.asarray(deltati)
    num1 = numpy.sum(numpy.log(deltati) ** 2 * deltati ** (-d)) * numpy.sum(
        deltati ** (-d)
    )
    num2 = -((numpy.sum(numpy.log(deltati) * deltati ** (-d))) ** 2)
    denom = (numpy.sum(deltati ** (-(d)))) ** 2
    return (num1 + num2) / denom


# omega = 1
def actr_ddq1_ds_ds_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return 2 * (a - tau) / s**3 * logistic(-X) - (tau - a) ** 2 / s**4 * (
        logistic(X) * logistic(-X)
    )


def actr_ddq1_dtau_dtau_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -1 / s**2 * (logistic(X) * logistic(-X))


def actr_ddq1_dd_dd_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -1 / s**2 * (logistic(X) * logistic(-X)) * da_dd(
        deltati, d
    ) ** 2 + 1 / s * logistic(-X) * dda_ddd(deltati, d)


def actr_ddq1_ds_dtau_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return (tau - a) / s**3 * (logistic(X) * logistic(-X)) + 1 / s**2 * logistic(-X)


def actr_ddq1_dd_dtau_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return (logistic(X) * logistic(-X)) * 1 / s**2 * da_dd(deltati, d)


def actr_ddq1_dd_ds_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -1 / s**2 * logistic(-X) * da_dd(deltati, d) - (tau - a) / s**3 * da_dd(
        deltati, d
    ) * (logistic(X) * logistic(-X))


# omega = 0


def actr_ddq0_ds_ds_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -2 * (a - tau) / s**3 * logistic(X) - (tau - a) ** 2 / s**4 * (
        logistic(X) * logistic(-X)
    )


def actr_ddq0_dtau_dtau_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -1 / s**2 * (logistic(X) * logistic(-X))


def actr_ddq0_dd_dd_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return -1 / s**2 * (logistic(X) * logistic(-X)) * da_dd(
        deltati, d
    ) ** 2 - 1 / s * logistic(X) * dda_ddd(deltati, d)


def actr_ddq0_ds_dtau_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return (tau - a) / s**3 * (logistic(X) * logistic(-X)) - 1 / s**2 * logistic(X)


def actr_ddq0_dd_dtau_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return (logistic(X) * logistic(-X)) * 1 / s**2 * da_dd(deltati, d)


def actr_ddq0_dd_ds_sample(tau, s, d, deltati):
    a = activation(deltati, d)
    X = (a - tau) / s
    return 1 / s**2 * logistic(X) * da_dd(deltati, d) - (tau - a) / s**3 * da_dd(
        deltati, d
    ) * (logistic(X) * logistic(-X))


if __name__ == "__main__":
    # [startdoc]
    from pyrbit.mle_utils import CI_asymptotical, confidence_ellipse
    from pyrbit.actr import (
        ACTR,
        diagnostics,
        actr_observed_information_matrix,
        identify_actr_from_recall_sequence,
        gen_data,
    )

    import numpy
    import matplotlib.pyplot as plt

    SEED = None
    N = 10000

    d = 0.6
    tau = -0.7
    s = 0.25
    rng = numpy.random.default_rng(seed=SEED)

    # ==================== Simulate some data
    actr = ACTR(1, 0.5, 0.25, -0.7, buffer_size=16, seed=SEED)
    recalls, deltatis = gen_data(actr, N)

    # ================= Run Diagnostics (logistic regression)
    ax = diagnostics(
        0.6,
        deltatis,
        recalls,
        line_kws={"color": "green"},
        recall_event_kwargs={"scatter_kws": {"marker": "*", "s": 5}},
    )
    ax.legend()
    plt.tight_layout()
    plt.show()

    # ==================== Perform ML Estimation
    optim_kwargs = {"method": "L-BFGS-B", "bounds": [(0, 1), (-5, 5), (-5, 5)]}
    verbose = False
    guess = (0.2, 0.5, -1)

    # An illustration of identifying with basin_hopping. This slows down inference, as optimization is repeated 1+niter times
    def _callable(x, f, accept):
        print(x, f, accept)

    inference_results = identify_actr_from_recall_sequence(
        recalls,
        deltatis,
        optim_kwargs=optim_kwargs,
        verbose=verbose,
        guess=guess,
        basin_hopping=True,
        basin_hopping_kwargs={"niter": 3, "callback": _callable},
    )
    # see scipy.optimize doc for returned object with basinhopping
    x = inference_results.lowest_optimization_result.x

    # ================= computing Confidence Intervals and Ellipses
    J = actr_observed_information_matrix(recalls, deltatis, *x)
    # covariance matrix
    covar = numpy.linalg.inv(J)
    # Confidence intervals
    cis = CI_asymptotical(covar, x)
    # Confidence ellipses
    # draw the three ellipses, because the confidence ellipsoid will be hard to interpret.
    fig, axs = plt.subplots(nrows=1, ncols=3)
    labels = [r"$d$", r"$s$", r"$\tau$"]
    for n in range(3):
        i = (n + 1) % 3
        j = (n + 2) % 3
        if i > j:
            i, j = j, i
        _cov = numpy.array([[covar[i, i], covar[i, j]], [covar[i, j], covar[j, j]]])
        ax = confidence_ellipse((x[i], x[j]), _cov, ax=axs[n])
        ax.set_xlabel(f"{labels[i]}")
        ax.set_ylabel(f"{labels[j]}")
    plt.tight_layout()
    plt.show()
