import requests
import time
import json 

#url = 'http://54.155.193.167:8082/'
url = 'http://localhost:8082/'
pathURL = 'code'
pathResult = 'result'
pathCircuit = 'circuit'

circuit="from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\nqreg_q = QuantumRegister(2, 'q')\ncreg_c = ClassicalRegister(2, 'c')\n\ncircuit = QuantumCircuit(qreg_q, creg_c)\ncircuit.h(qreg_q[0])\ncircuit.cx(qreg_q[0],qreg_q[1])\ncircuit.measure(qreg_q[0], creg_c[0])\ncircuit.measure(qreg_q[1], creg_c[1])"

data = {"code":circuit ,"shots" : 10000}
print(requests.post(url+pathURL, json = data).text)