#quantum executor
#simon ibm_brisbane -> 3s |  simon ibm_sherbrooke -> 3s
#teleportation ibm_brisbane -> 6s | teleportation ibm_sherbrooke -> 10s
#qft ibm_brisbane -> 3s | qft ibm_sherbrooke -> 3s
#berstein-vazirani ibm_brisbane -> 3s | berstein-vazirani ibm_sherbrooke -> 3s
#shor ibm_brisbane -> 3s | shor ibm_sherbrooke -> 3s
#full_adder ibm_brisbane -> 3s | full_adder ibm_sherbrooke -> 3s
#qwalk ibm_brisbane -> 3s | qwalk ibm_sherbrooke -> 3s 
#kickback ibm_brisbane -> 3s | kickback ibm_sherbrooke -> 3s
#qaoa ibm_brisbane -> 3s | qaoa ibm_sherbrooke -> 3s
#tsp ibm_brisbane -> 3s | tsp ibm_sherbrooke -> 3s
#phase_estimation ibm_brisbane -> 3s | phase_estimation ibm_sherbrooke -> 3s
#Deutsch-Jozsa ibm_brisbane -> 6s | Deutsch-Jozsa ibm_sherbrooke -> 10s
#grover ibm_brisbane -> 3s | grover ibm_sherbrooke -> 3s



#scheduled
#ibm brisbane -> 9s
#ibm sherbrooke -> 14s


#individual ibm brisbane
#simon  -> 5s
#teleportation  -> 8s
#qft  -> 4s
#berstein-vazirani  -> 4s
#shor  -> 4s
#full_adder  -> 4s 
#qwalk  -> 4s
#kickback  -> 4s
#qaoa  -> 4s
#tsp  -> 4s
#phase_estimation  -> 4s
#Deutsch-Jozsa  -> 4s
#grover  -> 4s

#individual ibm sherbrooke
#simon -> 5s
#teleportation -> 13s
#qft -> 4s
#berstein-vazirani -> 4s 
#shor -> 4s
#full_adder -> 4s  
#qwalk -> 4s
#kickback -> 4s
#qaoa -> 4s
#tsp -> 4s
#phase_estimation -> 4s
#Deutsch-Jozsa  -> 10s

#qe + scheduler
#ibm brisbane -> 6s
#ibm sherbrooke -> 10s

#cost = seconds * 96 / 60


import matplotlib.pyplot as plt

circuits = [
    "Simon", "Teleportation", "QFT", "Berstein-Vazirani", "Shor", "Full adder",
    "QWalk", "Kickback", "QAOA", "TSP", "Phase estimation", "Deutsch-Jozsa", "Grover"
]

quantum_executor_costs = {
    "Simon": (3 + 3) * 96 / 60,
    "Teleportation": (6 + 10) * 96 / 60,
    "QFT": (3 + 3) * 96 / 60,
    "Berstein-Vazirani": (3 + 3) * 96 / 60,
    "Shor": (3 + 3) * 96 / 60,
    "Full adder": (3 + 3) * 96 / 60,
    "QWalk": (3 + 3) * 96 / 60,
    "Kickback": (3 + 3) * 96 / 60,
    "QAOA": (3 + 3) * 96 / 60,
    "TSP": (3 + 3) * 96 / 60,
    "Phase estimation": (3 + 3) * 96 / 60,
    "Deutsch-Jozsa": (6 + 10) * 96 / 60,
    "Grover": (3 + 3) * 96 / 60,
}

scheduled_costs_ibm_brisbane = { # cost of the individual circuit = cost of the scheduled circuit * used qubits / total qubits
    "Simon": (9) * 6/46 * 96 / 60,
    "Teleportation": (9) * 3/46 * 96 / 60,
    "QFT": (9) * 3/46 * 96 / 60,
    "Berstein-Vazirani": (9) * 4/46 * 96 / 60,
    "Shor": (9) * 4/46 * 96 / 60,
    "Full adder": (9) * 4/46 * 96 / 60,
    "QWalk": (9) * 3/46 * 96 / 60,
    "Kickback": (9) * 2/46  * 96 / 60,
    "QAOA": (9) * 2/46 * 96 / 60,
    "TSP": (9) * 5/46 * 96 / 60,
    "Phase estimation": (9)* 4/46 * 96 / 60,
    "Deutsch-Jozsa": (9)* 4/46 * 96 / 60,
    "Grover": (9)* 2/46 * 96 / 60,
}

scheduled_costs_ibm_sherbrooke= { # cost of the individual circuit = cost of the scheduled circuit * used qubits / total qubits
    "Simon": (14) * 6/46 * 96 / 60,
    "Teleportation": (14) * 3/46 * 96 / 60,
    "QFT": (14) * 3/46 * 96 / 60,
    "Berstein-Vazirani": (14) * 4/46 * 96 / 60,
    "Shor": (14) * 4/46 * 96 / 60,
    "Full adder": (14) * 4/46 * 96 / 60,
    "QWalk": (14) * 3/46 * 96 / 60,
    "Kickback": (14) * 2/46  * 96 / 60,
    "QAOA": (14) * 2/46 * 96 / 60,
    "TSP": (14) * 5/46 * 96 / 60,
    "Phase estimation": (14)* 4/46 * 96 / 60,
    "Deutsch-Jozsa": (14)* 4/46 * 96 / 60,
    "Grover": (14)* 2/46 * 96 / 60,
}

ibm_brisbane_costs = {
    "Simon": (5) * 96 / 60,
    "Teleportation": (8) * 96 / 60,
    "QFT": (4) * 96 / 60,
    "Berstein-Vazirani": (4) * 96 / 60,
    "Shor": (4) * 96 / 60,
    "Full adder": (4) * 96 / 60,
    "QWalk": (4) * 96 / 60,
    "Kickback": (4)  * 96 / 60,
    "QAOA": (4) * 96 / 60,
    "TSP": (4) * 96 / 60,
    "Phase estimation": (4) * 96 / 60,
    "Deutsch-Jozsa": (4) * 96 / 60,
    "Grover": (4) * 96 / 60,
}

ibm_sherbrooke_costs = {
    "Simon": (5) * 96 / 60,
    "Teleportation": (13) * 96 / 60,
    "QFT": (4) * 96 / 60,
    "Berstein-Vazirani": (4) * 96 / 60,
    "Shor": (4) * 96 / 60,
    "Full adder": (4) * 96 / 60,
    "QWalk": (4) * 96 / 60,
    "Kickback": (4)  * 96 / 60,
    "QAOA": (4) * 96 / 60,
    "TSP": (4) * 96 / 60,
    "Phase estimation": (4) * 96 / 60,
    "Deutsch-Jozsa": (4) * 96 / 60,
    "Grover": (10) * 96 / 60,
}

qe_plus_scheduler_costs = { #Add here the costs of each machine because each one executed 5000 shots
    "Simon": (10+6) * 6/46 * 96 / 60,
    "Teleportation": (10+6) * 3/46 * 96 / 60,
    "QFT": (10+6) * 3/46 * 96 / 60,
    "Berstein-Vazirani": (10+6) * 4/46 * 96 / 60,
    "Shor": (10+6) * 4/46 * 96 / 60,
    "Full adder": (10+6) * 4/46 * 96 / 60,
    "QWalk": (10+6) * 3/46 * 96 / 60,
    "Kickback": (10+6) * 2/46  * 96 / 60,
    "QAOA": (10+6) * 2/46 * 96 / 60,
    "TSP": (10+6) * 5/46 * 96 / 60,
    "Phase estimation": (10+6)* 4/46 * 96 / 60,
    "Deutsch-Jozsa": (10+6)* 4/46 * 96 / 60,
    "Grover": (10+6)* 2/46 * 96 / 60,
}

scheduled_costs_mean = {  # Do the median of the costs of the scheduled circuits in the ibm_brisbane and ibm_sherbrooke because each one executed 10000 shots (qe doesnt need to to this because each one was 5000 shots, so adding the time is correct on that case)
    "Simon": (9+14)/2 * 6/46 * 96 / 60,
    "Teleportation": (9+14)/2 * 3/46 * 96 / 60,
    "QFT": (9+14)/2 * 3/46 * 96 / 60,
    "Berstein-Vazirani": (9+14)/2 * 4/46 * 96 / 60,
    "Shor": (9+14)/2 * 4/46 * 96 / 60,
    "Full adder": (9+14)/2 * 4/46 * 96 / 60,
    "QWalk": (9+14)/2 * 3/46 * 96 / 60,
    "Kickback": (9+14)/2 * 2/46  * 96 / 60,
    "QAOA": (9+14)/2 * 2/46 * 96 / 60,
    "TSP": (9+14)/2 * 5/46 * 96 / 60,
    "Phase estimation": (9+14)/2 * 4/46 * 96 / 60,
    "Deutsch-Jozsa": (9+14)/2 * 4/46 * 96 / 60,
    "Grover": (9+14)/2 * 2/46 * 96 / 60,
}

qe_plus_scheduler_plus_autoscheduler_costs = {
    "Simon": (5+9)/2 * 6/46 * 96 / 60,
    "Teleportation": (5+9)/2 * 3/46 * 96 / 60,
    "QFT": (5+9)/2 * 3/46 * 96 / 60,
    "Berstein-Vazirani": (5+9)/2 * 4/46 * 96 / 60,
    "Shor": (5+9)/2 * 4/46 * 96 / 60,
    "Full adder": (5+9)/2 * 4/46 * 96 / 60,
    "QWalk": (5+9)/2 * 3/46 * 96 / 60,
    "Kickback": (5+9)/2 * 2/46  * 96 / 60,
    "QAOA": (5+9)/2 * 2/46 * 96 / 60,
    "TSP": (5+9)/2 * 5/46 * 96 / 60,
    "Phase estimation": (5+9)/2 * 4/46 * 96 / 60,
    "Deutsch-Jozsa": (5+9)/2 * 4/46 * 96 / 60,
    "Grover": (5+9)/2 * 2/46 * 96 / 60,
}

executor_costs = [quantum_executor_costs[circuit] for circuit in circuits]
scheduled_costs = [scheduled_costs_mean[circuit] for circuit in circuits]
ibm_brisbane_costs = [ibm_brisbane_costs[circuit] for circuit in circuits]
ibm_sherbrooke_costs = [ibm_sherbrooke_costs[circuit] for circuit in circuits]
qe_plus_scheduler_costs_ = [qe_plus_scheduler_costs[circuit] for circuit in circuits]
qe_plus_scheduler_plus_autoscheduler_costs_ = [qe_plus_scheduler_plus_autoscheduler_costs[circuit] for circuit in circuits]

plt.figure(figsize=(12, 6))
plt.plot(circuits, executor_costs, label="Quantum Executor Cost", marker="o")
plt.plot(circuits, scheduled_costs, label="Scheduler Cost", marker="o")
plt.plot(circuits, qe_plus_scheduler_costs_, label="Quantum Executor+Scheduler Cost", marker="o")
plt.plot(circuits, qe_plus_scheduler_plus_autoscheduler_costs_, label="Quantum Executor+Scheduler+AutoScheduler Cost", marker="o")
plt.plot(circuits, ibm_brisbane_costs, label="IBM Brisbane Cost", marker="o")
plt.plot(circuits, ibm_sherbrooke_costs, label="IBM Sherbrooke Cost", marker="o")
plt.xlabel("Circuit")
plt.ylabel("Cost (USD)")
plt.title("Cost Comparison")
plt.legend()
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.savefig("quantum-executor-plots/cost-comparison.png")