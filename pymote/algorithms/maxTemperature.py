from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from pymote.sensor import NeighborsSensor
from pymote.algorithms.tempSensor import TemperatureSensor

'''
T(problem)
M(problem)>=2m=2(n-1)

simgui.net_gen = Networkgenerator(n)
simgui.net = simgui.net_gen.generate_random_-network()

from pymote.algorithms.prsa.maxTemperature import MaxFindng
simgui.net.algorithms = ( (maxFinding), )
simgui.sim = Simulation(simgui.net)

simgui.net.recalculate_edges()
'''

class MaxFinding(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors',\
        'temperatureKey': 'Temperature'}


    def initializer(self):
        for node in self.network.nodes():
            node.compositeSensor = ('TemperatureSensor',
                'NeighborsSensor')
            sensorRead = node.compositeSensor.read()
            print(sensorRead)
            node.memory[self.neighborsKey] = \
                sensorRead['Neighbors']
            node.memory[self.temperatureKey] = \
                sensorRead['Temperature']
            node.status = 'IDLE'
            node.memory['maxTemperature'] = sensorRead['Temperature']
            node.memory['tree-neighbors'] = []
            node.memory['root'] = False
        ini_node = self.network.nodes()[0]
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0,
                Message(destination=ini_node,
                header=NodeAlgorithm.INI))

    def initiator(self, node, message):
        node.send(Message(header="Q"))
        node.memory['counter'] = 0
        node.memory['root'] = True
        node.status = 'WORKING'

    def idle(self, node, message):
        if message.header == "Q":
            node.memory['parent'] = message.source
            node.memory['tree-neighbors'].append(node.memory['parent'])
            node.memory['counter'] = 1
            if node.memory['counter'] == len(node.memory['Neighbors']):
                node.send(Message(header='Yes',
                destination=node.memory['parent'],
                data=node.memory['maxTemperature']))
                node.status = 'WAITING'
            else:
                neighhborsWithoutParent = list(node.memory['Neighbors'])
                neighhborsWithoutParent.remove(node.memory['parent'])
                node.send(Message(header='Q',
                    destination=neighhborsWithoutParent))
                node.status = 'WORKING'

    def working(self, node, message):
        if (message.header == "Q") and (node.memory['counter'] >= 1):
            node.send(Message(header='No', destination=message.source))
        if message.header == "Yes":
            node.memory['tree-neighbors'].append(message.source)
            node.memory['counter'] += 1
            self.process_message(node, message.data)
            if node.memory['counter'] >= len(node.memory['Neighbors']) and \
                node.memory['root'] == False:
                node.send(Message(header='Yes',
                    destination=node.memory['parent'],
                    data=node.memory['maxTemperature']))
                node.status = 'WAITING'
            if node.memory['counter'] >= len(node.memory['Neighbors']) and \
                node.memory['root'] == True:
                node.send(Message(header="T",
                destination=node.memory['tree-neighbors'],
                data=node.memory['maxTemperature']))
                node.status = 'DONE'
        if message.header == "No":
            node.memory['counter'] += 1
            if node.memory['counter'] == len(node.memory['Neighbors']):
                node.send(Message(header='Yes',
                    destination=node.memory['parent'],
                    data=node.memory['maxTemperature']))
                node.status = 'WAITING'

    def waiting(self, node, message):
        if message.header == "T":
            self.process_message(node, message.data)
            neighhborsWithoutParent = list(node.memory['tree-neighbors'])
            neighhborsWithoutParent.remove(node.memory['parent'])
            node.send(Message(header="T",
                destination=neighhborsWithoutParent,
                data=node.memory['maxTemperature']))
            node.status = 'DONE'

    def done(self, node, message):
        pass

    def process_message(self, node, messageData):
        node.memory['maxTemperature'] = max(node.memory['maxTemperature'], messageData)


    '''def available(self, node, message):
        #node.send(Message(header='Activate'))
        node.memory['nodeNeighbors'] = list(node.memory[self.neighborsKey])
        isLeafCount = 1
        if len(node.memory['nodeNeighbors']) == isLeafCount:
            # self.send_message_to_parent(node)
            parent = node.memory['nodeNeighbors'][0]
            node.memory['parent'] = parent
            node.send(Message(header='Temperature',
                                destination=parent,
                                data=node.memory[self.temperatureKey]))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE'

    def active(self, node, message):
        # Receiving(M)
        if message.header == 'Temperature':
            self.process_message(node, message.data)
            node.memory['nodeNeighbors'].remove(message.source)
            isLeafCount = 1
            if len(node.memory['nodeNeighbors']) == isLeafCount:
                parent = node.memory['nodeNeighbors'][0]
                node.memory['parent'] = parent
                node.send(Message(header='Temperature',
                                    destination=parent,
                                    data=node.memory[self.temperatureKey]))
                node.status = 'PROCESSING'


    def processing(self, node, message):
        # receiving(M)
        if message.header == 'Temperature':
            self.process_message(node, message.data)
            self.resolve(node)

        if message.header == 'Notification':
            self.process_message(node, message.data)
            neighhborsWithoutParent = node.memory['Neighbors']
            neighhborsWithoutParent.remove(node.memory['parent'])
            node.send(Message(header='Notification',
                                destination=neighhborsWithoutParent))


    def saturated(self, node, message):
        pass'''

    '''def send_message_to_parent(self, node):
        parent = node.memory['nodeNeighbors'][0]
        message = self.prepare_message(node, parent)
        node.send(message)

    def prepare_message(self, node, parentNode):
        return Message(Message(header='Temperature',
                                destination=parentNode,
                                data=node.
                                memory[self.temperatureKey]))'''


    '''def process_message(self, node, messageData):
        node.memory['maxTemperature'] = max(node.memory['maxTemperature'], messageData)

    def resolve(self, node):
        neighhborsWithoutParent = node.memory['Neighbors']
        neighhborsWithoutParent.remove(node.memory['parent'])
        node.send(Message(header='Notification',
                        destination=neighhborsWithoutParent,
                        data=node.memory['maxTemperature']))
        node.status = 'SATURATED' '''



    STATUS = {
                'INITIATOR': initiator,
                'IDLE': idle,
                'WORKING': working,
                'WAITING': waiting,
                'DONE': done,
    }

    '''
    'AVAILABLE': available,
                'ACTIVE': active,
                'PROCESSING': processing,
                'SATURATED': saturated,'''