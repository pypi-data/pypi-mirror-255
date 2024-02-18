import numpy as np
import pandas as pd


def moving_average(data, window_size):
    """ Computes moving average using discrete linear convolution of two one dimensional sequences.
        Args:
        -----
                data (pandas.Series): independent variable
                window_size (int): rolling window size

        Returns:
        --------
                ndarray of linear convolution

        References:
        ------------
        [1] Wikipedia, "Convolution", http://en.wikipedia.org/wiki/Convolution.
        [2] API Reference: https://docs.scipy.org/doc/numpy/reference/generated/numpy.convolve.html

        """
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(data, window, 'same')


def low_pass_filter_anomaly(series: 'list' = [], window_frame: 'int' = 5,
                            sigma: 'float' = 1) -> '[index, y,avg]':
    """
        :param series: (list) list of number to analize
        :param window_frame: (int) rolling window size
        :param sigma:  (float): value for standard deviation
        :rtype: list of anomaly [index, y,avg]
        """
    avg_list = moving_average(series, window_frame).tolist()
    residual = np.array(series) - np.array(avg_list)
    # Calculate the variation in the distribution of the residual
    testing_std = pd.Series(residual).rolling(window_frame).std()
    testing_std_as_df = pd.DataFrame(testing_std)
    rolling_std = testing_std_as_df.replace(np.nan,
                                            testing_std_as_df.ix[window_frame - 1]).round(3).iloc[:, 0].tolist()

    return [(index, y_i, avg_i) for index, y_i, avg_i, rs_i in
            zip(list(range(len(series))), series, avg_list, rolling_std)
            if (y_i > avg_i + (sigma * rs_i)) | (
                    y_i < avg_i - (sigma * rs_i))], avg_list, rolling_std
