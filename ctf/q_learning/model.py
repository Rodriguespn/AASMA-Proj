import numpy as np


class Model:
    def __init__(self, initial, alpha=0.3, gamma=0.9, eps=0.15):
        self.state = initial
        self.alpha = alpha
        self.gamma = gamma
        self.eps = eps

    def e_greedy(self, actor):
        q = actor.get_q_values(self.state)
        if np.random.uniform() < self.eps:
            return np.random.randint(len(q))

        policy = np.isclose(q, q.min())
        policy = policy / policy.sum()
        return np.random.choice(len(q), p=policy)

    def q_learning(self, actor, action, cost, next_state):
        q_values = actor.get_q_values(self.state)
        next_q_values = actor.get_q_values(next_state)
        return q_values[action] + self.alpha * (cost + self.gamma * next_q_values.min() - q_values[action])

    def run(self):
        actors = self.state.get_actors()
        actions = np.array([self.e_greedy(actor) for actor in actors])

        next_state = self.state.copy()
        next_actors = next_state.get_actors()
        next_state.apply_actions(list(zip(next_actors, actions)))
        next_state.update_before()

        for actor, action in zip(actors, actions):
            actor.update_q_values(self.state, action, self.q_learning(
                actor,
                action,
                self.state.cost(actor, action),
                next_state
            ))

        self.state = next_state

        self.state.update_after()
