# classroom_agent.py
import asyncio
from autogen import AssistantAgent

class ClassroomAgent:
    def __init__(self, cid: str, class_strength: int, want_full: float, bottleneck_agent, batch_capacity=10):
        self.id = cid
        self.class_strength = class_strength
        self.want_full = want_full
        self.batch_capacity = batch_capacity  #bottleNeck capacity
        self.assigned_batches = []
        # self.commitment_history = {}  # {day: {peer_id: outcome}}
        self.avg_early = 0.0
        self.rejection_count = 0
        self.max_rejections = 3
        self.violations = 0

        self.bottleneck = bottleneck_agent
        self.agent = AssistantAgent(
            name=self.id,
            system_message=f"You are classroom agent {cid}. Negotiate exit slots with peers."
        )

    def propose_batches(self,classroom_attendance):
        """Initial proposal based on attendance & bottleneck cap"""
        remaining = classroom_attendance
        plan = []
        slot = 0
        while remaining > 0:
            num = min(self.batch_capacity, remaining)
            plan.append({"slot": slot, "num_students": num})
            remaining -= num
            slot += 1

        return plan

    async def propose_deal(self, day: int, peers: list, proposed_batches: list):
        """Propose batches one by one and broadcast proposals"""
        # proposed_batches = self.propose_batches()
        pending_batches = proposed_batches.copy()
        agreed_batches = []

        while pending_batches:
            batch = pending_batches.pop(0)

            # Collect peer evaluations
            response = await self.evaluate_peers(batch, day, peers)

            # accepted = all(responses)
            if response:
                self.assigned_batches.append(batch)
                agreed_batches.append(batch)
            else:
                # Modify slot and retry
                batch["slot"] -= 1
                # print(f"Doing for agent {self.id} and batch_size: {batch['num_students']}")
                pending_batches.append(batch)

        return agreed_batches

    async def evaluate_peers(self, batch, day, peers):
        """Simulate peer evaluation of a proposed batch"""
        responses = []
        for peer in peers:

            # Simple deterministic rule: reject if slot conflicts with previous commitment
            # peer_history = peer.commitment_history.get(day, {})
            for pab in peer.assigned_batches:
                 # CONFLICT DETECTED: The proposed slot is already taken by this peer. ---
                if pab["slot"]==batch["slot"]:

                    # CASE 1: The peer's slot is already completely full.
                    # The proposal must be rejected as no more students can be accommodated.
                    if pab["num_students"]==self.batch_capacity: #colliding batch wont be able to accomadate
                        peer.rejection_count += 1
                        if peer.rejection_count > peer.max_rejections:
                            peer.violations += 1

                        return False


                     # CASE 2: The peer's slot has enough capacity to merge both groups.
                     # The proposal is accepted, and the batches are combined.
                    if pab["num_students"]+batch["num_students"]<=self.batch_capacity:

                        # print("capacity suffice to accomadate other classroom's complete students")
                        # print(f"current batch is of agent: {self.id} and colliding batch is of Agent {peer.id}")
                        # print(f"previous agent's slot num of student {pab['num_students']}")
                        # print(f"current agent's slot num of student {batch['num_students']}")

                        total_students=pab["num_students"]+batch["num_students"]
                        pab["num_students"]=total_students
                        batch["num_students"]=total_students
                        return True

                    # CASE 3: The peer's slot has some space, but not enough for a full merge.
                    # A partial merge (split) will be performed.
                    else:
                        # print(f"current batch is of agent: {self.id} and colliding batch is of Agent {peer.id}")
                        students_to_move=self.batch_capacity-pab["num_students"]

                        pab["num_students"]=self.batch_capacity
                        b1={"slot": pab["slot"], "num_students": self.batch_capacity}

                        self.assigned_batches.append(b1)


                        batch["num_students"]=batch["num_students"]-students_to_move
                        # print(batch["num_students"])

                        peer.rejection_count += 1
                        if peer.rejection_count > peer.max_rejections:
                            peer.violations += 1

                        return False


         # --- NO CONFLICTS FOUND ---
        return True



    async def commit_batches(self, agreed_batches, day):
        """Commit agreed batches to bottleneck"""
        for batch in agreed_batches:
            resp = await self.bottleneck.request_hold(self.id, batch["slot"], batch["num_students"])
            if resp.get("status") == "ok":
                hid = resp["hold_id"]
                commit_info = {
                    "from_agent": self.id,
                    "to_agent": self.id,
                    "slot": batch["slot"],
                    "num_students": batch["num_students"],
                    "day": day
                }
                confirm = await self.bottleneck.confirm_holds_and_commit([hid], commit_info)
                if confirm.get("status") == "ok":
                    self.assigned_batches.append(batch)
        # Update commitment history
        # self.commitment_history[day] = {peer.id: "agreed" for peer in peers}
        return self.assigned_batches
