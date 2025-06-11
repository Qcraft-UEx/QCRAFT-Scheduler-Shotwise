from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np

def get_circuit():

    qreg_q = QuantumRegister(3, 'q')
    creg_c = ClassicalRegister(3, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)

    circuit.h(qreg_q[0])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2])
    circuit.h(qreg_q[1])
    circuit.cx(qreg_q[1], qreg_q[2])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2])
    circuit.h(qreg_q[0])
    circuit.p(np.pi / 4, qreg_q[0])
    circuit.h(qreg_q[0])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2])
    circuit.cx(qreg_q[0], qreg_q[1])
    circuit.h(qreg_q[0])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2])
    circuit.measure(qreg_q[0], creg_c[0])
    circuit.measure(qreg_q[1], creg_c[1])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2])
    with circuit.if_test((creg_c[0], 1)):
        circuit.z(qreg_q[1])
    with circuit.if_test((creg_c[1], 1)):
        circuit.x(qreg_q[2])

    return circuit