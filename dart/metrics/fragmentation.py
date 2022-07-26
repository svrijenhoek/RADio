import numpy as np
from dart.external.discount import harmonic_number
from dart.external.kl_divergence import compute_kl_divergence


class Fragmentation:
    """
    Class that calculates to what extent users have seen the same news stories.
    A "story" is considered a set of articles that are about the same 'event'.
    """

    def __init__(self):
        pass

    def compute_distr(self, items, adjusted=False):
        """Compute the genre distribution for a given list of Items."""
        n = len(items)
        sum_one_over_ranks = harmonic_number(n)
        count = 0
        distr = {}
        for indx, item in enumerate(items):
            rank = indx + 1
            story_freq = distr.get(item, 0.)
            distr[item] = story_freq + 1 * 1 / rank / sum_one_over_ranks if adjusted else story_freq + 1 * 1 / n
            count += 1

        return distr

    def calculate(self, sample, recommendation):
        with_discount = []
        without_discount = []
        stories_x = recommendation.story.tolist()
        for y in sample:
            try:
                stories_y = y.story.tolist()
                values = self.compare_recommendations(stories_x, stories_y)
                if values:
                    with_discount.append(values[0])
                    without_discount.append(values[1])
            except AttributeError:
                pass
        means_with_discount = [np.mean([f[0] for f in with_discount]), np.mean([f[1] for f in with_discount])]
        means_without_discount = [np.mean([f[0] for f in without_discount]), np.mean([f[1] for f in without_discount])]
        return [means_with_discount, means_without_discount]

    def compare_recommendations(self, x, y):
        if x and y:
            # output = rbo(x, y, 0.9)
            freq_x = self.compute_distr(x, adjusted=True)
            freq_y = self.compute_distr(y, adjusted=True)
            divergence_with_discount = compute_kl_divergence(freq_x, freq_y)

            freq_x = self.compute_distr(x, adjusted=False)
            freq_y = self.compute_distr(y, adjusted=False)
            divergence_without_discount = compute_kl_divergence(freq_x, freq_y)
            # xy = compute_kl_divergence(freq_x, freq_y)
            # yx = compute_kl_divergence(freq_y, freq_x)
            # kl = 1/2*(xy[0] + yx[0])
            # jsd = 1/2*(xy[1] + yx[1])
            return [divergence_with_discount, divergence_without_discount]
        else:
            return
