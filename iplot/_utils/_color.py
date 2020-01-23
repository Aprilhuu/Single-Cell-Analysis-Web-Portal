import math

import numpy as np
from matplotlib.cm import get_cmap


def get_weighted_color_blend(weights: np.ndarray,
                             palette: str = 'Accent'):
    """
    Given weights on each categories, get a weighted color for each point
    :param weights: a 2D numpy array in form of numb_obs * num_categories
    :param palette: the color palette name in matplotlib's color maps
    :return: a 2D numpy array in form of num_obs * (r, g, b)
    """
    num_categories = weights.shape[1]
    cmap = get_cmap(name=palette)
    if cmap is None:
        cmap = get_cmap(name='Accent')
    colors = cmap.colors
    colors *= math.ceil(num_categories / len(colors))
    colors = np.array(colors)
    colors = colors[np.linspace(0, len(colors) - 1, num_categories).astype(int), :]
    weights = weights / (weights.sum(axis=1)[:, np.newaxis] + 1e-3)
    c = (np.dot(weights, colors) * 255).astype(np.uint8)
    return c
