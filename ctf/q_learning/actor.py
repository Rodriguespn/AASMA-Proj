import numpy as np


class Actor:
    def __init__(self, number_actions, q_values=None):
        self.number_actions = number_actions
        self.q_values = q_values if q_values is not None else {}

    def get_q_values(self, state):
        q = self.q_values.get(state)
        if q is not None:
            return q

        q = np.zeros(self.number_actions).astype(np.float64)
        self.q_values[state] = q
        return q

    def update_q_values(self, state, action, q_value):
        self.q_values[state][action] = q_value
