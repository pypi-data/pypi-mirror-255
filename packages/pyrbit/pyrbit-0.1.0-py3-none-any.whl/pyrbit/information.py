from pyrbit.ef import (
    identify_ef_from_recall_sequence,
    ef_ddq0_dalpha_dalpha_sample,
    ef_ddq0_dalpha_dbeta_sample,
    ef_ddq0_dbeta_dbeta_sample,
    ef_ddq1_dalpha_dalpha_sample,
    ef_ddq1_dalpha_dbeta_sample,
    ef_ddq1_dbeta_dbeta_sample,
    ef_dq1_dalpha_sample,
    ef_dq1_dbeta_sample,
    ef_dq0_dalpha_sample,
    ef_dq0_dbeta_sample,
    ef_observed_information_matrix,
)
from pyrbit.mle_utils import nearestPD, compute_summary_statistics_estimation

import numpy
import pandas
import seaborn
from tqdm import tqdm
import json


def get_sample_observed_information(recall, delta, k, alpha, beta):
    J_11 = 0
    J_12 = 0
    J_22 = 0
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
    return J


def get_sample_J_for_sequence(recall_seq, deltas, k_vector, alpha, beta):
    J_list = []
    recall_sequence = []
    for r, d, k in zip(recall_seq, deltas, k_vector):
        J_list.append(get_sample_observed_information(r, d, k, alpha, beta))
        recall_sequence.append(r)

    return J_list, recall_sequence


def get_cumulative_J_for_sequence(recall_seq, deltas, k_vector, alpha, beta):
    J_list = []
    recall_sequence = []
    for n, (r, d, k) in enumerate(zip(recall_seq, deltas, k_vector)):
        J_list.append(
            ef_observed_information_matrix(
                recall_seq[:n], deltas[:n], alpha, beta, k_vector=k_vector[:n]
            )
        )
        recall_sequence.append(r)

    return J_list, recall_sequence


def get_sample_score(recall, delta, k, alpha, beta):
    s_1 = 0
    s_2 = 0
    if recall == 1:
        s_1 += ef_dq1_dalpha_sample(alpha, beta, k, delta)
        s_2 += ef_dq1_dbeta_sample(alpha, beta, k, delta)
    elif recall == 0:
        s_1 += ef_dq0_dalpha_sample(alpha, beta, k, delta)
        s_2 += ef_dq0_dbeta_sample(alpha, beta, k, delta)
    else:
        raise ValueError(f"recall is not either 1 or 0, but is {recall}")

    return numpy.array([s_1, s_2]).reshape(2, 1)


def get_sample_score_variance_for_sequence(recall_seq, deltas, k_vector, alpha, beta):
    J_list = []
    recall_sequence = []
    for r, d, k in zip(recall_seq, deltas, k_vector):
        score = get_sample_score(r, d, k, alpha, beta)
        J_list.append(score @ score.T)
        recall_sequence.append(r)

    return J_list, recall_sequence


def gen_hessians(
    N,
    REPETITION,
    TRUE_VALUE,
    population_model,
    play_schedule,
    subsample_sequence,
    play_schedule_args=None,
    optim_kwargs=None,
    filename=None,
    save=True,
):
    if play_schedule_args is None:
        play_schedule_args = ()

    default_optim_kwargs = {
        "method": "L-BFGS-B",
        "bounds": [(1e-5, 0.1), (0, 0.99)],
        "guess": (1e-2, 0.4),
        "verbose": False,
    }
    if optim_kwargs is None:
        pass
    else:
        default_optim_kwargs.update(optim_kwargs)

    basin_hopping = default_optim_kwargs.pop("basin_hopping", False)
    basin_hopping_kwargs = default_optim_kwargs.pop("basin_hopping", {"niter": 3})

    n_theta = len(TRUE_VALUE)
    recall_array = numpy.full((N, REPETITION), fill_value=numpy.nan)
    observed_hessians = numpy.full((n_theta**2, N, REPETITION), fill_value=numpy.nan)
    observed_scores = numpy.full((n_theta**2, N, REPETITION), fill_value=numpy.nan)
    observed_cum_hessians = numpy.full(
        (n_theta**2, N, REPETITION), fill_value=numpy.nan
    )
    estimated_parameters = numpy.full(
        (2, len(subsample_sequence), REPETITION), fill_value=numpy.nan
    )

    guess = default_optim_kwargs.pop("guess")
    verbose = default_optim_kwargs.pop("verbose")

    for repet in tqdm(range(REPETITION)):
        sequences = play_schedule(population_model, *play_schedule_args)
        J_list, recall_sequence = get_sample_J_for_sequence(*sequences, *TRUE_VALUE)
        cumJ_list, recall_sequence = get_cumulative_J_for_sequence(
            *sequences, *TRUE_VALUE
        )
        score_list, recall_sequence2 = get_sample_score_variance_for_sequence(
            *sequences, *TRUE_VALUE
        )

        recall_array[:, repet] = recall_sequence
        observed_hessians[..., repet] = numpy.array(
            [J.reshape((n_theta**2,)) for J in J_list]
        ).transpose(1, 0)
        observed_scores[..., repet] = numpy.array(
            [score.reshape((n_theta**2,)) for score in score_list]
        ).transpose(1, 0)
        observed_cum_hessians[..., repet] = numpy.array(
            [cumJ.reshape((n_theta**2,)) for cumJ in cumJ_list]
        ).transpose(1, 0)

        for ni, i in enumerate(subsample_sequence):
            idx = int(i)
            inference_results = identify_ef_from_recall_sequence(
                *[_input[:idx] for _input in sequences],
                guess=guess,
                verbose=verbose,
                optim_kwargs=default_optim_kwargs,
                basin_hopping=basin_hopping,
                basin_hopping_kwargs=basin_hopping_kwargs,
            )
            estimated_parameters[:, ni, repet] = inference_results.x
    json_data = {
        "recall_array": recall_array.tolist(),
        "observed_hessians": observed_hessians.tolist(),
        "observed_score": observed_scores.tolist(),
        "observed_cum_hessians": observed_cum_hessians.tolist(),
        "estimated_parameters": estimated_parameters.tolist(),
    }
    if filename is None:
        return json_data, filename
    if save:
        with open(filename, "w") as _file:
            json.dump(json_data, _file)

    return json_data, filename


def compute_observed_information(
    observed_hessians,
    axs=None,
    observed_information_kwargs=None,
):
    default_observed_information_kwargs = {
        "label": "Average Sample Fisher information",
    }
    if observed_information_kwargs is not None:
        default_observed_information_kwargs.update(observed_information_kwargs)

    cum_color = default_observed_information_kwargs.pop("cum_color", "red")

    fischer_cumulative = default_observed_information_kwargs.pop("cumulative", True)

    N = observed_hessians.shape[1]
    n = int(numpy.sqrt(observed_hessians.shape[0]))

    information = numpy.zeros((N,))
    cum_inf = numpy.zeros((N,))
    mean_observed_information = numpy.mean(observed_hessians, axis=2)
    mean_observed_information = mean_observed_information.transpose(1, 0)

    for ni, i in enumerate(mean_observed_information):
        try:
            information[ni] = numpy.sqrt(numpy.linalg.det(nearestPD(i.reshape(n, n))))
        except:
            print("warning -- could not compute information properly")
            information[ni] = 0

    for ni, i in enumerate(mean_observed_information):
        try:
            cum_inf[ni] = numpy.sqrt(
                numpy.linalg.det(
                    nearestPD(
                        numpy.sum(mean_observed_information[:ni, :], axis=0).reshape(
                            n, n
                        )
                    )
                )
            )
        except:
            print("warning -- could not compute information properly")
            cum_inf[ni] = 0

    if axs is None:
        return mean_observed_information, information, cum_inf

    seaborn.regplot(
        x=list(range(1, N + 1)),
        y=information,
        fit_reg=False,
        scatter=True,
        ci=None,
        ax=axs,
        label="Sample Fisher information",
    )

    seaborn.regplot(
        x=list(range(1, N + 1)),
        y=information,
        fit_reg=False,
        scatter=True,
        ax=axs,
        **default_observed_information_kwargs,
    )

    if fischer_cumulative:
        _ax = axs.twinx()

        _ax.set_ylabel("Sequence Fisher information", color=cum_color)
        _ax.tick_params(axis="y", labelcolor=cum_color)
        _ax.set_yscale("linear")
        _ax.plot(
            list(range(1, N + 1)),
            cum_inf,
            label="Sequence Fisher information",
            color=cum_color,
        )

    axs.set_xlabel("N")
    axs.set_ylabel("Observed Information")
    axs.legend()
    _ax.legend()
    return mean_observed_information, information, cum_inf, axs


def compute_full_observed_information(
    TRUE_VALUE,
    recall_array,
    observed_hessians,
    estimated_parameters,
    subsample_sequence,
    axs=None,
    recall_kwargs=None,
    observed_information_kwargs=None,
    bias_kwargs=None,
    std_kwargs=None,
):
    """
    recall_array.shape = (REPET, N)

    """
    default_recall_kwargs = {
        "fit_reg": False,
        "ci": None,
        "label": "estimated probabilities",
    }
    if recall_kwargs is not None:
        default_recall_kwargs.update(recall_kwargs)

    n = len(TRUE_VALUE)

    if axs is None:
        mean_observed_information = numpy.mean(observed_hessians, axis=2)
        mean_observed_information2 = mean_observed_information.transpose(1, 0)
        agg_data, df = compute_summary_statistics_estimation(
            estimated_parameters, subsample_sequence, TRUE_VALUE, ax=None
        )
        return mean_observed_information, agg_data, df

    X = numpy.ones((recall_array.shape))
    X = numpy.cumsum(X, axis=1)
    seaborn.regplot(
        x=X.ravel(),
        y=recall_array.ravel(),
        scatter=True,
        fit_reg=False,
        ci=None,
        ax=axs[0],
        label="events",
    )

    seaborn.regplot(
        x=X.ravel(), y=recall_array.ravel(), ax=axs[0], **default_recall_kwargs
    )

    _ax = axs[1]
    mean_observed_information, information, cum_inf, _ax = compute_observed_information(
        observed_hessians,
        axs=_ax,
        observed_information_kwargs=observed_information_kwargs,
    )
    agg_data, df, _axs = compute_summary_statistics_estimation(
        estimated_parameters,
        subsample_sequence,
        TRUE_VALUE,
        ax=[axs[2], axs[3]],
        bias_kwargs=bias_kwargs,
        std_kwargs=std_kwargs,
    )

    axs[0].set_ylim([-0.05, 1.05])
    axs[0].set_xlabel("N")
    axs[0].set_ylabel("Recalls")
    axs[0].legend()

    return (
        mean_observed_information,
        agg_data,
        information,
        cum_inf,
    )


if __name__ == "__main__":
    # [information-start]
    from pyrbit.ef import ExponentialForgetting
    from pyrbit.information import gen_hessians, compute_full_observed_information

    import matplotlib.pyplot as plt

    ALPHA_TRUE = 1e-2
    BETA_TRUE = 4e-1
    SEED = 999
    rng = numpy.random.default_rng(seed=SEED)
    REPETITION = 1000
    SUBSAMPLE = 15  # use a subsample such that N/subsample is integer. A ratio of 10 as used here should be fine for most cases.
    N = 150
    subsample_sequence = numpy.logspace(0.5, numpy.log10(N), int(N / SUBSAMPLE))

    # IID schedule --- This is what you want to modify to evaluate a different schedule
    def play_iid_schedule(ef, N):
        k_vector = rng.integers(low=-1, high=10, size=N)
        deltas = rng.integers(low=1, high=5000, size=N)
        recall_probs = simulate_arbitrary_traj(ef, k_vector, deltas)
        recall = [rp[0] for rp in recall_probs]
        k_repetition = [k for k in k_vector]
        return recall, deltas, k_repetition

    # helpfer function
    def simulate_arbitrary_traj(ef, k_vector, deltas):
        recall = []
        for k, d in zip(k_vector, deltas):
            ef.update(0, 0, N=(k + 1))
            recall.append(ef.query_item(0, d))
        return recall

    ef = ExponentialForgetting(1, ALPHA_TRUE, BETA_TRUE, seed=SEED)
    play_schedule = play_iid_schedule
    play_schedule_args = (N,)

    optim_kwargs = {
        "method": "L-BFGS-B",
        "bounds": [(1e-5, 0.1), (0, 0.99)],
        "guess": (1e-3, 0.7),
        "verbose": False,
    }
    filename = None  # change if you want to save the data (json)
    json_data, _ = gen_hessians(
        N,
        REPETITION,
        [ALPHA_TRUE, BETA_TRUE],
        ef,
        play_schedule,
        subsample_sequence,
        play_schedule_args=play_schedule_args,
        optim_kwargs=optim_kwargs,
        filename=filename,
    )

    # reshaping the output of gen_hessians
    recall_array = numpy.asarray(json_data["recall_array"])
    observed_hessians = numpy.asarray(json_data["observed_hessians"])
    observed_cum_hessians = numpy.asarray(json_data["observed_cum_hessians"])
    estimated_parameters = numpy.asarray(json_data["estimated_parameters"])
    recall_array = recall_array.transpose(1, 0)

    # parameters for the information plots
    recall_kwargs = {
        "x_bins": 10,
    }
    observed_information_kwargs = {"x_bins": 10, "cum_color": "orange"}

    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(20, 15))

    (
        fischer_information,
        agg_data,
        cumulative_information,
        cum_inf,
    ) = compute_full_observed_information(
        [ALPHA_TRUE, BETA_TRUE],
        recall_array,
        observed_hessians,
        estimated_parameters,
        subsample_sequence,
        axs=axs.ravel(),
        recall_kwargs=recall_kwargs,
        observed_information_kwargs=observed_information_kwargs,
        bias_kwargs=None,
        std_kwargs=None,
    )

    plt.tight_layout(w_pad=2, h_pad=2)
    plt.show()
