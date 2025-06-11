import matplotlib.pyplot as plt

scheduler_tasks = 1
quantum_executor_tasks = 26
individual_tasks = 13
qe_plus_scheduler_tasks = 2

labels = ["Quantum Executor", "Scheduler", "QE+Sched", "QE+Sched+Auto" , "Individual"]
tasks = [26, 1, 2, 2 ,13]

plt.figure(figsize=(8, 6))
plt.bar(labels, tasks, color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#7F525D"])
plt.xlabel("Task Type")
plt.ylabel("Number of Tasks")
plt.title("Number of Tasks by Type")
plt.tight_layout()
plt.savefig("quantum-executor-plots/tasks-comparison.png")