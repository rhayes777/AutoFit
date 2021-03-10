import autofit as af
from autofit import database as db


def test_is_complete(
        gaussian_1,
        aggregator
):
    assert aggregator.query(
        aggregator.is_complete
    ) == [gaussian_1]


class NovelClass:
    def __init__(self, argument: float):
        self.argument = argument


def test_():
    model = af.PriorModel(
        NovelClass
    )
    model.argument = af.UniformPrior()
    instance = model.instance_from_prior_medians()
    print(instance.argument)


def test_is_not_complete(
        gaussian_2,
        aggregator
):
    assert aggregator.query(
        ~aggregator.is_complete
    ) == [gaussian_2]


def test_call(
        gaussian_1,
        aggregator
):
    assert aggregator(
        aggregator.is_complete
    ) == [gaussian_1]


def test_completed_only(
        gaussian_1,
        session
):
    aggregator = db.Aggregator.from_database(
        '',
        completed_only=True
    )
    aggregator.session = session
    assert aggregator == [gaussian_1]


def test_query_dataset(
        gaussian_1,
        gaussian_2,
        aggregator
):
    assert aggregator.query(
        aggregator.dataset_name == "dataset 1"
    ) == [gaussian_1]
    assert aggregator.query(
        aggregator.dataset_name == "dataset 2"
    ) == [gaussian_2]
    assert aggregator.query(
        aggregator.dataset_name.contains(
            "dataset"
        )
    ) == [gaussian_1, gaussian_2]


def test_combine(
        aggregator,
        gaussian_1
):
    assert aggregator.query(
        (aggregator.dataset_name == "dataset 1") & (aggregator.centre == 1)
    ) == [gaussian_1]
    assert aggregator.query(
        (aggregator.dataset_name == "dataset 2") & (aggregator.centre == 1)
    ) == []
    assert aggregator.query(
        (aggregator.dataset_name == "dataset 1") & (aggregator.centre == 2)
    ) == []


def test_combine_attributes(
        aggregator,
        gaussian_1,
        gaussian_2
):
    assert aggregator.query(
        (aggregator.dataset_name == "dataset 1") & (aggregator.phase_name == "phase")
    ) == [gaussian_1]
    assert aggregator.query(
        (aggregator.dataset_name == "dataset 2") & (aggregator.phase_name == "phase")
    ) == [gaussian_2]
    assert aggregator.query(
        (aggregator.dataset_name == "dataset 1") & (aggregator.phase_name == "face")
    ) == []
