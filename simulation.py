# simulation.py
import asyncio

async def run_day(agents,todays_attendance,bottleneck,day):
    """Run negotiation among classroom agents for one day"""

    # for i,agent in enumerate(agents):
    #     agent.proposed_batches = agent.propose_batches(todays_attendance[i])

    # all_pending_batches = []
    # for agent in agents:
    #     for batch in agent.proposed_batches:
    #         # Add a reference to the agent with each batch
    #         all_pending_batches.append({"agent": agent, "batch": batch})


    # while all_pending_batches:
    #     current_batch=all_pending_batches.pop(0)
    #     proposing_agent = current_batch["agent"]
    #     batch_to_propose = current_batch["batch"]

    #     # The agent proposes to its peers
    #     peers = [a for a in agents]  # there could be 2 batches of the same classroom

    #     # This check now happens sequentially
    #     responses = await proposing_agent.evaluate_peers(batch_to_propose, day, peers)

    #     if all(responses):
    #         # print(f"sucessfully assigned {proposing_agent.id} with batch_size {batch_to_propose['num_students']}  in the slot: {batch_to_propose['slot']}")
    #         proposing_agent.assigned_batches.append(batch_to_propose)
    #         # for peer in peers:
    #         #     print(peer.assigned_batches)
    #         # print(proposing_agent.assigned_batches)
    #     else:
    #         current_batch['batch']['slot']-=1
    #         all_pending_batches.append(current_batch)

    # all_agreed_batches = [agent.assigned_batches for agent in agents]


    initial_proposals = {}
    for i,agent in enumerate(agents):
        initial_proposals[agent.id] = agent.propose_batches(todays_attendance[i])

    tasks = []
    for agent in agents:
        peers = [a for a in agents]
        tasks.append(agent.propose_deal(day,peers,initial_proposals[agent.id]))  # there could be 2 batches of the same classroom
    all_agreed_batches = await asyncio.gather(*tasks)



    # tasks = []
    # for agent in agents:
    #     peers = [a for a in agents if a != agent]
    #     tasks.append(agent.propose_deal(day, peers))
    # all_agreed_batches = await asyncio.gather(*tasks)


    # Commit all batches after negotiation
    commit_tasks = []
    for agent, batches in zip(agents, all_agreed_batches):
        commit_tasks.append(agent.commit_batches(batches, day))
    await asyncio.gather(*commit_tasks)

    # Evaluate day
    timeline, congestion, total_students = bottleneck.evaluate_day()
    class_metrics = {}
    for agent in agents:
        class_metrics[agent.id] = {
            "assigned_batches": agent.assigned_batches,
            "rejections": agent.rejection_count,
            "violations": agent.violations
        }

    commitments = await bottleneck.get_commitments()
    return {"timeline": timeline, "congestion_slots": congestion, "total_students": total_students,
            "class_metrics": class_metrics, "commitments": commitments}


async def run_simulation(env,attendance_seq, bottleneck, classrooms, days=10):
    """Run full multi-day simulation"""
    results = []
    for day in range(1, days+1):
        todays_attend=attendance_seq[day-1]
        for cls in classrooms:
            cls.assigned_batches = []  # reset per day
        day_result = await run_day(classrooms,todays_attend, bottleneck, day)
        results.append((day, day_result))
    return results
