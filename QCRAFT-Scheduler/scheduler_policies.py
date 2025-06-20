import json
import requests
from flask import request
import re
from executeCircuitIBM import executeCircuitIBM
from executeCircuitAWS import runAWS, runAWS_save, code_to_circuit_aws, obtain_machine_aws, get_available_machines_aws
from ResettableTimer import ResettableTimer
from threading import Thread
from typing import Callable

class Policy:
    """
    Class to store the queues and timers of a policy
    """
    def __init__(self, policy, machine_qubits, time_limit_seconds, executeCircuit, aws_machines, ibm_machines):
        """
        Attributes:
            queues (dict): The queues of the policy
            timers (dict): The timers of the policy
        """
        self.queues = {'ibm': {}, 'aws': {}}
        self.timers = {'ibm': {}, 'aws': {}}

        for machine in ibm_machines:
            self.queues['ibm'][machine] = []
            self.timers['ibm'][machine] = ResettableTimer(
                time_limit_seconds, 
                lambda m=machine: policy(self.queues['ibm'][m], machine_qubits['ibm'][m], 'ibm', executeCircuit, m)
            )

        for machine in aws_machines:
            self.queues['aws'][machine] = []
            self.timers['aws'][machine] = ResettableTimer(
                time_limit_seconds, 
                lambda m=machine: policy(self.queues['aws'][m], machine_qubits['aws'][m], 'aws', executeCircuit, m)
            )

class SchedulerPolicies:
    """
    Class to manage the policies of the scheduler

    Methods:
    --------
    service(service_name) 
        The request handler, adding the circuit to the selected queue
    
    executeCircuit(data,qb,shots,provider,urls)
        Executes the circuit in the selected provider
    
    most_repetitive(array)
        Returns the most repetitive element in an array
    
    create_circuit(urls,code,qb,provider)
        Creates the circuit to execute based on the URLs
    
    send_shots_optimized(queue, max_qubits, provider, executeCircuit, machine)
        Sends the URLs to the server with the minimum number of shots using the shots_optimized policy
    
    send_shots_depth(queue, max_qubits, provider, executeCircuit, machine)
        Sends the URLs to the server with the minimum number of shots and similar depth using the shots_depth policy
    
    send_depth(queue, max_qubits, provider, executeCircuit, machine)
        Sends the URLs to the server with the most similar depth using the depth policy
    
    send_shots(queue, max_qubits, provider, executeCircuit, machine)
        Sends the URLs to the server with the minimum number of shots using the shots policy
    
    send(queue, max_qubits, provider, executeCircuit, machine)
        Sends the URLs to the server using the time policy
    """
    def __init__(self, app):
        """
        Initializes the SchedulerPolicies class

        Attributes:
            app (Flask): The Flask app            
            time_limit_seconds (int): The time limit in seconds            
            max_qubits (int): The maximum number of qubits            
            machine_ibm (str): The IBM machine            
            machine_aws (str): The AWS machine            
            services (dict): The services of the scheduler            
            translator (str): The URL of the translator            
            unscheduler (str): The URL of the unscheduler
        """
        self.app = app
        self.time_limit_seconds = 90
        self.executeCircuitIBM = executeCircuitIBM()

        self.available_devices_ibm = ['local'] + self.executeCircuitIBM.get_available_machines()
        self.available_devices_aws = ['local'] + get_available_machines_aws()

        print(f"Available devices IBM: {self.available_devices_ibm}")
        print(f"Available devices AWS: {self.available_devices_aws}")

        self.machine_qubits = {'ibm': {}, 'aws': {}}
        for machine in self.available_devices_ibm:
            if machine == 'local':
                self.machine_qubits['ibm'][machine] = 10
            else:
                self.machine_qubits['ibm'][machine] = self.executeCircuitIBM.obtain_machine(self.executeCircuitIBM.load_account_ibm(), machine).configuration().n_qubits
        
        for machine in self.available_devices_aws:
            self.machine_qubits['aws'][machine] = obtain_machine_aws(machine).properties.dict()['paradigm']['qubitCount']

        print(f"Machine qubits IBM: {self.machine_qubits['ibm']}")
        print(f"Machine qubits AWS: {self.machine_qubits['aws']}")

        self.services = {'time': Policy(self.send, self.machine_qubits, self.time_limit_seconds, self.executeCircuit, self.available_devices_aws, self.available_devices_ibm),
                        'shots': Policy(self.send_shots, self.machine_qubits, self.time_limit_seconds, self.executeCircuit, self.available_devices_aws, self.available_devices_ibm),
                        'depth': Policy(self.send_depth, self.machine_qubits, self.time_limit_seconds, self.executeCircuit, self.available_devices_aws, self.available_devices_ibm),
                        'shots_depth': Policy(self.send_shots_depth, self.machine_qubits, self.time_limit_seconds, self.executeCircuit, self.available_devices_aws, self.available_devices_ibm),
                        'shots_optimized': Policy(self.send_shots_optimized, self.machine_qubits, self.time_limit_seconds, self.executeCircuit, self.available_devices_aws, self.available_devices_ibm)}
        
        #Print the machine and qubits of each service
        for service in self.services:
            print(f"Service: {service}")
            for provider in self.services[service].queues:
                print(f"Provider: {provider}")
                for machine in self.services[service].queues[provider]:
                    print(f"Machine: {machine}, Qubits: {self.machine_qubits[provider][machine]}")
            

        self.translator = f"http://{self.app.config['TRANSLATOR']}:{self.app.config['TRANSLATOR_PORT']}/code/"
        self.unscheduler = f"http://{self.app.config['HOST']}:{self.app.config['PORT']}/unscheduler"
        self.app.route('/service/<service_name>', methods=['POST'])(self.service)
        

    def service(self, service_name:str) -> tuple:
        """
        The request handler, adding the circuit to the selected queue

        Args:
            service_name (str): The name of the service

        Request Parameters:
            circuit (str): The circuit to execute
            num_qubits (int): The number of qubits of the circuit            
            shots (int): The number of shots of the circuit            
            user (str): The user that executed the circuit
            circuit_name (str): The name of the circuit            
            maxDepth (int): The depth of the circuit            
            provider (str): The provider of the circuit
            machine (str): The machine to execute the circuit

        Returns:
            tuple: The response of the request
        """
        if service_name not in self.services:
            return 'This service does not exist', 404
        circuit = request.json['circuit']
        num_qubits = request.json['num_qubits']
        shots = request.json['shots']
        user = request.json['user']
        circuit_name = request.json['circuit_name']
        maxDepth = request.json['maxDepth']
        provider = request.json['provider']
        machine = request.json['machine']

        if(provider not in self.services[service_name].queues or machine not in self.services[service_name].queues[provider]):
            return 'This provider or machine does not exist', 404

        data = (circuit, num_qubits, shots, user, circuit_name, maxDepth)
        self.services[service_name].queues[provider][machine].append(data)
        if not self.services[service_name].timers[provider][machine].is_alive():
            self.services[service_name].timers[provider][machine].start()
        n_qubits = sum(item[1] for item in self.services[service_name].queues[provider][machine])
        if abs(n_qubits - self.machine_qubits[provider][machine]) <= 5 or n_qubits >= self.machine_qubits[provider][machine]:
            self.services[service_name].timers[provider][machine].execute_and_reset()
        return 'Data received', 200
        
    
    def executeCircuit(self,data:dict,qb:list,shots:list,provider:str,urls:list, machine:str) -> None: #Data is the composed circuit to execute, qb is the number of qubits per circuit, shots is the number of shots per circut, provider is the provider of the circuit, urls is the array with data of each circuit (url, num_qubits, shots, user, circuit_name)
        """
        Executes the circuit in the selected provider

        Args:
            data (dict): The data of the circuit to execute            
            qb (list): The number of qubits per circuit            
            shots (list): The number of shots per circuit
            provider (str): The provider of the circuit            
            urls (list): The data of each circuit            
            machine (str): The machine to execute the circuit

        Raises:
            Exception: If an error occurs during the execution of the circuit
        """

        circuit = ''
        for data in json.loads(data)['code']:
            circuit = circuit + data + '\n'
        loc = {}
        if provider == 'ibm':
            loc['circuit'] = self.executeCircuitIBM.code_to_circuit_ibm(circuit)
        else:
            loc['circuit'] = code_to_circuit_aws(circuit)
        try:
            if provider == 'ibm':

                counts = self.executeCircuitIBM.runIBM_save(machine,loc['circuit'],max(shots),[url[3] for url in urls],qb,[url[4] for url in urls])
            else:
                counts = runAWS_save(machine,loc['circuit'],max(shots),[url[3] for url in urls],qb,[url[4] for url in urls],'')
        except Exception as e:
            print(f"Error executing circuit: {e}")

        print(counts.items())

        data = {"counts": counts, "shots": shots, "provider": provider, "qb": qb, "users": [url[3] for url in urls], "circuit_names": [url[4] for url in urls]}

        requests.post(self.unscheduler, json=data)


    def most_repetitive(self, array:list) -> int: #Check the most repetitive element in an array and if there are more than one, return the smallest
        """
        Returns the most repetitive element in an array

        Args:
            array (list): The array to check
        
        Returns:
            int: The most repetitive element in the array
        """
        count_dict = {}
        for element in array: #Hashing the elements and counting them
            if element in count_dict:
                count_dict[element] += 1
            else:
                count_dict[element] = 1

        max_count = 0
        max_element = None
        for element, count in count_dict.items(): #Simple search for the higher element in the hash. If two elements have the same count, the smallest is returned
            if count > max_count or (count == max_count and element < max_element):
                max_count = count
                max_element = element

        return max_element

    def create_circuit(self,urls:list,code:list,qb:list,provider:str) -> None: #TODO add there the returning queue and in the other methods, check if the queue is not empty after the execution of thid method, so it adds the circuits back
        """
        Creates the circuit to execute based on the URLs

        Args:
            urls (list): The data of each circuit            
            code (list): The code of the composed circuit            
            qb (list): The number of qubits of each individual circuit            
            provider (str): The provider of the circuit
        """
        composition_qubits = 0
        for url, num_qubits, shots, user, circuit_name, depth in urls:
        #Change the q[...] and c[...] to q[composition_qubits+...] and c[composition_qubits+...]
            if 'algassert' in url: 
                # Send a request to the translator, in the post, the field url will be url and the field d will be composition_qubits
                try: # TODO, if error, maybe add the url to another list or something so its added after this to the waiting_urls queue
                    x = requests.post(self.translator+provider+'/individual', json = {'url':url, 'd':composition_qubits})
                except:
                    print("Error in the request to the translator")
                    # Add the url to the returning queue
                data = json.loads(x.text)
                for elem in data['code']:
                    code.append(elem)
            else:
                lines = url.split('\n')
                for i, line in enumerate(lines):
                    if provider == 'ibm':
                        line = line.replace('qreg_q[', f'qreg_q[{composition_qubits}+')
                        line = line.replace('meas[', f'meas[{composition_qubits}+')
                    elif provider == 'aws':
                        # In the AWS case, all elements have circuit. the integer elements in this line will be replaced by the element+composition_qubits
                        #line = re.sub(r'circuit\.(\w+)\(([\d, ]+)\)', lambda x: f'circuit.{x.group(1)}({", ".join(str(int(num)+composition_qubits) for num in x.group(2).split(","))})', line)
                        gate_name = re.search(r'circuit\.(.*?)\(', line).group(1)
                        if gate_name in ['rx', 'ry', 'rz', 'gpi', 'gpi2', 'phaseshift']:
                            # These gates have a parameter
                            # Edit the first parameter
                            line = re.sub(rf'{gate_name}\(\s*(\d+)', lambda m: f"{gate_name}({int(m.group(1)) + composition_qubits}", line, count=1)
                        elif gate_name in ['xx', 'yy', 'zz','ms'] or 'cphase' in gate_name:
                            # These gates have 2 parameters
                            # Edit the first and second parameters
                            line= re.sub(rf'{gate_name}\((\d+),\s*(\d+)', lambda m: f"{gate_name}({int(m.group(1)) + composition_qubits},{int(m.group(2)) + composition_qubits}", line, count=1)

                        else:
                            # These gates have no parameters, so change the number of qubits on all
                            line = re.sub(r'(\d+)', lambda m: str(int(m.group(1)) + composition_qubits), line)
                    code.append(line)
            composition_qubits += num_qubits
            qb.append(num_qubits)

        if provider == 'ibm':
            # Add at the first position of the code[]
            code.insert(0,"circuit = QuantumCircuit(qreg_q, meas)")
            code.insert(0, f"meas = ClassicalRegister({composition_qubits}, 'c')")  # Set composition_qubits as the number of classical bits
            code.insert(0, f"qreg_q = QuantumRegister({composition_qubits}, 'q')")  # Set composition_qubits as the number of classical bits
            code.insert(0,"from numpy import pi")
            code.insert(0,"import numpy as np")
            code.insert(0,"from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit")
            code.insert(0,"from qiskit.circuit.library import MCXGate, MCMT, XGate, YGate, ZGate")
            code.append("return circuit")
        elif provider == 'aws':
            code.insert(0,"circuit = Circuit()")
            code.insert(0,"from numpy import pi")
            code.insert(0,"import numpy as np")
            code.insert(0,"from collections import Counter")
            code.insert(0,"from braket.circuits import Circuit")
            code.append("return circuit")

    def send_shots_optimized(self,queue:list, max_qubits:int, provider:str, executeCircuit:Callable, machine:str) -> None:
        """
        Sends the URLs to the server with the minimum number of shots using the shots_optimized policy

        Args:
            queue (list): The waiting list
            max_qubits (int): The maximum number of qubits            
            provider (str): The provider of the circuit            
            executeCircuit (Callable): The function to execute the circuit            
            machine (str): The machine to execute the circuit
        """
        if len(queue) != 0:
            # Send the URLs to the server
            qb = []
            sumQb = 0
            urls = []
            iterator = queue.copy()
            iterator = sorted(iterator, key=lambda x: x[2]) #Sort the waiting list by shots ascending
            minShots = self.most_repetitive([url[2] for url in iterator]) #Get the most repetitive number of shots in the waiting list
            for url in iterator:
                if url[1]+sumQb <= max_qubits and url[2] >= minShots:
                    sumQb = sumQb + url[1]
                    urls.append(url)
                    index = queue.index(url)
                    #Reduce number of shots of the url in waiting_url instead of removing it
                    if queue[index][2] - minShots <= 0: #If the url has no shots left, remove it from the waiting list
                        queue.remove(url)
                    else:
                        old_tuple = queue[index]
                        new_tuple = old_tuple[:2] + (old_tuple[2] - minShots,) + old_tuple[3:]
                        queue[index] = new_tuple
            print(f"Sending {len(urls)} URLs to the server")
            print(urls)
            # Convert the dictionary to JSON
            code,qb = [],[]
            shotsUsr = [minShots] * len(urls) # The shots for all will be the most repetitive number of shots in the waiting list
            self.create_circuit(urls,code,qb,provider)
            data = {"code":code}
            Thread(target=executeCircuit, args=(json.dumps(data),qb,shotsUsr,provider,urls,machine)).start()
            #executeCircuit(json.dumps(data),qb,shotsUsr,provider,urls)
            self.services['shots_optimized'].timers[provider][machine].reset()

    def send_shots_depth(self,queue:list, max_qubits:int, provider:str, executeCircuit:Callable, machine:str) -> None:
        """
        Sends the URLs to the server with the minimum number of shots and similar depth using the shots_depth policy

        Args:
            queue (list): The waiting list            
            max_qubits (int): The maximum number of qubits            
            provider (str): The provider of the circuit            
            executeCircuit (Callable): The function to execute the circuit            
            machine (str): The machine to execute the circuit
        """
        # Send the URLs to the server
        if len(queue) != 0:
            qb = []
            sumQb = 0
            urls = []
            iterator = queue.copy()
            iterator = sorted(iterator, key=lambda x: x[2]) #Sort the waiting list by shots ascending
            minShots = iterator[0][2] #Get the minimum number of shots in the waiting list
            depth = iterator[0][5] #Get the depth of the first url in the waiting list
            for url in iterator:
                if url[1]+sumQb <= max_qubits and url[5] <= depth * 1.1 and url[5] >= depth * 0.9:
                    sumQb = sumQb + url[1]
                    urls.append(url)
                    index = queue.index(url)
                    #Reduce number of shots of the url in waiting_url instead of removing it
                    if queue[index][2] - minShots <= 0: #If the url has no shots left, remove it from the waiting list
                        queue.remove(url)
                    else:
                        old_tuple = queue[index]
                        new_tuple = old_tuple[:2] + (old_tuple[2] - minShots,) + old_tuple[3:]
                        queue[index] = new_tuple
            print(f"Sending {len(urls)} URLs to the server")
            print(urls)
            code,qb = [],[]
            shotsUsr = [minShots] * len(urls) # The shots for all will be the minimum number of shots in the waiting list
            self.create_circuit(urls,code,qb,provider)
            data = {"code":code}
            Thread(target=executeCircuit, args=(json.dumps(data),qb,shotsUsr,provider,urls,machine)).start()
            #executeCircuit(json.dumps(data),qb,shotsUsr,provider,urls)
            self.services['shots_depth'].timers[provider][machine].reset()

    def send_depth(self,queue:list, max_qubits:int, provider:str, executeCircuit:Callable, machine:str) -> None:
        """
        Sends the URLs to the server with the most similar depth using the depth policy

        Args:
            queue (list): The waiting list
            max_qubits (int): The maximum number of qubits            
            provider (str): The provider of the circuit            
            executeCircuit (Callable): The function to execute the circuit            
            machine (str): The machine to execute the circuit
        """
        # Send the URLs to the server
        if len(queue) != 0:
            print('Sent')
            qb = []
            # Convert the dictionary to JSON
            urls = []
            sumQb = 0
            depth = queue[0][5] #Get the depth of the first url in the waiting list
            iterator = queue.copy()
            iterator = iterator[:1] + sorted(iterator[1:], key=lambda x: abs(x[5] - depth)) #Sort the waiting list by difference in depth by the first circuit in the waiting list so it picks the most similar circuit (dont sort the first element because is the reference for the calculation)
            for url in iterator: #Add them to the valid_url only if they fit and are similar to the first circuit in the waiting list
                if url[1]+ sumQb <= max_qubits and url[5] <= depth * 1.1 and url[5] >= depth * 0.9:
                    urls.append(url)
                    sumQb += url[1]
                    queue.remove(url)
            print(f"Sending {len(urls)} URLs to the server")
            print(urls)
            code,qb = [],[]
            shotsUsr = [url[2] for url in urls] #Each one will have its own number of shots, a statistic will be used to get the results after
            self.create_circuit(urls,code,qb,provider)
            data = {"code":code}
            Thread(target=executeCircuit, args=(json.dumps(data),qb,shotsUsr,provider,urls,machine)).start()
            #executeCircuit(json.dumps(data),qb,shotsUsr,provider,urls)
            self.services['depth'].timers[provider][machine].reset()

    def send_shots(self,queue:list, max_qubits:int, provider:str, executeCircuit:Callable, machine:str) -> None:
        """
        Sends the URLs to the server with the minimum number of shots using the shots policy

        Args:
            queue (list): The waiting list            
            max_qubits (int): The maximum number of qubits            
            provider (str): The provider of the circuit            
            executeCircuit (Callable): The function to execute the circuit            
            machine (str): The machine to execute the circuit
        """
        # Send the URLs to the server
        if len(queue) != 0:
            print('Sent')
            qb = []
            sumQb = 0
            urls = []
            iterator = queue.copy()
            iterator = sorted(iterator, key=lambda x: x[2]) #Sort the waiting list by shots ascending
            minShots = iterator[0][2] #Get the minimum number of shots in the waiting list
            for url in iterator:
                if url[1]+sumQb <= max_qubits:
                    sumQb = sumQb + url[1]
                    urls.append(url)
                    index = queue.index(url)
                    #Reduce number of shots of the url in waiting_url instead of removing it
                    if queue[index][2] - minShots <= 0: #If the url has no shots left, remove it from the waiting list
                        queue.remove(url)
                    else:
                        old_tuple = queue[index]
                        new_tuple = old_tuple[:2] + (old_tuple[2] - minShots,) + old_tuple[3:]
                        queue[index] = new_tuple
            code,qb = [],[]
            shotsUsr = [minShots] * len(urls) # All the urls will have the minimum number of shots in the waiting list
            self.create_circuit(urls,code,qb,provider)
            data = {"code":code}
            Thread(target=executeCircuit, args=(json.dumps(data),qb,shotsUsr,provider,urls,machine)).start() #Parece que sin esto no se resetea el timer cuando termina de componer
            #executeCircuit(json.dumps(data),qb,shotsUsr,provider,urls)
            self.services['shots'].timers[provider][machine].reset()

    def send(self,queue:list, max_qubits:int, provider:str, executeCircuit:Callable, machine:str) -> None:
        """
        Sends the URLs to the server using the time policy

        Args:
            queue (list): The waiting list            
            max_qubits (int): The maximum number of qubits            
            provider (str): The provider of the circuit            
            executeCircuit (Callable): The function to execute the circuit            
            machine (str): The machine to execute the circuit
        """
        if len(queue) != 0:
            print('Sent')
            urls = []
            iterator = queue.copy() #Make a copy to not delete on search
            sumQb = 0
            for url in iterator:
                if url[1] + sumQb <= max_qubits: #Shots of current url + shots of all the urls on urls
                    urls.append(url)
                    sumQb += url[1]
                    queue.remove(url)
            code,qb = [],[]
            shotsUsr = [10000] * len(urls)
            #shotsUsr = [url[2] for url in urls] # Each url will have its own number of shots, a statistic will be used to get the results after
            self.create_circuit(urls,code,qb,provider)
            data = {"code":code}
            Thread(target=executeCircuit, args=(json.dumps(data),qb,shotsUsr,provider,urls,machine)).start()
            #executeCircuit(json.dumps(data),qb,shotsUsr,provider,urls)
            self.services['time'].timers[provider][machine].reset()
    
    def get_ibm(self):
        return self.executeCircuitIBM
    
    def get_available_devices_ibm(self) -> list:
        """
        Returns the available devices of the scheduler

        Returns:
            list: The available devices of the scheduler
        """
        return self.available_devices_ibm
    
    def get_available_devices_aws(self) -> list:
        """
        Returns the available devices of the scheduler

        Returns:
            list: The available devices of the scheduler
        """
        return self.available_devices_aws
