from pyrbit.mem_utils import MemoryModel
from pyrbit.plot_utils import regplot
from pyrbit.mle_utils import mle_sequence

import matplotlib.pyplot as plt
import numpy
import pandas
import statsmodels.formula.api as smf
import seaborn
import warnings


class ExponentialForgetting(MemoryModel):
    def __init__(self, nitems, a, b, max_a=0.5, min_a=10 ** (-6), **kwargs):
        super().__init__(nitems, **kwargs)
        if a > max_a or a < min_a:
            warnings.warn(
                f"value a = {a} is outside admissible range ({min_a} < a < {max_a}). I am clipping it"
            )
            a = numpy.clip(a, min_a, max_a)
        self.a, self.b = a, b
        self.reset()

    def reset(self, *args, a=None, b=None):
        if a is not None:
            self.a = a
        if b is not None:
            self.b = b

        # self.counters is number of presentations, not repetitions
        if len(args) == 0:
            self.counters = numpy.zeros((self.nitems, 2))
            self.counters[:, 1] = -numpy.inf
        else:
            self.counters = numpy.zeros((self.n_items, 2))
            self.counters[:, 0] = args[0]
            self.counters[:, 1] = args[1]

    def update(self, item, time, N=None):
        item = int(item)
        if N is None:
            self.counters[item, 0] += 1
        else:
            self.counters[item, 0] = N
        self.counters[item, 1] = time

    def _print_info(self):
        print(f"counters: \t {self.counters}")

    def compute_probabilities(self, time=None):
        if time is None:
            time = numpy.max(self.counters[:, 1])
        n = self.counters[:, 0]
        deltat = time - self.counters[:, 1]
        return numpy.exp(-self.a * (1 - self.b) ** (n - 1) * deltat)

    def __repr__(self):
        return f"{self.__class__.__name__}\n a = {self.a}\n b = {self.b}"


def identify_ef_from_recall_sequence(
    recall_sequence,
    deltas,
    k_vector=None,
    guess=(1e-3, 0.5),
    optim_kwargs={"method": "L-BFGS-B", "bounds": [(1e-7, 5e-1), (0, 0.99)]},
    verbose=True,
    basin_hopping=False,
    basin_hopping_kwargs=None,
):
    infer_results = mle_sequence(
        _ef_get_sequence_likelihood,
        optim_kwargs,
        guess,
        deltas,
        recall_sequence,
        k_vector,
        basin_hopping=basin_hopping,
        basin_hopping_kwargs=basin_hopping_kwargs,
    )

    if verbose:
        print(infer_results)

    return infer_results


def covar_delta_method_log_alpha(alpha, var):
    """var should be inverse of J observed information matrix"""
    grad = numpy.array([[1 / alpha / numpy.log(10), 0], [0, 1]])
    return grad.T @ var @ grad


def ef_observed_information_matrix(recall_sequence, deltas, alpha, beta, k_vector=None):
    return _ef_get_sequence_observed_information_matrix(
        recall_sequence, deltas, alpha, beta, k_vector=k_vector
    )[0]


def diagnostics(
    alpha,
    beta,
    k_repetition,
    deltas,
    recall,
    exponent_kwargs=None,
    loglogplot_kwargs=None,
):
    _exponent_kwargs = {"xbins": int(len(deltas) ** (1 / 3)), "inf_to_int": -10}
    if exponent_kwargs is not None:
        _exponent_kwargs.update(exponent_kwargs)

    _loglogplot_kwargs = {}
    if loglogplot_kwargs is not None:
        _loglogplot_kwargs.update(loglogplot_kwargs)

    exponent = [
        -alpha * (1 - beta) ** (k) * dt for (k, dt) in zip(k_repetition, deltas)
    ]

    fig, axs = plt.subplots(nrows=1, ncols=1)
    ax, regplot = plot_exponent_scatter(exponent, recall, ax=axs, **_exponent_kwargs)
    ax.legend()
    fg, ax, estim = loglogpplot(k_repetition, recall, deltas, **_loglogplot_kwargs)

    return fig, (fg, ax, estim)


def flatten(
    data,
    schedule=None,
    population_model=None,
    test_blocks=None,
    get_k_delta=False,
    replications=1,
):
    if replications != 1:
        raise NotImplementedError("not supported yet")
    if not get_k_delta:
        return data[0, 0, ...].ravel()
    if test_blocks is None:
        k, d = get_k_delta_schedule(schedule)

        k = numpy.tile(k, (replications, len(population_model), 1))
        k = k.transpose(0, 2, 1)

        d = numpy.tile(d, (replications, len(population_model), 1))
        d = d.transpose(0, 2, 1)

    else:
        k, d = get_k_delta_schedule(schedule, test_blocks=test_blocks, data=data)
        k = numpy.array(k).reshape(len(population_model), len(test_blocks)).T
        d = numpy.array(d).reshape(len(population_model), len(test_blocks)).T

    return data[0, 0, ...].ravel(), d.ravel(), k.ravel()


def get_k_delta_schedule(schedule, test_blocks=None, data=None):
    if test_blocks is None:
        return _get_k_delta_schedule_no_test_blocks(schedule)
    else:
        return _get_k_delta_schedule_test_blocks(
            schedule, test_blocks=test_blocks, data=data
        )


def _get_k_delta_schedule_no_test_blocks(schedule):
    counter = {str(i): -1 for i in range(schedule.nitems)}
    timer = {str(i): -numpy.inf for i in range(schedule.nitems)}
    k_vec = []
    delta_vec = []
    for item, time in schedule:
        k_vec.append(counter[str(item)])
        delta_vec.append(time - timer[str(item)])
        counter[str(item)] += 1
        timer[str(item)] = time
    return k_vec, delta_vec


def _get_k_delta_schedule_test_blocks(schedule, test_blocks, data):
    recall = data[0, 0, :, :].transpose(1, 0)
    k_vec = []
    delta_vec = []
    for r in recall:
        counter = {str(i): -1 for i in range(schedule.nitems)}
        timer = {str(i): -numpy.inf for i in range(schedule.nitems)}

        nr = 0
        for n, (item, time) in enumerate(schedule):
            m = int(n / (schedule.nitems * schedule.repet_trials))
            if m in test_blocks:
                k_vec.append(counter[str(item)])
                delta_vec.append(time - timer[str(item)])
                if r[nr]:
                    counter[str(item)] += 1
                    timer[str(item)] = time
                nr += 1
            else:
                counter[str(item)] += 1
                timer[str(item)] = time

    return k_vec, delta_vec


# def serialize_experiment(data, times):
#     _, block_size = data.shape
#     k_vector = []
#     deltas = []
#     for i in data:
#         k_vector += [k for k in range(-1, block_size - 1)]
#         deltas += [numpy.infty] + numpy.diff(numpy.asarray(times)).tolist()
#     data = data.reshape(
#         -1,
#     )
#     return data, numpy.asarray(k_vector), numpy.asarray(deltas)


## ============ for observed information matrix ============= ##
## p1, q1, p0, q0
def ef_p1_sample(alpha, beta, k, deltat):
    return numpy.exp(ef_q1_sample(alpha, beta, k, deltat))


def ef_p0_sample(alpha, beta, k, deltat):
    return 1 - ef_p1_sample(alpha, beta, k, deltat)


def ef_q1_sample(alpha, beta, k, deltat):
    return -alpha * (1 - beta) ** k * deltat


def ef_q0_sample(alpha, beta, k, deltat):
    return numpy.log(1 - numpy.exp(ef_q1_sample(alpha, beta, k, deltat)))


## first order derivatives
def ef_dq1_dalpha_sample(alpha, beta, k, deltat):
    return -((1 - beta) ** k) * deltat


def ef_dq1_dbeta_sample(alpha, beta, k, deltat):
    return alpha * k * (1 - beta) ** (k - 1) * deltat


def ef_dq0_dalpha_sample(alpha, beta, k, deltat):
    return (
        (1 - beta) ** k
        * deltat
        * ef_p1_sample(alpha, beta, k, deltat)
        / ef_p0_sample(alpha, beta, k, deltat)
    )


def ef_dq0_dbeta_sample(alpha, beta, k, deltat):
    return (
        -k
        * alpha
        * (1 - beta) ** (k - 1)
        * deltat
        * ef_p1_sample(alpha, beta, k, deltat)
        / ef_p0_sample(alpha, beta, k, deltat)
    )


## Second order derivatives


def ef_ddq1_dalpha_dalpha_sample(alpha, beta, k, deltat):
    # return __sym_ef_ddq1_dalpha_dalpha_sample(alpha, beta, k, deltat)
    return 0


def ef_ddq1_dalpha_dbeta_sample(alpha, beta, k, deltat):
    # return __sym_ef_ddq1_dalpha_dbeta_sample(alpha, beta, k, deltat)
    return k * (1 - beta) ** (k - 1) * deltat


def ef_ddq1_dbeta_dbeta_sample(alpha, beta, k, deltat):
    # return __sym_ef_ddq1_dbeta_dbeta_sample(alpha, beta, k, deltat)
    return -alpha * k * (k - 1) * (1 - beta) ** (k - 2) * deltat


def ef_ddq0_dalpha_dalpha_sample(alpha, beta, k, deltat):
    # return __sym_ef_ddq0_dalpha_dalpha_sample(alpha, beta, k, deltat)
    if deltat == numpy.inf:
        return 0
    with numpy.errstate(divide="raise"):
        try:
            return (
                -((1 - beta) ** (2 * k))
                * deltat**2
                * (
                    ef_p1_sample(alpha, beta, k, deltat)
                    / ef_p0_sample(alpha, beta, k, deltat) ** 2
                )
            )
        except FloatingPointError:
            return -1 / alpha**2


def ef_ddq0_dalpha_dbeta_sample(alpha, beta, k, deltat):
    # return __sym_ef_ddq0_dalpha_dbeta_sample(alpha, beta, k, deltat)
    if deltat == numpy.inf:
        return 0
    with numpy.errstate(divide="raise", invalid="raise"):
        try:
            return (
                -k
                * (1 - beta) ** (k - 1)
                * deltat
                * ef_p1_sample(alpha, beta, k, deltat)
                / ef_p0_sample(alpha, beta, k, deltat)
                + alpha
                * k
                * (1 - beta) ** (2 * k - 1)
                * deltat**2
                * ef_p1_sample(alpha, beta, k, deltat)
                / ef_p0_sample(alpha, beta, k, deltat) ** 2
            )
        except FloatingPointError:
            return 0


def ef_ddq0_dbeta_dbeta_sample(alpha, beta, k, deltat):
    # return __sym_ef_ddq0_dbeta_dbeta_sample(alpha, beta, k, deltat)
    if deltat == numpy.inf:
        return 0
    with numpy.errstate(divide="raise", invalid="raise"):
        try:
            return (
                alpha
                * k
                * (k - 1)
                * (1 - beta) ** (k - 2)
                * deltat
                * ef_p1_sample(alpha, beta, k, deltat)
                / ef_p0_sample(alpha, beta, k, deltat)
                - alpha**2
                * k**2
                * deltat**2
                * (1 - beta) ** (2 * k - 2)
                * ef_p1_sample(alpha, beta, k, deltat)
                / ef_p0_sample(alpha, beta, k, deltat) ** 2
            )
        except FloatingPointError:
            return -k * (k * beta - 1) / (1 - beta)


def _ef_log_likelihood_sample(recall, k, deltat, alpha, beta, transform):
    # rescaling value to linear
    a, b = transform(alpha, beta)
    if recall == 1:  # Warning: passing to array converts recall to float
        return -a * (1 - b) ** k * deltat
    elif recall == 0:
        with numpy.errstate(over="raise", invalid="raise", divide="raise"):
            try:
                exp = numpy.exp(-a * (1 - b) ** k * deltat)

                # exp = numpy.clip(exp, a_min=0, a_max=1 - 1e-4)
                return numpy.log(1 - exp)
            except FloatingPointError:
                return -1e6

    else:
        raise ValueError(f"Recall is not 0 or 1, but is {recall}")


def _ef_get_sequence_likelihood(
    theta,
    deltas,
    recalls,
    k_vector=None,
):
    transform = lambda a, b: (a, b)
    return __ef_get_sequence_likelihood_with_transform(
        theta,
        deltas,
        recalls,
        k_vector=k_vector,
        transform=transform,
    )


def _ef_get_sequence_observed_information_matrix(
    recall_sequence, deltas, alpha, beta, k_vector=None
):
    J_11 = 0
    J_12 = 0
    J_22 = 0
    if k_vector is None:
        k_vector = list(range(1, len(deltas)))

    for recall, delta, k in zip(recall_sequence, deltas, k_vector):
        if recall == 1:
            J_11 += ef_ddq1_dalpha_dalpha_sample(alpha, beta, k, delta)
            J_12 += ef_ddq1_dalpha_dbeta_sample(alpha, beta, k, delta)
            J_22 += ef_ddq1_dbeta_dbeta_sample(alpha, beta, k, delta)
        elif recall == 0:
            J_11 += ef_ddq0_dalpha_dalpha_sample(alpha, beta, k, delta)
            J_12 += ef_ddq0_dalpha_dbeta_sample(alpha, beta, k, delta)
            J_22 += ef_ddq0_dbeta_dbeta_sample(alpha, beta, k, delta)
        else:
            raise ValueError(f"recall is not either 1 or 0, but is {recall}")

    J = -numpy.array([[J_11, J_12], [J_12, J_22]])
    return J, len(deltas)


def __ef_get_sequence_likelihood_with_transform(
    theta,
    deltas,
    recalls,
    k_vector=None,
    transform=None,
):
    ll = 0
    alpha, beta = theta

    if k_vector is None:
        for nsched, recall in enumerate(recalls):
            dll = _ef_log_likelihood_sample(
                recall, nsched, deltas[nsched], alpha, beta, transform
            )
            ll += dll
    else:
        for n, (k, recall) in enumerate(zip(k_vector, recalls)):
            dll = _ef_log_likelihood_sample(
                recall, k, deltas[n], alpha, beta, transform
            )
            ll += dll
    return ll


#### ============================= Plot


def plot_exponent_scatter(exponent, recall, ax=None, xbins=15, inf_to_int=None):
    if inf_to_int is not None:
        exponent = numpy.nan_to_num(exponent, neginf=inf_to_int)

    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1)

    _, _regplot = regplot(
        x=exponent,
        y=recall,
        ax=ax,
        fit_reg=False,
        x_bins=xbins,
        label="Estimated recall probability",
    )
    _, _ = regplot(
        x=exponent,
        y=recall,
        ax=ax,
        fit_reg=False,
        label="Recall events",
        marker=".",
        color="orange",
    )
    _x = numpy.linspace(numpy.min(exponent), numpy.max(exponent), 100)
    ax.plot(_x, [numpy.exp(x) for x in _x], "-", label="exponential forgetting model")
    ax.set_xlabel(r"$\mathrm{exponent~}\omega$")
    ax.set_ylabel("Recall (events and probabilities)")
    return ax, _regplot


def loglogpplot(k_repetition, recall, deltas, x_bins=7, mode="log"):
    sequence = [(k, r, d) for k, r, d in zip(k_repetition, recall, deltas)]
    df = pandas.DataFrame(sequence)
    df.columns = ["repetition", "recall", "deltat"]
    df = df[df["repetition"] >= 0]

    if mode == "log":
        _x_bins = numpy.logspace(
            numpy.log10(numpy.min(df["deltat"])),
            numpy.log10(numpy.max(df["deltat"])),
            x_bins,
        )
    else:
        _x_bins = numpy.linspace(
            numpy.min(df["deltat"]), numpy.max(df["deltat"]), x_bins
        )

    df["discretized_deltas"] = pandas.cut(df["deltat"], bins=_x_bins, labels=False)

    df_group = df.groupby(["repetition", "discretized_deltas"]).mean()
    df_group["log_delta"] = numpy.log(df_group["deltat"])
    df_group = df_group[df_group["recall"] != 0]
    df_group["minuslogp"] = -numpy.log(df_group["recall"])
    df_group = df_group[df_group["minuslogp"] != 0]
    df_group["logminuslogp"] = numpy.log(df_group["minuslogp"])

    df_group = df_group.reset_index()

    try:
        model = smf.mixedlm(
            "logminuslogp ~ log_delta", df_group, groups=df_group["repetition"]
        )
        _fit = model.fit()
        ri = [v[0] for v in _fit.random_effects.values()]
        beta_estim = 1 - numpy.exp(numpy.mean(numpy.diff(ri)))
        alpha_estim = numpy.exp(_fit.params["Intercept"] + ri[0])
        estim = {"alpha_estim": alpha_estim, "beta_estim": beta_estim}
    except:
        estim = None

    fg = seaborn.lmplot(
        x="log_delta",
        y="logminuslogp",
        data=df_group.reset_index(),
        hue="repetition",
    )
    ax = fg.axes.flatten()[0]
    xlim = ax.get_xlim()
    ax.plot(xlim, xlim, "r-", lw=2, label="y=x")
    ax.text(numpy.mean(xlim) + 0.2, numpy.mean(xlim) - 0.2, "y=x", color="r")
    fg.set_xlabels(r"$\log(\Delta_t)$")
    fg.set_ylabels(r"$\log(-\log p)$")
    return fg, ax, estim


if __name__ == "__main__":
    # [startdoc]
    from pyrbit.mle_utils import CI_asymptotical, confidence_ellipse
    from pyrbit.ef import (
        ExponentialForgetting,
        diagnostics,
        identify_ef_from_recall_sequence,
        ef_observed_information_matrix,
        covar_delta_method_log_alpha,
    )
    from pyrbit.mem_utils import BlockBasedSchedule, experiment
    import numpy
    import matplotlib.pyplot as plt

    SEED = None
    N = 10000
    alpha = 0.001
    beta = 0.4

    # Initialize an EF memory model with 1 item
    ef = ExponentialForgetting(1, alpha, beta, seed=SEED)

    # Helper function for simulation
    rng = numpy.random.default_rng(seed=SEED)

    def simulate_arbitrary_traj(ef, k_vector, deltas):
        recall = []
        for k, d in zip(k_vector, deltas):
            ef.update(0, 0, N=k)
            recall.append(ef.query_item(0, d))
        return recall

    # ============== Simulate some data
    k_vector = rng.integers(low=0, high=10, size=N)
    deltas = rng.integers(low=1, high=5000, size=N)
    recall_probs = simulate_arbitrary_traj(ef, k_vector, deltas)
    recall = [rp[0] for rp in recall_probs]
    k_repetition = [k - 1 for k in k_vector]

    # ================ Run diagnostics
    # some options that you can set to tweak the diagnostics output
    exponent_kwargs = dict(xbins=15, inf_to_int=None)
    loglogplot_kwargs = dict(x_bins=7, mode="lin")
    # Run the diagnostics
    fig, (fg, ax, estim) = diagnostics(
        alpha,
        beta,
        k_repetition,
        deltas,
        recall,
        exponent_kwargs=exponent_kwargs,
        loglogplot_kwargs=loglogplot_kwargs,
    )
    plt.tight_layout()
    plt.show()

    # ==================== Perform ML Estimation
    # Solver parameters; this should work well and be quite fast
    optim_kwargs = {"method": "L-BFGS-B", "bounds": [(1e-5, 0.1), (0, 0.99)]}
    verbose = False
    guess = (1e-2, 0.5)
    # Pass all the observed data to the inference function. You can use basin_hopping for more precise estimates but this will take more time, see actr.py for an example. Returns the output of scipy.optimize
    inference_results = identify_ef_from_recall_sequence(
        recall_sequence=recall,
        deltas=deltas,
        k_vector=k_repetition,
        optim_kwargs=optim_kwargs,
        verbose=verbose,
        guess=guess,
        basin_hopping=False,
        basin_hopping_kwargs=None,
    )

    ## ==== computing Confidence Intervals and Ellipses

    # Get observed information matrix
    J = ef_observed_information_matrix(
        recall, deltas, *inference_results.x, k_vector=k_repetition
    )

    fig, axs = plt.subplots(nrows=1, ncols=2)

    # Compute covariance matrix:
    covar = numpy.linalg.inv(J)
    # get 95% confidence intervals
    cis = CI_asymptotical(covar, inference_results.x, critical_value=1.96)
    ax_lin = confidence_ellipse(inference_results.x, covar, ax=axs[0])

    # with log transform --- should be better
    transformed_covar = covar_delta_method_log_alpha(inference_results.x[0], covar)
    x = [numpy.log10(inference_results.x[0]), inference_results.x[1]]
    cis = CI_asymptotical(transformed_covar, x, critical_value=1.96)
    ax_log = confidence_ellipse(x, transformed_covar, ax=axs[1])
    ax_lin.set_title("CE with linear scale")
    ax_log.set_title("CE with alpha log scale")
    plt.tight_layout()
    plt.show()

    # ========== An example of inference when using a BlockBasedSchedule
    # Define a blockbasedschedule
    schedule = BlockBasedSchedule(
        1,
        5,
        [200, 200, 200, 200, 2000, 86400, 200, 2000],
        repet_trials=1,
        seed=123,
        sigma_t=None,
    )
    # Alternative way of defining a population as a list
    population_model = [
        ExponentialForgetting(1, 10 ** (-2.5), 0.75, seed=None) for i in range(200)
    ]

    data = experiment(
        population_model,
        schedule,
        test_blocks=[
            1,
            3,
            5,
            6,
            8,
        ],  # If there are learning vs recall blocks, define which are the test blocks. This changes behavior of the memory model (false recall during test does not count as an extra repetition in the models)
        replications=1,  # untested for != 1, but is not useful
    )

    # make a big one D array out of the recall data, and get the corresponding deltas and ks
    r, d, k = flatten(
        data,
        schedule=schedule,
        population_model=population_model,
        test_blocks=[1, 3, 5, 6, 8],
        get_k_delta=True,
        replications=1,
    )

    # infer model parameters
    optim_kwargs = {"method": "L-BFGS-B", "bounds": [(1e-5, 0.1), (0, 0.99)]}
    verbose = False
    guess = (1e-2, 0.5)
    # Pass all the observed data to the inference function. You can use basin_hopping for more precise estimates but this will take more time, see actr.py for an example. Returns the output of scipy.optimize
    inference_results = identify_ef_from_recall_sequence(
        recall_sequence=r,
        deltas=d,
        k_vector=k,
        optim_kwargs=optim_kwargs,
        verbose=verbose,
        guess=guess,
        basin_hopping=False,
        basin_hopping_kwargs=None,
    )
    J = ef_observed_information_matrix(r, d, *inference_results.x, k_vector=k)
    covar = numpy.linalg.inv(J)
    # get 95% confidence intervals
    transformed_covar = covar_delta_method_log_alpha(inference_results.x[0], covar)
    x = [numpy.log10(inference_results.x[0]), inference_results.x[1]]
    cis = CI_asymptotical(transformed_covar, x, critical_value=1.96)
    print(cis)
