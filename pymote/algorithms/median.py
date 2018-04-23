from pymote.algorithm import Message
from pymote.algorithms.saturation import saturacija
from pymote.algorithm import NodeAlgorithm

class Median(saturacija):
    required_params = {}
    default_params = {'nofNKey': 'NumberOfNeighbors', 'nKey': 'NumberOfNodesInNetwork',
    'constantNeighborsKey': 'constantNeighbors'}

    def initialize(self, node):
        node.memory[self.nofNKey] = {}
        node.memory[self.constantNeighborsKey] = node.compositeSensor.read()['Neighbors']
        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.nofNKey][neighbor] = 0

    def processing(self, node, message):
        saturacija.processing(self, node, message)
        if message.header=="Median":
            node.memory[self.nKey] = message.data
            node.memory[self.nofNKey][message.source] = node.memory[self.nKey] -(sum(node.memory[self.nofNKey].values()) + 1)
            prepared_destination = list(x for x in node.memory[self.constantNeighborsKey] if x != message.source)
            node.send(Message(header='Median', destination=prepared_destination,
            data=node.memory[self.nKey]))
            if self.determine_self_median(node)==True:
                node.status = 'MEDIAN'
            else:
                node.status = 'NON_MEDIAN'

    def non_median(self, node, message):
        pass

    def median(self, node, message):
        pass

    def saturated_median(self, node, message):
        pass

    def prepare_message(self, node):
        #debug
        print 'median' + str(node.memory[self.nofNKey])
        return int(sum(node.memory[self.nofNKey].values())) + 1

    def process_message(self, node, message):
        node.memory[self.nofNKey][message.source] = message.data
        pass

    def resolve(self, node):
        node.memory[self.nKey] = sum(node.memory[self.nofNKey].values()) + 1
        #destination_list = list(set(node.memory[self.constantNeighborsKey]) -
        #set(node.memory[self.neighborsKey]))
        node.send(Message(header='Median', destination=node.memory[self.constantNeighborsKey],
        data=node.memory[self.nKey]))
        if self.determine_self_median(node)==True:
            node.status = 'SATURATED_MEDIAN'
        else:
            node.status = 'SATURATED'

    def determine_self_median(self, node):
        #debug
        '''node.memory['test'] = [-1]
        for neighbor in node.memory[self.nofNKey]:
            T = self.calculate_G(node.memory[self.nKey], node.memory[self.nofNKey][neighbor])
            node.memory['test'].append(T)'''
        for neighbor in node.memory[self.nofNKey]:
            if self.calculate_G(node.memory[self.nKey], node.memory[self.nofNKey][neighbor]) < 0:
                return False
        return True

    def calculate_G(self, n, numberOfNeighbors):
        return n - 2*numberOfNeighbors



    STATUS = {
        'AVAILABLE' :saturacija.STATUS.get('AVAILABLE'),
        'ACTIVE': saturacija.STATUS.get('ACTIVE'),
        'PROCESSING': processing,
        'SATURATED': saturacija.STATUS.get('SATURATED'),
        'NON_MEDIAN': non_median,
        'MEDIAN': median,
        'SATURATED_MEDIAN': saturated_median,



    }
