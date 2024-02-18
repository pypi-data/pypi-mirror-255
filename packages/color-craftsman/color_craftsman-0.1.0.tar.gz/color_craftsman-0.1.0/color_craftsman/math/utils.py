import numpy as np


def generate_evenly_spaced_points_on_sphere(original_point, N, radius, seed=None):
    # Allow for random rotation of the sphere
    np.random.seed(seed)
    start_angle = np.random.uniform(0, 2 * np.pi)
    phi = np.linspace(start_angle, np.pi + start_angle, N)
    theta = np.linspace(start_angle, (2 * np.pi) + start_angle, N)

    x = original_point[0] + radius * np.sin(phi) * np.cos(theta)
    y = original_point[1] + radius * np.sin(phi) * np.sin(theta)
    z = original_point[2] + radius * np.cos(phi)
    points = np.array([x, y, z]).T

    return points
