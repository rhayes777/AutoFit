import numpy as np
import pytest
from scipy import stats

from autofit import graphical as g


def normal_loglike(x, centre, precision, _variables=None):
    diff = np.asanyarray(x) - centre
    se = np.square(diff)
    loglike = np.sum(-precision * se - np.log(2 * np.pi) + np.log(precision)) / 2
    if _variables is not None:
        grad = ()
        for v in _variables:
            if v == 'x':
                grad += -precision * diff,
            elif v == 'centre':
                grad += np.sum(precision * diff),
            elif v == 'precision':
                grad += np.sum(1 / precision - se) / 2,

        return loglike, grad
    return loglike


def normal_loglike_t(x, centre, precision, _variables=None):
    # Make log transform of precision so that optimisation is unbounded
    _precision = np.exp(precision)
    val = normal_loglike(
        x, centre, _precision, _variables=_variables)
    if _variables is not None:
        loglike, grad = val
        grad = tuple(
            g * _precision if v == 'precision' else g
            for v, g in zip(_variables, grad)
        )
        return loglike, grad
    return val


n = 10


@pytest.fixture(
    name="centres"
)
def make_centres():
    mu = .5
    sigma = 0.5
    centre_dist = stats.norm(loc=mu, scale=sigma)

    return centre_dist.rvs(n)


@pytest.fixture(
    name="widths"
)
def make_widths():
    a = 10
    b = 4000
    precision_dist = stats.invgamma(a, scale=b)

    return precision_dist.rvs(n) ** -0.5


def compute_posteriors(
        centres
):
    mu0 = centres.mean()
    lambda0 = n
    alpha0 = n / 2
    beta0 = centres.var() / 2 * n

    # Marginal Posterior Distributions from Normal-Gamma distributions
    posterior_mean = stats.t(
        alpha0 * 2, loc=mu0,
        scale=np.sqrt(beta0 / alpha0 / lambda0))
    posterior_x = stats.t(
        alpha0 * 2, loc=mu0,
        scale=np.sqrt(beta0 / alpha0))
    posterior_t = stats.gamma(alpha0, scale=1 / beta0)

    t_mode = (alpha0 - 1) / beta0
    t_cov = beta0 ** 2 / (alpha0 - 1)

    x = np.linspace(-1.5, 2.5, 200)


@pytest.fixture(
    name="model"
)
def define_model(
        centres,
        widths
):
    centres_ = [g.Variable(f'x_{i}') for i in range(n)]
    mu_ = g.Variable('mu')
    logt_ = g.Variable('logt')

    centre_likelihoods = [
        g.NormalMessage(c, w).as_factor(x)
        for c, w, x in zip(centres, widths, centres_)
    ]
    normal_likelihoods = [
        g.FactorJacobian(
            normal_loglike_t, x=centre, centre=mu_, precision=logt_)
        for centre in centres_
    ]

    model = g.utils.prod(centre_likelihoods + normal_likelihoods)

    model_approx = g.EPMeanField.from_approx_dists(
        model,
        {
            mu_: g.NormalMessage(0, 10),
            logt_: g.NormalMessage(0, 10),
            **{
                x_: g.NormalMessage(0, 10) for x_ in centres_
            },
        }
    )

    return model_approx


def test(model):
    print(model)