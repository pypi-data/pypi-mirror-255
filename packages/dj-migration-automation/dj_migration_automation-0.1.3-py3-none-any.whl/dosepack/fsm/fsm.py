#! /usr/bin/env python
"""
    fsm
    ~~~~~~~~~~~~~~~~

    This is FSM (FINITE STATE MACHINE) object. This is where we inherit most of the conveyor units.
    We implement multi-threading and finite state machine design on this object.

    Example:

    Todo:

    :copyright: (c) 2016 by Dosepack LLC.

"""
import time

# get the logger for the pack from global configuration file logging.json
# logger = logging.getLogger("root")


class FSM(object):
    FSM_STATUS_RUN = 1
    FSM_STATUS_PAUSE = 2

    def __init__(self, name):
        self.name = name                # just a name
        self.state_routine_map = {}     # a map which contains a next state and a state_routine
        self.current_state = None       # holds the current state
        self.exit_requested = False     # used to exit the thread
        self.standby = False
        self.current_status = 1

    def add_state(self, state, default_next_state, routine):
        self.state_routine_map[state] = (default_next_state, routine)

    def set_current_state(self, state):
        self.current_state = state
        if state == 'Standby':
            self.standby = True

    def start_fsm(self):
        while not self.exit_requested:
            if self.current_status == self.FSM_STATUS_RUN:
                if not len(self.state_routine_map):
                    # as long as there are some state
                    # the thread is alive
                    break

                func = self.state_routine_map[self.current_state][1]
                next_state = func()
                if next_state is not None:
                    self.current_state = next_state
                else:
                    self.current_state = self.state_routine_map[self.current_state][0]
            else:
                time.sleep(1)

    def stop(self):
        self.exit_requested = True
        self.name = ''

    def stand_by(self):
        time.sleep(1)


