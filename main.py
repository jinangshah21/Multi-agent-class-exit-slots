# main.py
import asyncio
import random

from classroom import ClassroomAgent
from bottleneck import BottleneckAgent
from simulation import run_simulation

# User parameters
N = 6
BASE_ATTENDANCES = [48, 32, 60, 25, 80, 30]
BASE_WANTS = [0.7, 0.9, 0.4, 0.3, 0.8, 0.2]
BOTTLE_CAPACITY = 50
DAYS = 10
SLOT_RANGE = (-10, 10)

def make_daily_sequences(base_list, days, jitter=0.2, integer=True):
    seq = []
    for _ in range(days):
        day_vals = []
        for v in base_list:
            if integer:
                val = max(1, int(round(random.uniform(1 - jitter, 1 + jitter) * v)))
            else:
                val = max(0.0, random.uniform(1 - jitter, 1 + jitter) * v)
            day_vals.append(val)
        seq.append(day_vals)
    return seq

async def main():
    attendances_seq = make_daily_sequences(BASE_ATTENDANCES, DAYS)
    wants_seq = make_daily_sequences(BASE_WANTS, DAYS, integer=False)

    bottleneck = BottleneckAgent(max_capacity_per_slot=BOTTLE_CAPACITY, slot_range=SLOT_RANGE)

    # Initialize classroom agents
    classrooms = []
    for i in range(N):
        cls = ClassroomAgent(f"C{i+1}", BASE_ATTENDANCES[i], BASE_WANTS[i], bottleneck, BOTTLE_CAPACITY)
        classrooms.append(cls)

    # Run simulation
    results = await run_simulation(env=None, bottleneck=bottleneck, classrooms=classrooms, days=DAYS)

    # Reporting
    for day, r in results:
        print(f"\n=== Day {day} report ===")
        print("Slot timeline (slot -> students):")
        for s in sorted(r["timeline"].keys()):
            print(f"  slot {s:+d}: {r['timeline'][s]} students {'[CONGESTION]' if s in r['congestion_slots'] else ''}")
        print("Classroom metrics:")
        for cid, m in r["class_metrics"].items():
            print(f"  {cid}: assigned_batches={m['assigned_batches']}, rejections={m['rejections']}, violations={m['violations']}")

if __name__ == "__main__":
    asyncio.run(main())
