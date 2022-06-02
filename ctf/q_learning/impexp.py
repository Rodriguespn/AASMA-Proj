import numpy as np


class ImpExp:
    def __init__(self, input_file=None, output_file=None, initial_q_values=None, transformation=None):
        self.output_file = output_file
        self.transformation = transformation

        if input_file is not None:
            self.initial_q_values = np.load(input_file, allow_pickle=True)[()]
        else:
            self.initial_q_values = initial_q_values

    def export_q_values(self, actor):
        if self.output_file is not None:
            np.save(self.output_file, actor.q_values)

    def get_q_values(self, actor, key):
        if self.initial_q_values is None:
            return np.zeros(actor.number_actions).astype(np.float64)

        key2 = self.transformation(key)

        return self.initial_q_values.get(key2, np.zeros(actor.number_actions).astype(np.float64))
