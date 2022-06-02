import numpy as np


class Actor:
    def __init__(self, number_actions, q_values=None, initial_q_values=None, output_file=None):
        self.number_actions = number_actions
        self.q_values = q_values if q_values is not None else {}
        self.initial_q_values = initial_q_values
        self.output_file = output_file

    def import_q_values(self, input_file):
        self.initial_q_values = np.load(input_file, allow_pickle=True)[()]

    def export_q_values(self):
        if self.output_file is not None:
            np.save(self.output_file, self.q_values)

    def get_q_values(self, state):
        key = state.observation(self)

        q = self.q_values.get(key)
        if q is not None:
            return q

        if self.initial_q_values is None:
            q = np.zeros(self.number_actions).astype(np.float64)
        else:
            key2 = (key[0], ())
            q = self.initial_q_values.get(key2, np.zeros(self.number_actions).astype(np.float64))
        self.q_values[key] = q
        return q

    def update_q_values(self, state, action, q_value):
        key = state.observation(self)

        self.q_values[key][action] = q_value

        self.export_q_values()
