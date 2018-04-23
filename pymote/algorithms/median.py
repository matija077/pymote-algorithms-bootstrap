from pymote.algorithm import Message
from pymote.algorithms.saturation import saturacija
from pymote.algorithm import NodeAlgorithm

class Median(saturacija):
    required_params = {}
    default_params = {'nofNKey': 'NumberOfNeighbors', 'nKey': 'NumberOfNodesInNetwork',
    'constantNeighborsKey': 'constantNeighbors'}

    def initialize(self, node):
        '''
            every node needs to know number of neighbors in the network and the sum of
            all neighbor child nodes and their children
        '''
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

    def prepare_message(self, node):
        return int(sum(node.memory[self.nofNKey].values())) + 1

    def process_message(self, node, message):
        node.memory[self.nofNKey][message.source] = message.data
        pass

    def resolve(self, node):
        '''
            saturation nodes: calculate number of nodes in the network
        '''
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
        '''
            Lemma 2.6.7 Entity x is a median if and only if G[y,x]>=0 for all neighbors y.
            Lemma 2.6.6 G[x,y]=g[T,x]−g[T,y], where g[T,x]=sum(d(x,y)) and g[T,y]=sum(d,(y,x))
                Also G[y,x]= n -2*numberOfNodes(sub_tree(y-x)), where (y-x) means sub_tree(y)
                without bridge(y,x)
            Lemma 2.6.8 If x is not the median, there exists a unique neighbor y such that
                G[y,x]<0; such a neighbor lies in the path from x to the median.
                This was not used in this version of algorithm. We are using Flood(net)
.
        '''
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

    def non_median(self, node, message):
        pass

    def median(self, node, message):
        pass

    def saturated_median(self, node, message):
        pass


    STATUS = {
        'AVAILABLE' :saturacija.STATUS.get('AVAILABLE'),
        'ACTIVE': saturacija.STATUS.get('ACTIVE'),
        'PROCESSING': processing,
        'SATURATED': saturacija.STATUS.get('SATURATED'),
        'NON_MEDIAN': non_median,
        'MEDIAN': median,
        'SATURATED_MEDIAN': saturated_median,



    }
