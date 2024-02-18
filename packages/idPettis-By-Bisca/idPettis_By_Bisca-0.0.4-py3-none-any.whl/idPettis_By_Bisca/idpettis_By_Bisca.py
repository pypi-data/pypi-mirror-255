import numpy as np
from scipy.special import gamma
from scipy.stats import linregress


def idpettis(ydist, n, K=10):
    """
    Estimates the intrinsic dimensionality of the data using the IDPettis algorithm.

    Parameters
    ----------
    ydist : ndarray
        A 2D array containing the nearest neighbor distances for each point, sorted in ascending order.
    n : int
        The sample size.
    K : int, optional
        The maximum number of nearest neighbors to consider.

    Returns
    -------
    idhat : float
        The estimate of the intrinsic dimensionality of the data.
    """
    # Step 2: Determine all the distances r_{k, x_i}
    # Assuming ydist is already sorted and contains distances for up to K nearest neighbors

    # Step 3: Remove outliers
    m_max = np.max(ydist[:, K - 1])
    s_max = np.std(ydist[:, K - 1])
    valid_indices = np.where(ydist[:, K - 1] <= m_max + s_max)[0]
    ydist_filtered = ydist[valid_indices, :]

    # Add a small constant to avoid log(0)
    epsilon = 1e-10
    ydist_filtered = np.maximum(ydist_filtered, epsilon)  # Ensures all values are above 0

    # Step 4: Calculate log(mean(r_k))
    log_rk_means = np.log(np.mean(ydist_filtered[:, :K], axis=0))


    # Step 5: Initial estimate d0
    k_values = np.arange(1, K + 1)
    slope, _, _, _, _ = linregress(np.log(k_values), log_rk_means)
    d_hat = 1 / slope

    # Initialize variables for iteration
    d_prev = d_hat
    convergence_threshold = 1e-3
    max_iterations = 100
    iterations = 0

    while iterations < max_iterations:
        iterations += 1

        # Step 6: Calculate log(G_{k, d_hat})
        G_k_d = (k_values ** (1 / d_prev)) * gamma(k_values) / gamma(k_values + (1 / d_prev))
        log_G_k_d = np.log(G_k_d)

        # Step 7: Update estimate of intrinsic dimensionality
        combined_log = log_G_k_d + log_rk_means
        slope, _, _, _, _ = linregress(np.log(k_values), combined_log)
        d_hat = 1 / slope

        # Check for convergence
        if np.abs(d_hat - d_prev) < convergence_threshold:
            break

        d_prev = d_hat

    return d_hat


def generate_helix_data(num_points=1000):
    """
    Generates data points along a helix.

    Parameters
    ----------
    num_points : int, optional
        Number of data points to generate.

    Returns
    -------
    data : ndarray
        Data points along the helix.
    """
    theta = np.random.uniform(low=0, high=4 * np.pi, size=num_points)
    x = np.cos(theta)
    y = np.sin(theta)
    z = 0.1 * theta

    return np.vstack((x, y, z)).T

