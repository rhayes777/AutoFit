import autofit as af

from howtofit.chapter_2_results.src.fit import fit as f
from howtofit.chapter_2_results.src.phase import visualizer

import pickle

# The `analysis.py` module is unchanged from the previous tutorial.

class Analysis(af.Analysis):
    def __init__(self, masked_dataset, settings, image_path=None):

        # The `MaskedDataset` and visualizer are created in the same way as tutorial 4.

        self.masked_dataset = masked_dataset
        self.settings = settings

        self.visualizer = visualizer.Visualizer(
            masked_dataset=self.masked_dataset, image_path=image_path
        )

    def log_likelihood_function(self, instance):
        """
        Returns the fit of a list of Profiles (Gaussians, Exponentials, etc.) to the dataset, using a
        model instance.

        Parameters
        ----------
        instance
            The list of Profile model instance (e.g. the Gaussians, Exponentials, etc.).

        Returns
        -------
        fit : Fit.log_likelihood
            The log likelihood value indicating how well this model fit the `MaskedDataset`.
        """
        model_data = self.model_data_from_instance(instance=instance)
        fit = self.fit_from_model_data(model_data=model_data)
        return fit.log_likelihood

    def model_data_from_instance(self, instance):
        return sum(
            [
                profile.profile_from_xvalues(xvalues=self.masked_dataset.xvalues)
                for profile in instance.profiles
            ]
        )

    def fit_from_model_data(self, model_data):
        return f.FitDataset(masked_dataset=self.masked_dataset, model_data=model_data)

    def visualize(self, instance, during_analysis):

        model_data = self.model_data_from_instance(instance=instance)
        fit = self.fit_from_model_data(model_data=model_data)

        self.visualizer.visualize_fit(fit=fit, during_analysis=during_analysis)

    def save_for_aggregator(self, paths):
        """Save files like the dataset, mask and settings as pickle files so they can be loaded in the ``Aggregator``"""

        # These functions save the objects we will later access using the aggregator. They are saved via the `pickle`
        # module in Python, which serializes the data on to the hard-disk.

        with open(f"{paths.pickle_path}/dataset.pickle", "wb") as f:
            pickle.dump(self.masked_dataset.dataset, f)

        with open(f"{paths.pickle_path}/mask.pickle", "wb") as f:
            pickle.dump(self.masked_dataset.mask, f)

        with open(f"{paths.pickle_path}/settings.pickle", "wb+") as f:
            pickle.dump(self.settings, f)