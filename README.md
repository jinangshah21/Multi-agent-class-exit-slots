# Classroom Bottleneck Simulation

A multi-agent simulation where classroom agents negotiate for time slots to pass through a capacity-limited bottleneck.

-----

## Project Files

  * `main.py`: The main entry point to run the simulation. It loads parameters, initializes the agents, and prints the final report.
  * `simulation.py`: Manages the overall simulation flow, running the day-by-day negotiation loop and collecting results.
  * `classroom.py`: Defines the `ClassroomAgent`, which contains the core logic for proposing schedules and negotiating time slots.
  * `bottleneck.py`: Defines the `BottleneckAgent`, which acts as the shared, capacity-limited resource that agents compete for.

-----

## How to Run

**Run the Simulation**: Execute the main script from your terminal.

    ```bash
    python main.py
    ```

The script will run with default parameters hardcoded in `main.py`.

-----

## Custom Configuration

To run the simulation with custom parameters without editing the code, follow these steps:

1.  Create a file named `input.txt` in the same directory.
2.  Add your desired parameters to the file. The script will automatically detect and use this file if it exists.

### Example `input.txt`

```text
MAX_ATTENDANCES = 50, 20, 75  #Total number of students in each of the three classrooms.
BASE_WANTS = 0.8, 0.8, 0.5 #A value between 0.0 and 1.0 representing how strongly each classroom prefers to exit early.
BOTTLE_CAPACITY = 60 #The maximum number of students that can pass through the bottleneck in a single time slot.
DAYS = 5 #The total number of days the simulation will run for.
SLOT_RANGE = -15, 15 #The range of available time slots where 0 being the ideal time
```
