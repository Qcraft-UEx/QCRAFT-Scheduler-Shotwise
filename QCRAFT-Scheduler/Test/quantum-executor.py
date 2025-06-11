from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from quantum_executor import QuantumExecutor
from quantum_executor.result_collector import ResultCollector, MergedResultCollector
import requests
from time import sleep
import json
import numpy as np
import os
import importlib

def load_all_circuits():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the circuits directory
    circuits_dir = os.path.join(script_dir, "circuits")
    
    circuits = []
    for filename in os.listdir(circuits_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove the .py extension
            # Import the module dynamically
            module = importlib.import_module(f"circuits.{module_name}")
            if hasattr(module, "get_circuit"):
                circuit = module.get_circuit()
                if isinstance(circuit, QuantumCircuit):
                    circuits.append((filename,circuit))
    return circuits

def circuit_to_code_ibm(circuit) -> str:
    """
    Parses any Qiskit circuit into a string representation
    
    Args:
        circuit (qiskit.QuantumCircuit): The circuit that will be parsed.
    
    Returns:
        str: A string representation of the circuit.
    """
    code = ""
    
    # Handle various ways circuits might be constructed
    if len(circuit.qregs) == 0:
        # Circuit with no named registers - create default qreg
        code += f"qreg_q = QuantumRegister({circuit.num_qubits}, 'q')\n"
        qreg_dict = {i: 'qreg_q' for i in range(circuit.num_qubits)}
    else:
        # Handle multiple quantum registers if present
        qreg_dict = {}
        qubit_index = 0
        for qreg in circuit.qregs:
            code += f"{qreg.name} = QuantumRegister({len(qreg)}, '{qreg.name}')\n"
            for i in range(len(qreg)):
                qreg_dict[qubit_index] = qreg.name
                qubit_index += 1
    
    if len(circuit.cregs) == 0:
        # Circuit with no classical registers
        if circuit.num_clbits > 0:
            # If there are classical bits but no named register
            code += f"creg_c = ClassicalRegister({circuit.num_clbits}, 'c')\n"
            creg_dict = {i: 'creg_c' for i in range(circuit.num_clbits)}
        else:
            creg_dict = {}
    else:
        # Handle multiple classical registers if present
        creg_dict = {}
        clbit_index = 0
        for creg in circuit.cregs:
            code += f"{creg.name} = ClassicalRegister({len(creg)}, '{creg.name}')\n"
            for i in range(len(creg)):
                creg_dict[clbit_index] = creg.name
                clbit_index += 1
    
    # Create the quantum circuit with appropriate registers
    if len(circuit.qregs) == 0 and len(circuit.cregs) == 0:
        if circuit.num_clbits > 0:
            code += f"circuit = QuantumCircuit(qreg_q, creg_c)\n"
        else:
            code += f"circuit = QuantumCircuit(qreg_q)\n"
    else:
        registers = []
        for qreg in circuit.qregs:
            registers.append(qreg.name)
        for creg in circuit.cregs:
            registers.append(creg.name)
        code += f"circuit = QuantumCircuit({', '.join(registers)})\n"
    
    # Process all instructions
    for instruction in circuit.data:
        gate = instruction.operation
        qubits = instruction.qubits
        cbits = instruction.clbits
        gate_name = gate.name
        
        # Generate code for qubit indices
        qubit_indices = []
        for qubit in qubits:
            idx = circuit.qubits.index(qubit)
            reg_name = qreg_dict.get(idx)
            qubit_idx = idx
            for qreg in circuit.qregs:
                if qubit in qreg:
                    qubit_idx = qreg[:].index(qubit)
                    break
            qubit_indices.append(f"{reg_name}[{qubit_idx}]")
        qubit_args = ", ".join(qubit_indices)
        
        # Handle different gate types
        if gate_name == "measure":
            if cbits:
                cbit_indices = []
                for cbit in cbits:
                    idx = circuit.clbits.index(cbit)
                    reg_name = creg_dict.get(idx)
                    cbit_idx = idx
                    for creg in circuit.cregs:
                        if cbit in creg:
                            cbit_idx = creg[:].index(cbit)
                            break
                    cbit_indices.append(f"{reg_name}[{cbit_idx}]")
                cbit_args = ", ".join(cbit_indices)
                code += f"circuit.{gate_name}({qubit_args}, {cbit_args})\n"
            else:
                # Handle measurements without classical bits
                code += f"circuit.{gate_name}({qubit_args})\n"
        elif hasattr(gate, 'condition') and gate.condition is not None:
            # Handle conditional operations
            condition_bits, condition_value = gate.condition
            for param in gate.params[0].data:
                for creg in circuit.cregs:
                    operation = param.operation.name

                    creg_name = creg.name
                    if len(cbits) > 1:
                        cbit_args = f"{creg_name}"
                    else:
                        clbit_index = cbits[0]._index
                        cbit_args = f"{creg_name}[{clbit_index}]"

                    code += f"circuit.{operation}({qubit_args}).c_if({cbit_args}, {condition_value})\n"
        elif gate.params:
            # Format parameters properly
            params = ', '.join(str(param) for param in gate.params)
            code += f"circuit.{gate_name}({params}, {qubit_args})\n"
        else:
            code += f"circuit.{gate_name}({qubit_args})\n"
    
    return code

qiskit_circuits = load_all_circuits()

dispatch = {
    "local_aer": [  # Local Aer provider
        "ibm_brisbane",
        "ibm_sherbrooke",
        #"aer_simulator"
    ]
}#para qe+scheduler poner que se lancen todas a la vez pero en ambos proveedores, asi se van a lanzar 2 ejecuciones de 5000 shots

url = 'http://localhost:8082/'
pathURL = 'url'
pathResult = 'result'
pathCircuit = 'code'

executor = QuantumExecutor()

all_jobs_records = []

for i, (filename, qiskit_circuit) in enumerate(qiskit_circuits):
    print(f"Processing circuit: {filename}")

    results = executor.generate_dispatch(qiskit_circuit, 10000, dispatch)

    print("Dispatch results:", results)

    print(executor.default_providers())

    dispatch_obj = results[0].to_dict()
    for provider_name, machines in dispatch_obj.items():
        for machine_name, jobs in machines.items():
            # Process each job individually
            for job in jobs:
                qc = job['circuit']      # Get circuit from this specific job
                shots = job['shots']     # Get shots for this job
                quantum_executor_id = job['id']

                # Generate circuit code str using the autoscheduler
                circuit = "from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\n"
                circuit += circuit_to_code_ibm(qc)

                # Submit this specific job
                machine = 'local' if machine_name == 'aer_simulator' else machine_name
                data = {"code": circuit, "shots": shots, "policy": "shots", "machine": machine}
                scheduler_id = requests.post(url + pathCircuit, json=data).text
                all_jobs_records.append({
                    'scheduler_id': scheduler_id,
                    'quantum_executor_id': quantum_executor_id,
                    'provider_name': provider_name,
                    'machine_name': machine_name,
                    'result': None,
                    'filename': filename  # Track the circuit filename
                })

# Phase 2: Poll for results
while any(record['result'] is None for record in all_jobs_records):
    for record in all_jobs_records:
        if record['result'] is None:
            try:
                scheduler_data = requests.get(url + pathResult + f"?id={record['scheduler_id']}")
                if 'value' in scheduler_data.json():
                    parsed = json.loads(scheduler_data.json())
                    print(parsed)
                    record['result'] = parsed[0]['value']

            except requests.exceptions.RequestException as e:
                print(f"Error fetching result for scheduler ID {record['scheduler_id']}: {e}")
            except ValueError as e:
                print(f"Error decoding JSON for scheduler ID {record['scheduler_id']}: {e}")

    sleep(10)

# Phase 3: Process results
collector = ResultCollector()

for record in all_jobs_records:
    collector.register_job_mapping(record['quantum_executor_id'], record['provider_name'], record['machine_name'])
    collector.store_result(record['quantum_executor_id'], record['result'])

results_by_provider = collector.get_results()
print("Results by provider and backend:")
print(results_by_provider)

# Group results by circuit filename
merged_counts_by_circuit = {}

for record in all_jobs_records:
    filename = record['filename']
    if filename not in merged_counts_by_circuit:
        merged_counts_by_circuit[filename] = {}

    result = record['result']
    if result:
        for bit_string, count in result.items():
            merged_counts_by_circuit[filename][bit_string] = (
                merged_counts_by_circuit[filename].get(bit_string, 0) + count
            )

# Print merged counts for each circuit
for filename, counts in merged_counts_by_circuit.items():
    print(f"Merged counts for {filename}: {counts}")

# Save results for each circuit
for filename, counts in merged_counts_by_circuit.items():
    with open(f"results/results_{filename}.json", "w") as f:
        json.dump(counts, f, indent=4)