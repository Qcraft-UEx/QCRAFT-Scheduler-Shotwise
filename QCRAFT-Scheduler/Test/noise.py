import os
import json
import math
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#######################
# FUNCIONES AUXILIARES
#######################

def hellinger(p, q):
    """Calcula la distancia de Hellinger entre dos distribuciones p y q."""
    return math.sqrt(sum((math.sqrt(p_i) - math.sqrt(q_i))**2 for p_i, q_i in zip(p, q)) / 2)

def add_missing_keys(d1, d2):
    """Si algún diccionario no contiene claves que están en el otro, las añade con valor 0.
       Ordena las claves y devuelve dos nuevos diccionarios.
    """
    for key in d1.keys():
        if key not in d2:
            d2[key] = 0
    for key in d2.keys():
        if key not in d1:
            d1[key] = 0

    d1 = dict(sorted(d1.items()))
    d2 = dict(sorted(d2.items()))
    return d1, d2

def dict_to_prob(d):
    """Convierte un diccionario {evento: cuenta} a una lista de probabilidades."""
    total = sum(d.values())
    # Evita división por 0
    if total == 0:
        return [0]*len(d)
    return [count / total for count in d.values()]

##############################
# FUNCIÓN PARA LEER ARCHIVOS JSON
##############################

def load_json_files(directory):
    """Carga todos los archivos JSON de un directorio."""
    files = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as f:
                files[filename] = json.load(f)
    return files

##############################
# DIRECTORIOS DE LOS ARCHIVOS
##############################

quantum_executor_results_dir = "quantum-executor-results"
quantum_executor_scheduler_brisbane_dir = "quantum-executor-results-scheduler-brisbane"
quantum_executor_scheduler_sherbrooke_dir = "quantum-executor-results-scheduler-sherbrooke"
ibm_brisbane_dir = "quantum-executor-results-ibm-brisbane"
ibm_sherbrooke_dir = "quantum-executor-results-ibm-sherbrooke"
quantum_executor_plus_scheduler_results_dir = "quantum-executor-plus-scheduler-results"
quantum_executor_plus_scheduler_plus_autoscheduler_results_dir = "quantum-executor-plus-scheduler-plus-autoscheduler-results"

##############################
# CARGA DE ARCHIVOS JSON
##############################

quantum_executor_results = load_json_files(quantum_executor_results_dir)
quantum_executor_scheduler_results_brisbane = load_json_files(quantum_executor_scheduler_brisbane_dir)
quantum_executor_scheduler_results_sherbrooke = load_json_files(quantum_executor_scheduler_sherbrooke_dir)
ibm_brisbane_results = load_json_files(ibm_brisbane_dir)
ibm_sherbrooke_results = load_json_files(ibm_sherbrooke_dir)
quantum_executor_plus_scheduler_results = load_json_files(quantum_executor_plus_scheduler_results_dir)
quantum_executor_plus_scheduler_plus_autoscheduler_results = load_json_files(quantum_executor_plus_scheduler_plus_autoscheduler_results_dir)

##############################
# CÁLCULO DE DISTANCIAS
##############################

def calculate_hellinger_distances(results1, results2):
    """Calcula la distancia de Hellinger entre archivos con el mismo nombre."""
    distances = {}
    for filename in results1.keys():
        if filename in results2:
            dict1, dict2 = add_missing_keys(results1[filename], results2[filename])
            prob1 = dict_to_prob(dict1)
            prob2 = dict_to_prob(dict2)
            distances[filename] = hellinger(prob1, prob2)
    return distances

# Distancias entre los archivos de los diferentes directorios
distances_executor_brisbane = calculate_hellinger_distances(quantum_executor_results, ibm_brisbane_results)
distances_executor_sherbrooke = calculate_hellinger_distances(quantum_executor_results, ibm_sherbrooke_results)
distances_scheduler_brisbane = calculate_hellinger_distances(quantum_executor_scheduler_results_brisbane, ibm_brisbane_results)
distances_scheduler_sherbrooke = calculate_hellinger_distances(quantum_executor_scheduler_results_sherbrooke, ibm_sherbrooke_results)
#TODO add here the distances between the results of the individuals and the results of the qe+scheduler
distances_executor_plus_scheduler_brisbane = calculate_hellinger_distances(quantum_executor_plus_scheduler_results, ibm_brisbane_results)
distances_executor_plus_scheduler_sherbrooke = calculate_hellinger_distances(quantum_executor_plus_scheduler_results, ibm_sherbrooke_results)
distances_executor_plus_scheduler_plus_autoscheduler_brisbane = calculate_hellinger_distances(quantum_executor_plus_scheduler_plus_autoscheduler_results, ibm_brisbane_results)
distances_executor_plus_scheduler_plus_autoscheduler_sherbrooke = calculate_hellinger_distances(quantum_executor_plus_scheduler_plus_autoscheduler_results, ibm_sherbrooke_results)

##############################
# PROMEDIO DE DISTANCIAS
##############################

def average_distances(distances1, distances2):
    """Calcula el promedio de las distancias de Hellinger entre dos conjuntos."""
    averaged_distances = {}
    for filename in distances1.keys():
        if filename in distances2:
            averaged_distances[filename] = (distances1[filename] + distances2[filename]) / 2
    return averaged_distances

executor_avg_distances = average_distances(distances_executor_brisbane, distances_executor_sherbrooke)
scheduler_avg_distances = average_distances(distances_scheduler_brisbane, distances_scheduler_sherbrooke)
qe_plus_scheduler_avg_distances = average_distances(distances_executor_plus_scheduler_brisbane, distances_executor_plus_scheduler_sherbrooke)
quantum_executor_plus_scheduler_plus_autoscheduler_avg_distances = average_distances(distances_executor_plus_scheduler_plus_autoscheduler_brisbane, distances_executor_plus_scheduler_plus_autoscheduler_sherbrooke)

##############################
# PLOT DE RESULTADOS
##############################

def plot_combined_distances(executor_distances, scheduler_distances, qe_scheduler_distances, qe_scheduler_plus_autoscheduler_distances):

    circuits = [
    "Simon", "Teleportation", "QFT", "Berstein-Vazirani", "Shor", "Full adder",
    "QWalk", "Kickback", "QAOA", "TSP", "Phase estimation", "Deutsch-Jozsa", "Grover"
    ]
    executor_values = list(executor_distances.values())
    scheduler_values = list(scheduler_distances.values())
    qe_scheduler_values = list(qe_scheduler_distances.values())
    qe_scheduler_autoscheduler_values = list(qe_scheduler_plus_autoscheduler_distances.values())

    x = range(len(circuits))

    plt.figure(figsize=(12, 6))
    plt.plot(x, executor_values, label="Quantum Executor", marker='o', linestyle='-')
    plt.plot(x, scheduler_values, label="Scheduler", marker='o', linestyle='-')
    plt.plot(x, qe_scheduler_values, label="QE+Scheduler", marker='o', linestyle='-')
    plt.plot(x, qe_scheduler_autoscheduler_values, label="QE+Scheduler+AutoScheduler", marker='o', linestyle='-')
    plt.xticks(x, circuits, rotation=45)
    plt.xlabel("Circuit")
    plt.ylabel("Hellinger Distance")
    plt.title("Hellinger Distances Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"quantum-executor-plots/noise-comparison.png")

def plot_heatmap_distances(executor_distances, scheduler_distances, qe_scheduler_distances, qe_scheduler_plus_autoscheduler_distances):
    circuits = [
        "Simon", "Teleportation", "QFT", "Berstein-Vazirani", "Shor", "Full adder",
        "QWalk", "Kickback", "QAOA", "TSP", "Phase estimation", "Deutsch-Jozsa", "Grover"
    ]
    
    # Create data matrix
    data = np.array([
        list(executor_distances.values()),
        list(scheduler_distances.values()),
        list(qe_scheduler_distances.values()),
        list(qe_scheduler_plus_autoscheduler_distances.values())
    ])
    
    methods = ["Quantum Executor", "Scheduler", "QE+Scheduler", "QE+Scheduler+AutoScheduler"]
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(data, 
                xticklabels=circuits, 
                yticklabels=methods, 
                annot=True, 
                fmt='.3f', 
                cmap='viridis',
                cbar_kws={'label': 'Hellinger Distance'})
    plt.title("Hellinger Distances Heatmap")
    plt.xlabel("Circuit")
    plt.ylabel("Method")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("quantum-executor-plots/noise-heatmap.png")    

def plot_boxplot_distances(executor_distances, scheduler_distances, qe_scheduler_distances, qe_scheduler_plus_autoscheduler_distances):
    data = [
        list(executor_distances.values()),
        list(scheduler_distances.values()),
        list(qe_scheduler_distances.values()),
        list(qe_scheduler_plus_autoscheduler_distances.values())
    ]
    
    labels = ["Quantum Executor", "Scheduler", "QE+Scheduler", "QE+Scheduler+AutoScheduler"]
    
    plt.figure(figsize=(10, 6))
    plt.boxplot(data, tick_labels=labels)
    plt.ylabel("Hellinger Distance")
    plt.title("Hellinger Distance Distribution by Method")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("quantum-executor-plots/noise-boxplot.png")

def plot_grouped_bar_distances(executor_distances, scheduler_distances, qe_scheduler_distances, qe_scheduler_plus_autoscheduler_distances):
    circuits = [
        "Simon", "Teleportation", "QFT", "Berstein-Vazirani", "Shor", "Full adder",
        "QWalk", "Kickback", "QAOA", "TSP", "Phase estimation", "Deutsch-Jozsa", "Grover"
    ]
    
    x = np.arange(len(circuits))
    width = 0.2
    
    plt.figure(figsize=(14, 6))
    plt.bar(x - 1.5*width, list(executor_distances.values()), width, label='Quantum Executor', color='C0')
    plt.bar(x - 0.5*width, list(scheduler_distances.values()), width, label='Scheduler', color='C1')
    plt.bar(x + 0.5*width, list(qe_scheduler_distances.values()), width, label='QE+Scheduler', color='C2')
    plt.bar(x + 1.5*width, list(qe_scheduler_plus_autoscheduler_distances.values()), width, label='QE+Scheduler+AutoScheduler', color='C3')
    
    plt.xlabel('Circuit')
    plt.ylabel('Hellinger Distance')
    plt.title('Hellinger Distance Comparison by Circuit')
    plt.xticks(x, circuits, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("quantum-executor-plots/noise-grouped-bar.png")

plot_combined_distances(executor_avg_distances, scheduler_avg_distances, qe_plus_scheduler_avg_distances, quantum_executor_plus_scheduler_plus_autoscheduler_avg_distances)
plot_heatmap_distances(executor_avg_distances, scheduler_avg_distances, qe_plus_scheduler_avg_distances, quantum_executor_plus_scheduler_plus_autoscheduler_avg_distances)
plot_boxplot_distances(executor_avg_distances, scheduler_avg_distances, qe_plus_scheduler_avg_distances, quantum_executor_plus_scheduler_plus_autoscheduler_avg_distances)
plot_grouped_bar_distances(executor_avg_distances, scheduler_avg_distances, qe_plus_scheduler_avg_distances, quantum_executor_plus_scheduler_plus_autoscheduler_avg_distances)

print(f"Average Hellinger Distances for Quantum Executor: {sum(executor_avg_distances.values()) / len(executor_avg_distances)}")
print(f"Average Hellinger Distances for Scheduler: {sum(scheduler_avg_distances.values()) / len(scheduler_avg_distances)}")
print(f"Average Hellinger Distances for QE + Scheduler: {sum(qe_plus_scheduler_avg_distances.values()) / len(qe_plus_scheduler_avg_distances)}")
print(f"Average Hellinger Distances for QE + Scheduler + AutoScheduler: {sum(quantum_executor_plus_scheduler_plus_autoscheduler_avg_distances.values()) / len(quantum_executor_plus_scheduler_plus_autoscheduler_avg_distances)}")