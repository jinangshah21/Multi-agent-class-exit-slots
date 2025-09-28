# main.py
import asyncio
import random
import os
from classroom import ClassroomAgent
from bottleneck import BottleneckAgent
from simulation import run_simulation

# User parameters

DEFAULT_MAX_ATTENDANCES = [43, 23, 59, 16, 52, 29]
DEFAULT_BASE_WANTS = [0.7, 0.9, 0.4, 0.3, 0.8, 0.2]
DEFAULT_BOTTLE_CAPACITY = 50
DEFAULT_DAYS = 10
DEFAULT_SLOT_RANGE = (-10, 10)



def load_params_from_file(filepath="input.txt"):
    params = {}
    print(f"Found {filepath}. Loading simulation parameters from file...")
    with open(filepath, 'r') as f:
        for line in f:
            # Ignore comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Convert value string to the correct Python type
            if key == "MAX_ATTENDANCES":
                params[key] = [int(x.strip()) for x in value.split(',')]
            elif key == "BASE_WANTS":
                params[key] = [float(x.strip()) for x in value.split(',')]
            elif key == "SLOT_RANGE":
                # Create a list of ints first, then convert to a tuple
                params[key] = tuple([int(x.strip()) for x in value.split(',')])
            else: # Handles BOTTLE_CAPACITY, DAYS
                params[key] = int(value)
    return params



def make_daily_sequences(max_list, days, integer=True):
    """
    Generates daily sequences by taking a random fraction (0.5 to 1.0)
    of the values in max_list.
    """
    seq = []
    for _ in range(days):
        day_vals = []
        for v in max_list:
            fraction = random.uniform(0.5, 1.0)
            if integer:
                val = max(1, int(round(fraction * v)))
            else:
                val = max(0.0, fraction * v)
            day_vals.append(val)
        seq.append(day_vals)
    return seq

async def main():
    if os.path.exists("input.txt"):
        try:
            # If file exists, load parameters from it
            file_params = load_params_from_file()
            MAX_ATTENDANCES = file_params.get("MAX_ATTENDANCES", DEFAULT_MAX_ATTENDANCES)
            BASE_WANTS = file_params.get("BASE_WANTS", DEFAULT_BASE_WANTS)
            BOTTLE_CAPACITY = file_params.get("BOTTLE_CAPACITY", DEFAULT_BOTTLE_CAPACITY)
            DAYS = file_params.get("DAYS", DEFAULT_DAYS)
            SLOT_RANGE = file_params.get("SLOT_RANGE", DEFAULT_SLOT_RANGE)
        except Exception as e:
            print(f"⚠️ Error reading input.txt: {e}. Falling back to default parameters.")
            # On error, use defaults
            MAX_ATTENDANCES = DEFAULT_MAX_ATTENDANCES
            BASE_WANTS = DEFAULT_BASE_WANTS
            BOTTLE_CAPACITY = DEFAULT_BOTTLE_CAPACITY
            DAYS = DEFAULT_DAYS
            SLOT_RANGE = DEFAULT_SLOT_RANGE
    else:
        # If file does not exist, use the hardcoded defaults
        print("Input.txt not found. Using default simulation parameters.")
        MAX_ATTENDANCES = DEFAULT_MAX_ATTENDANCES
        BASE_WANTS = DEFAULT_BASE_WANTS
        BOTTLE_CAPACITY = DEFAULT_BOTTLE_CAPACITY
        DAYS = DEFAULT_DAYS
        SLOT_RANGE = DEFAULT_SLOT_RANGE

    N = len(MAX_ATTENDANCES)

    attendances_seq = make_daily_sequences(MAX_ATTENDANCES, DAYS)  #randomly generate
    wants_seq = make_daily_sequences(BASE_WANTS, DAYS, integer=False)

    bottleneck = BottleneckAgent(max_capacity_per_slot=BOTTLE_CAPACITY, slot_range=SLOT_RANGE)

    # Initialize classroom agents
    classrooms = []
    for i in range(N):
        cls = ClassroomAgent(f"C{i+1}", MAX_ATTENDANCES[i], BASE_WANTS[i], bottleneck, BOTTLE_CAPACITY)
        classrooms.append(cls)

    # Run simulation
    results = await run_simulation(env=None,attendance_seq=attendances_seq,bottleneck=bottleneck, classrooms=classrooms, days=DAYS)

    all_slot_shifts = []
    total_batches_across_days = 0


    # Reporting
    for day, r in results:
        print(f"\n=== Day {day} report ===")
        print("Classroom Attendance: ")
        print(attendances_seq[day-1])
        print("Slot timeline (slot -> students):")
        for s in sorted(r["timeline"].keys()):
            print(f"  slot {s:+d}: {r['timeline'][s]} students {'[CONGESTION]' if s in r['congestion_slots'] else ''}")
        print("Classroom metrics:")
        for cid, m in r["class_metrics"].items():
            print(f"  {cid}: assigned_batches={m['assigned_batches']}, rejections={m['rejections']}, violations={m['violations']}")
        for batch in m['assigned_batches']:
            # The "shift" is the absolute distance of the slot from 0
            all_slot_shifts.append(abs(batch['slot']))
            total_batches_across_days += 1

    if total_batches_across_days > 0:
        average_shift = sum(all_slot_shifts) / total_batches_across_days
    else:
        average_shift = 0

    print(f"\n{'='*20} Overall Simulation Metrics {'='*20}")
    print(f"Total Days Simulated: {DAYS}")
    print(f"Average Slot Shift from 0: {average_shift:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
