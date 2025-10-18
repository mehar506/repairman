import random
import numpy as np
from typing import List, Dict


def generate_positive_normal(mean: float, std: float) -> float:
    """Generate positive values from normal distribution"""
    while True:
        value = random.gauss(mean, std)
        if value > 0:
            return value


def run_repairman_simulation(M: int, N: int, mean_repair: float, std_repair: float,
                             mean_break: float, std_break: float, num_simulations: int) -> Dict:
    """
    Proper discrete-event simulation of repairman problem
    Returns time until factory halts (working machines < N)
    """
    results = []

    for sim in range(1, num_simulations + 1):
        # Initial state
        time = 0.0
        working_machines = M
        broken_machines = 0
        factory_halt_time = None

        # Event queue: list of (time, machine_id, event_type)
        event_queue = []

        # Schedule initial breakdowns for all machines
        for machine_id in range(M):
            breakdown_time = generate_positive_normal(mean_break, std_break)
            event_queue.append((breakdown_time, machine_id, 'breakdown'))

        # Sort events by time
        event_queue.sort(key=lambda x: x[0])

        simulation_events = []
        event_count = 0

        while event_queue and factory_halt_time is None:
            # Get next event
            event_time, machine_id, event_type = event_queue.pop(0)
            time = event_time
            event_count += 1

            # Store state BEFORE processing
            working_before = working_machines
            broken_before = broken_machines

            if event_type == 'breakdown':
                # Machine breaks down
                working_machines -= 1
                broken_machines += 1

                simulation_events.append({
                    'time': round(time, 2),
                    'type': 'breakdown',
                    'machine_id': machine_id,
                    'working_before': working_before,
                    'broken_before': broken_before,
                    'working_after': working_machines,
                    'broken_after': broken_machines
                })

                # CRITICAL: Check if factory halts AFTER the breakdown
                if working_machines < N:
                    factory_halt_time = round(time, 2)
                    # Log the halt with the actual state
                    simulation_events.append({
                        'time': round(time, 2),
                        'type': 'FACTORY_HALT',
                        'machine_id': None,
                        'working_before': working_before,
                        'broken_before': broken_before,
                        'working_after': working_machines,
                        'broken_after': broken_machines
                    })
                    break  # Stop simulation immediately

                # Schedule repair for this broken machine
                repair_time = time + generate_positive_normal(mean_repair, std_repair)
                event_queue.append((repair_time, machine_id, 'repair'))

            else:  # repair event
                # Machine gets repaired
                working_machines += 1
                broken_machines -= 1

                simulation_events.append({
                    'time': round(time, 2),
                    'type': 'repair',
                    'machine_id': machine_id,
                    'working_before': working_before,
                    'broken_before': broken_before,
                    'working_after': working_machines,
                    'broken_after': broken_machines
                })

                # Schedule next breakdown for this repaired machine
                breakdown_time = time + generate_positive_normal(mean_break, std_break)
                event_queue.append((breakdown_time, machine_id, 'breakdown'))

            # Sort events for next iteration
            event_queue.sort(key=lambda x: x[0])

        # Calculate statistics
        if factory_halt_time:
            # When factory halts, working_machines is the actual count at halt
            utilization = working_machines / M
            working_at_halt = working_machines
        else:
            # If no halt, use final state
            utilization = working_machines / M
            working_at_halt = working_machines

        # Generate random samples for display
        random_repair_sample = round(generate_positive_normal(mean_repair, std_repair), 2)
        random_breakdown_sample = round(generate_positive_normal(mean_break, std_break), 2)

        results.append({
            "simulation": sim,
            "time_until_halt": factory_halt_time,
            "final_working_machines": working_machines,
            "final_broken_machines": broken_machines,
            "working_at_halt": working_at_halt,  # This should vary now!
            "utilization_at_halt": round(utilization, 4),
            "random_repair_sample": random_repair_sample,
            "random_breakdown_sample": random_breakdown_sample,
            "total_events": event_count,
            "events": simulation_events[:10]  # First 10 events for display
        })

        # Debug output to console
        print(f"Simulation {sim}: Halted at {factory_halt_time} with {working_at_halt} working machines")

    return {"results": results}


# Add this to your simulation.py file to test it
if __name__ == "__main__":
    # Test the simulation directly
    print("🧪 Testing simulation with M=10, N=6...")
    result = run_repairman_simulation(M=10, N=6, mean_repair=100, std_repair=50,
                                      mean_break=300, std_break=80, num_simulations=10)

    for r in result["results"]:
        print(f"Sim {r['simulation']}: Halt at {r['time_until_halt']} with {r['working_at_halt']} working machines")

    # Count different halt states
    halt_states = {}
    for r in result["results"]:
        if r['time_until_halt']:
            state = r['working_at_halt']
            halt_states[state] = halt_states.get(state, 0) + 1

    print(f"Halt states distribution: {halt_states}")