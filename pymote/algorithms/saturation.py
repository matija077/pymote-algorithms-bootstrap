from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from pymote.sensor import NeighborsSensor
import random


class saturacija(NodeAlgorithm):
    #required_params = ('informationKey',)
    #default_params = {'neighborsKey':'Neighbors', 'temperatureKey': 'Temperature', 'maxtempKey': 'Maxtemp'}
    default_params = {'neighborsKey': 'Neighbors', 'saturationKey': 'saturation_neighbors'}
    network_ini_nodes_percentage = 0.3
    def initializer(self):
        ini_nodes = []
        for i in range (int(len(self.network.nodes())*self.network_ini_nodes_percentage)):
            self.randomini = random.randint(0,len(self.network.nodes())-1)
            ini_nodes.append(self.network.nodes()[self.randomini])
        for node in self.network.nodes():
            node.compositeSensor = ('NeighborsSensor')
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.memory['neighbors'] = node.compositeSensor.read()['Neighbors']

            self.initialize(node)
            #node.memory['Maxtemp'] = node.compositeSensor.read()['Temp']
            node.memory['Ini'] = 0
            node.status = 'AVAILABLE'
            #if node.memory.has_key(self.informationKey):
            #    node.status = 'INITIATOR'
            #    ini_nodes.append(node)
        print (ini_nodes)
        for ini_node in ini_nodes:
            ini_node.memory['Ini'] = 1
            self.network.outbox.insert(0,Message(header=NodeAlgorithm.INI,
                                                 destination=ini_node))

    def available(self, node, message):
        # OVO JE ZA PRVOG (INIT)
        if message.header==NodeAlgorithm.INI:
            node.send(Message(header='Wakeup'))
            if (len(node.memory['neighbors']) == 1): # Poseban slucaj kad init ima samo 1 susjeda? (Graf ima 2 cvora)
                prepared_data = self.prepare_message(node)
                node.send(Message(header='M', data=prepared_data,
                destination=node.memory['neighbors']))
                node.status = 'PROCESSING'
            else:
                node.status = 'ACTIVE'
        # OVO JE ZA SVE OSTALE CVOROVE
        if message.header=='Wakeup':
            destination_nodes = list(node.memory['neighbors'])
            destination_nodes.remove(message.source) # Pobrisali smo sendera iz liste primatelja
            node.send(Message(header='Wakeup', destination=destination_nodes))
            if (len(node.memory['neighbors']) == 1):
                '''#prepared_data = ""
                #self.prepare_message(prepared_data)
                prepared_data = "Saturation"'''
                prepared_data = self.prepare_message(node)
                node.send(Message(header="M", data = prepared_data,
                destination=node.memory['neighbors']))
                node.status = 'PROCESSING'
                #debug
                print 'saturation_avaiable_1' + str(node.memory[self.nofNKey])
            else:
                node.status = 'ACTIVE'
                #debug
                print 'saturation_available_multiple' + str(node.memory[self.nofNKey])

    def active(self, node, message):
        if message.header=="M":
            node.memory['neighbors'].remove(message.source)
            self.process_message(node, message)
            destination_nodes = list(node.memory['neighbors'])
            if len(node.memory["neighbors"])==1:
                '''#prepared_data = ""
                #self.prepare_message(prepared_data)
                prepared_data = "Saturation"'''
                #debug
                print 'saturation' + str(node.memory[self.nofNKey])
                prepared_data = self.prepare_message(node)
                node.send(Message(header="M", data = prepared_data,
                destination=node.memory["neighbors"]))
                node.status = 'PROCESSING'

    def processing(self, node, message):
        if message.header=="M":
            self.process_message(node, message)
            node.memory['neighbors'].remove(message.source)
            self.resolve(node)

    def initialize(self, node):
        pass

    def saturated(self, node, message):
        pass

    def prepare_message(self, prepared_data):
        #debug
        print 'saturation_prepare_message'
        #prepared_data = "Saturation"

    def process_message(self,node,message):
        pass
        #node.memory['neighbors'].remove(message.source)

    def resolve(self, node):
        node.status = "SATURATED"


    STATUS = {
              'AVAILABLE' : available,
              'ACTIVE': active,
              'PROCESSING': processing,
              'SATURATED': saturated,
    }