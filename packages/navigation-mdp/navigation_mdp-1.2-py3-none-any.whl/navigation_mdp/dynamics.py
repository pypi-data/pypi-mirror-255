import numpy as np
"""
How.
"""

class AbstractDynamics:

    def __init__(self, state_space):
        self.state_space = state_space
        pass

    def actions(self):
        raise NotImplementedError

    def take_action(self, state, action):
        raise NotImplementedError

    def get_next_states_distribution(self, state, action):
        raise NotImplementedError

    def infer_action(self, s1, s2):
        raise NotImplementedError

    def __call__(self, state, action):
        return self.get_next_states_distribution(state, action)

class VonNeumannDynamics(AbstractDynamics): # Von Neumann neighborhood | Four-Connected | Cardinal / X XOR Y Directions
    """
        U
        ↑
    L ← o → R
        ↓
        D
    """
    ACTIONS = ["U", "D", "L", "R"]
    OOPS_ACTIONS = {"U": ["L", "R"], "D": ["R", "L"], "L": ["D", "U"], "R": ["U", "D"]}
    NBR_LOC = {
        "U": lambda loc: (loc[0] - 1, loc[1]),
        "D": lambda loc: (loc[0] + 1, loc[1]),
        "L": lambda loc: (loc[0], loc[1] - 1),
        "R": lambda loc: (loc[0], loc[1] + 1),
    }

    def __init__(self, state_space, slip_prob=0.):
        super().__init__(state_space)
        self.slip_prob = slip_prob
        self.H, self.W = self.state_space.limits
        self.a_to_idx = {a: i for i, a in enumerate(self.ACTIONS)}

    def actions(self):
        return self.ACTIONS

    def action_idx(self, action):
        return self.a_to_idx[action]

    def _next_state(self, state, action):
        loc = state.location

        if action not in self.ACTIONS:
            raise Exception("Invalid action {}!".format(action))

        if self._is_valid_loc(self.NBR_LOC[action](loc)):
            loc_prime = self.NBR_LOC[action](loc)
        else:
            loc_prime = loc
        # print(state, action, "->", loc_prime)
        return self.state_space.loc_to_state_dict[loc_prime]

    def get_next_states_distribution(self, state, action):
        action_list = [action, ] + self.OOPS_ACTIONS[action]
        p_vals = [ 1. - self.slip_prob, ] + [ self.slip_prob ] * len(self.OOPS_ACTIONS[action])
        return [(self._next_state(state, action), p_vals[idx]) for idx, action in enumerate(action_list)]

    def take_action(self, state, action):
        if state.is_terminal():
            return state
        if self.slip_prob > np.random.random():
            action = np.random.choice(self.OOPS_ACTIONS[action])
        return self._next_state(state, action)

    def _is_valid_loc(self, loc):
        if 0 <= loc[0] < self.H and 0 <= loc[1] < self.W:
            return True
        return False

    def infer_action_by_loc(self, loc1, loc2):
        # TODO: handle self.slip_prob
        if not self._is_valid_loc(loc1) or not self._is_valid_loc(loc2):
            raise Exception("Invalid input: locations out of bound!")
        if loc1[0] == loc2[0] and loc1[1] == loc2[1]:
            raise Exception("Invalid input: action not supported!")
        if loc1[0] != loc2[0] and loc1[1] != loc2[1]:
            raise Exception("Invalid input: action not supported!")

        if loc2[0] - loc1[0] > 0:
            return "D"
        elif loc2[0] - loc1[0] < 0:
            return "U"
        elif loc2[1] - loc1[1] > 0:
            return "R"
        else: # loc2[1] - loc1[1] < 0
            return "L"

    def infer_action(self, s1, s2):
        return self.infer_action_by_loc(s1.location, s2.location)

    def loc_lst_to_a_lst(self, loc_lst):
        return [self.infer_action_by_loc(loc_lst[i], loc_lst[i+1]) for i in range(len(loc_lst)-1)] + [None,]

    def a_lst_to_loc_lst(self, loc_0, a_lst):
        loc_lst = [loc_0]
        loc = loc_0
        for a in a_lst:
            loc = self.take_action(self.state_space.loc_to_state_dict[loc], a).location
            loc_lst.append(loc)
        return loc_lst


class MooreDynamics(VonNeumannDynamics): # Moore neighborhood | Eight-Connected | Compass Directions
    """
      UL U UR
       ↖ ↑ ↗
     L ← o → R
       ↙ ↓ ↘
      DL D DR
    """
    ACTIONS = ["R", "UR", "U", "UL", "L", "DL", "D", "DR"]
    OOPS_ACTIONS = {"R": ["UR", "DR"], "UR": ["U", "R"],
                    "U": ["UL", "UR"], "UL": ["L", "U"],
                    "L": ["DL", "UL"], "DL": ["D", "L"],
                    "D": ["DR", "DL"], "DR": ["R", "D"]}
    NBR_LOC = {
        "R": lambda loc: (loc[0], loc[1] + 1),
        "UR": lambda loc: (loc[0] - 1, loc[1] + 1),
        "U": lambda loc: (loc[0] - 1, loc[1]),
        "UL": lambda loc: (loc[0] - 1, loc[1] - 1),
        "L": lambda loc: (loc[0], loc[1] - 1),
        "DL": lambda loc: (loc[0] + 1, loc[1] - 1),
        "D": lambda loc: (loc[0] + 1, loc[1]),
        "DR": lambda loc: (loc[0] + 1, loc[1] + 1)
    }

    def infer_action_by_loc(self, loc1, loc2):
        # TODO: handle self.slip_prob
        if not self._is_valid_loc(loc1) or not self._is_valid_loc(loc2):
            raise Exception("Invalid input: locations out of bound!")
        if loc1[0] == loc2[0] and loc1[1] == loc2[1]:
            raise Exception("Invalid input: action not supported!")

        if loc2[0] == loc1[0] and loc2[1] > loc1[1]:
            return "R"
        elif loc2[0] < loc1[0] and loc2[1] > loc1[1]:
            return "UR"
        elif loc2[0] < loc1[0] and loc2[1] == loc1[1]:
            return "U"
        elif loc2[0] < loc1[0] and loc2[1] < loc1[1]:
            return "UL"
        elif loc2[0] == loc1[0] and loc2[1] < loc1[1]:
            return "L"
        elif loc2[0] > loc1[0] and loc2[1] < loc1[1]:
            return "DL"
        elif loc2[0] > loc1[0] and loc2[1] == loc1[1]:
            return "D"
        else: # if loc2[0] > loc1[0] and loc2[1] > loc1[1]:
            return "DR"
