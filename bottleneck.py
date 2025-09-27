# bottleneck_agent.py
import asyncio

class BottleneckAgent:
    def __init__(self, max_capacity_per_slot: int, slot_range=(-10, 10)):
        self.max_capacity = max_capacity_per_slot
        self.slot_min, self.slot_max = slot_range
        self.assigned = {}  # {slot: total_students}
        self.commitments = []

    async def request_hold(self, agent_id: str, slot: int, num_students: int, ttl_seconds=15):
        if slot < self.slot_min or slot > self.slot_max:
            return {"status": "fail", "reason": "invalid_slot"}
        current = self.assigned.get(slot, 0)
        if current + num_students <= self.max_capacity:
            return {"status": "ok", "hold_id": f"{agent_id}_{slot}_{num_students}"}
        else:
            return {"status": "fail", "reason": "over_capacity"}

    async def confirm_holds_and_commit(self, hold_ids, commit_info: dict):
        slot = commit_info["slot"]
        num_students = commit_info["num_students"]
        current = self.assigned.get(slot, 0)
        if current + num_students <= self.max_capacity:
            self.assigned[slot] = current + num_students
            self.commitments.append(commit_info)
            return {"status": "ok"}
        else:
            return {"status": "fail", "reason": "over_capacity"}

    async def get_commitments(self):
        return self.commitments

    def evaluate_day(self):
        """Return timeline, congested slots and total students"""
        timeline = self.assigned.copy()
        congestion_slots = [s for s, n in timeline.items() if n > self.max_capacity]
        total_students = sum(timeline.values())
        return timeline, congestion_slots, total_students
