from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def get_circuit():

    qreg_q = QuantumRegister(6, 'q')
    creg_c = ClassicalRegister(6, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)

    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[2])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2], qreg_q[3], qreg_q[4], qreg_q[5])
    circuit.cx(qreg_q[0], qreg_q[3])
    circuit.cx(qreg_q[1], qreg_q[4])
    circuit.cx(qreg_q[2], qreg_q[5])
    circuit.cx(qreg_q[1], qreg_q[4])
    circuit.cx(qreg_q[1], qreg_q[5])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2], qreg_q[3], qreg_q[4], qreg_q[5])
    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[2])
    circuit.measure(qreg_q[0], creg_c[0])
    circuit.measure(qreg_q[1], creg_c[1])
    circuit.measure(qreg_q[2], creg_c[2])
    circuit.measure(qreg_q[3], creg_c[3])
    circuit.measure(qreg_q[4], creg_c[4])
    circuit.measure(qreg_q[5], creg_c[5])

    return circuit