from pyrbit.mem_utils import (
    experiment,
    GaussianPopulation,
    BlockBasedSchedule,
    reshape_experiment,
)
from pyrbit.ef import ExponentialForgetting

import copy
import numpy
import pandas
import scipy
from tqdm import tqdm


def run_comparative_experiment(
    population_model_one,
    population_model_two,
    schedule,
    test_blocks=None,
    replications=1,
):
    memory_models_A = [p for p in population_model_one]
    memory_models_B = [p for p in population_model_two]

    data_A = experiment(
        memory_models_A, schedule, test_blocks=test_blocks, replications=replications
    )
    data_B = experiment(
        memory_models_B, schedule, test_blocks=test_blocks, replications=replications
    )
    return data_A, data_B


def diff_eval_block_percentages(
    population_model_one,
    population_model_two,
    schedule,
    test_blocks=None,
    output_df=True,
):
    # [run-comparative-experiment-start]
    data_A, data_B = run_comparative_experiment(
        population_model_one,
        population_model_two,
        schedule,
        test_blocks=test_blocks,
        replications=1,
    )
    # [run-comparative-experiment-after]
    if test_blocks is None:
        nblocks = len(set(schedule.blocks))
    else:
        nblocks = len(test_blocks)

    recall_events_A = reshape_experiment(
        data_A, schedule.nitems, schedule.repet_trials, nblocks
    )[:, 0, ...]
    recall_events_B = reshape_experiment(
        data_B, schedule.nitems, schedule.repet_trials, nblocks
    )[:, 0, ...]
    mean_recall_A = numpy.mean(recall_events_A, axis=(2, 3))
    mean_recall_B = numpy.mean(recall_events_B, axis=(2, 3))

    if not output_df:
        return mean_recall_A, mean_recall_B

    iter_mean_recall_A = mean_recall_A[0, ...]
    iter_mean_recall_B = mean_recall_B[0, ...]
    block1 = numpy.array(
        [i for i in range(1, nblocks + 1) for p in population_model_one]
    )
    block2 = numpy.array(
        [i for i in range(1, nblocks + 1) for p in population_model_two]
    )

    df = pandas.DataFrame(
        {
            "block recall %": numpy.concatenate(
                (iter_mean_recall_A.ravel(), iter_mean_recall_B.ravel()), axis=0
            ),
            "block": numpy.concatenate((block1, block2), axis=0),
            "Condition": numpy.concatenate(
                (
                    numpy.full(block1.shape, fill_value="A"),
                    numpy.full(block1.shape, fill_value="B"),
                ),
                axis=0,
            ),
        }
    )

    return df, mean_recall_A, mean_recall_B


def get_p_value_diff(
    population_model_one,
    population_model_two,
    schedule,
    combine_pvalues="fisher",
    test_blocks=None,
    **kwargs
):
    df, mr_A, mr_B = diff_eval_block_percentages(
        population_model_one,
        population_model_two,
        schedule,
        test_blocks=test_blocks,
        output_df=True,
    )

    # import seaborn
    # import matplotlib.pyplot as plt

    # fix, ax = plt.subplots(nrows=1, ncols=1)
    # seaborn.barplot(
    #     data=df,
    #     x="block",
    #     y="block recall %",
    #     hue="Condition",
    #     errorbar="se",
    #     ax=ax,
    # )
    # plt.show()

    p = numpy.zeros(
        len(combine_pvalues),
    )
    for n, combine_pvalue in enumerate(combine_pvalues):
        if combine_pvalue in ["fisher", "stouffer"]:
            # pvalues = scipy.stats.ttest_rel(mr_A[0, :], mr_B[0, :], axis=0).pvalue[1:]
            pvalues = scipy.stats.ttest_rel(mr_A[0, ...], mr_B[0, ...], axis=1).pvalue[
                1:
            ]
            p[n] = scipy.stats.combine_pvalues(pvalues, method=combine_pvalue).pvalue

        else:
            p[n] = combine_pvalue(mr_A[0, ...], mr_B[0, ...], **kwargs)

    return p


def get_p_values_frequency(
    populations_one,
    populations_two,
    schedule,
    combine_pvalues="fisher",
    test_blocks=None,
    significance_level=0.05,
):
    if not hasattr(combine_pvalues, "__iter__"):
        combine_pvalues = [combine_pvalues]

    p_value_container = numpy.zeros((len(populations_one), len(combine_pvalues)))
    for n, (population_model_one, population_model_two) in tqdm(
        enumerate(zip(populations_one, populations_two))
    ):
        p_value_container[n, :] = get_p_value_diff(
            population_model_one,
            population_model_two,
            schedule,
            combine_pvalues=combine_pvalues,
            test_blocks=test_blocks,
        )

    positives = numpy.sum(p_value_container < significance_level, axis=0)
    positive_rate = positives / len(p_value_container)
    negative_rate = 1 - positive_rate
    return positive_rate, negative_rate, p_value_container


if __name__ == "__main__":
    from pyrbit.mem_utils import (
        BlockBasedSchedule,
        experiment,
        GaussianPopulation,
        Schedule,
    )
    from pyrbit.ef import (
        get_k_delta_schedule,
        ExponentialForgetting,
        diagnostics,
        identify_ef_from_recall_sequence,
    )

    schedule = BlockBasedSchedule(
        1,
        0,
        [200, 200, 200, 200, 2000, 86400, 200, 2000],
        repet_trials=1,
        seed=123,
        sigma_t=None,
    )

    population_model = [
        ExponentialForgetting(1, 10 ** (-2.5), 0.75, seed=None) for i in range(200)
    ]

    data = experiment(
        population_model,
        schedule,
        test_blocks=[1, 3, 5, 6, 8],
        replications=1,
    )

    # [diff-block-percentage]

    # example with two equivalent population groups and RBITs
    population_model_one = GaussianPopulation(
        ExponentialForgetting,
        mu=[10 ** (-2.5), 0.75],
        sigma=1e-7 * numpy.array([[0.01, 0], [0, 1]]),
        population_size=24 * 16,
        n_items=1,
        seed=None,
    )

    population_model_two = GaussianPopulation(
        ExponentialForgetting,
        mu=[10 ** (-2.5), 0.75],
        sigma=1e-7 * numpy.array([[0.01, 0], [0, 1]]),
        population_size=24 * 16,
        n_items=1,
        seed=None,
    )

    # L1   R1   L2   R2    L3    R3    R4   L4    R5
    #   200  1000  200   200  2000 86400 200  2000
    schedule = BlockBasedSchedule(
        1,
        15,
        [200, 200, 1000, 200, 2000, 86400, 200, 2000],
        repet_trials=1,
        seed=123,
        sigma_t=1,
    )

    # get mean recall rates, as two arrays and optionnally as a large dataframe
    df, mA, mB = diff_eval_block_percentages(
        population_model_one,
        population_model_two,
        schedule,
        test_blocks=[1, 3, 5, 6, 8],
        output_df=True,
    )

    # plot the evaluation
    import seaborn
    import matplotlib.pyplot as plt

    fix, ax = plt.subplots(nrows=1, ncols=1)
    seaborn.barplot(
        data=df,
        x="block",
        y="block recall %",
        hue="Condition",
        errorbar="se",
        ax=ax,
    )
    plt.show()

    # [power analysis]
    # Empirical Statistical power analysis
    REPETITIONS = 100

    # Case 1: Equal RBITs, should find statistical significance alpha=0.05 at 5%
    population_model_one = [
        GaussianPopulation(
            ExponentialForgetting,
            mu=[10 ** (-2), 0.75],
            sigma=1e-7 * numpy.array([[0.01, 0], [0, 1]]),
            population_size=24,
            n_items=1,
            seed=None,
        )
        for i in range(REPETITIONS)
    ]
    population_model_two = [
        GaussianPopulation(
            ExponentialForgetting,
            mu=[10 ** (-2), 0.75],
            sigma=1e-7 * numpy.array([[0.01, 0], [0, 1]]),
            population_size=24,
            n_items=1,
            seed=None,
        )
        for i in range(REPETITIONS)
    ]

    # Define here custom methods to compute p values from mean recalls
    # compute the average of p values
    def mean_pvalue(mr_A, mr_B, **kwargs):
        pvalues = scipy.stats.ttest_rel(mr_A, mr_B, axis=1).pvalue[1:]
        return numpy.mean(pvalues)

    # Bonferonni-like correction
    def bonf(mr_A, mr_B, **kwargs):
        pvalues = scipy.stats.ttest_rel(mr_A, mr_B, axis=1).pvalue[1:]
        return numpy.min(pvalues) * len(pvalues)

    # Fisher and Stouffer methods can be called by their names to trigger their scipy implementation
    pos_one, neg_one, p_container = get_p_values_frequency(
        population_model_one,
        population_model_two,
        schedule,
        combine_pvalues=["stouffer", "fisher", bonf, mean_pvalue],
        test_blocks=None,
        significance_level=0.05,
    )
    # Type 1 errors: we reject the null that there is no difference in RBITs but there was actually none
    type1error = pos_one

    # Case 2: Unequal RBITs (alpha = 10**-2.1 versus alpha = 10**-2). The rate at which the test finds significant differences is an estimate of its power
    population_model_one = [
        GaussianPopulation(
            ExponentialForgetting,
            mu=[10 ** (-2.3), 0.75],
            sigma=1e-5 * numpy.array([[0.01, 0], [0, 1]]),
            population_size=24,
            n_items=1,
            seed=None,
        )
        for i in range(REPETITIONS)
    ]
    population_model_two = [
        GaussianPopulation(
            ExponentialForgetting,
            mu=[10 ** (-2), 0.75],
            sigma=1e-5 * numpy.array([[0.01, 0], [0, 1]]),
            population_size=24,
            n_items=1,
            seed=None,
        )
        for i in range(REPETITIONS)
    ]

    pos_two, neg_two, p_container = get_p_values_frequency(
        population_model_one,
        population_model_two,
        schedule,
        combine_pvalues=["stouffer", "fisher", bonf, mean_pvalue],
        test_blocks=None,
        significance_level=0.05,
    )

    # Type 2 errors: we failed to reject the null hypothesis that there is no difference between RBITs (even though it was False)
    type2error = neg_two
