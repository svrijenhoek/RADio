import numpy as np
from scipy.stats import entropy
from numpy.linalg import norm
import math


def opt_merge_max_mappings(dict1, dict2):
    """ Merges two dictionaries based on the largest value in a given mapping.
    Parameters
    ----------
    dict1 : Dict[Any, Comparable]
    dict2 : Dict[Any, Comparable]
    Returns
    -------
    Dict[Any, Comparable]
        The merged dictionary
    """
    # we will iterate over `other` to populate `merged`
    merged, other = (dict1, dict2) if len(dict1) > len(dict2) else (dict2, dict1)
    merged = dict(merged)

    for key in other:
        if key not in merged or other[key] > merged[key]:
            merged[key] = other[key]
    return merged

def compute_kl_divergence(s, q, alpha=0.001):
    """
    KL (p || q), the lower the better.
    alpha is not really a tuning parameter, it's just there to make the
    computation more numerically stable.
    """
    try:
        assert 0.99 <= sum(s.values()) <= 1.01
        assert 0.99 <= sum(q.values()) <= 1.01
    except AssertionError:
        print("Assertion Error")
        pass
    kl_div = 0.
    ss = []
    qq = []
    merged_dic = opt_merge_max_mappings(s, q)
    for key in sorted(merged_dic.keys()):
        q_score = q.get(key, 0.)
        s_score = s.get(key, 0.)
        ss.append((1 - alpha) * s_score + alpha * q_score)
        qq.append((1 - alpha) * q_score + alpha * s_score)
        # by contruction they cannot be both 0
        # if s_score == 0 and q_score == 0:
        #     pass
        #     # raise Exception('Something is wrong in compute_kl_divergence')
        # elif s_score == 0:
        #     ss_score = (1 - alpha) * s_score + alpha * q_score
        #     ss.append(ss_score)
        #     qq.append(q_score)
        # elif q_score == 0:
        #     qq_score = (1 - alpha) * q_score + alpha * s_score
        #     ss.append(s_score)
        #     qq.append(qq_score)
        # else:
        #     ss.append(s_score)
        #     qq.append(q_score)
    kl = entropy(ss, qq, base=2)
    jsd = JSD(ss,qq)
    return [kl, jsd]


def KL_symmetric(a, b):
    return (entropy(a, b, base=2) + entropy(b, a, base=2))/2


def JSD(P, Q):
    _P = P / norm(P, ord=1)
    _Q = Q / norm(Q, ord=1)
    _M = 0.5 * (_P + _Q)
    # return 0.5 * (KL(_P, _M) + KL(_Q, _M))
    # added the abs to catch situations where the disocunting causes a very small <0 value, check this more!!!!
    try:
        jsd_root = math.sqrt(abs(0.5 * (entropy(_P, _M, base=2) + entropy(_Q, _M, base=2))))
    except ZeroDivisionError:
        print(P)
        print(Q)
        print()
        jsd_root = None
    return jsd_root
