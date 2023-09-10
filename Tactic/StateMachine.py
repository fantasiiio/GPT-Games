class StateMachine:
    def __init__(self):
        self.state = 'IDLE'
        self.transitions = {}
        self.enter_actions = {}
        self.exit_actions = {}

    def add_transition(self, from_state, to_state, condition_func):
        self.transitions[(from_state, to_state)] = condition_func

    def set_enter_action(self, state, action):
        self.enter_actions[state] = action

    def set_exit_action(self, state, action):
        self.exit_actions[state] = action

    def set_state(self, new_state):
        if (self.state, new_state) in self.transitions:
            condition = self.transitions[(self.state, new_state)]
            if condition():
                # Call the exit action for the current state
                if self.state in self.exit_actions:
                    self.exit_actions[self.state]()
                self.state = new_state
                # Call the enter action for the new state
                if new_state in self.enter_actions:
                    self.enter_actions[new_state]()

    def get_state(self):
        return self.state
