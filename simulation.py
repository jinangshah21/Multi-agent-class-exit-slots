# simulation.py
import asyncio

async def run_day(agents, bottleneck, day):
    """Run negotiation among classroom agents for one day"""
    # Broadcast bottleneck info (optional)
    tasks = []
    for agent in agents:
        peers = [a for a in agents if a != agent]
        tasks.append(agent.propose_deal(day, peers))
    all_agreed_batches = await asyncio.gather(*tasks)

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


async def run_simulation(env, bottleneck, classrooms, days=10):
    """Run full multi-day simulation"""
    results = []
    for day in range(1, days+1):
        for cls in classrooms:
            cls.assigned_batches = []  # reset per day
        day_result = await run_day(classrooms, bottleneck, day)
        results.append((day, day_result))
    return results
