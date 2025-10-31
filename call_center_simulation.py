import simpy
import random
import csv

def call_process(env, agents, service_rate, wait_times):
    arrival_time = env.now
    with agents.request() as request:
        yield request
        wait = env.now - arrival_time
        wait_times.append(wait)
        service_time = random.expovariate(service_rate)
        yield env.timeout(service_time)

def call_arrivals(env, agents, arrival_rate, service_rate, wait_times):
    i = 0
    while True:
        inter_arrival = random.expovariate(arrival_rate)
        yield env.timeout(inter_arrival)
        i += 1
        env.process(call_process(env, agents, service_rate, wait_times))

def run_simulation(num_agents, arrival_rate, service_rate, simulation_time):
    env = simpy.Environment()
    agents = simpy.Resource(env, capacity=num_agents)
    wait_times = []

    queue_lengths = []
    def monitor_queue():
        while True:
            queue_lengths.append(len(agents.queue))
            yield env.timeout(1)

    env.process(call_arrivals(env, agents, arrival_rate, service_rate, wait_times))
    env.process(monitor_queue())
    env.run(until=simulation_time)

    total_calls = len(wait_times)
    avg_wait = sum(wait_times) / total_calls if total_calls > 0 else 0
    avg_queue = sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0
    avg_service_time = 1 / service_rate
    total_busy_time = total_calls * avg_service_time
    utilization = (total_busy_time / (num_agents * simulation_time)) * 100

    return {
        "Number of Agents": num_agents,
        "Arrival Rate": arrival_rate,
        "Service Rate": service_rate,
        "Total Calls Handled (Throughput)": total_calls,
        "Average Wait Time (min)": avg_wait,
        "Average Queue Length": avg_queue,
        "Agent Utilization (%)": utilization
    }

def run_experiments_and_save():
    results = []
    # Experiment 1: Vary number of agents
    for num_agents in [2, 3, 6]:
        res = run_simulation(num_agents=num_agents, arrival_rate=0.5, service_rate=1/3, simulation_time=120)
        results.append(res)

    # Experiment 2: Vary arrival rate
    for arrival_rate in [0.5, 0.75, 1.0]:
        res = run_simulation(num_agents=3, arrival_rate=arrival_rate, service_rate=1/3, simulation_time=120)
        results.append(res)

    # Experiment 3: Vary service rate
    for service_rate in [1/3, 1/2, 1]:
        res = run_simulation(num_agents=3, arrival_rate=0.5, service_rate=service_rate, simulation_time=120)
        results.append(res)

    # Write results to CSV
    fieldnames = list(results[0].keys())
    with open('call_center_simulation_results.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print("Simulation results saved to call_center_simulation_results.csv")

if __name__ == "__main__":
    run_experiments_and_save()
