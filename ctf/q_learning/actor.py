import numpy as np


class Actor:
    def __init__(self, number_actions, q_values=None):
        self.number_actions = number_actions
        self.q_values = q_values if q_values is not None else {}

    def get_q_values(self, state):
        key = state.key()

        q = self.q_values.get(key)
        if q is not None:
            return q

        q = np.zeros(self.number_actions).astype(np.float64)
        self.q_values[key] = q
        return q

    def update_q_values(self, state, action, q_value):
        key = state.key()

        self.q_values[key][action] = q_value

        np.save("../ctf/data/simple_1_0.npy", self.q_values)
