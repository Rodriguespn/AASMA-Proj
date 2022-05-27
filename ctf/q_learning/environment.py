class Environment:
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def get_actors(self):
        raise NotImplementedError

    def cost(self, actor, action):
        raise NotImplementedError

    def apply_actions(self, actions):
        raise NotImplementedError

    def update_before(self):
        raise NotImplementedError

    def update_after(self):
        raise NotImplementedError
