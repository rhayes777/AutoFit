import numpy as np
import pytest

from autofit import mock
from autofit.mapper import model_mapper as mm
from autofit.optimize import grid_search as gs
from autofit.optimize import non_linear


@pytest.fixture(name="mapper")
def make_mapper():
    mapper = mm.ModelMapper()
    mapper.profile = mock.GeometryProfile
    return mapper


@pytest.fixture(name="grid_search")
def make_grid_search(mapper):
    return gs.GridSearch(model_mapper=mapper, step_size=0.1)


class TestGridSearchablePriors(object):
    def test_generated_models(self, grid_search):
        mappers = list(grid_search.models_mappers(
            grid_priors=[grid_search.variable.profile.centre_0, grid_search.variable.profile.centre_1]))

        assert len(mappers) == 100

        assert mappers[0].profile.centre_0.lower_limit == 0.0
        assert mappers[0].profile.centre_0.upper_limit == 0.1
        assert mappers[0].profile.centre_1.lower_limit == 0.0
        assert mappers[0].profile.centre_1.upper_limit == 0.1

        assert mappers[-1].profile.centre_0.lower_limit == 0.9
        assert mappers[-1].profile.centre_0.upper_limit == 1.0
        assert mappers[-1].profile.centre_1.lower_limit == 0.9
        assert mappers[-1].profile.centre_1.upper_limit == 1.0

    def test_non_grid_searched_dimensions(self, mapper):
        grid_search = gs.GridSearch(model_mapper=mapper, step_size=0.1)
        mappers = list(grid_search.models_mappers(grid_priors=[mapper.profile.centre_0]))

        assert len(mappers) == 10

        assert mappers[0].profile.centre_0.lower_limit == 0.0
        assert mappers[0].profile.centre_0.upper_limit == 0.1
        assert mappers[0].profile.centre_1.lower_limit == 0.0
        assert mappers[0].profile.centre_1.upper_limit == 1.0

        assert mappers[-1].profile.centre_0.lower_limit == 0.9
        assert mappers[-1].profile.centre_0.upper_limit == 1.0
        assert mappers[-1].profile.centre_1.lower_limit == 0.0
        assert mappers[-1].profile.centre_1.upper_limit == 1.0

    def test_tied_priors(self, grid_search):
        grid_search.variable.profile.centre_0 = grid_search.variable.profile.centre_1

        mappers = list(grid_search.models_mappers(
            grid_priors=[grid_search.variable.profile.centre_0, grid_search.variable.profile.centre_1]))

        assert len(mappers) == 10

        assert mappers[0].profile.centre_0.lower_limit == 0.0
        assert mappers[0].profile.centre_0.upper_limit == 0.1
        assert mappers[0].profile.centre_1.lower_limit == 0.0
        assert mappers[0].profile.centre_1.upper_limit == 0.1

        assert mappers[-1].profile.centre_0.lower_limit == 0.9
        assert mappers[-1].profile.centre_0.upper_limit == 1.0
        assert mappers[-1].profile.centre_1.lower_limit == 0.9
        assert mappers[-1].profile.centre_1.upper_limit == 1.0

        for mapper in mappers:
            assert mapper.profile.centre_0 == mapper.profile.centre_1


class MockClassContainer(object):
    def __init__(self):
        init_args = []
        fit_args = []

        class MockOptimizer(non_linear.NonLinearOptimizer):
            def __init__(self, model_mapper, name):
                super().__init__(model_mapper, name)
                init_args.append((model_mapper, name))

            def fit(self, analysis):
                fit_args.append(analysis)
                # noinspection PyTypeChecker
                return non_linear.Result(None, analysis.fit(None), None)

        class MockAnalysis(non_linear.Analysis):
            def fit(self, instance):
                return 1

            def visualize(self, instance, suffix, during_analysis):
                pass

            def log(self, instance):
                pass

        self.init_args = init_args
        self.fit_args = fit_args

        self.MockOptimizer = MockOptimizer
        self.MockAnalysis = MockAnalysis


@pytest.fixture(name="container")
def make_mock_class_container():
    return MockClassContainer()


@pytest.fixture(name="grid_search_05")
def make_grid_search_05(mapper, container):
    return gs.GridSearch(model_mapper=mapper, optimizer_class=container.MockOptimizer, step_size=0.5,
                         name="sample_name")


class TestGridNLOBehaviour(object):
    def test_calls(self, grid_search_05, container, mapper):
        result = grid_search_05.fit(container.MockAnalysis(), [mapper.profile.centre_0])

        assert len(container.init_args) == 2
        assert len(container.fit_args) == 2
        assert len(result.results) == 2

    def test_names_1d(self, grid_search_05, container, mapper):
        grid_search_05.fit(container.MockAnalysis(), [mapper.profile.centre_0])

        assert len(container.init_args) == 2
        assert container.init_args[0][1] == "sample_name/0.0"
        assert container.init_args[1][1] == "sample_name/0.5"

    def test_names_2d(self, grid_search_05, mapper, container):
        grid_search_05.fit(container.MockAnalysis(), [mapper.profile.centre_0, mapper.profile.centre_1])

        assert len(container.init_args) == 4
        assert container.init_args[0][1] == "sample_name/0.0_0.0"
        assert container.init_args[1][1] == "sample_name/0.0_0.5"
        assert container.init_args[2][1] == "sample_name/0.5_0.0"
        assert container.init_args[3][1] == "sample_name/0.5_0.5"

    def test_results(self, grid_search_05, mapper, container):
        result = grid_search_05.fit(container.MockAnalysis(), [mapper.profile.centre_0, mapper.profile.centre_1])

        assert len(result.results) == 4
        assert result.no_dimensions == 2
        assert np.equal(result.figure_of_merit_array, np.array([[1.0, 1.0],
                                                                [1.0, 1.0]])).all()

        grid_search = gs.GridSearch(model_mapper=mapper, optimizer_class=container.MockOptimizer, step_size=0.1,
                                    name="sample_name")
        result = grid_search.fit(container.MockAnalysis(), [mapper.profile.centre_0, mapper.profile.centre_1])

        assert len(result.results) == 100
        assert result.no_dimensions == 2
        assert result.figure_of_merit_array.shape == (10, 10)
