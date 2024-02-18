import numpy
from abc import ABC, abstractmethod


class MemoryModel:
    def __init__(self, nitems, seed=None, **kwargs):
        self.nitems = nitems
        self.rng = numpy.random.default_rng(seed=seed)

    @abstractmethod
    def update(self, item, time):
        raise NotImplementedError

    @abstractmethod
    def compute_probabilities(self, time=None):
        raise NotImplementedError

    def query_item(self, item, time):
        prob = self.compute_probabilities(time=time)[item]
        return (self.rng.random() < prob, prob)


class GaussianPopulation:
    """A Population where parameters are sampled according to a Gaussian.

    You can iterate over this object until you have used up all its pop_size members.
    """

    def __init__(
        self,
        model,
        mu,
        sigma,
        population_size=1,
        n_items=1,
        seed=None,
        **kwargs,
    ):
        self.pop_size = population_size
        self.seed = numpy.random.SeedSequence(seed)
        self.n_items = n_items
        self.kwargs = kwargs
        self.rng = numpy.random.default_rng(seed=self.seed)
        self.model = model

        self.mu = mu
        self.sigma = sigma

    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter < self.pop_size:
            self.counter += 1
            theta = self.rng.multivariate_normal(self.mu, self.sigma)

            return self.model(
                self.n_items,
                *theta,
                seed=self.seed.spawn(1)[0],
                **self.kwargs,
            )
        raise StopIteration

    def __len__(self):
        return self.pop_size


def run_trials(
    memory_model, schedule, reset=True, test_blocks=None, get_time_info=False
):
    if test_blocks is None:
        return _trial(memory_model, schedule, reset=reset, get_time_info=get_time_info)
    else:
        return _trial_test_blocks(
            memory_model,
            schedule,
            test_blocks,
            reset=reset,
            get_time_info=get_time_info,
        )


def _trial(memory_model, schedule, reset=True, get_time_info=False):
    """trial applies a schedule to a memory model and gathers queries


    :param memory_model: The memory model that will be queried from
    :type memory_model: inherits from MemoryModel
    :param schedule: schedule of interrogations
    :type schedule: inherits from Schedule
    :return: (queries, memory_model), where queries = [(good recall?, recall_probability)]
    :rtype: list(tuple(boolean, float))
    """
    queries = []
    times = []
    if reset:
        memory_model.reset()
    for item, time in schedule:
        query = memory_model.query_item(item, time)
        queries.append(query)
        memory_model.update(item, time)
        times.append(time)

    if get_time_info:
        return queries, memory_model, times

    return queries, memory_model


def _trial_test_blocks(
    memory_model, schedule, test_blocks, reset=True, get_time_info=False
):
    queries = []
    times = []
    if reset:
        memory_model.reset()
    for n, (item, time) in enumerate(schedule):
        if (
            int(n / (schedule.nitems * schedule.repet_trials)) in test_blocks
        ):  # if recall block
            query = memory_model.query_item(item, time)
            queries.append(query)
            times.append(time)
            if query[0]:
                memory_model.update(item, time)
        else:  # if learning block
            memory_model.update(item, time)

    if get_time_info:
        return queries, memory_model, times
    return queries, memory_model


def experiment(
    population_model,
    schedule,
    replications=1,
    test_blocks=None,
    reset=True,
    get_trial_info=False,
):
    if test_blocks is None:
        schedule_length = len(schedule)
    else:
        schedule_length = len(test_blocks) * schedule.nitems * schedule.repet_trials

    data = numpy.zeros(
        (
            replications,
            2,
            schedule_length,
            len(population_model),
        )
    )
    trial_info = numpy.zeros(
        (
            replications,
            2,
            schedule_length,
            len(population_model),
        )
    )

    for n, memory_model in enumerate(population_model):
        for i in range(replications):
            trial_data = run_trials(
                memory_model,
                schedule,
                test_blocks=test_blocks,
                reset=True,
                get_time_info=get_trial_info,
            )
            data[i, :, :, n] = numpy.array(trial_data[0]).T
            if get_trial_info:
                trial_info[i, 0, :, n] = list(range(data.shape[2]))
                trial_info[i, 1, :, n] = trial_data[2]
    if not get_trial_info:
        return data
    return data, trial_info


def reshape_experiment(data, nitems, repet_trials, nblocks):
    _shape = data.shape
    new_shape = (_shape[0], _shape[1], nblocks, repet_trials, nitems, _shape[-1])
    return data.reshape(new_shape)


# def experiment_test_blocks(population_model, schedule, test_blocks, replications=1):
#     data = numpy.zeros(
#         (replications, schedule.nitems, 2, len(test_blocks), population_model.pop_size)
#     )

#     for n, memory_model in enumerate(population_model):
#         for i in range(replications):
#             trial_data = numpy.array(
#                 trial_test_blocks(memory_model, schedule, test_blocks)[0]
#             )
#             trial_data = trial_data.reshape(-1, schedule.nitems, 2)

#             data[i, :, :, :, n] = trial_data.transpose(1, 2, 0)
#     return data.squeeze()


class Schedule:
    """Iterate over (items, times) pairs.

    A schedule is an association between presented items and the times at which these where presented. One can iterate over a schedule to get a pair (item, time).
    """

    def __init__(self, items, times):
        """__init__ _summary_

        _extended_summary_

        :param items: item identifier
        :type items: numpy array_like
        :param times: timestamp at which item was presented to participant
        :type times: numpy array_like
        """
        self.items = items
        self.nitems = len(set(items))
        self.times = times
        self.max = numpy.array(times).squeeze().shape[0]

    def __len__(self):
        return self.max

    def __getitem__(self, item):
        return (self.items[item], self.times[item])

    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter < self.max:
            ret_value = self[self.counter]
            self.counter += 1
            return ret_value
        else:
            raise StopIteration

    def __repr__(self):
        return f"items: {self.items}\ntimes: {self.times}"


class BlockBasedSchedule(Schedule):
    def __init__(
        self,
        nitems,
        intertrial_time,
        interblock_time,
        repet_trials=1,
        seed=None,
        sigma_t=None,
    ):
        self.seed = seed
        self.rng = numpy.random.default_rng(self.seed)
        self.sigma_t = sigma_t

        self.nitems = nitems
        self.intertrial_time = intertrial_time
        self.interblock_time = interblock_time
        self.repet_trials = repet_trials if repet_trials is not None else 1

        self.items, self.times, self.blocks = self.regen_schedule()
        self.max = numpy.array(self.times).squeeze().shape[0]

    def regen_schedule(
        self, intertrial_time=None, interblock_time=None, repet_trials=None
    ):
        self.intertrial_time = (
            self.intertrial_time if intertrial_time is None else intertrial_time
        )
        self.interblock_time = (
            self.interblock_time if interblock_time is None else interblock_time
        )
        self.repet_trials = self.repet_trials if repet_trials is None else repet_trials

        items = []
        times = []
        blocks = []
        t = 0
        for nb, ibt in enumerate((self.interblock_time + [0])):
            for r in range(self.repet_trials):
                if self.sigma_t is not None:
                    _rdm = self.rng.lognormal(sigma=self.sigma_t, size=(self.nitems,))
                else:
                    _rdm = numpy.zeros((self.nitems,))
                for i, r in zip(range(self.nitems), _rdm):
                    items.append(i)
                    times.append(t)

                    t += self.intertrial_time + r
                    blocks.append(nb)
            t += ibt

        return items, times, blocks

    def print_schedule(self):
        print("item, time, block")
        for i, t, b in zip(self.items, self.times, self.blocks):
            print(i, t, b)


if __name__ == "__main__":
    # [schedule]
    from pyrbit.mem_utils import Schedule, BlockBasedSchedule

    items = [0, 1, 0, 1, 0, 1, 0, 0]
    times = [0, 100, 126, 200, 252, 500, 4844, 5877]

    # Building a schedule
    schedule = Schedule(items, times)
    # You can iterate over a schedule
    for item, time in schedule:
        print(item, time)

    # [block-schedule]
    # You can create a block based schedule, where you specify a constant intertrial time (which includes execution time), interblock times (this also implicitly specifies the number of blocks), and whether items are repeated. You can also add some randomness by adding a random time for each item, drawn from a lognormal distribution with scale sigma_t.
    schedule = BlockBasedSchedule(
        5, 5, [10, 20, 30, 30], repet_trials=2, seed=123, sigma_t=1
    )
    # you can print the schedule, which also shows block identifiers
    schedule.print_schedule()

    # [trial]
    # You can apply a schedule to a memory model and gather queries using run_trials
    from pyrbit.ef import ExponentialForgetting
    from pyrbit.mem_utils import run_trials

    ef = ExponentialForgetting(5, 0.01, 0.4, seed=123)
    queries, ef = run_trials(ef, schedule, reset=True)
    print(queries)
    print(ef.counters)

    # If you have learning blocks distinct from test blocks, you can use the test_blocks argument. This assumes that in a learning block the memory model is always updated, but not queried, while in a testing block, the memory model is always queried, and updated when that query is correct.
    queries, ef = run_trials(ef, schedule, test_blocks=[1, 3], reset=True)
    print(queries)
    print(ef.counters)

    # [population]
    # You can sample from a Gaussian population of memory models. Each memory model will have a different seed that spawns from the population's seed.
    population_model = GaussianPopulation(
        ExponentialForgetting,
        mu=[0.01, 0.4],
        sigma=1e-3 * numpy.array([[0.1, 0], [0, 1]]),
        population_size=3,
        n_items=5,
        seed=123,
    )
    # you can iterate over a population
    for p in population_model:
        print(p)

    # [experiment]
    # You can perform an experiment, by having members of the population perform trials. The data has shape (replication, 2, schedule_length, population_size); The dimension 2 is for (recall, recall_probability). Note that you can use a list of memory models rather than population objects.
    data = experiment(population_model, schedule, replications=4)

    population_model = GaussianPopulation(
        ExponentialForgetting,
        mu=[0.01, 0.4],
        sigma=1e-7 * numpy.array([[0.1, 0], [0, 1]]),
        population_size=4,
        n_items=5,
        seed=123,
    )
    data = experiment(population_model, schedule, replications=1)
    data, trials = experiment(
        population_model,
        schedule,
        replications=1,
        test_blocks=[1, 3, 4],
        get_trial_info=True,
    )
    # You can also reshape the experiment data to have shape (replication, 2, nblocks, repet_trials, nitems, population_size)
    rdata = reshape_experiment(data, 5, 2, 3)

