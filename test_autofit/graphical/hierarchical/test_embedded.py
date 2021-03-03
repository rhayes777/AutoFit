import numpy as np
import pytest

import matplotlib.pyplot as plt

import autofit as af
from autofit import graphical as g
from autofit.mock.mock import Gaussian
from test_autofit.graphical.gaussian.model import Analysis

x = np.arange(100)
n = 3

should_plot = True


@pytest.fixture(
    name="centre_model"
)
def make_centre_model():
    return af.PriorModel(
        af.GaussianPrior,
        mean=af.GaussianPrior(
            mean=50,
            sigma=10
        ),
        sigma=af.GaussianPrior(
            mean=10,
            sigma=5
        )
    )


def test_embedded_priors(
        centre_model
):
    assert isinstance(
        centre_model.random_instance().value_for(0.5),
        float
    )


def test_hierarchical_factor(
        centre_model
):
    factor = g.HierarchicalFactor(
        centre_model,
        af.GaussianPrior(50, 10)
    )

    assert len(factor.priors) == 3

    laplace = g.LaplaceFactorOptimiser()

    gaussian = factor.optimise(laplace)
    assert gaussian.instance_from_prior_medians().mean == pytest.approx(50, abs=0.1)


@pytest.fixture(
    name="data"
)
def generate_data(
        centre_model
):
    data = []
    for _ in range(n):
        centre = centre_model.random_instance().value_for(0.5)
        gaussian = Gaussian(
            centre=centre,
            intensity=20,
            sigma=5,
        )

        data.append(
            gaussian(x)
        )
    return data


def test_generate_data(
        data
):
    if should_plot:
        for gaussian in data:
            plt.plot(x, gaussian)
        plt.show()


def test_full_fit(centre_model, data):
    graph = g.FactorGraphModel()
    for y in data:
        centre_argument = af.GaussianPrior(
            mean=50,
            sigma=20
        )
        prior_model = af.PriorModel(
            Gaussian,
            centre=centre_argument,
            intensity=20,
            sigma=5
        )
        graph.add(
            g.AnalysisFactor(
                prior_model,
                analysis=Analysis(
                    x=x,
                    y=y
                )
            )
        )
        graph.add(
            g.HierarchicalFactor(
                centre_model,
                centre_argument
            )
        )

    laplace = g.LaplaceFactorOptimiser()

    collection = graph.optimise(laplace)
    for obj in collection:
        print(obj.centre)