# strategy/generate_random_strategy.py
import numpy as np

def generate_random_strategy(data):
    np.random.seed(42)
    data['strategy'] = np.random.choice([1, 0, -1], size=len(data))
    return data
