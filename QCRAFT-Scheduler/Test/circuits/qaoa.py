from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

def get_circuit():

    qreg_q = QuantumRegister(2, 'q')
    creg_c = ClassicalRegister(2, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)

    circuit.rx(0.5, qreg_q[0])
    circuit.rx(0.5, qreg_q[1])
    circuit.cx(qreg_q[0], qreg_q[1])
    circuit.rx(0.5, qreg_q[1])
    circuit.rx(0.5, qreg_q[0])
    circuit.rx(0.5, qreg_q[1])
    circuit.cx(qreg_q[0], qreg_q[1])
    circuit.rx(0.5, qreg_q[0])
    circuit.measure(qreg_q[0], creg_c[0])
    circuit.measure(qreg_q[1], creg_c[1])

    return circuit