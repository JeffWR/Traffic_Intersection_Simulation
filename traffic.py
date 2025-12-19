import time
import unittest
from unittest.mock import patch
class Lane:
    def __init__(self, direction, lane_type):
        self.direction = direction
        self.lane_type = lane_type

class SignalPhase:
    def __init__(self, green_time, yellow_time):
        self.green_time = green_time
        self.yellow_time = yellow_time
        self.red_time = 0

class TrafficLight:
    def __init__(self, signal_phase: SignalPhase):
        self.signal_phase = signal_phase
        self.state = 'RED'
        self.timer = signal_phase.red_time

    def update(self):
        self.timer -= 1
        if self.timer < 0:
            self.__advance_state()

    def __advance_state(self):
        if self.state == 'RED':
            self.state = 'GREEN'
            self.timer = self.signal_phase.green_time
        elif self.state == 'GREEN':
            self.state = 'YELLOW'
            self.timer = self.signal_phase.yellow_time
        elif self.state == 'YELLOW':
            self.state = 'RED'
            self.timer = self.signal_phase.red_time


class IntersectionController:
    def __init__(self, all_red_time=4):
        self.all_red_time = all_red_time
        self.time_in_all_red = 0
        self.timer = 0
        self.lights = {}
        self.current_group = 0
        self.current_group_phase = []

    def add_light(self, direction, lane_type, signal_phase):
        self.lights[(direction, lane_type)] = TrafficLight(signal_phase)
        self.current_group_phase.append([(direction, lane_type)])

    def update(self):
        if self.time_in_all_red > 1:
            self.time_in_all_red -= 1
            return

        for key, light in self.lights.items():
            if key in self.current_group_phase[self.current_group]:
                light.update()
            else:
                if light.state != 'RED':
                    light.state = 'RED'

        if all(self.lights[key[0]].state == 'RED' and self.lights[key[0]].timer == 0 for key in self.current_group_phase):
            self.current_group = (self.current_group + 1) % len(self.current_group_phase)
            self.time_in_all_red = self.all_red_time

    def print_status(self):
        status_display = f"[{self.timer//60:02}:{self.timer % 60:02}]:"
        for key in sorted(self.lights,reverse=True):
            status_display += (f"{"," if status_display[-1:]!=":" else ""} {key[0]} "
                               f"{"through lanes" if key[1] == "through" else "Left-turn"}: "
                               f"{self.lights[key].state} ({self.lights[key].timer}s)")
        print(status_display)

    def update_timer(self):
        self.timer += 1

    def sort_lights(self):
        self.current_group_phase.sort(reverse=True)

    def simulate(self, run_time):
        through_green_time = int(input("How many seconds does the GREEN signal for through lane last: "))
        through_yellow_time = int(input("How many seconds does the YELLOW signal for through lane last: "))
        left_green_time = int(input("How many seconds does the GREEN signal for left-turn lane last: "))
        left_yellow_time = int(input("How many seconds does the YELLOW signal for left-turn lane last: "))

        phase_through = SignalPhase(green_time=through_green_time, yellow_time=through_yellow_time)
        phase_left = SignalPhase(green_time=left_green_time, yellow_time=left_yellow_time)

        while True:
            flag = input("Add a lanes to the traffic system: 'n' for no, 'y' for yes: ")
            if flag == 'n':
                break
            elif flag == 'y':
                direction = input("Which direction: 'NS' for North-South, 'EW' for East-West: ")
                lane_type = input("Which lane type: 'through' for through lanes, 'left-turn' for left-turn lanes: ")
                self.add_light(direction, lane_type, phase_through if lane_type == 'through' else phase_left)
                print("----------Lane added successfully----------\n")
            else:
                print("Invalid input. Please try again.")
                continue
        self.sort_lights()
        for _ in range(run_time):
            self.update()
            self.print_status()
            self.update_timer()
            time.sleep(0.1)  # 0.1 as 1 second

class TestTrafficLightSystem(unittest.TestCase):
    def test_lane_initialization(self):
        lane = Lane("NS", "through")
        self.assertEqual(lane.direction, "NS")
        self.assertEqual(lane.lane_type, "through")

    def test_signal_phase_initialization(self):
        phase = SignalPhase(green_time=10, yellow_time=3)
        self.assertEqual(phase.green_time, 10)
        self.assertEqual(phase.yellow_time, 3)
        self.assertEqual(phase.red_time, 0)

    def test_traffic_light_cycle(self):
        phase = SignalPhase(green_time=3, yellow_time=2)
        light = TrafficLight(phase)

        # Initial state is RED
        self.assertEqual(light.state, "RED")

        # First update (RED to GREEN)
        light.update()
        self.assertEqual(light.state, "GREEN")
        self.assertEqual(light.timer, 3)

        # Simulate GREEN countdown
        for _ in range(4):
            light.update()
        self.assertEqual(light.state, "YELLOW")
        self.assertEqual(light.timer, 2)

        # Simulate YELLOW countdown
        for _ in range(3):
            light.update()
        self.assertEqual(light.state, "RED")

    def test_add_light_to_controller(self):
        controller = IntersectionController()
        phase = SignalPhase(green_time=4, yellow_time=2)
        controller.add_light("NS", "through", phase)

        self.assertIn(("NS", "through"), controller.lights)
        self.assertEqual(len(controller.current_group_phase), 1)

    def test_controller_update_red_reset(self):
        controller = IntersectionController()
        phase = SignalPhase(green_time=2, yellow_time=1)
        controller.add_light("NS", "through", phase)
        controller.add_light("EW", "left-turn", phase)
        # Initially all lights are RED
        for light in controller.lights.values():
            self.assertEqual(light.state, "RED")
        # Simulate a few cycles
        for _ in range(10):
            controller.update()
        # Check states are within expected set
        for light in controller.lights.values():
            self.assertIn(light.state, ['RED', 'GREEN', 'YELLOW'])

    def test_controller_print_status(self):
        controller = IntersectionController()
        phase = SignalPhase(green_time=3, yellow_time=2)
        controller.add_light("NS", "through", phase)
        with patch('builtins.print') as mocked_print:
            controller.print_status()
            mocked_print.assert_called()

if __name__ == "__main__":
    controller = IntersectionController()
    controller.simulate(300)
    #unittest.main()
