""" orthogonal.py

An example of orthogonal regions
"""
import sys
import unittest
import logging
import time
import enum

# setting path
sys.path.append('..')
from src.pyrarchical import hsm


class OrthogonalController:
    """ Example controller to manage continuous state for the orthogonal regions example """

    def __init__(self):
        self.action_history = []
        self.temperature = 0.0
        self.input = None

    def clear_action_history(self):
        self.action_history = []

    def record_action_history(self, action):
        self.action_history.append(action)

    def set_input(self, input):
        self.input = input


class TrackedState(hsm.State):
    """ States that record their actions in the controller for debugging and testing purposes """

    def init_action(self):
        super().init_action()
        self._controller.action_history.append(f'{self.name}_init')

    def entry_action(self):
        super().entry_action()
        self._controller.action_history.append(f'{self.name}_entry')

    def exit_action(self):
        super().exit_action()
        self._controller.action_history.append(f'{self.name}_exit')

    def during_action(self):
        super().during_action()
        self._controller.action_history.append(f'{self.name}_during')


class Events(enum.Enum):
    A = enum.auto()
    B = enum.auto()
    C = enum.auto()
    D = enum.auto()
    E = enum.auto()
    F = enum.auto()
    G = enum.auto()
    H = enum.auto()


class OrthogonalHsm(hsm.HSM):

    def __init__(self):
        # TODO: clean this up
        super().__init__()

        # First thing to do is to instantiate the controller for managing continuous state
        self._controller = OrthogonalController()

        # Add states by name
        self.add_region('left')  # HSM is implied parent
        self.add_region('right')  # orthogonal region names need to be unique across the HSM just like states
        self.add_state(TrackedState("s1"), parent='left', initial=True)
        self.add_state(TrackedState("s2"), parent='left')
        self.add_state(TrackedState("sA"), parent='right', initial=True)
        self.add_state(TrackedState("sB"), parent='right')
        self.add_region('fred', parent='s1')
        self.add_region('george', parent='s1')
        self.add_state(TrackedState("s11"), parent='fred', initial=True)
        self.add_state(TrackedState("s12"), parent='fred')
        self.add_state(TrackedState("s1X"), parent='george', initial=True)
        self.add_state(TrackedState("s1Y"), parent='george')

        # self.add_transition(source='s1', event=Events.E, target='sA') INVALID
        self.add_transition(source='sB', event=Events.A, target='sA')
        self.add_transition(source='sA', event=Events.B, target='sB')
        self.add_transition(source='s1X', event=Events.C, target='s2')
        self.add_transition(source='s1X', event=Events.D, target='s1')
        self.add_transition(source='s2', event=Events.E, target='s1')

        # TODO: clean this up
        self._initialize()


class OrthogonalTest(unittest.TestCase):

    def test_initial_conditions(self):
        orthogonal_hsm = OrthogonalHsm()

        # Active states provided as a nested dict by region
        initial_states = orthogonal_hsm.state
        self.assertEqual(initial_states['fred'].name, 's11')
        self.assertEqual(initial_states['george'].name, 's1X')
        self.assertEqual(initial_states['right'].name, 'sA')

        expected_actions = ['s1_entry', 's1_init', 's11_entry', 's1X_entry', 'sA_entry']
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

    def test_transitions(self):
        """Test that a sequence of events go to the correct states."""
        orthogonal_hsm = OrthogonalHsm()

        # Event B in state sA
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.B)
        expected_actions = ['sA_exit', 'sB_entry']
        self.assertIs(orthogonal_hsm.state['right'].name, 'sB')
        self.assertEqual(orthogonal_hsm.state['fred'].name, 's11')  # unaffected
        self.assertEqual(orthogonal_hsm.state['george'].name, 's1X')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event A in state sB
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.A)
        expected_actions = ['sB_exit', 'sA_entry']
        self.assertIs(orthogonal_hsm.state['right'].name, 'sA')
        self.assertEqual(orthogonal_hsm.state['fred'].name, 's11')  # unaffected
        self.assertEqual(orthogonal_hsm.state['george'].name, 's1X')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event C in state s1X
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.C)
        expected_actions = ['s1X_exit', 's11_exit', 's1_exit', 's2_entry']
        self.assertEqual(orthogonal_hsm.state['left'].name, 's2')
        self.assertIs(orthogonal_hsm.state['right'].name, 'sA')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event E in state s2
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.E)
        expected_actions = ['s2_exit', 's1_entry', 's1_init', 's11_entry', 's1X_entry']
        self.assertEqual(orthogonal_hsm.state['fred'].name, 's11')
        self.assertEqual(orthogonal_hsm.state['george'].name, 's1X')
        self.assertIs(orthogonal_hsm.state['right'].name, 'sA')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event D in state s1X
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.D)
        # expected_actions = ['s1X_exit', 's11_exit', 's1_exit', 's1_entry', 's1_init', 's11_entry', 's1X_entry']  # external
        expected_actions = ['s1X_exit', 's11_exit', 's1_init', 's11_entry', 's1X_entry']  # local
        self.assertEqual(orthogonal_hsm.state['fred'].name, 's11')
        self.assertEqual(orthogonal_hsm.state['george'].name, 's1X')
        self.assertIs(orthogonal_hsm.state['right'].name, 'sA')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

    def test_speed(self):
        orthogonal_hsm = OrthogonalHsm()
        self.assertIs(orthogonal_hsm.state['right'].name, 'sA')
        self.assertEqual(orthogonal_hsm.state['fred'].name, 's11')
        self.assertEqual(orthogonal_hsm.state['george'].name, 's1X')

        num_cycles = 1E3
        num_transitions = 4
        start_time = time.time()
        for idx in range(int(num_cycles)):

            # Event B in state sA
            orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
            orthogonal_hsm.dispatch(Events.B)
            self.assertIs(orthogonal_hsm.state['right'].name, 'sB')

            # Event C in state s1X
            orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
            orthogonal_hsm.dispatch(Events.C)
            self.assertEqual(orthogonal_hsm.state['left'].name, 's2')

            # Event A in state sB
            orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
            orthogonal_hsm.dispatch(Events.A)
            self.assertIs(orthogonal_hsm.state['right'].name, 'sA')

            # Event E in state s2
            orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
            orthogonal_hsm.dispatch(Events.E)
            self.assertEqual(orthogonal_hsm.state['fred'].name, 's11')
            self.assertEqual(orthogonal_hsm.state['george'].name, 's1X')

        stop_time = time.time()
        duration_ms = (stop_time - start_time) * 1E3
        print(f'Executed {int(num_cycles)} cycles of {num_transitions} in {duration_ms:.2f} ms')
        print(f'Average transition time = {duration_ms / num_cycles / num_transitions * 1E3:.2f} us')


##############################
#  Module Level Test Harness #
##############################
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Kick off all unit tests contained in the file
    unittest.main()

    # test_case = OrthogonalTest()
    # test_case.test_transitions()
