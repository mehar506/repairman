import random
import numpy as np

def simulate_once(M, N, mean_repair, std_repair, mean_break, std_break):
    n = M  # Working machines
    b = 0  # Broken machines
    t = 0  # Time
    repair_times = []
    breakdown_times = [abs(random.gauss(mean_break, std_break)) for _ in range(M)]
    explanation = []

    explanation.append(f"Simulation start: {M} machines, factory needs at least {N} working machines.")

    while n >= N:
        # Get next breakdown time
        next_break = min(breakdown_times)
        next_repair = min(repair_times) if repair_times else float('inf')

        # Find next event
        if next_break < next_repair:
            t += next_break
            breakdown_times = [x - next_break for x in breakdown_times]
            repair_times = [x - next_break for x in repair_times]
            n -= 1
            b += 1
            explanation.append(f"At time {round(t,2)}: Machine broke down. Working={n}, Broken={b}")

            # Generate new breakdown for that machine
            breakdown_times.remove(0)
            breakdown_times.append(abs(random.gauss(mean_break, std_break)))

            # If a machine broke, start its repair
            repair_times.append(abs(random.gauss(mean_repair, std_repair)))

        else:
            t += next_repair
            breakdown_times = [x - next_repair for x in breakdown_times]
            repair_times = [x - next_repair for x in repair_times]
            n += 1
            b -= 1
            explanation.append(f"At time {round(t,2)}: Machine repaired. Working={n}, Broken={b}")

            repair_times.remove(0)

    explanation.append(f"⚠️ Factory stopped at time {round(t,2)} (only {n} working machines left).")
    return t, explanation


def run_repairman_simulation(M, N, mean_repair, std_repair, mean_break, std_break, num_simulations):
    results = []
    all_explanations = []

    for i in range(num_simulations):
        time_to_stop, explanation = simulate_once(M, N, mean_repair, std_repair, mean_break, std_break)
        results.append(time_to_stop)
        all_explanations.append({
            "simulation": i + 1,
            "steps": explanation,
            "time_to_stop": round(time_to_stop, 2)
        })

    avg_time = np.mean(results)
    summary = {
        "average_time_to_stop": round(avg_time, 2),
        "num_simulations": num_simulations,
        "details": all_explanations,
        "explanation": f"After {num_simulations} runs, the factory stopped on average after {round(avg_time, 2)} time units. " \
                       f"This shows how random breakdowns and repairs affect system reliability."
    }

    return summary
