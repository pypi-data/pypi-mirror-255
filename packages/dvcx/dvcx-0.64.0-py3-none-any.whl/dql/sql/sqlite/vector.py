import json

import numpy as np
from scipy.spatial import distance


def euclidean_distance(a: str, b: str):
    a_np = np.array(json.loads(a))
    b_np = np.array(json.loads(b))

    return np.linalg.norm(b_np - a_np)


def cosine_distance(a: str, b: str):
    return distance.cosine(json.loads(a), json.loads(b))
