from qiskit import transpile
import qiskit.providers
from qiskit_ibm_runtime import SamplerV2 as Sampler, QiskitRuntimeService
from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate
from qiskit_aer import AerSimulator
import json
import os
import qiskit
import numpy as np
import re
import threading
from quantum_executor import QuantumExecutor


dispatch = {
    "local_aer": ['aer_simulator', 'aer_simulator']
}
executor = QuantumExecutor()
total_shots = [1000]  # Create a list of shots for each circuit
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure(0, 0)
circuit.measure(1, 1)
dispatch_ = executor.generate_dispatch(circuit, total_shots, dispatch)[0]
print("Dispatch generated:", dispatch_)
results = executor.run_dispatch(
    dispatch=dispatch_,
    multiprocess=False,  # Multi-process execution
    wait=True        # Non-blocking call
)
        
results_dict = results.get_results()

aggregated = {}
for provider, backends in results_dict.items():
    for backend, result_list in backends.items():
        for result in result_list:
            if isinstance(result, dict) and not result.get('error'):
                for bit_string, count in result.items():
                    aggregated[bit_string] = aggregated.get(bit_string, 0) + count
    
print("Aggregated results:", aggregated)