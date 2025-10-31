import simpy
import random

def call_process(env, agents, service_rate, wait_times):
    """ Simulate a single call process:
    - Request an agent (resource)
    - Wait if none available (queue)
    - Get served for a random service time """
    arrival_time = env.now  # Record when the call arrives
    with agents.request() as request:
        yield request  # Wait for an available agent
        wait = env.now - arrival_time  # Calculate wait time
        wait_times.append(wait)  # Store wait time for later analysis
        service_time = random.expovariate(service_rate)  # Generate random service time
        yield env.timeout(service_time)  # Simulate service duration

def call_arrivals(env, agents, arrival_rate, service_rate, wait_times):
    """ Generate calls arriving at the call center with realistic inter-arrival times. """
    i = 0  # Counter for call numbering
    while True:
        inter_arrival = random.expovariate(arrival_rate)  # Time between arrivals
        yield env.timeout(inter_arrival)  # Wait for next arrival
        i += 1  # Increment call counter
        env.process(call_process(env, agents, service_rate, wait_times))  # Start call process

def run_simulation(num_agents, arrival_rate, service_rate, simulation_time):
    """ Parameters:
    - num_agents: Number of agents (workers/resources)
    - arrival_rate: Average calls per minute (traffic)
    - service_rate: Average service rate per minute (faster machines/agents)
    - simulation_time: Total simulation time in minutes """
    env = simpy.Environment()  # Create simulation environment
    agents = simpy.Resource(env, capacity=num_agents)  # Limited agents as a resource
    wait_times = []  # List to track individual wait times

    # Track queue length over time for average queue length
    queue_lengths = []

    def monitor_queue():
        while True:
            queue_lengths.append(len(agents.queue))  # Record current queue length
            yield env.timeout(1)  # Sample every 1 minute

    # Start the arrival and monitoring processes
    env.process(call_arrivals(env, agents, arrival_rate, service_rate, wait_times))
    env.process(monitor_queue())
    env.run(until=simulation_time)  # Run simulation for specified time

    # Calculate metrics
    total_calls = len(wait_times)  # Throughput: total calls handled
    avg_wait = sum(wait_times) / total_calls if total_calls > 0 else 0  # Average wait time
    avg_queue = sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0  # Average queue length

    # Agent utilization: Approximate total busy time / total available time
    avg_service_time = 1 / service_rate
    total_busy_time = total_calls * avg_service_time
    utilization = (total_busy_time / (num_agents * simulation_time)) * 100  # Resource use %

    return {
        "Total Calls Handled (Throughput)": total_calls,
        "Average Wait Time (min)": avg_wait,
        "Average Queue Length": avg_queue,
        "Agent Utilization (%)": utilization
    }

def run_experiments():
    """ Conduct three distinct experiments:
    1. Vary number of agents (workers/resources)
    2. Vary arrival rate (traffic)
    3. Vary service rate (agent efficiency) """
    print("=== Experiment 1: Vary Number of Agents ===")
    for num_agents in [2, 3, 6]:
        results = run_simulation(num_agents=num_agents, arrival_rate=0.5, service_rate=1/3, simulation_time=120)
        print(f"\nNumber of Agents: {num_agents}")
        for k, v in results.items():
            print(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")

    print("\n=== Experiment 2: Vary Arrival Rate ===")
    for arrival_rate in [0.5, 0.75, 1.0]:
        results = run_simulation(num_agents=3, arrival_rate=arrival_rate, service_rate=1/3, simulation_time=120)
        print(f"\nArrival Rate: {arrival_rate} calls/min")
        for k, v in results.items():
            print(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")

    print("\n=== Experiment 3: Vary Service Rate ===")
    for service_rate in [1/3, 1/2, 1]:
        results = run_simulation(num_agents=3, arrival_rate=0.5, service_rate=service_rate, simulation_time=120)
        print(f"\nService Rate: {service_rate:.2f} calls/min")
        for k, v in results.items():
            print(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")

if __name__ == "__main__":
    run_experiments()