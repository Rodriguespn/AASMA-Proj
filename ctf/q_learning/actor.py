class Actor:
    def __init__(self, number_actions, q_values=None, impexp=None):
        self.number_actions = number_actions
        self.q_values = q_values if q_values is not None else {}
        self.impexp = impexp

    def get_q_values(self, state):
        key = state.observation(self)

        q = self.q_values.get(key)
        if q is not None:
            return q

        q = self.impexp.get_q_values(self, key)

        self.q_values[key] = q
        return q

    def update_q_values(self, state, action, q_value):
        key = state.observation(self)

        self.q_values[key][action] = q_value

        self.impexp.export_q_values(self)
