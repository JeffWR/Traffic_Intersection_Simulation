# Traffic Light Simulation
This is a Python-based simulation of a traffic light control system for an intersection. It allows you to configure lanes (through or left-turn) in different directions (NS or EW), assign signal timings, and simulate how traffic lights would operate over a fixed period.

- Define through and left-turn lanes
- Assign individual green and yellow light durations
- Automatically computes red-light times based on opposing lanes
- Manages multiple signal phases with a configurable all-red safety period
- Prints the status of all lanes every simulated second
## Class Design:
### 1.Lane
- Defined the direction and lane_type
- ! Currently not actively used in simulation logic, but available for future extensions like car movement.
```python
def __init__(self, direction, lane_type):
    self.direction = direction 
    #Direction of the lanes (NS or EW)
    self.lane_type = lane_type 
    #left-turn or through lanes
    
```
### 2.SignalPhase
- Encapsulates the time durations of a signal
- A compact way of recording time rule
```python
def __init__(self, green_time, yellow_time):
    self.green_time = green_time 
    # Custom green light time
    self.yellow_time = yellow_time 
    # Custom yellow light time
    self.red_time = 0 
    # Red indicate no time on the clock - the default state
```
### 3.TrafficLight
- Class that updates the time of a traffic light
- The class stores three different values: the phase of the lights, the state (color) of the current light, and the time display
```python
def __init__(self, signal_phase):
    self.signal_phase = signal_phase
    self.state = 'RED'
    self.timer = signal_phase.red_time
```
- The class contains one method: 'update' which update clock and state of the light
- The state of the light is written in a subfunction called '__advance_state'

```python
def update(self):
    self.timer -= 1
    # Decreasing the time
    if self.timer < 0:
        # If the clock became negative, update the color of the light
        self.__advance_state()

def __advance_state(self):
    #update the light to the next color in the cycle, reset the clock
    if self.state == 'RED':
        self.state = 'GREEN'
        self.timer = self.signal_phase.green_time
    elif self.state == 'GREEN':
        self.state = 'YELLOW'
        self.timer = self.signal_phase.yellow_time
    elif self.state == 'YELLOW':
        self.state = 'RED'
        self.timer = self.signal_phase.red_time
```
### 4.IntersectionController
- The class handles the overall control and simulation of the traffic light system,
- The class stores six different information:
  1. The All-red interval 
  2. Timer for the all-red interval
  3. A timer for the whole simulation
  4. A dictionary for all the lights created for all lanes
  5. A number for the current active group
  6. A list of the types of light included
```python
def __init__(self, all_red_time=4):
    self.all_red_time = all_red_time
    self.time_in_all_red = 0
    self.timer = 0
    self.lights = {}
    self.current_group = 0
    self.current_group_phase = []
```
- The class includes six total methods:
  - 'add_light': add a lane and its traffic light to the 'lights' dictionary and the "current_group_phase" list
  - 'update': update all the clock for all traffic-lights, and roll to the next phase when the current phase is over
  - 'print_status': print the log message detailing, the time of the simulation, and the timer of different lights
  - 'update_timer': timer+1
  - 'sort_lights': sort the light into orders like NS through, NS left-turn, EW through, and EW left-turn
  - 'simulation': manage input and the simulation of the traffic system
```python
def add_light(self, direction, lane_type, signal_phase):
    self.lights[(direction, lane_type)] = TrafficLight(signal_phase)
    # A new lane will receive a new traffic light, in the position of the direction and type tuple
    self.current_group_phase.append([(direction, lane_type)])
    # append the type and direction of this new lane added to the current group
```
```python
def update(self):
    if self.time_in_all_red > 1:
        self.time_in_all_red -= 1
        return
    # Check if the crossroad is still in the all-red interval
    
    for key, light in self.lights.items():
        if key in self.current_group_phase[self.current_group]:
            light.update()
        else:
            if light.state != 'RED':
                light.state = 'RED'
    #update every light in the current group (timer & state) 

    if all(self.lights[key[0]].state == 'RED' and self.lights[key[0]].timer == 0 for key in self.current_group_phase):
        self.current_group = (self.current_group + 1) % len(self.current_group_phase)
        self.time_in_all_red = self.all_red_time
    # When the all-red interval just ended, transition to the next group, reset the all-red interval counter
```
```python
def print_status(self):
    status_display = f"[{self.timer//60:02}:{self.timer % 60:02}]:"
    for key in sorted(self.lights,reverse=True):
        status_display += (f"{"," if status_display[-1:]!=":" else ""} {key[0]} "
                           f"{"through lanes" if key[1] == "through" else "Left-turn"}: "
                           f"{self.lights[key].state} ({self.lights[key].timer}s)")
    print(status_display)
    # output the current status, time, lights timer and color
```
```python
def update_timer(self):
    self.timer += 1
```
```python
def sort_lights(self):
    self.current_group_phase.sort(reverse=True)
```
```python
def simulate(self, run_time):
    through_green_time = int(input("How many seconds does the GREEN signal for through lane last: "))
    through_yellow_time = int(input("How many seconds does the YELLOW signal for through lane last: "))
    left_green_time = int(input("How many seconds does the GREEN signal for left-turn lane last: "))
    left_yellow_time = int(input("How many seconds does the YELLOW signal for left-turn lane last: "))
    # input the time for green and yellow light time for both the through lane and the left-turn lanes
    phase_through = SignalPhase(green_time=through_green_time, yellow_time=through_yellow_time)
    phase_left = SignalPhase(green_time=left_green_time, yellow_time=left_yellow_time)
    #update the times into two class instances
    while True:
        #input as many lanes as demand, quit when the user pressed 'n'
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
        # update the time and status of the lights
        self.print_status()
        # output the time and status of the lights
        self.update_timer()
        # update the overall timer
        time.sleep(0.1)  # 0.1 as 1 second
        #simulate 1 second using 0.1 second
```

## Simulation:
- To run the simulation simply write the following code: define a controller "controller = IntersectionController()" then run the simulation using 'controller.simulate(time)'
```python
if __name__ == "__main__":
    controller = IntersectionController()
    controller.simulate(120)
    #simulat the program for 2 minute (12 second for the program)
```
- The simulation will follow the steps below:
  - 1. Input the green-light time for through lane
  - 2. Input the yellow-light time for through lane
  - 3. Input the green-light time for left-turn lane
  - 4. Input the yellow-light time for left-turn lane
  - 5. Input 'y' to add a new lane
  - 6. Enter the direction of the lane first, 'NS' for north-south, 'EW' for East-West
  - 7. Enter the lane type: through or left-turn
  - 8. repeat step 5-7 to add more lanes
  - 9. When finished enter 'n'


  
