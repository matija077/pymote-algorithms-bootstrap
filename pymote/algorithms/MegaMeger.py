# -*- coding: utf-8 -*-
#12:45
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from random import random

class MegaMerger(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors', 'treeKey': 'TreeNeighbors', 'parentKey' : 'Parent', 'weightKey': 'Weight',
    'levelKey': 'Level', 'nameKey': 'Name', 'debugKey': 'DEBUG' , 'linkStatusKey':'LinkStatus'}

    def initializer(self):
        ini_nodes = []
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
           #node.memory[self.treeKey] = list(node.memory[self.neighborsKey])
            self.initialize(node)
            node.status = 'AVAILABLE'
            '''if random()<0.3:                #random initializers
                node.status = 'AVAILABLE'
                ini_nodes.append(node)'''

        # just for testing purposes
        node = self.network.nodes()[0]
        node.memory[self.levelKey] = 1
        node2 = self.network.nodes()[1]
        node2.memory[self.levelKey] = 1
        node2.memory[self.parentKey] = node
        node2.memory[self.nameKey] = node.memory[self.nameKey]
        node4 = self.network.nodes()[3]
        node4.memory[self.levelKey] = 2

        # starting node has lover lvl for absorpton to work
        
        ini_nodes.append(self.network.nodes()[1])
        
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))  # to je spontani impuls
        
        
        # ne znam kako radi ovaj ini_nodes YOLO
        #ini_node = self.network.nodes()[1]                                                         ### 0. ili 1. imalvl 1? odluci se
        #self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))

    def available(self, node, message):

        #inicijatori
        if message.header == NodeAlgorithm.INI: #Spontaneously
            prepared_data = self.prepare_message_data_concatenate(node)
            #for testing send Let us merge to the first neighbor.
            node.send(Message(header='Let Us Merge', data=prepared_data, destination=node.memory[self.neighborsKey][0]))
            node.send(Message(header='Let Us Merge', data=prepared_data, destination=node.memory[self.neighborsKey][1])) 
            ## Iskljucivo inicijatori, bilo jedan ili svi poslat ce svom prvom i drugm susjedu Let Us Merge
            node.status = 'PROCESSING'

        # ja ne kuzim kako rade ovi statusi stvarno
        if message.header=="Let Us Merge":
            # izradi novu funkciju!
            self.process_message_check_levels(node,message)
            #self.resolve(node, message)
            node.status = 'PROCESSING'

        '''node.send(Message(header='Activate', data='Activate'))
        if len(node.memory[self.neighborsKey])==1 : #ako je čvor list
            node.memory[self.parentKey] = list(node.memory[self.neighborsKey])[0]
            updated_data=self.prepare_message(node)
            node.send(Message(header='M', data = updated_data, destination = node.memory[self.parentKey]))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE' #izvrši se

    if message.header == 'Activate':
        destination_nodes = list(node.memory[self.treeKey])

        destination_nodes.remove(message.source)
        node.send(Message(header='Activate', data='Activate', destination=destination_nodes))
        if len(node.memory[self.treeKey])==1 :
            node.memory[self.parentKey] = list(node.memory[self.treeKey])[0]
            updated_data=self.prepare_message(node)
            node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
            node.status = 'PROCESSING'
        else:
            node.status='ACTIVE' #izvrši se'''

    def active(self, node, message):
        '''if message.header=='M':
            self.process_message(node,message)
            node.memory[self.treeKey].remove(message.source)
            if len(node.memory[self.treeKey])==1 :
                node.memory[self.parentKey] = list(node.memory[self.treeKey])[1]
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
                node.status = 'PROCESSING' '''
        pass

    def processing(self, node, message):
        if message.header=="Let Us Merge":
            # izradi novu funkciju!
            self.process_message_check_levels(node,message)
            #self.resolve(node, message)
            
        ## or umjesto || ?
        if message.header=="absorption+orientation_of_roads" or message.header=="absorption":
            
            node.memory[self.nameKey] = message.data[self.nameKey]
            node.memory[self.levelKey] = message.data[self.levelKey]
            #dal ce mozda prema internal /external linku mocu zakljuciti umjesto param begin?
            self.absorption(node, message)
            if message.header=="absorption+orientation_of_roads":
                #REDOSLJED FUNKCIJA MORA BITI OVAKAV. Prvo posaljemo parentu poruku, onda maknemo parenta.
                self.absorption(node, message, False, True)
                node.memory[self.parentKey] = message.source
            
    def saturated(self, node):
        pass

    def prepare_message(self,node):
        pass

    def prepare_message_data_concatenate(self, node):
      
        args = {self.nameKey: node.memory[self.nameKey], self.levelKey: node.memory[self.levelKey]}
        #data = ",".join(args)
        return args

    def process_message(self, node, message):
        pass

    def process_message_check_levels(self, node, message):
        if message.source.memory[self.levelKey] < node.memory[self.levelKey]:
            self.absorption(node, message, True)


    def absorption(self, node, message, param_begining=False, orientation_of_roads=False):
        #TODO prepare_message()
        if param_begining==True:
            prepared_data = self.prepare_message_data_concatenate(node)
            node.send(Message(header="absorption+orientation_of_roads", data=prepared_data, destination=message.source))
        else:
            prepared_data = message.data

            if orientation_of_roads==True:
                if node.memory[self.parentKey]!=None:
                    node.send(Message(header="absorption+orientation_of_roads", data=prepared_data, destination=node.memory[self.parentKey]))
                else:
                    # DEBUG
                    node.memory[self.debugKey] = "Nemam parenta"
                '''try:
                    node.send(Message(header="absorption+orientation_of_roads", data=prepared_data, destination=node.memory[self.parentKey]))
                except Exception as e:
                    # DeBUGGER
                    #node.memory[self.debugKey] = e
                    pass'''
            else:
                #mising internal, exernal
                destination_nodes = list(filter(lambda neighbor:  neighbor != node.memory[self.neighborsKey] and neighbor != message.source, node.memory[self.neighborsKey])) 
                node.send(Message(header="absorption", data=prepared_data, destination=destination_nodes))

    def initialize(self, node):
        node.memory[self.weightKey] = {}
        node.memory[self.linkStatusKey] = {}
        node.memory[self.levelKey] = 0
        node.memory[self.nameKey] = node.id
        node.memory[self.parentKey] = None
        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [min(node.id, neighbor.id),
            max(node.id, neighbor.id)]

        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [min(node.id, neighbor.id),max(node.id, neighbor.id)]
            node.memory[self.linkStatusKey][neighbor] = "UNUSED"

    def resolve(self,node, message):
        node.status='SATURATED'
        pass


    STATUS = {
              'AVAILABLE': available,
              'PROCESSING': processing,
              'SATURATED': saturated,
             }