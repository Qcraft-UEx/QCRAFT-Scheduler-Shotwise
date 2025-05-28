from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from quantum_executor import QuantumExecutor
from quantum_executor.result_collector import ResultCollector, MergedResultCollector
import requests
from time import sleep
import json
import numpy as np

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
        elif gate.params:
            # Format parameters properly
            params = ', '.join(str(param) for param in gate.params)
            code += f"circuit.{gate_name}({params}, {qubit_args})\n"
        else:
            code += f"circuit.{gate_name}({qubit_args})\n"
    
    return code

# Qiskit circuit
qreg_q = QuantumRegister(9, 'q')
creg_c = ClassicalRegister(9, 'c')
qiskit_circuit = QuantumCircuit(qreg_q, creg_c)

qiskit_circuit.h(qreg_q[0])
qiskit_circuit.h(qreg_q[1])
qiskit_circuit.h(qreg_q[2])
qiskit_circuit.h(qreg_q[3])
qiskit_circuit.h(qreg_q[4])
qiskit_circuit.h(qreg_q[5])
qiskit_circuit.h(qreg_q[6])
qiskit_circuit.h(qreg_q[7])
qiskit_circuit.x(qreg_q[8])
qiskit_circuit.h(qreg_q[8])
qiskit_circuit.cx(qreg_q[0], qreg_q[8])
qiskit_circuit.cx(qreg_q[1], qreg_q[8])
qiskit_circuit.h(qreg_q[0])
qiskit_circuit.cx(qreg_q[2], qreg_q[8])
qiskit_circuit.h(qreg_q[1])
qiskit_circuit.cx(qreg_q[3], qreg_q[8])
qiskit_circuit.h(qreg_q[2])
qiskit_circuit.cx(qreg_q[4], qreg_q[8])
qiskit_circuit.h(qreg_q[3])
qiskit_circuit.cx(qreg_q[5], qreg_q[8])
qiskit_circuit.h(qreg_q[4])
qiskit_circuit.cx(qreg_q[6], qreg_q[8])
qiskit_circuit.h(qreg_q[5])
qiskit_circuit.measure(qreg_q[5], creg_c[5])
qiskit_circuit.cx(qreg_q[7], qreg_q[8])
qiskit_circuit.h(qreg_q[6])
qiskit_circuit.h(qreg_q[7])
qiskit_circuit.h(qreg_q[8])
qiskit_circuit.measure(qreg_q[0], creg_c[0])
qiskit_circuit.measure(qreg_q[1], creg_c[1])
qiskit_circuit.measure(qreg_q[2], creg_c[2])
qiskit_circuit.measure(qreg_q[3], creg_c[3])
qiskit_circuit.measure(qreg_q[4], creg_c[4])
qiskit_circuit.measure(qreg_q[6], creg_c[6])
qiskit_circuit.measure(qreg_q[7], creg_c[7])
qiskit_circuit.measure(qreg_q[8], creg_c[8])

dispatch = {
    "local_aer": [  # Local Aer provider
        "aer_simulator",
        "aer_simulator"
    ]
}

executor = QuantumExecutor()
results = executor.generate_dispatch(qiskit_circuit, [1000,1000], dispatch)

print("Dispatch results:", results)

print(executor.default_providers())


url = 'http://localhost:8082/'
pathURL = 'url'
pathResult = 'result'
pathCircuit = 'code'

jobs_records = []

dispatch_obj = results[0].to_dict()
for provider_name, machines in dispatch_obj.items():
    
    for machine_name, jobs in machines.items():
        # Process each job individually
        for job in jobs:
            qc = job['circuit']      # Get circuit from this specific job
            shots = job['shots']     # Get shots for this job
            quantum_executor_id = job['id']
            
            # Generate circuit code str using the autoscheduler
            # This is a workaround to get the circuit code as a string
            # Another way is to put the circuit in a file and read it or put the previous circuit code in a string
            circuit = "from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\n"
            circuit += circuit_to_code_ibm(qc)
            
            # Submit this specific job
            machine = 'local' if machine_name == 'aer_simulator' else machine_name
            data = {"code": circuit, "shots": shots, "policy": "shots", "machine": machine}
            scheduler_id = requests.post(url+pathCircuit, json=data).text
            jobs_records.append({
                'scheduler_id': scheduler_id,
                'quantum_executor_id': quantum_executor_id,
                'provider_name': provider_name,
                'machine_name': machine_name,
                'result': None
            })

while any(record['result'] is None for record in jobs_records):
    for record in jobs_records:
        if record['result'] is None:
            try:
                scheduler_data = requests.get(url+pathResult+f"?id={record['scheduler_id']}")
                if 'value' in scheduler_data.json():
                    parsed = json.loads(scheduler_data.json()) 
                    record['result'] = parsed[0]['value']
            except requests.exceptions.RequestException as e:
                print(f"Error fetching result for scheduler ID {scheduler_id}: {e}")
            except ValueError as e:
                print(f"Error decoding JSON for scheduler ID {scheduler_id}: {e}")

    sleep(10)

collector = ResultCollector()

for record in jobs_records:
    collector.register_job_mapping(record['quantum_executor_id'], record['provider_name'], record['machine_name'])
    collector.store_result(record['quantum_executor_id'], record['result'])

results_by_provider = collector.get_results()
print("Results by provider and backend:")
print(results_by_provider)

merged_counts = {}

for provider, backends in results_by_provider.items():
    for backend, results_list in backends.items():
        for result in results_list:
            if not result:
                continue
            for bit_string, count in result.items():
                merged_counts[bit_string] = merged_counts.get(bit_string, 0) + count

print("Merged counts:", merged_counts)