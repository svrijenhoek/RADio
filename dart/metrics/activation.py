import numpy as np
from sklearn.preprocessing import KBinsDiscretizer
from dart.external.kl_divergence import compute_kl_divergence
from dart.external.discount import harmonic_number
import warnings


class Affect:
    """
    Class that calculates the average Affect score based on absolute sentiment polarity values.
    This approach is an initial approximation of the concept, and should be refined in the future.
    Should also implement polarity analysis at index time.
    """

    def __init__(self, config):
        n_bins = 5
        self.bins_discretizer = KBinsDiscretizer(encode='ordinal', n_bins=n_bins, strategy='uniform')
        warnings.filterwarnings("ignore", category=UserWarning)

    def compute_distr(self, arr, bins_discretizer, adjusted=False):
        """
            Args:
            Return"
        """
        n = len(arr)
        sum_one_over_ranks = harmonic_number(n)
        arr_binned = bins_discretizer.transform(arr)
        distr = {}
        if adjusted:
            for bin in list(range(bins_discretizer.n_bins)):
                for indx, ele in enumerate(arr_binned[:,0]):
                    if ele == bin:
                        rank = indx + 1
                        bin_freq = distr.get(bin, 0.)
                        distr[bin] = bin_freq + 1 * 1 / rank / sum_one_over_ranks

        else:
            for bin in list(range(bins_discretizer.n_bins)):
                distr[bin] = round(np.count_nonzero(arr_binned == bin) / arr_binned.shape[0], 3)
        return distr

    def calculate(self, pool, recommendation):
        pool_affect = np.array(pool.sentiment.apply(lambda x: abs(x))).reshape(-1, 1)
        recommendation_affect = np.array(recommendation.sentiment.apply(lambda x: abs(x))).reshape(-1, 1)
        # arr_pool = np.array([abs(item.sentiment) for item in pool]).reshape(-1, 1)
        # arr_recommendation = np.array([abs(item.sentiment) for item in recommendation]).reshape(-1, 1)

        self.bins_discretizer.fit(pool_affect)
        distr_pool = self.compute_distr(pool_affect, self.bins_discretizer, False)
        distr_recommendation = self.compute_distr(recommendation_affect, self.bins_discretizer, True)
        divergence_with_discount = compute_kl_divergence(distr_pool, distr_recommendation)

        distr_recommendation = self.compute_distr(recommendation_affect, self.bins_discretizer, False)
        divergence_without_discount = compute_kl_divergence(distr_pool, distr_recommendation)
        return [divergence_with_discount, divergence_without_discount]
