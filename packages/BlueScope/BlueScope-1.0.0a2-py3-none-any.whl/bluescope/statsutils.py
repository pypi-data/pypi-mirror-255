import scipy.stats as st


def calculate_sample_size(confidence_level: float = .90, margin_of_error: float = 0.10, p: float = 0.5):
    """
    Estimate the sample size needed to achieve a desired confidence level and margin of error
    :param confidence_level:
    :param margin_of_error:
    :param p:
    :return:
    """
    z_score = st.norm.ppf(1 - (1 - confidence_level) / 2)
    sample_size = (z_score ** 2 * p * (1 - p)) / (margin_of_error ** 2)
    return round(sample_size)


def find_significance(mean_a: float, mean_b: float, std_a: float, std_b: float, n_a: int, n_b: int):
    """
    Test if the performance of two groups is significantly different
    :param mean_a:
    :param mean_b:
    :param std_a:
    :param std_b:
    :param n_a:
    :param n_b:
    :return:
    """
    t_stat, p_value = st.ttest_ind_from_stats(mean1=mean_a, std1=std_a, nobs1=n_a,
                                              mean2=mean_b, std2=std_b, nobs2=n_b,
                                              equal_var=False)  # Welch's t-test
    return t_stat, p_value